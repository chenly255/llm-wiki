#!/usr/bin/env python3
"""微信公众号文章兜底抓取器 (llm-wiki fallback)。

用途：当 tavily_extract 抓不到或抓得不干净时，直连公众号单篇文章页
(mp.weixin.qq.com/s/...) 取正文。单篇文章页腾讯不反爬，直连即可。

相比 tavily 的优势：
  - 能抓到图片（处理懒加载 data-src），可下载到本地
  - 能提取标题 / 作者 / 发布时间等元信息
  - 自动剥掉页脚的"小程序 / Scan to Follow / Got It"等垃圾

依赖：requests, beautifulsoup4, lxml（均已装）。不需要 markdownify。

用法：
    python3 fetch_wechat.py <url>                      # 打印 markdown 到 stdout
    python3 fetch_wechat.py <url> --images-dir DIR     # 同时把图片下载到 DIR
    python3 fetch_wechat.py <url> --json               # 输出结构化 JSON

注意代理：本机 17890 仅供 Claude Code 自身。抓公众号属境外访问，应走 17891：
    http_proxy=http://127.0.0.1:17891 https_proxy=http://127.0.0.1:17891 \
    python3 fetch_wechat.py <url>
"""
import argparse
import json
import os
import re
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def fetch_html(url: str, timeout: int = 30) -> str:
    headers = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    # 公众号页面固定 UTF-8；requests 无 charset 头时会误判为 ISO-8859-1，故锁死
    resp.encoding = "utf-8"
    return resp.text


def _clean(text: str) -> str:
    return re.sub(r"[ \t   ]+", " ", text or "").strip()


def extract_meta(soup: BeautifulSoup, url: str) -> dict:
    def first_text(*selectors):
        for sel in selectors:
            el = soup.select_one(sel)
            if el and _clean(el.get_text()):
                return _clean(el.get_text())
        return None

    title = first_text("#activity-name", "h1.rich_media_title", "meta[property='og:title']")
    if not title:
        og = soup.select_one("meta[property='og:title']")
        title = _clean(og["content"]) if og and og.get("content") else None
    author = first_text("#js_name", ".rich_media_meta_nickname", "#meta_content .rich_media_meta_text")
    # 发布时间常在 #publish_time 或 script 变量 ct/createTime 里
    publish = first_text("#publish_time", "em#publish_time")
    if not publish:
        m = re.search(r'(?:var\s+)?(?:ct|createTime)\s*=\s*["\']?(\d{9,})', soup_text_for_scripts(soup))
        if m:
            try:
                import datetime
                publish = datetime.datetime.fromtimestamp(int(m.group(1))).strftime("%Y-%m-%d %H:%M")
            except Exception:
                publish = None
    return {"title": title, "author": author, "publish_time": publish, "url": url}


def soup_text_for_scripts(soup: BeautifulSoup) -> str:
    return "\n".join(s.get_text() for s in soup.find_all("script"))


def _img_url(tag: Tag) -> str | None:
    # 公众号图片懒加载：真实地址在 data-src
    for attr in ("data-src", "data-backsrc", "src"):
        v = tag.get(attr)
        if v and not v.startswith("data:"):
            return v
    return None


