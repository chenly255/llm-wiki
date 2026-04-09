---
name: llm-wiki
description: >
  Build and maintain LLM-powered personal knowledge bases (inspired by Karpathy + kepano).
  TRIGGER when: user mentions knowledge base, wiki compilation, knowledge management with LLM,
  "build a wiki", "organize my notes/papers/articles", "llm wiki", or uses
  /llm-wiki command. Also trigger when user says "整理知识库", "编译wiki",
  "知识工厂", "帮我整理这些资料". Subcommands: init, digest, compile, query, check, export, trust, status.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# LLM Wiki

Build and maintain LLM-powered personal knowledge bases.

Two core principles:
1. **Karpathy**: Raw docs → LLM "compiles" a structured wiki → Q&A → outputs loop back in.
2. **kepano (Obsidian CEO)**: AI-generated content must be **isolated** from your trusted knowledge. Only `trust` moves content to your main vault after your explicit approval.

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

Every subcommand (digest, compile, query, check, export, trust, status) MUST locate the wiki before doing anything. Follow this order:

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
| `/bilibili-render-pdf` skill | Extracts Bilibili video content into structured notes + PDF | When a `bilibili.com` or `b23.tv` URL is provided | Check if skill exists: `ls ~/.claude/skills/bilibili-render-pdf/SKILL.md` |
| `/youtube-render-pdf` skill | Extracts YouTube video content into structured notes + PDF | When a `youtube.com` or `youtu.be` URL is provided | Check if skill exists: `ls ~/.claude/skills/youtube-render-pdf/SKILL.md` |
| `tavily` MCP server | Web page extraction and search | When processing web URLs (blogs, news, WeChat articles) | Check if tavily tools are available in the current session |
| `github` MCP server | GitHub repo extraction | When processing GitHub repo URLs | Check if github MCP tools are available in the current session |
| `pymupdf4llm` (Python) | Enhanced PDF to Markdown conversion | When processing PDF files | `python3 -c "import pymupdf4llm"` |
| `MinerU` (Python) | Best-quality PDF conversion (LaTeX formulas, tables) | When processing academic PDFs | `python3 -c "import magic_pdf"` |

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
| `bilibili.com` / `b23.tv` | `/bilibili-render-pdf` skill (generates structured notes + PDF) | `tavily_extract` for basic page info; or prompt user to paste transcript |
| `youtube.com` / `youtu.be` | `/youtube-render-pdf` skill (generates structured notes + PDF) | `tavily_extract` for basic page info; or prompt user to paste transcript |
| `x.com` / `twitter.com` | `web_reader` | Prompt user to copy content manually |
| `mp.weixin.qq.com` | `tavily_extract` | Prompt user to copy content manually |
| `arxiv.org` | `web_reader` | `tavily_extract` |
| `zhihu.com` | — | Anti-scraping blocks extraction — prompt user to copy content manually |
| `xiaohongshu.com` | — | Requires xiaohongshu-mcp (external) — prompt user to copy content manually |
| `github.com` / `gitlab.com` | GitHub MCP (`get_file_contents` for tree + README + key files) | `git clone` + Bash + Read |
| Other (blogs, docs, Medium) | `web_reader` | `tavily_extract` |

### Video URL Processing

When a Bilibili or YouTube URL is detected:

1. **Check if the required skill is installed:**
   ```bash
   ls ~/.claude/skills/bilibili-render-pdf/SKILL.md 2>/dev/null  # for Bilibili
   ls ~/.claude/skills/youtube-render-pdf/SKILL.md 2>/dev/null    # for YouTube
   ```

2. **If skill is available:**
   a. Invoke the skill using the Skill tool (e.g., `Skill("bilibili-render-pdf", args: "<url>")`).
   b. The skill generates structured notes (typically a `.md` or `.tex` file and a PDF).
   c. Read the generated markdown/notes content.
   d. Treat the content as the "document" and proceed with normal digest flow (create source summary).
   e. Optionally move/copy the generated PDF to `raw/sources/` for archival.

