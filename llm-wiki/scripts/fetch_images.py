#!/usr/bin/env python3
"""通用图片批量下载器 (llm-wiki helper)。

用途：把一批图片 URL 下载到本地目录，自动判扩展名、按序命名、可带 Referer
绕防盗链。主要给小红书入库用（图床地址带时效签名，会过期，须及时下载归档），
也可用于任何"拿到一批图片地址要存下来"的场景。

URL 来源：命令行参数，或 stdin（每行一个）。

用法：
    python3 fetch_images.py --out DIR --referer https://www.xiaohongshu.com/ URL1 URL2 ...
    echo "URL1\nURL2" | python3 fetch_images.py --out DIR --referer https://www.xiaohongshu.com/

输出：DIR/image1.ext, image2.ext ...；并打印 JSON 映射 {url: 本地文件名} 到 stdout。

注意代理：境外/CDN 访问应走 17891（见全局规则），在外层设好 http_proxy 等再调。
小红书图床带防盗链，必须传 --referer https://www.xiaohongshu.com/ 才能 200。
"""
import argparse
import json
import os
import re
import sys

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def guess_ext(url: str, content_type: str) -> str:
    ct = (content_type or "").lower()
    if "webp" in ct:
        return "webp"
    if "jpeg" in ct or "jpg" in ct:
        return "jpg"
    if "png" in ct:
        return "png"
    if "gif" in ct:
        return "gif"
    # 从 URL 里猜（公众号 wx_fmt=，或常规后缀）
    m = re.search(r"wx_fmt=(\w+)", url)
    if m:
        return m.group(1)
    m = re.search(r"\.(jpe?g|png|webp|gif)(?:\?|$)", url, re.I)
    if m:
        return m.group(1).lower().replace("jpeg", "jpg")
    if "webp" in url:
        return "webp"
    return "jpg"


def main():
    ap = argparse.ArgumentParser(description="通用图片批量下载器")
    ap.add_argument("urls", nargs="*", help="图片 URL（也可从 stdin 逐行读）")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--referer", default="", help="Referer 头（小红书需 https://www.xiaohongshu.com/）")
    ap.add_argument("--prefix", default="image", help="文件名前缀，默认 image")
    ap.add_argument("--start", type=int, default=1, help="起始序号，默认 1")
    args = ap.parse_args()

    urls = list(args.urls)
    if not sys.stdin.isatty():
        urls += [ln.strip() for ln in sys.stdin if ln.strip()]
    # 去重保序
    seen, deduped = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    urls = deduped

    if not urls:
        print("[error] 没有提供任何 URL。", file=sys.stderr)
        sys.exit(2)

    os.makedirs(args.out, exist_ok=True)
    headers = {"User-Agent": UA}
    if args.referer:
        headers["Referer"] = args.referer

    mapping = {}
    for i, url in enumerate(urls, args.start):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            ext = guess_ext(url, r.headers.get("Content-Type", ""))
            fname = f"{args.prefix}{i}.{ext}"
            with open(os.path.join(args.out, fname), "wb") as f:
                f.write(r.content)
            mapping[url] = fname
            print(f"[ok] {fname}  ({len(r.content)} bytes)", file=sys.stderr)
        except Exception as e:
            print(f"[warn] 下载失败 {url}: {e}", file=sys.stderr)

    print(json.dumps(mapping, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
