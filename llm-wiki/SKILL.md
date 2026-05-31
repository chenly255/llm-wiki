---
name: llm-wiki
description: >
  Build and maintain LLM-powered personal/local knowledge bases (inspired by Karpathy + kepano).
  这是"个人知识库"，本地文件系统上的 wiki，与团队共享云端知识库（kb-search）完全不同。
  TRIGGER when: user mentions personal knowledge base, wiki compilation, knowledge management with LLM,
  "build a wiki", "organize my notes/papers/articles", "llm wiki", "个人知识库", or uses
  /llm-wiki command. Also trigger when user says "整理知识库", "编译wiki",
  "知识工厂", "帮我整理这些资料". Also trigger when the user pastes a content URL (微信公众号
  mp.weixin.qq.com link, 小红书 xiaohongshu.com / xhslink.com note, blog, paper, video) and
  wants it saved/ingested ("存到知识库", "把这个链接存下来", "存这篇公众号", "存这篇小红书").
  Subcommands: init, digest, compile, query, check, export, trust, status, save, read-paper.
  DO NOT trigger when: 用户说"搜共享知识库"、"搜论文"、"搜文献"、"kb search"——这些属于 kb-search skill。
  区分规则：涉及"整理/构建/管理个人知识"→ 用 llm-wiki；
  涉及"搜索/检索团队共享文献或资料"→ 用 kb-search。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# LLM Wiki

Build and maintain LLM-powered personal knowledge bases.

Two core principles:
1. **Karpathy**: Raw docs → LLM "compiles" a structured wiki → Q&A → outputs loop back in.
2. **kepano (Obsidian CEO)**: AI-generated content must be **isolated** from your trusted knowledge. Only `trust` moves content to your main vault after your explicit approval.

> **铁律 · 获取 ≠ 入库（ACQUIRE ≠ INGEST）**
> When the user pastes ANY link (WeChat / Xiaohongshu / YouTube / blog / paper …), the default
> action is to **FETCH the content and SHOW it** — never silently write it into the knowledge
> base. Only ingest (create source summary / wiki articles / download assets into the vault)
> when the user EXPLICITLY says so ("加进去 / 存到知识库 / 入库 / save it"). Fetching is free;
> ingesting is a deliberate, user-triggered act. If unsure whether the user wants ingestion,
> fetch first, then ask "要把这篇加进知识库吗？".

---

## Global Configuration

llm-wiki uses a global config file to remember the user's knowledge base path across sessions.

**Config file:** `~/.claude/llm-wiki.json`

```json
{
  "wiki_path": "/absolute/path/to/your/knowledge-base"
}
```

### Locate Wiki Procedure (MUST follow for ALL subcommands except `init`)

Every subcommand (digest, compile, query, check, export, trust, status, save, read-paper) MUST locate the wiki before doing anything. Follow this order:

1. **Check global config**: read `~/.claude/llm-wiki.json`. If it exists and `wiki_path` points to a directory with a valid `.kf.md`, use it.
2. **Check current directory**: if no global config, look for `.kf.md` in the current working directory.
3. **Ask the user**: if neither works, tell the user:
   > "未找到知识库配置。请告诉我你的知识库路径，或运行 `init` 创建一个新的。"
   
   After the user provides a path, validate it (check for `.kf.md`), then **save it to `~/.claude/llm-wiki.json`** so they never need to specify it again.

**IMPORTANT:** Never hardcode any user-specific path in this skill file. Always resolve paths dynamically via the procedure above.

---

## Optional Dependencies (Skills & Tools)

llm-wiki can leverage other Claude Code skills for richer content ingestion. These are **optional** — the skill works without them, but will prompt the user when a dependency would help.

| Dependency | What it does | When needed | How to check |
|-----------|-------------|-------------|-------------|
| `video-notes` conda env (`yt-dlp`+`ffmpeg`+`whisper`) | Pull video subtitles → text (default), or whisper-transcribe when no subs | Any YouTube/Bilibili URL where the user wants the **text** | `conda activate video-notes && yt-dlp --version` |
| `/youtube-render-pdf` skill (OPT-IN) | Heavy figure-rich LaTeX+PDF teaching note | ONLY when user explicitly wants a **PDF** note | `ls ~/.claude/skills/youtube-render-pdf/SKILL.md` |
| `/bilibili-render-pdf` skill (OPT-IN) | Heavy figure-rich LaTeX+PDF teaching note | ONLY when user explicitly wants a **PDF** note | `ls ~/.claude/skills/bilibili-render-pdf/SKILL.md` |
| `tavily` MCP server | Web page extraction and search | When processing web URLs (blogs, news, WeChat articles) | Check if tavily tools are available in the current session |
| `github` MCP server | GitHub repo extraction | When processing GitHub repo URLs | Check if github MCP tools are available in the current session |
| `pymupdf4llm` (Python) | Enhanced PDF to Markdown conversion | When processing PDF files | `python3 -c "import pymupdf4llm"` |
| `MinerU` (conda env: mineru) | Best-quality PDF→MD conversion (LaTeX formulas, tables, figures) | `read-paper` and academic PDF processing | `conda run -n mineru mineru --version` |

#### MinerU Runtime Configuration (IMPORTANT)

MinerU 3.0+ requires specific environment variables to work correctly:

```bash
# Step 1: 先选一张空闲 GPU（不要硬编码 GPU 0 — 它经常被别人占满！）
GPU_ID=$(nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader,nounits \
  | awk -F', ' '$2<10 {print $1; exit}')
echo "Using GPU $GPU_ID"

# Step 2: 跑 mineru — 默认用 pipeline 后端（快 7×，原生 PDF 质量没差别）
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
  MINERU_MODEL_SOURCE=local \
  CUDA_VISIBLE_DEVICES=$GPU_ID \
  conda run -n mineru \
  mineru -p "{pdf_path}" -o "{output_path}" -b pipeline
```

Key points:
- **MUST disable proxy** (`env -u http_proxy ...`) — MinerU tries to phone home otherwise.
- **MUST set `MINERU_MODEL_SOURCE=local`** — models are pre-downloaded at `/data3/liying/mineru_models/`.
- **MUST pick a free GPU dynamically** — do NOT hardcode `CUDA_VISIBLE_DEVICES=0`.
  GPU 0 on this machine is frequently 100% busy (e.g., by sc-bias). If mineru grabs a
  busy card it competes for compute and gets several times slower (looks like it's not
  using GPU at all). Always run `nvidia-smi` first and pick a card with <10% util.
- **Default backend is now `pipeline`** (use `-b pipeline`). For a 16-page native PDF on an
  idle A800 it finishes in ~60–70 seconds. Pipeline uses 6 small models (Layout, OCR, MFR
  formula recognition, OriCls orientation, TabCls + TabRec table recognition) totalling 2.4 GB,
  all GPU-accelerated.
- **Why default switched away from hybrid-auto-engine**: hybrid runs pipeline + a 2.2 GB
  VLM (MinerU2.5-2509) per page and merges. On the STAligner Nature paper benchmark
  (16 pages, original PDF), pipeline produced **identical formula count (18 vs 18)** and
  ~93 % same markdown size as hybrid, but in 65 s vs ~480 s. The VLM only helps on
  scanned PDFs, handwriting, badly OCR'd legacy papers, or very complex multi-page tables.
- **When to fall back to hybrid** (add `-b hybrid` instead, or drop `-b` entirely): scanned
  PDFs / image-only PDFs / handwritten content / user explicitly asks for highest accuracy.