3. **If skill is NOT available:**
   a. Inform the user:
      > "处理 Bilibili/YouTube 视频需要安装对应的 skill。要我帮你安装吗？"
      > - Bilibili: "安装命令：`git clone <repo-url> ~/.claude/skills/bilibili-render-pdf`"
      > - YouTube: "安装命令：`git clone <repo-url> ~/.claude/skills/youtube-render-pdf`"
   b. Offer fallback: try `tavily_extract` for basic page metadata (title, description).
   c. If fallback also fails, prompt user to paste transcript or summary manually.

4. **Source naming for videos:**
   - `bilibili.com/video/BV1xxxx` → `bilibili-{title-slug}`
   - `youtube.com/watch?v=xxx` → `youtube-{title-slug}`

### PDF Processing

PDF files in `raw/inbox/` are processed with a tiered strategy:

1. **Default (zero config)**: Use the Read tool to extract PDF text content. Works for born-digital PDFs with text layers.
2. **Enhanced (pymupdf4llm)**: If `pymupdf4llm` is installed (`pip install pymupdf4llm`), use it for better Markdown output with structure preservation. Lightweight, no GPU required.
3. **Best quality (MinerU)**: If MinerU is installed (`pip install magic-pdf[full]`), use it for academic papers with formulas, tables, and figures. Converts formulas to LaTeX. GPU recommended but not required.
4. **Manual fallback**: If all automated methods fail or produce poor results, prompt the user to provide the paper's arXiv page or manually paste key sections.

Detection order: try pymupdf4llm → try MinerU → fall back to Read tool.

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

   a. **Try pymupdf4llm** (if installed): run `pymupdf4llm.to_markdown("path/to/file.pdf")` to convert.
   b. If pymupdf4llm not available, **try MinerU** (if installed): run `magic-pdf` to convert.
   c. If neither is installed, **use the Read tool** to extract text (works for born-digital PDFs).
   d. If all methods fail or produce poor results (<200 chars), prompt the user to provide an alternative (arXiv URL, manual paste).
   e. Convert the extracted text to a source summary with `> Source: raw/sources/{filename}`.
   f. **Move** the PDF to `raw/sources/`.

9. **For each video URL** (Bilibili or YouTube):

   a. **Detect**: URL matches `bilibili.com`, `b23.tv`, `youtube.com`, or `youtu.be`.
   b. **Check skill availability**:
      ```bash
      ls ~/.claude/skills/bilibili-render-pdf/SKILL.md 2>/dev/null  # Bilibili
      ls ~/.claude/skills/youtube-render-pdf/SKILL.md 2>/dev/null    # YouTube
      ```
   c. **If skill is available**: invoke via the Skill tool. Read the generated notes/markdown output. Treat the content as a regular document for source summary creation.
   d. **If skill is NOT available**: inform the user what's missing, offer to help install, and offer fallback (tavily_extract for page metadata, or manual paste).
   e. Create source summary with `> Source: {video-url}` and `> Type: video`.

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
7. **Rebuild backlink graph** (`wiki/_graph.md`): run the index script to update tables + Mermaid graph.
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/index.py --wiki-dir wiki/
   ```
8. Update `.kf.md` stats and last-compiled date.
9. Report: how many concepts, entities, and source summaries now exist.

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
3. Search for relevant articles:
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/search.py --wiki-dir wiki/ --query "question" --top-k 10
   ```
3. Read top relevant articles (up to 5-8).
4. Synthesize answer with citations: `[[source-name]]`.
5. Ask: "Save this answer to the wiki?"
   - If yes: save to `wiki/concepts/{topic}.md` or `output/reports/{topic}.md`.
   - Update index and backlinks.

**Rules:**
- Always cite wiki articles.
- If the wiki lacks info, say so — never fabricate.
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