def node_to_md(node, images: list) -> str:
    """递归把正文 DOM 转成 markdown。只处理公众号常见标签，够用即可。"""
    if isinstance(node, NavigableString):
        return _clean(str(node))
    if not isinstance(node, Tag):
        return ""

    name = node.name.lower()

    if name == "img":
        src = _img_url(node)
        if src:
            idx = len(images) + 1
            images.append(src)
            return f"\n![image{idx}]({src})\n"
        return ""

    if name in ("script", "style", "mpvoice", "qqmusic"):
        return ""

    if name in ("br",):
        return "\n"

    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(name[1])
        inner = "".join(node_to_md(c, images) for c in node.children).strip()
        return f"\n\n{'#' * level} {inner}\n\n" if inner else ""

    if name in ("strong", "b"):
        inner = "".join(node_to_md(c, images) for c in node.children).strip()
        return f"**{inner}**" if inner else ""

    if name in ("em", "i"):
        inner = "".join(node_to_md(c, images) for c in node.children).strip()
        return f"*{inner}*" if inner else ""

    if name == "a":
        inner = "".join(node_to_md(c, images) for c in node.children).strip()
        href = node.get("href", "")
        if href and href.startswith("http"):
            return f"[{inner}]({href})" if inner else ""
        return inner

    if name == "li":
        inner = "".join(node_to_md(c, images) for c in node.children).strip()
        return f"\n- {inner}" if inner else ""

    if name in ("ul", "ol"):
        return "\n" + "".join(node_to_md(c, images) for c in node.children) + "\n"

    if name in ("blockquote",):
        inner = "".join(node_to_md(c, images) for c in node.children).strip()
        return "\n\n" + "\n".join(f"> {ln}" for ln in inner.splitlines() if ln) + "\n\n"

    if name in ("pre", "code"):
        text = node.get_text()
        if "\n" in text:
            return f"\n\n```\n{text.rstrip()}\n```\n\n"
        return f"`{_clean(text)}`"

    if name in ("p", "section", "div"):
        inner = "".join(node_to_md(c, images) for c in node.children)
        # 段落之间留空行；section/div 常被公众号嵌套很多层，靠 strip 收敛
        block = inner.strip("\n ")
        return f"\n\n{block}\n\n" if block else ""

    # 其它标签透传子节点
    return "".join(node_to_md(c, images) for c in node.children)


def html_to_markdown(soup: BeautifulSoup) -> tuple[str, list]:
    content = soup.select_one("#js_content") or soup.select_one(".rich_media_content")
    if content is None:
        return "", []
    images: list = []
    md = node_to_md(content, images)
    # 收敛多余空行
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md, images


def download_images(images: list, images_dir: str, proxies=None) -> dict:
    os.makedirs(images_dir, exist_ok=True)
    mapping = {}
    headers = {"User-Agent": UA, "Referer": "https://mp.weixin.qq.com/"}
    for i, url in enumerate(images, 1):
        try:
            r = requests.get(url, headers=headers, timeout=30, proxies=proxies)
            r.raise_for_status()
            ctype = r.headers.get("Content-Type", "")
            ext = "png"
            if "jpeg" in ctype or "jpg" in ctype:
                ext = "jpg"
            elif "gif" in ctype:
                ext = "gif"
            elif "webp" in ctype:
                ext = "webp"
            elif "wx_fmt=" in url:
                ext = re.search(r"wx_fmt=(\w+)", url).group(1)
            fname = f"image{i}.{ext}"
            with open(os.path.join(images_dir, fname), "wb") as f:
                f.write(r.content)
            mapping[url] = fname
        except Exception as e:
            print(f"[warn] image {i} 下载失败: {e}", file=sys.stderr)
    return mapping


def main():
    ap = argparse.ArgumentParser(description="微信公众号文章兜底抓取器")
    ap.add_argument("url")
    ap.add_argument("--images-dir", help="把图片下载到该目录，并把正文图片改为本地相对路径")
    ap.add_argument("--json", action="store_true", help="输出结构化 JSON 而非 markdown")
    args = ap.parse_args()

    if "mp.weixin.qq.com" not in args.url:
        print("[warn] 这不是 mp.weixin.qq.com 链接，可能不是公众号文章。", file=sys.stderr)

    html = fetch_html(args.url)
    soup = BeautifulSoup(html, "lxml")
    meta = extract_meta(soup, args.url)
    md, images = html_to_markdown(soup)

    if not md or len(md) < 50:
        print("[error] 未能从页面提取到正文（可能文章已删除/需登录/链接失效）。", file=sys.stderr)
        sys.exit(2)

    if args.images_dir and images:
        # 下载用环境里的代理设置（脚本默认继承 env；境外访问应在外层设 17891）
        mapping = download_images(images, args.images_dir)
        for src, fname in mapping.items():
            md = md.replace(f"]({src})", f"](images/{fname})")

    if args.json:
        print(json.dumps({**meta, "markdown": md, "image_count": len(images)}, ensure_ascii=False, indent=2))
        return

    # markdown 带 YAML frontmatter
    fm = ["---"]
    fm.append(f"title: {meta.get('title') or ''}")
    fm.append(f"author: {meta.get('author') or ''}")
    fm.append(f"publish_time: {meta.get('publish_time') or ''}")
    fm.append(f"source: {meta['url']}")
    fm.append("---\n")
    print("\n".join(fm))
    if meta.get("title"):
        print(f"# {meta['title']}\n")
    print(md)


if __name__ == "__main__":
    main()