- Config file: `~/mineru.json` (auto-generated, points to local models).
- Models location: `/data3/liying/mineru_models/modelscope_cache/models/OpenDataLab/`.

**Output directory layout differs by backend:**
- `-b pipeline` (default): `{output}/{name}/auto/{name}.md` + `auto/images/`
- `-b hybrid` (fallback for scanned PDFs): `{output}/{name}/hybrid_auto/{name}.md` + `hybrid_auto/images/`

The `read-paper` step below picks files from `auto/` by default. If you fall back to
hybrid for a scanned PDF, change the source path to `hybrid_auto/` accordingly.

### Dependency Resolution

When a URL or file requires an unavailable dependency:

1. **Inform the user** what's missing and why it's needed.
2. **Offer to help install** if possible:
   - For skills: "要我帮你安装 `/bilibili-render-pdf` skill 吗？"
   - For Python packages: "要我运行 `pip install pymupdf4llm` 吗？"
   - For MCP servers: "你需要在 Claude Code 设置中配置 tavily MCP server。"
3. **Offer a fallback** if one exists (e.g., use `tavily_extract` instead of a missing skill).
4. **Never silently skip** — always tell the user what happened and what they can do.

## Project Structure

```
<project-root>/
├── raw/
│   ├── inbox/              # Drop new materials here (files OR url-list files)
│   └── sources/            # Processed originals (LLM moves here after ingest)
├── wiki/                   # Compiled wiki (LLM's domain — don't edit manually)
│   ├── _index.md           # Master index with 1-line summaries
│   ├── _graph.md           # Backlink graph + Mermaid knowledge graph
│   ├── concepts/           # Concept articles (ideas, methods, patterns)
│   ├── entities/           # Entity articles (people, tools, orgs, datasets)
│   └── sources/            # Source summaries (1 per digested document)
├── papers/                 # Structured literature library (via read-paper)
│   ├── _papers_index.md    # Master paper index (title, authors, year, tags)
│   └── {paper-slug}/       # One folder per paper (GXL Sy-inspired)
│       ├── meta.json       # Structured metadata
│       ├── paper.pdf       # Original PDF (renamed to title)
│       ├── full.md         # Complete markdown (from MinerU)
│       ├── sections/       # Split by section headings
│       ├── figures/        # Extracted images
│       └── README.md       # Quick navigation index
├── output/                 # Generated deliverables
│   ├── reports/
│   ├── slides/
│   └── charts/
├── trusted/               # Content you approved via `trust` (your trusted knowledge)
├── log.md                  # Operation log (auto-maintained)
└── .kf.md                  # Project config
```

## The Pipeline

```
inbox/ (files + URLs) ──digest──→ sources/    (tag & move)
                                │
                             compile     (build wiki)
                                │
                                ▼
                             wiki/       (concepts + entities + source summaries + Mermaid graph)
                                │
                        ┌───────┼───────┐
                        ▼       ▼       ▼
                     query    check    export
                        │       │       │
                        └───────┼───────┘
                                ▼
                              trust     (you approve → trusted/)
```

---

## Content Handlers (decoupled by knowledge type)

