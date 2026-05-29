#!/usr/bin/env python3
"""YouTube 字幕（现成文字稿）抓取器 (llm-wiki helper)。

设计目标（Lily 指定）：优先拿现成的 manuscript（字幕），只做文本提取，**不生成 PDF**，
不下载视频本身。重型的图文 PDF 笔记仍由独立的 youtube-render-pdf skill 负责（互不干扰）。

三层降级：
  1. 人工字幕（作者上传的，质量最好）—— 这就是"现成 manuscript"
  2. 自动字幕（YouTube 机器生成）
  3. 都没有 → 报告 none，提示可用 video-notes 环境里的 whisper 听写（重，占 GPU，先问用户）

复用现有环境：yt-dlp / ffmpeg / whisper 都在 conda 环境 video-notes 里，不另装。
本脚本只调 yt-dlp 抓字幕；whisper 听写那一步交回上层按需触发（避免在脚本里硬塞重依赖）。

用法（境外访问 → 走 17891 代理）：
    http_proxy=http://127.0.0.1:17891 https_proxy=http://127.0.0.1:17891 \
    all_proxy=socks5h://127.0.0.1:17891 ALL_PROXY=socks5h://127.0.0.1:17891 \
    python3 fetch_youtube.py "<youtube-url>" [--langs zh,en] [--json]

输出：默认 markdown（带 YAML frontmatter）；--json 输出结构化
      {title, uploader, duration, url, sub_type: manual|auto|none, lang, transcript}
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# yt-dlp 优先用 PATH 上的；找不到再退到 video-notes 环境的已知位置
_FALLBACK_YTDLP = "/data/liying_environ/anaconda3_liying/envs/video-notes/bin/yt-dlp"


def find_ytdlp() -> str:
    p = shutil.which("yt-dlp")
    if p:
        return p
    if os.path.exists(_FALLBACK_YTDLP):
        return _FALLBACK_YTDLP
    print("[error] 找不到 yt-dlp。它在 conda 环境 video-notes 里：\n"
          "  conda activate video-notes  然后再跑本脚本。", file=sys.stderr)
    sys.exit(3)


def run(cmd: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def get_metadata(ytdlp: str, url: str) -> dict:
    cp = run([ytdlp, "-J", "--skip-download", "--no-warnings", url])
    if cp.returncode != 0:
        print(f"[error] yt-dlp 取元信息失败：{cp.stderr.strip()[:500]}", file=sys.stderr)
        sys.exit(2)
    return json.loads(cp.stdout)


def pick_lang(available: dict, prefs: list) -> str | None:
    """available: {lang_code: [...]}; prefs: ['zh','en'] 等。模糊匹配前缀。"""
    if not available:
        return None
    keys = list(available.keys())
    for pref in prefs:
        # 精确
        if pref in available:
            return pref
        # 前缀模糊：zh 命中 zh-Hans / zh-CN；en 命中 en-US 等
        for k in keys:
            if k.lower().startswith(pref.lower()):
                return k
    # 没匹配偏好就给第一个
    return keys[0]


def vtt_to_text(path: str) -> str:
    """把 .vtt 字幕转成干净纯文本：去时间轴/标签，去滚动重复行。"""
    lines_out = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    for block in raw.split("\n"):
        s = block.strip()
        if not s or s == "WEBVTT" or "-->" in s:
            continue
        if s.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if re.fullmatch(r"\d+", s):  # 序号行
            continue
        s = re.sub(r"<[^>]+>", "", s)        # 去 <c>、<00:00:00.000> 等标签
        s = re.sub(r"\s+", " ", s).strip()
        if not s:
            continue
        # 去掉与上一行完全相同的滚动重复（自动字幕常见）
        if lines_out and lines_out[-1] == s:
            continue
        lines_out.append(s)
    # 自动字幕还会出现"上一行是下一行前缀"的滚动累积，再压一遍
    deduped = []
    for s in lines_out:
        if deduped and (s.startswith(deduped[-1]) or deduped[-1].endswith(s)):
            if len(s) >= len(deduped[-1]):
                deduped[-1] = s
            continue
        deduped.append(s)
    return "\n".join(deduped).strip()


def fetch_subs(ytdlp: str, url: str, lang: str, auto: bool, outdir: str) -> str | None:
    flag = "--write-auto-subs" if auto else "--write-subs"
    cp = run([ytdlp, "--skip-download", flag, "--sub-langs", lang,
              "--sub-format", "vtt/best", "--no-warnings",
              "-o", os.path.join(outdir, "sub.%(ext)s"), url])
    files = glob.glob(os.path.join(outdir, "*.vtt"))
    if not files:
        return None
    return vtt_to_text(files[0])


def main():
    ap = argparse.ArgumentParser(description="YouTube 字幕抓取器（不出 PDF）")
    ap.add_argument("url")
    ap.add_argument("--langs", default="zh,en", help="偏好语言，逗号分隔，默认 zh,en")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    prefs = [x.strip() for x in args.langs.split(",") if x.strip()]
    ytdlp = find_ytdlp()
    meta = get_metadata(ytdlp, args.url)

    title = meta.get("title")
    uploader = meta.get("uploader") or meta.get("channel")
    duration = meta.get("duration_string") or (str(meta.get("duration", "")) + "s")
    manual = meta.get("subtitles") or {}
    auto = meta.get("automatic_captions") or {}

    sub_type, lang, transcript = "none", None, None
    with tempfile.TemporaryDirectory() as td:
        # Tier 1：人工字幕
        lang = pick_lang(manual, prefs)
        if lang:
            transcript = fetch_subs(ytdlp, args.url, lang, auto=False, outdir=td)
            if transcript:
                sub_type = "manual"
        # Tier 2：自动字幕
        if not transcript:
            lang = pick_lang(auto, prefs)
            if lang:
                transcript = fetch_subs(ytdlp, args.url, lang, auto=True, outdir=td)
                if transcript:
                    sub_type = "auto"

    result = {
        "title": title, "uploader": uploader, "duration": duration,
        "url": args.url, "sub_type": sub_type, "lang": lang,
        "transcript": transcript,
    }

    if sub_type == "none":
        print("[info] 该视频没有任何字幕（人工/自动都没有）。", file=sys.stderr)
        print("[info] 如需文字，可用 video-notes 环境里的 whisper 听写（重，占 GPU）——"
              "请回上层让用户确认后再做。", file=sys.stderr)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    fm = ["---", f"title: {title or ''}", f"uploader: {uploader or ''}",
          f"duration: {duration or ''}", f"source: {args.url}",
          f"subtitle: {sub_type} ({lang or '-'})", "---\n"]
    print("\n".join(fm))
    if title:
        print(f"# {title}\n")
    print(transcript or "（无字幕，未提取到文本。）")


if __name__ == "__main__":
    main()