llm-wiki is **decoupled by knowledge type**. Each type declares two INDEPENDENT things —
**how to FETCH it (处理方式)** and **how to INGEST it (入库方式)**. Adding a new type = adding
one row + its handler section; the core flow never changes. Retrieval-only sources (semantic
search backends) are a SEPARATE axis — they are queried, never ingested (see
[External Retrieval Sources](#external-retrieval-sources)).

| Knowledge type | Detect | FETCH (处理方式) | INGEST (入库方式) | Handler section |
|---|---|---|---|---|
| WeChat article | `mp.weixin.qq.com` | tavily_extract → `scripts/fetch_wechat.py` | `wiki/sources/` article summary | [WeChat](#wechat-article-processing) |
| Xiaohongshu note | `xiaohongshu.com` / `xhslink.com` | tavily_extract + `fetch_images.py` + **image→text via Read/vision** | note summary + images, image-text merged into body | [Xiaohongshu](#xiaohongshu-note-processing) |
| YouTube / Bilibili | `youtube.com`/`youtu.be`/`bilibili.com`/`b23.tv` | `scripts/fetch_youtube.py` (subtitles→text, NO PDF) | video transcript summary | [Video](#video-url-processing) |
| Academic PDF / arXiv | `.pdf` file / `arxiv.org` | MinerU → md+figures | `papers/{slug}/` structured folder | [read-paper](#10-read-paper--import-and-structure-a-scientific-paper) |
| Web page (blog/docs) | other http(s) | tavily_extract / web reader | article summary | Extraction Strategy table |
| Code repo | `github.com`/`gitlab.com` | GitHub MCP / `git clone` | entity (tool) summary | [Code Repo](#code-repository-processing) |
| Plain file | `.md/.txt/.py/...` | Read | source summary | digest step 6 |
| **Semantic retrieval source** | n/a (query-time) | external RAG (e.g. private DashVector) | **never ingested — query-only** | [External Retrieval Sources](#external-retrieval-sources) |

Two universal rules cut across every handler: **获取 ≠ 入库** (fetch & show by default; ingest
only on explicit request) and **provenance** (every ingested item records its `> Source:`).

## URL Handling

llm-wiki supports ingesting content from URLs. Users can drop URL list files into `raw/inbox/`.

### URL List File Format

A `.txt` or `.md` file in inbox where each line is a URL:
```
https://x.com/karpathy/status/2039805659525644595
https://mp.weixin.qq.com/s/xxxxx
https://arxiv.org/abs/2401.00001
https://youtube.com/watch?v=xxxxx
```

### Extraction Strategy (by domain)

| Domain | Primary Tool | Fallback |
|--------|-------------|----------|
| `youtube.com` / `youtu.be` | `scripts/fetch_youtube.py` — pulls existing subtitles → clean text, **NO PDF, no video download**. See [Video URL Processing](#video-url-processing). | no subs → whisper (video-notes env, ask first) → `/youtube-render-pdf` only if user explicitly wants a figure-rich PDF |
| `bilibili.com` / `b23.tv` | `scripts/fetch_youtube.py` (yt-dlp supports bilibili too) → text if subs exist | bilibili 常无字幕 → whisper (video-notes env, ask first) → `/bilibili-render-pdf` only if user explicitly wants a PDF |
| `x.com` / `twitter.com` | `web_reader` | Prompt user to copy content manually |
| `mp.weixin.qq.com` | `tavily_extract` | `scripts/fetch_wechat.py` (local direct fetch) → prompt user to copy manually. See [WeChat Article Processing](#wechat-article-processing). |
| `arxiv.org` | `web_reader` | `tavily_extract` |
| `zhihu.com` | — | Anti-scraping blocks extraction — prompt user to copy content manually |
| `xiaohongshu.com` / `xhslink.com` | `tavily_extract` (works — note text + image URLs come back) | `scripts/fetch_images.py` for image archival → prompt user to copy manually. See [Xiaohongshu Note Processing](#xiaohongshu-note-processing). |
| `github.com` / `gitlab.com` | GitHub MCP (`get_file_contents` for tree + README + key files) | `git clone` + Bash + Read |
| Other (blogs, docs, Medium) | `web_reader` | `tavily_extract` |

### Video URL Processing

**Design intent (Lily):** for videos the goal is the **text content**, not a fancy document.
Prefer a ready-made transcript (subtitles = "现成 manuscript"), extract text, **never generate
a PDF by default**. The heavy figure-rich PDF skills (`youtube-render-pdf` / `bilibili-render-pdf`)
are kept as an OPT-IN only when the user explicitly asks for a PDF note. Remember the
**获取 ≠ 入库** rule — fetch & show the transcript; only ingest when the user says so.

**Reused environment:** `yt-dlp`, `ffmpeg`, and `whisper` all already live in conda env
`video-notes`. Do NOT install them again. `scripts/fetch_youtube.py` finds yt-dlp automatically
(PATH → video-notes env). It works for YouTube AND Bilibili (yt-dlp supports both).

**Tier 1 — existing subtitles → text (default, light, no PDF, no video download):**
   ```bash
   eval "$(conda shell.bash hook)" && conda activate video-notes   # or let the script auto-find yt-dlp
   http_proxy=http://127.0.0.1:17891 https_proxy=http://127.0.0.1:17891 \
   all_proxy=socks5h://127.0.0.1:17891 ALL_PROXY=socks5h://127.0.0.1:17891 \
   python3 ~/.claude/skills/llm-wiki/scripts/fetch_youtube.py "<url>" --langs zh,en --json
   ```
   - Internally: Tier 1a manual subtitles (best) → Tier 1b auto captions. `sub_type` in the
     output tells you which (`manual` / `auto` / `none`). `--langs` sets language preference
     (default `zh,en`, fuzzy-matches `zh-Hans`/`zh-CN`/`en-US`…).
   - Overseas access → MUST use 17891 proxy (yt-dlp reads `http_proxy`/`ALL_PROXY` env).
   - Output: clean transcript text. Treat it as the "document" for a source summary IF the
     user wants it ingested.

**Tier 2 — no subtitles at all (`sub_type: none`):** the video has neither manual nor auto
   captions. Transcription then needs Whisper (available in the `video-notes` env, but it's
   **heavy / GPU-bound**). **Ask the user first** before running it:
   > "这个视频没有字幕。要我用 whisper 听写吗？（会下载音轨 + 占 GPU，慢一些）"
   If yes: download audio with yt-dlp (`-f bestaudio -x`) into a temp dir, run whisper in the
   video-notes env, then treat the transcript like Tier 1. (Pick a free GPU like the MinerU
   section does — don't hardcode GPU 0.)

**Tier 3 — figure-rich PDF note (OPT-IN only):** ONLY when the user explicitly asks for a
   teaching PDF / 图文笔记, invoke the dedicated skill via the Skill tool
   (`youtube-render-pdf` / `bilibili-render-pdf`). This downloads the full video, extracts key
   frames, builds LaTeX, and compiles a PDF — do not trigger it for plain text-extraction asks.

**Source naming for videos:**
   - `youtube.com/watch?v=xxx` → `youtube-{title-slug}`
   - `bilibili.com/video/BV1xxxx` → `bilibili-{title-slug}`

### WeChat Article Processing

When a `mp.weixin.qq.com/s/...` URL is detected (in inbox, a URL list, or pasted directly in
conversation), use this **3-tier fallback chain**. Single-article pages are public and NOT
behind WeChat's anti-scraping wall (that wall only guards *batch history-list / read-count*
crawling, which we never do). So extraction is reliable.

**Tier 1 — `tavily_extract` (primary, verified, zero-install):**
   - Call `tavily_extract(url, extract_depth="advanced")`.
   - Best for clean body text. **Known quirks to handle:**
     - `title` field often comes back `null` — the real title is the first `# H1` line in
       `raw_content`. Use that.
     - Footer junk appears at the very end (`Scan to Follow`, `Got It`, `Video Mini Program
       Like`, `微信扫一扫`, repeated `Cancel/Allow`). **Strip everything from the first of
       these markers onward** before creating the source summary.
     - `images` is usually `[]` — WeChat lazy-loads images via `data-src`, which Tavily
       doesn't resolve. If the article's images matter, fall to Tier 2 with `--images-dir`.
   - If `raw_content` is empty or <100 meaningful chars, go to Tier 2.

**Tier 2 — local direct fetch (`scripts/fetch_wechat.py`):**
   - Adds what Tavily misses: **images** (resolves lazy-loaded `data-src`, downloads locally)
     and **metadata** (title / author / publish_time). Footer is auto-stripped (it only parses
     `#js_content`, so no junk).
   - **Proxy: WeChat 公众号 (mp.weixin.qq.com) is a DOMESTIC service (Tencent) → 直连，剥掉代理，
     绝不走 17891 也绝不走 17890** (per global rules: 国内服务直连剥代理). Run with proxy env
     stripped:
     ```bash
     env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
         -u all_proxy -u ALL_PROXY -u no_proxy -u NO_PROXY \
       python3 ~/.claude/skills/llm-wiki/scripts/fetch_wechat.py "<url>" --json
     ```
   - Output modes: default = markdown with YAML frontmatter to stdout; `--json` = structured
     `{title, author, publish_time, url, markdown, image_count}`; `--images-dir DIR` =
     download images into `DIR` and rewrite body image links to `images/imageN.ext`.
   - For knowledge-base ingestion of an article **with figures**, point `--images-dir` at the
     source's asset folder so images are archived alongside the markdown.
   - Exit code 2 = couldn't extract body (article deleted / needs login / link expired) → Tier 3.
   - Dependencies (`requests`, `bs4`, `lxml`) are already installed; no markdown library needed.

**Tier 3 — manual paste:** only if both above fail, tell the user:
   > "这篇公众号文章自动抓取失败（可能已删除/需登录/链接失效）。请在微信里打开，复制全文粘贴给我。"

**Source naming:** derive slug from the article title (Tier 1 H1 or Tier 2 `title`), kebab-case.
`> Source:` field records the original `mp.weixin.qq.com` URL. `> Type: article`.

### Xiaohongshu Note Processing

For `xiaohongshu.com` notes and `xhslink.com/...` shortlinks. Xiaohongshu has heavy
anti-scraping, BUT `tavily_extract` reliably renders the note and returns BOTH the full
note text AND the image CDN URLs — verified working. The catch is the `raw_content` is
buried in a lot of page boilerplate (login prompts, ICP/legal footer, nav menus, ad-block
warnings). The LLM must select signal from noise.

**Step 1 — extract with Tavily:**
   - Call `tavily_extract(url, extract_depth="advanced")` on the shortlink or full URL
     (shortlinks resolve fine — no need to expand them first).
   - `raw_content` contains everything. The `images` field is usually `[]` (image URLs are
     inline in `raw_content`, not in that field).

**Step 2 — LLM cleans `raw_content`, KEEP only:**
   - **Title**: the first `# H1`; strip the trailing ` - 小红书` suffix.
   - **Author**: the Xiaohongshu user-profile display name (e.g. the `[小盖](.../user/profile/...)` link text).
   - **Body**: the main prose block — the note's actual text. It sits between the author/carousel
     section and the date line.
   - **Date / location**: a line like `05-19 北京` (MM-DD + city).
   - **Engagement**: three numbers near the end = 赞 / 收藏 / 评论 (e.g. `510 812 15`).
   - **Image URLs**: all `https://sns-webpic-qc.xhscdn.com/...` URLs. The carousel total is the
     `1/N` marker. **Dedupe** — Tavily repeats the first images (the carousel preview reuses
     the first 2). Keep the unique set, in order.

   **DISCARD**: login/QR boilerplate (`登录后...`, `获取验证码`, 用户协议/隐私政策 links),
   the ICP/营业执照/网络文化经营许可证 legal footer, nav menus (发现/直播/发布/通知),
   `温馨提示`/ad-block warning, `创作服务`/`蒲公英`/`商家入驻` activity menu, `blob:http://localhost/...`
   placeholder images.

**Step 3 — archive images (recommended; XHS CDN URLs are time-signed and EXPIRE):**
   - The note's real content is often IN the images (screenshots / "原文放附件"), so archiving
     matters. Download promptly with `scripts/fetch_images.py`. **XHS CDN has hotlink
     protection → MUST pass `--referer https://www.xiaohongshu.com/`.** 小红书是国内服务
     (xiaohongshu.com / xhscdn.com) → 直连，剥掉代理，绝不走 17891/17890 (国内服务直连剥代理):
     ```bash
     env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
         -u all_proxy -u ALL_PROXY -u no_proxy -u NO_PROXY \
       python3 ~/.claude/skills/llm-wiki/scripts/fetch_images.py \
       --out <source-asset-dir> --referer "https://www.xiaohongshu.com/" <url1> <url2> ...
     ```
   - Rewrite body image refs to the local `images/imageN.ext` files it returns.

**Step 4 — read text OUT OF the images (Claude vision, NOT a separate OCR engine):**
   Many Xiaohongshu notes carry their real content as **text inside the images** (screenshots,
   "原文放附件了"). The short caption alone is not the knowledge — the images are. So after
   downloading:
   - **Convert webp→png/jpg if needed** (the `Read`/vision tool may not accept `.webp`). XHS
     images are usually webp:
     ```bash
     python3 -c "from PIL import Image; import sys,glob,os
     for p in glob.glob(sys.argv[1]+'/*.webp'):
         Image.open(p).convert('RGB').save(os.path.splitext(p)[0]+'.png')" <images-dir>
     ```
   - **Read each image** with the `Read` tool (Claude's own vision) — it reads the text
     directly, no `tesseract`/OCR engine required. Verified: XHS screenshot text comes through
     cleanly and legibly.
   - **Merge** the text extracted from the images into the note body, in carousel order, so the
     ingested note captures the FULL knowledge (caption + everything written in the images).
   - This whole chain is verified working: tavily (urls) → fetch_images (download, Referer,
     直连剥代理) → PIL webp→png → Read (vision) → text.

**Step 5 — fallback:** if Tavily returns no note body (rare — happens if the note was deleted
or the link is malformed), prompt the user:
   > "这篇小红书笔记自动抓取失败。请在小红书 App 里打开，复制正文粘贴给我（图片也可以发我）。"

**Source naming:** slug from the note title, kebab-case. `> Source:` records the original
`xiaohongshu.com` / `xhslink.com` URL. `> Type: note`.

### PDF Processing

PDF files in `raw/inbox/` are processed with a tiered strategy:

1. **Best quality (MinerU — preferred)**: Use MinerU with pipeline backend for academic papers. GPU-accelerated, best LaTeX formula and table support. See [MinerU Runtime Configuration](#mineru-runtime-configuration-important) for the correct command.
2. **Enhanced (pymupdf4llm)**: If MinerU is unavailable, use `pymupdf4llm` for decent Markdown output. Lightweight, CPU-only.
3. **Default (zero config)**: Use the Read tool to extract PDF text content. Works for born-digital PDFs with text layers.
4. **Manual fallback**: If all automated methods fail or produce poor results, prompt the user to provide the paper's arXiv page or manually paste key sections.

Detection order: try MinerU (best) → try pymupdf4llm → fall back to Read tool.

### Code Repository Processing

When a GitHub/GitLab URL is detected in inbox (or user provides a repo URL):

1. **Detect repo URLs**: any URL matching `github.com/{owner}/{repo}` or `gitlab.com/{owner}/{repo}`.
2. **Extract via GitHub MCP** (for GitHub repos):
   - Get directory tree: `get_file_contents` with the repo root
   - Get README: `get_file_contents` for README.md
   - Get config files: `package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`, `Dockerfile`
   - Get docs: `docs/` directory contents
   - Get key source files: `__init__.py`, `index.ts`, `main.py`, entry points
3. **Local repo fallback**: if URL is a local path or clone is needed, use `git clone` then Bash (`tree -L 3`) + Glob + Read.
4. **Generate structured output** — create two files in `raw/inbox/`:
   - `repo-{name}-overview.md`: repo metadata, directory tree, README summary, architecture overview, dependencies, key config
   - `repo-{name}-code.md`: entry points, core modules, public APIs/interfaces
5. These files are then processed by the normal digest flow as regular markdown files.
6. During compile, repo sources create an `entity` article (tool/project type) rather than splitting into separate concepts.

### Extraction Rules

1. For **each URL**, try the primary tool first. If it returns meaningful content (>100 chars), use it.
2. If primary tool fails or returns too little content, try the fallback.
3. If both fail, log the failure and skip with a note: tell the user after digest which URLs failed.
4. Extracted content is treated as the "document" for source summary creation.
5. For X/Twitter: if extraction fails, tell the user:
   > "无法自动提取该 X 链接内容。请在浏览器中打开链接，复制全文粘贴给我，我会手动处理。"

### URL Source Naming

- Source slug: derive from URL or page title.
  - `x.com/karpathy/status/123` → `karpathy-tweet-123`
  - `mp.weixin.qq.com/s/xxx` → `{page-title-slug}`
  - `arxiv.org/abs/2401.00001` → `arxiv-2401-00001`
  - `bilibili.com/video/BV1xxxx` → `bilibili-{title-slug}`
  - `youtube.com/watch?v=xxx` → `youtube-{title-slug}`

---

## External Retrieval Sources

This is a **pluggable, query-time** axis, fully decoupled from ingestion. The wiki and any
external source stay separate stores; `query` federates across them at search time and clearly
attributes each result. **No external source is part of the default open-source install** — the
mechanism only activates if the user has registered sources locally, so this skill stays
generic and shippable.

**Registration (local, private):** sources are declared in `~/.claude/llm-wiki.local.json`
(NOT in this repo — it is gitignored, so each user's private backends never publish). Schema:
```json
{
  "retrieval_sources": [
    {
      "name": "<display name>",
      "id": "<stable id>",
      "description": "<what it is>",
      "trigger": "opt-in | always",
      "run": {
        "cwd": "<dir to run from, optional>",
        "strip_proxy": true,
        "command": "<shell command with {query} and {top_k} placeholders, prints JSON>",
        "default_top_k": 5
      },
      "output": "json",
      "result_label": "<how to attribute results in the answer>"
    }
  ]
}
```

**Contract for a source command:** given `{query}`/`{top_k}`, print JSON
`{ "source": "...", "query": "...", "hits": [{title, score, snippet, ...}], "chunks": [...] }`
to stdout. Honor `cwd` and `strip_proxy` (国内服务直连剥代理；境外走 17891) when invoking it.

**Trigger semantics:**
- `opt-in` (default, recommended): query the source ONLY when the user explicitly names it
  ("也搜<name> / 搜RAG / 查文献库 / also search <name>"). Keeps cost predictable — external
  semantic search may consume API quota per call.
- `always`: query on every `query` call.

**Usage:** the `query` subcommand reads this file, runs the matching sources, and merges results
labeled by each source's `result_label` (see [query](#4-query--query-the-knowledge-base)).
External hits are **citations, not wiki content** — never auto-ingest them (获取 ≠ 入库).

> Implementation note: registered source commands and any adapter scripts live under
> `llm-wiki/extensions/` (gitignored). They are private to the user's machine and never shipped.

---

## Subcommands

### 1. `init` — Initialize Project

**Usage:** `llm-wiki init <project-name>` or "帮我初始化一个知识库"

**Steps:**

1. If `<project-name>` is not provided, ask the user:
   "给这个知识库起个名字？（如：llm-research、paper-notes）"

2. **Ask where to create the project** (MUST ask, do not skip):
   "项目建在哪个目录？（输入路径，或回车用当前目录）"

3. **Ask if user already has a materials folder**:
   "你已经有一个存资料的文件夹吗？（输入路径，或回车创建新的 inbox）"
   - If yes: record the path in `.kf.md` as the inbox source.

4. Check if `.kf.md` already exists. If yes, inform and stop.

5. Create directory structure:
   ```bash
   mkdir -p raw/inbox raw/sources wiki/concepts wiki/entities wiki/sources output/reports output/slides output/charts trusted
   ```

6. Create `.kf.md`:
   ```markdown
   # LLM Wiki Config
   - Project: {name}
   - Created: {date}
   - Language: {auto or ask}
   - Inbox: raw/inbox/
   - Sources: raw/sources/
   - Wiki articles: 0
   - Last digested: never
   - Last compiled: never
   ```

7. Create empty `wiki/_index.md`, `wiki/_graph.md`, and `log.md`.

8. **Save to global config** — write `~/.claude/llm-wiki.json`:
   ```json
   {
     "wiki_path": "/absolute/path/to/the/new/project"
   }
   ```
   If the file already exists (user has another wiki), ask:
   > "你已经有一个知识库配置在 {existing_path}。要替换为新的吗？还是保留旧的？"

9. Report success, show structure, tell user to drop materials (files or URL lists) into `raw/inbox/`.

10. **Log:** append `[init] Project "{name}" created at {path}` to `log.md`.

---

### 2. `digest` — Digest Inbox

**Usage:** `llm-wiki digest` or "帮我消化 inbox 里的新资料"

Also supports **direct URL input**: user can say "帮我把这个链接存到知识库 https://..." or paste a URL directly without dropping it into inbox first. In this case, treat the URL as if it were in a URL list file and process it immediately.

Digest only **processes and records** new documents. It does NOT rebuild the wiki — that's `compile`.

**Steps:**

1. **Locate wiki** using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init). All subsequent paths are relative to the wiki root.
2. Read `.kf.md` to get project state.
3. Scan `raw/inbox/` for all readable files (.md, .txt, .pdf, .py, .ipynb, etc.).
3. If inbox is empty, inform user and stop.

4. **Classify each inbox file (or direct URL input):**
   - **URL list file**: a file where most non-empty lines are URLs (start with `http://` or `https://`). Each URL becomes a separate source.
   - **Direct URL**: user provided a URL in the conversation (not in a file). Treat as a single-URL list.
   - **Video URL** (Bilibili or YouTube): routed to skill-based processing (see [Video URL Processing](#video-url-processing)).
   - **PDF file** (`.pdf`): processed with PDF tiered strategy (see [PDF Processing](#pdf-processing)).
   - **Regular file**: any other file (.md, .txt, .py, .ipynb, etc.). Treated as a single document source.

5. **Process with batch progress:** for every 5 items processed, report:
   > "已处理 5/{total}..."

6. **For each regular file (non-PDF, non-URL):**

   a. **Read** the document.

   b. **Determine processing tier** by content length:
      - **Full processing** (>1000 chars): create complete source summary with all sections.
      - **Simplified processing** (≤1000 chars): create a brief summary — skip "Key Facts" and "Quotes" sections.

   c. **Create source summary** at `wiki/sources/{slug}.md`:
   ```markdown
   # {Document Title}
   > Source: `raw/sources/{filename}`
   > Digested: {date}
   > Type: {paper|article|code|dataset|other}
   > Status: digested (pending compile)

   ## Summary
   {3-5 sentence summary}

   ## Key Concepts
   - [[{concept-a}]]: {relevance}
   - [[{concept-b}]]: {relevance}

   ## Key Entities
   - [[{entity-a}]]: {relevance}
   - [[{entity-b}]]: {relevance}

   ## Key Facts
   - {fact 1}
   - {fact 2}

   ## Quotes / Key Passages
   > {notable passage}
   ```

   d. **Move** the file from `raw/inbox/` to `raw/sources/`:
   ```bash
   mv raw/inbox/{file} raw/sources/{file}
   ```

7. **For each URL** (extracted from URL list files):

   a. **Route to extraction tool** based on domain (see [URL Handling](#url-handling)).

   b. **Extract content.** If extraction succeeds:
      - Treat extracted markdown as the document content.
      - Determine processing tier by content length.
      - Create source summary with `> Source: {url}` (not a local file path).
      - **Move** the URL list file to `raw/sources/` after all its URLs are processed.

   c. If extraction fails:
      - Record the failure.
      - Do NOT create a source summary.
      - Continue with next URL.

8. **For each PDF file** in inbox:

   a. **Try MinerU** (preferred): run with pipeline backend and GPU. See [MinerU Runtime Configuration](#mineru-runtime-configuration-important) for the exact command. Output is in `{output}/auto/{name}.md` with `images/` directory.
   b. If MinerU not available, **try pymupdf4llm** (if installed): `pymupdf4llm.to_markdown("path/to/file.pdf")`.
   c. If neither is installed, **use the Read tool** to extract text (works for born-digital PDFs).
   d. If all methods fail or produce poor results (<200 chars), prompt the user to provide an alternative (arXiv URL, manual paste).
   e. Convert the extracted text to a source summary with `> Source: raw/sources/{filename}`.
   f. **Move** the PDF to `raw/sources/`.

9. **For each video URL** (YouTube or Bilibili) — see [Video URL Processing](#video-url-processing):

   a. **Detect**: URL matches `youtube.com`, `youtu.be`, `bilibili.com`, or `b23.tv`.
   b. **Default = transcript text, NO PDF**: run `scripts/fetch_youtube.py` (via 17891 proxy)
      to pull existing subtitles → clean text. This is the light default.
   c. **No subtitles** (`sub_type: none`): ask the user before running whisper (video-notes env,
      GPU). Don't auto-transcribe.
   d. **PDF only on explicit request**: invoke `youtube-render-pdf`/`bilibili-render-pdf` via the
      Skill tool ONLY when the user explicitly wants a figure-rich PDF note.
   e. Create source summary with `> Source: {video-url}` and `> Type: video` — **but only if the
      user asked to ingest** (获取 ≠ 入库). Otherwise just show the transcript.

10. **For each GitHub/GitLab repo URL** (from URL list files):

   a. **Extract via GitHub MCP** (GitHub repos): get tree, README, config files, key source files.
   b. For local paths or GitLab: `git clone` then `tree -L 3` + Glob + Read.
   c. **Generate** `repo-{name}-overview.md` and `repo-{name}-code.md` in `raw/inbox/`.
   d. These generated files will be picked up as regular markdown files in the next digest cycle.

11. After processing all items, **report summary:**
    - "Digested N files, M URLs, P PDFs, V videos, R repos. (K items failed — see details above)"
    - List any failures with the suggested action.

12. Update `.kf.md` with new source count and last-digested date.

13. **Log:** append to `log.md`:
    ```
    [{date}] digest: processed {n_files} files, {n_urls} URLs, {n_pdfs} PDFs, {n_videos} videos, {n_repos} repos ({n_failed} failed)
    - Sources: {list of source slugs}
    - Failed: {list of failed items, if any}
    ```

**Key rule:** Digest does NOT create or update concept/entity articles. It only creates source
summaries and moves files out of inbox. This keeps digest fast and separable from compile.

---

### 3. `compile` — Build Wiki from Sources

**Usage:** `llm-wiki compile` or "编译知识库"

Compile reads ALL source summaries and builds/rebuilds the concept and entity articles.

**Steps:**

1. **Locate wiki** using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).
2. Read `wiki/_index.md` to understand current state.
2. Scan `wiki/sources/` for all source summaries.
3. Extract all referenced concepts and entities across all sources.
4. For each **concept** (ideas, methods, patterns, techniques):

   Create or update `wiki/concepts/{concept}.md`:
   ```markdown
   # {Concept Name}
   > Auto-compiled by llm-wiki.

   ## Overview
   {Synthesized from all sources that mention this concept}

   ## Key Points
   - {point 1}
   - {point 2}

   ## Sources
   - [[sources/{source-a}]]: {what this source says}
   - [[sources/{source-b}]]: {what this source says}

   ## Related Concepts
   - [[{related-concept}]]: {relationship}

   ## Related Entities
   - [[{related-entity}]]: {relationship}
   ```

5. For each **entity** (people, tools, organizations, datasets, products):

   Create or update `wiki/entities/{entity}.md`:
   ```markdown
   # {Entity Name}
   > Auto-compiled by llm-wiki.
   > Type: {person|tool|organization|dataset|product|other}

   ## Overview
   {Who/what this is, synthesized from all sources}

   ## Mentioned In
   - [[sources/{source-a}]]: {context}

   ## Related Concepts
   - [[{concept}]]: {how this entity relates}

   ## Related Entities
   - [[{other-entity}]]: {relationship}
   ```

6. **Rebuild index** (`wiki/_index.md`): list all articles with 1-line summaries.
   Summaries in `_index.md` MUST be under 80 characters. If the extracted summary exceeds 80 chars, truncate with `...`.
7. **Rebuild backlink graph** (`wiki/_graph.md`): run the index script to update tables + Mermaid graph.
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/index.py --wiki-dir wiki/
   ```
8. Update `.kf.md` stats and last-compiled date.
9. Report: how many concepts, entities, and source summaries now exist.

10. **Auto-check (lightweight):** After compile, scan for broken `[[wikilinks]]`. For any unresolved link referenced by **3 or more** articles, auto-create a stub at the appropriate location (`wiki/concepts/` or `wiki/entities/`):
   ```markdown
   # {Link Name}
   > Auto-compiled by llm-wiki.
   > Status: stub (pending content)

   ## Overview
   (Referenced by {N} articles but not yet documented. Run `compile` after adding source material.)

   ## Referenced By
   - {list of referencing articles}
   ```
   Report: "Auto-created {N} stub articles for frequently-referenced missing links."

**Rules:**
- When updating existing articles, **merge** new info — don't overwrite.
- Use `[[wiki-link]]` for all cross-references.
- Concepts: lowercase-kebab-case filenames, Title Case in headings.
- Entities: lowercase-kebab-case filenames.
- Use search script to avoid creating duplicate articles for the same thing.

10. **Log:** append to `log.md`:
    ```
    [{date}] compile: {n_concepts} concepts, {n_entities} entities, {n_sources} sources
    - New: {list of new article slugs}
    - Updated: {list of updated article slugs}
    ```

---

### 4. `query` — Query the Knowledge Base

**Usage:** `llm-wiki query "your question"` or just ask a question naturally.

**Steps:**

1. **Locate wiki** using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).
2. Read `wiki/_index.md` for scope.
3. Search the **local wiki** (always):
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/search.py --wiki-dir wiki/ --query "question" --top-k 10
   ```
4. **Federated search across external retrieval sources** (see [External Retrieval Sources](#external-retrieval-sources)):
   - Load `~/.claude/llm-wiki.local.json` if it exists. If absent or it has no
     `retrieval_sources`, skip this step entirely (the default open-source install has none).
   - For each registered source, honor its `trigger`:
     - `opt-in` → query it ONLY when the user explicitly names it ("也搜论文 / 搜RAG /
       查文献库 / also search papers / search <source name>"). Do NOT call opt-in sources on a
       plain question (they may cost API quota).
     - `always` → query it on every question.
   - Run the source's `run.command` (substituting `{query}` / `{top_k}`), respecting `cwd` and
     `strip_proxy` (国内服务直连剥代理；境外走 17891). Parse its JSON output.
5. Read top relevant local articles (up to 5-8).
6. **Synthesize one answer, clearly attributing each source.** Cite local wiki as
   `[[source-name]]`; label external-source results with that source's `result_label`
   (e.g. "据 论文RAG（DashVector）：…"). Never blend them so the user can't tell which store a
   claim came from.
7. Ask: "Save this answer to the wiki?"
   - If yes: save to `wiki/concepts/{topic}.md` or `output/reports/{topic}.md`.
   - Update index and backlinks. (External-source hits are references, not wiki content — cite
     them, but do not silently ingest them; honor 获取 ≠ 入库.)

**Rules:**
- Always cite wiki articles; label external-source results distinctly.
- If both wiki and (queried) external sources lack info, say so — never fabricate.
- Suggest follow-up questions.

**Log:** append query and result type to `log.md`:
```
[{date}] query: "{question}" → {n_results} results, answer saved: {yes/no}
```

---

### 5. `check` — Health Check

**Usage:** `llm-wiki check` or "检查一下知识库"

**First:** Locate wiki using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).

**Checks:**
- **Broken links:** `[[...]]` pointing to non-existent articles.
- **Orphans:** articles with no links in or out.
- **Inconsistencies:** contradictory claims across articles.
- **Coverage gaps:** concepts/entities mentioned but lacking their own article.
- **Stale sources:** summaries referencing files no longer in `raw/sources/`.
- **Missing backlinks:** A links to B but B doesn't link back.

**Output:** A health report with score, issues, and suggested fixes.
Ask user: "Auto-fix what I can? (broken links, missing backlinks, orphans)"

**Log:** append to `log.md`:
```
[{date}] check: score {score}/100, {n_issues} issues found, {n_fixed} auto-fixed
```

---

### 6. `export` — Export Deliverables

**Usage:** `llm-wiki export "topic" [format]` or "生成一份报告"

**First:** Locate wiki using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).

**Formats:**
- `report` (default): markdown report in `output/reports/`
- `slides`: Marp-format slides in `output/slides/`
- `brief`: 1-page summary

**Steps:**
1. Search + read relevant wiki articles.
2. Generate deliverable.
3. Save to `output/{format}/{topic-slug}.md`.
4. Ask: "File key findings back into the wiki?"

**Log:** append to `log.md`:
```
[{date}] export: "{topic}" as {format} → output/{format}/{slug}.md
```

---

### 7. `trust` — Approve Content

**Usage:** `llm-wiki trust` or "把确认过的内容导出来"

**First:** Locate wiki using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).

The wiki is AI-generated draft territory. `trust` lets you review and export
specific articles to `trusted/` — your trusted, human-approved knowledge.

**Steps:**

1. Show a list of wiki articles (from `wiki/_index.md`).
2. Ask user to select which articles to trust (by number or name).
3. For each selected article:
   a. Show the full content to the user.
   b. Ask: "确认导出这篇？(y/n/edit)"
      - **y**: copy to `trusted/{path}.md` as-is.
      - **edit**: let user describe changes, apply them, then copy.
      - **n**: skip.
4. Report: "Trusted N articles to trusted/."

**Why trust exists:**
- Wiki content is AI-generated, may contain errors or hallucinations.
- `trusted/` is YOUR vetted knowledge — you've read and approved every article in it.
- If you use Obsidian or another vault, you can point it at `trusted/` with confidence.
- This follows kepano's isolation principle: AI drafts and trusted knowledge stay separate.

**Log:** append to `log.md`:
```
[{date}] trust: {n} articles approved → trusted/
- {list of trusted article paths}
```

---

### 8. `status` — Knowledge Base Status

**Usage:** `llm-wiki status` or "知识库什么状态了"

Display a quick overview of the knowledge base.

**Steps:**

1. **Locate wiki** using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).
2. Read `.kf.md`, `wiki/_index.md`, and `log.md`.
2. Display:

```
## llm-wiki Status — {project-name}

### Statistics
- Concepts:     {n}
- Entities:     {n}
- Sources:      {n}
- Total words:  ~{n}
- Inbox items:  {n} (unread files in raw/inbox/)

### Timeline
- Created:      {date}
- Last digest:  {date}
- Last compile: {date}
- Last action:  {most recent log entry}

### Health
- Broken links: {n}
- Orphans:      {n}
```

3. If inbox has items, remind: "Inbox 中有 {n} 个未处理的文件，运行 `digest` 处理。"

---

### 9. `save` — Save Conversation Insights Directly

**Usage:** `llm-wiki save` or "把刚才了解的存到知识库" or "存到wiki"

**Trigger:** User wants to save knowledge gained during the current conversation (e.g., from exploring a local codebase, debugging a tool, reading documentation, or discussing a topic) directly to the wiki — without going through the inbox → digest pipeline.

**This is the key difference from `digest`:** `digest` processes files/URLs from inbox. `save` captures insights that exist only in the conversation context (explored code, discussed concepts, learned facts).

**Steps:**

1. **Locate wiki** using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).

2. **Full conversation harvest — scan everything, not just the main topic.**

   Go through the ENTIRE conversation and collect ALL of the following:

   a. **Direct discussion**: entities and concepts explicitly discussed or designed.

   b. **Research artifacts** (MANDATORY — most commonly missed):
      - Every tool/project/paper/dataset **named in web search results**
      - Every entity **mentioned in WebFetch / tavily / Semantic Scholar outputs**
      - Every concept **explained or compared** during research

   c. **Incidentally mentioned**: tools referenced in passing, papers cited as background, APIs discussed as alternatives.

   Build a flat list: `[entity/concept name → new info learned → exists in wiki?]`

   **Zero-leakage rule**: if something was named in ANY tool output during this session, it belongs on this list. Omitting it is a failure.

3. **For each item on the harvest list:**
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/search.py --wiki-dir wiki/ --query "{name}" --top-k 3
   ```
   - **Exists + has new info** → **update** the article with what was learned this session
   - **Exists + nothing new** → skip
   - **Does not exist** → **create** new entity/concept article

   Do NOT only create new articles. Updating existing ones with fresh research details is equally important.

4. **Create source summary** at `wiki/sources/{slug}.md`:
   ```markdown
   # {Title}
   > Source: {local path / URL / "conversation context"}
   > Digested: {date}
   > Type: {code|discussion|documentation|other}
   > Status: digested

   ## Summary
   {3-5 sentence summary of what was learned}

   ## Key Concepts
   - [[{concept}]]: {relevance}

   ## Key Entities
   - [[{entity}]]: {relevance}

   ## Key Facts
   - {fact 1}
   - {fact 2}
   ```

5. **Create or update entity/concept articles** following the standard wiki format (see `compile` for templates).

6. **Rebuild index:**
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/index.py --wiki-dir wiki/
   ```

7. **Update `.kf.md`** with new article count and last-digested date.

8. **Log:** append to `log.md`:
   ```
   [{date}] save: {n_entities} entities, {n_concepts} concepts from conversation
   - New: {list of new article slugs}
   - Updated: {list of updated article slugs}
   - Topic: {brief description of what was saved}
   ```

9. **Report** to user: what was saved, with links to the articles.
10. **Auto-check (lightweight):** Same as compile — scan for newly-introduced broken links and auto-create stubs for those referenced 3+ times.

**Common scenarios:**
- "我刚看了一个本地代码库，存到知识库" → create entity (tool type) + source summary
- "把刚才讨论的调试经验存下来" → create concept or update existing + source summary
- "这个工具的用法记到wiki里" → create/update entity + source summary
- "把这个项目的架构理解存一下" → create entity + related concepts + source summary

**Rules:**
- **Zero leakage**: every entity/concept named in any tool output (web search, fetch, Semantic Scholar, code read) during the session must be checked against the wiki. Not just the main topic.
- **Update = as important as create**: finding new details about an existing article and NOT updating it is a failure equivalent to missing a new entity.
- Save captures **your understanding**, not raw data. Summarize and structure.
- Always create a source summary to track provenance.
- Cross-reference existing wiki articles with `[[wiki-link]]`.
- For local repos: record the local path in `> Source:` field for future reference.
- If the conversation contains both entity and concept knowledge, create both.
- When saving from code exploration: record the specific repo path (e.g., `> Source: /path/to/repo`) not just "conversation context".
- When saving from paper/article discussion: record the URL or DOI.
- `> Source: conversation context` should be the LAST resort, only when no specific source is identifiable.

---

### 10. `read-paper` — Import and Structure a Scientific Paper

**Usage:** `llm-wiki read-paper <pdf-path>` or "帮我读这篇论文并存到知识库" or "把这个 PDF 存到文献库"

**Trigger:** User provides a PDF path (or URL to a paper) and wants it ingested into the knowledge base as a structured, navigable literature entry.

**Design principle (inspired by [GXL Sy](https://gxl.ai/blog/biomedical-literature-as-a-filesystem)):** Scientific papers are born as structured artifacts (sections, figures, tables, supplements). PDF flattens them. `read-paper` reverses this compression — each paper becomes a folder that AI agents can navigate like a code repository.

**Steps:**

1. **Locate wiki** using the [Locate Wiki Procedure](#locate-wiki-procedure-must-follow-for-all-subcommands-except-init).

2. **Ensure `papers/` directory exists** in the wiki root:
   ```bash
   mkdir -p {wiki_root}/papers
   ```

3. **Convert PDF to Markdown + extract images** using MinerU (see [MinerU Runtime Configuration](#mineru-runtime-configuration-important) for the full rationale; the command below is the short form):
   ```bash
   GPU_ID=$(nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader,nounits \
     | awk -F', ' '$2<10 {print $1; exit}')
   env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
     MINERU_MODEL_SOURCE=local \
     CUDA_VISIBLE_DEVICES=$GPU_ID \
     conda run -n mineru \
     mineru -p "{pdf_path}" -o /tmp/mineru_output -b pipeline
   ```
   MinerU pipeline backend outputs (under `auto/` subdirectory):
   - `{name}.md` — full markdown with LaTeX formulas and table preservation
   - `images/` — extracted figures as PNG/JPG

   For scanned PDFs / handwritten content / explicit "highest accuracy" requests, drop
   `-b pipeline` to use the default hybrid backend — it adds a 2.2 GB VLM pass per page
   (~7× slower) and outputs to `hybrid_auto/` instead of `auto/`.

   **Fallback chain** (if MinerU fails or is unavailable):
   - Try `pymupdf4llm` (if installed): `python3 -c "import pymupdf4llm; md = pymupdf4llm.to_markdown('{pdf_path}'); ..."`
   - Try `pypdf` (basic text only): `python3 -c "from pypdf import PdfReader; ..."`
   - If all fail: inform user and suggest installing MinerU (`conda run -n mineru pip install mineru`)

4. **Extract metadata** from the markdown content using LLM analysis:
   ```json
   {
     "title": "Full paper title",
     "authors": ["Author 1", "Author 2"],
     "year": "2026",
     "doi": "10.xxxx/...",
     "journal": "bioRxiv / Nature Methods / ...",
     "keywords": ["keyword1", "keyword2"],
     "abstract": "Full abstract text"
   }
   ```

5. **Generate paper slug** from title:
   - Lowercase, kebab-case, max 60 chars
   - Example: "Formalized scientific methodology enables rigorous AI-conducted research" → `formalized-scientific-methodology-ai-research`

6. **Create paper folder structure** at `{wiki_root}/papers/{slug}/`:
   ```
   📂 {slug}/
   ├── meta.json              # Structured metadata (step 4)
   ├── paper.pdf              # Original PDF (copied and renamed)
   ├── full.md                # Complete markdown from MinerU
   ├── sections/              # Split by section headings
   │   ├── abstract.md
   │   ├── introduction.md
   │   ├── related-work.md    # (if exists)
   │   ├── methods.md
   │   ├── results.md
   │   ├── discussion.md
   │   ├── conclusion.md      # (if exists)
   │   └── references.md
   ├── figures/                # Extracted images from MinerU
   │   ├── fig1.png
   │   ├── fig2.png
   │   └── ...
   └── README.md              # Quick navigation index
   ```

7. **Split markdown into sections** using the helper script:
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/split_paper.py \
     --input /tmp/mineru_output/{name}.md \
     --output {wiki_root}/papers/{slug}/sections/
   ```
   The script splits on `## ` or `# ` headings, normalizes section filenames to kebab-case, and creates a `README.md` with a table of contents.

   **If the script is unavailable or fails**, do the split manually:
   - Read the full markdown
   - Identify major section headings (Abstract, Introduction, Methods/Materials, Results, Discussion, Conclusion, References)
   - Write each section to its own `.md` file in `sections/`

8. **Copy figures**: move extracted images from MinerU output to `{slug}/figures/`.

9. **Copy and rename PDF**: copy the original PDF to `{slug}/paper.pdf`.

10. **Generate README.md** for the paper folder:
    ```markdown
    # {Paper Title}
    > Authors: {Author 1}, {Author 2}, ...
    > Year: {year} | Journal: {journal}
    > DOI: {doi}

    ## Quick Navigation
    - [Abstract](sections/abstract.md)
    - [Introduction](sections/introduction.md)
    - [Methods](sections/methods.md)
    - [Results](sections/results.md)
    - [Discussion](sections/discussion.md)
    - [References](sections/references.md)
    - [Full Text](full.md)
    - [Original PDF](paper.pdf)

    ## Figures
    - ![Fig 1](figures/fig1.png)
    - ...

    ## Keywords
    {keyword1}, {keyword2}, ...
    ```

11. **Update papers index** — create or update `{wiki_root}/papers/_papers_index.md`:
    ```markdown
    # Papers Index
    > Auto-maintained by llm-wiki read-paper.

    | Title | Authors | Year | Journal | Tags | Folder |
    |-------|---------|------|---------|------|--------|
    | {title} | {first author} et al. | {year} | {journal} | {keywords} | [{slug}]({slug}/) |
    ```

12. **Auto-digest to wiki** — automatically create a source summary in `wiki/sources/`:
    - Read the paper's abstract, key findings, and methods
    - Create `wiki/sources/paper-{slug}.md` following the standard source summary template
    - Extract key concepts and entities
    - Create or update relevant concept/entity articles in `wiki/concepts/` and `wiki/entities/`
    - Rebuild wiki index:
      ```bash
      python3 ~/.claude/skills/llm-wiki/scripts/index.py --wiki-dir wiki/
      ```

13. **Log:** append to `log.md`:
    ```
    [{date}] read-paper: "{title}" → papers/{slug}/
    - Sections: {n} | Figures: {n} | Pages: {n}
    - Auto-digested: source summary + {n_concepts} concepts + {n_entities} entities
    ```

14. **Report** to user:
    > 论文已入库：`papers/{slug}/`
    > - {n} 个章节、{n} 张图片
    > - 已自动生成 wiki source summary 和相关知识条目
    > - 可以用 `cat papers/{slug}/sections/methods.md` 精确阅读某个章节

**Batch mode:** If user provides a directory of PDFs, process each one sequentially. Report progress every 3 papers.

**URL support:** If user provides an arXiv URL (e.g., `https://arxiv.org/abs/2401.00001`):
1. Download PDF: `wget https://arxiv.org/pdf/2401.00001 -O /tmp/paper.pdf`
2. Proceed with normal read-paper flow.

**Rules:**
- Never modify or delete the original PDF — always copy.
- Section splitting is best-effort; some papers have non-standard structures. If headings are ambiguous, keep the full.md as the authoritative source.
- Figures extracted by MinerU may not perfectly correspond to paper figures. Include all extracted images.
- The `papers/` directory is separate from `wiki/` — papers are structured literature storage, wiki is synthesized knowledge. They are linked through source summaries.

---

## Built-in Tools

### Search Script
```bash
python3 ~/.claude/skills/llm-wiki/scripts/search.py \
  --wiki-dir wiki/ --query "search terms" --top-k 10
```

### Index Generator
```bash
python3 ~/.claude/skills/llm-wiki/scripts/index.py --wiki-dir wiki/
```

### Stats Only
```bash
python3 ~/.claude/skills/llm-wiki/scripts/index.py --wiki-dir wiki/ --stats-only
```

## Wiki Conventions

See [references/wiki-conventions.md](references/wiki-conventions.md) for detailed format rules.

Key rules:
- `[[wiki-link]]` for all cross-references
- Filenames: lowercase-kebab-case
- Articles start with `# Title` then `> Auto-compiled by llm-wiki.`
- `_index.md` and `_graph.md` are auto-maintained
- **concepts/**: ideas, methods, patterns, techniques
- **entities/**: people, tools, organizations, datasets, products
- `_graph.md` includes a Mermaid knowledge graph section (Obsidian-compatible)

## Tips

1. **Drop → Digest → Compile**: drop files or URL lists into inbox, digest to process, compile to build wiki.
2. **Query often**: every answer can feed back into the wiki.
3. **Check regularly**: catch issues before they compound.
4. **Trust carefully**: only export what you've actually reviewed.
5. **Don't edit wiki/ manually**: that's the LLM's domain. Add info via raw/inbox/.
6. **Obsidian compatible**: the `wiki/` directory uses Obsidian-native `[[wiki-link]]` syntax and Mermaid graphs. Open it directly as an Obsidian vault for visual browsing. The `trusted/` folder is your clean, human-approved vault — safe for Obsidian daily use.
7. **Track changes**: check `log.md` to see what changed and when. Every operation is recorded.
