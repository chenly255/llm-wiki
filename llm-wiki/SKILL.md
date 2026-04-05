---
name: llm-wiki
description: >
  Build and maintain LLM-powered personal knowledge bases (inspired by Karpathy's methodology).
  TRIGGER when: user mentions knowledge base, wiki compilation, knowledge management with LLM,
  "build a wiki", "organize my notes/papers/articles", "llm wiki", or uses
  /llm-wiki command. Also trigger when user says "整理知识库", "编译wiki",
  "知识工厂", "帮我整理这些资料". Subcommands: init, ingest, compile, qa, lint, output.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# LLM Wiki

Build and maintain LLM-powered personal knowledge bases. Raw documents go in, a structured,
interlinked wiki comes out. The wiki grows smarter with every query, every lint pass, and
every output you file back.

Inspired by [Karpathy's LLM Knowledge Bases](https://x.com/karpathy/status/2039805659525644595).

## Core Principle

**The wiki is the LLM's domain.** The human feeds raw material and asks questions. The LLM
compiles, maintains, lints, and grows the knowledge base. The human rarely edits the wiki
directly.

## Project Structure

```
<project-root>/
├── raw/                    # Source documents (user manages)
│   ├── papers/
│   ├── articles/
│   ├── code/
│   └── ...
├── wiki/                   # Compiled wiki (LLM manages)
│   ├── _index.md           # Master index: list of all articles with 1-line summaries
│   ├── _graph.md           # Backlink graph: which articles link to which
│   ├── concepts/           # Concept articles (auto-categorized)
│   │   ├── concept-name.md
│   │   └── ...
│   └── sources/            # Source summaries (1 per raw document)
│       ├── source-name.md
│       └── ...
├── output/                 # Generated deliverables
│   ├── reports/
│   ├── slides/
│   └── charts/
└── .kf.md                  # Project config
```

## Subcommands

### 1. `init` — Initialize an LLM Wiki Project

**Usage:** `/llm-wiki init` or "帮我初始化一个知识工厂"

**Steps:**

1. **Ask the user where to create the project** (MUST ask, do not skip):
   - "你想把知识工厂建在哪个目录？（直接输入路径，或回车使用当前目录）"
   - If user provides a path, use that path. Create it if it doesn't exist.
   - If user presses enter / says "当前目录", use the current working directory.

2. **Ask if the user already has a folder of raw materials**:
   - "你已经有一个存放资料的文件夹了吗？（输入路径，或回车让我创建一个新的 raw/ 目录）"
   - If user provides a path, symlink or copy it as the `raw/` source. Record the path in `.kf.md`.
   - If user says no / presses enter, create a new `raw/` directory.

3. Check if `.kf.md` already exists at the target directory. If yes, inform user and stop.

4. Create the directory structure at the chosen path:
   ```
   mkdir -p raw wiki/concepts wiki/sources output/reports output/slides output/charts
   ```

5. Create `.kf.md` config:
   ```markdown
   # LLM Wiki Config
   - Project: {ask user or infer from directory name}
   - Created: {date}
   - Language: {auto or ask user}
   - Raw path: {the raw/ path, could be external}
   - Raw sources: 0
   - Wiki articles: 0
   - Last compiled: never
   ```

6. Create `wiki/_index.md`:
   ```markdown
   # Knowledge Index
   > Auto-maintained by llm-wiki. Do not edit manually.

   ## Articles
   (none yet — run ingest to populate)

   ## Statistics
   - Total articles: 0
   - Total sources: 0
   - Last updated: {date}
   ```

7. Create `wiki/_graph.md`:
   ```markdown
   # Backlink Graph
   > Auto-maintained by llm-wiki. Do not edit manually.

   (empty — will populate after ingest)
   ```

8. Report success, show the project structure, and remind user to put source documents in `raw/`.

---

### 2. `ingest` — Process Raw Documents into Wiki

**Usage:** `/llm-wiki ingest` or "帮我把 raw/ 里的资料整理进知识库"

**Steps:**

1. Read `.kf.md` to understand project state.
2. Scan `raw/` recursively for all readable files (.md, .txt, .pdf, .py, .ipynb, etc.).
3. Read `wiki/_index.md` to know what's already been ingested.
4. For each **new** raw file (not yet in index):

   a. **Read** the raw document completely.

   b. **Create source summary** at `wiki/sources/{slug}.md`:
   ```markdown
   # {Document Title}
   > Source: `raw/{path}`
   > Ingested: {date}
   > Type: {paper|article|code|dataset|other}

   ## Summary
   {3-5 sentence summary of the document}

   ## Key Concepts
   - [[concept-a]]: {how this document relates to concept-a}
   - [[concept-b]]: {how this document relates to concept-b}

   ## Key Facts
   - {important fact 1}
   - {important fact 2}
   - ...

   ## Quotes / Key Passages
   > {notable quote or passage, if applicable}
   ```

   c. **Create or update concept articles** at `wiki/concepts/{concept}.md`:
   ```markdown
   # {Concept Name}
   > Auto-compiled by llm-wiki.

   ## Overview
   {What this concept is, synthesized from all sources that mention it}

   ## Sources
   - [[sources/{source-a}]]: {what source-a says about this concept}
   - [[sources/{source-b}]]: {what source-b says about this concept}

   ## Related Concepts
   - [[concepts/{related-a}]]: {relationship description}
   - [[concepts/{related-b}]]: {relationship description}
   ```

   d. If a concept article already exists, **merge** new information into it rather than
   overwriting. Preserve existing content and add new source references.

5. **Rebuild index** (`wiki/_index.md`):
   - List all articles with 1-line summaries
   - Update statistics

6. **Rebuild backlink graph** (`wiki/_graph.md`):
   - Scan all wiki articles for `[[...]]` links
   - Build a table: `Article → Links to → Linked from`

7. Update `.kf.md` statistics.

**Important rules:**
- Process documents one at a time to avoid context overflow.
- For large documents (>1000 lines), summarize in sections.
- Use `[[wiki-link]]` syntax for cross-references (Obsidian-compatible).
- Concept names should be lowercase-kebab-case for filenames, Title Case in content.
- Use the search script to check for existing related concepts before creating new ones.

---

### 3. `compile` — Full Wiki Recompilation

**Usage:** `/llm-wiki compile` or "重新编译整个知识库"

This is a destructive rebuild — it re-reads ALL raw documents and rewrites the entire wiki.

**Steps:**

1. Confirm with user: "This will recompile the entire wiki from raw sources. Continue?"
2. Back up current wiki: `cp -r wiki wiki.bak.{timestamp}`
3. Clear wiki contents (keep directory structure).
4. Run full `ingest` on all raw documents.
5. After completion, run `lint` to verify quality.
6. Report diff: how many articles changed, added, removed.

**When to use:** After significant changes to raw documents, or when the wiki has accumulated
too many incremental inconsistencies.

---

### 4. `qa` — Ask the Knowledge Base

**Usage:** `/llm-wiki qa "your question"` or just ask a question when the skill is active.

**Steps:**

1. Read `wiki/_index.md` to understand the full scope.
2. Use the search script to find relevant articles:
   ```bash
   python3 ~/.claude/skills/llm-wiki/scripts/search.py --wiki-dir wiki/ --query "user's question" --top-k 10
   ```
3. Read the top relevant articles (up to 5-8 articles depending on size).
4. Synthesize a comprehensive answer with citations: `[[source-name]]`.
5. Ask user: "Should I file this answer into the wiki?"
   - If yes: save to `wiki/concepts/{topic}.md` or `output/reports/{topic}.md`
   - Update index and backlinks accordingly.

**Q&A rules:**
- Always cite which wiki articles you drew from.
- If the wiki doesn't contain enough information, say so explicitly.
- Never fabricate information not present in the wiki.
- Suggest follow-up questions the user might want to explore.

---

### 5. `lint` — Health Check the Wiki

**Usage:** `/llm-wiki lint` or "检查一下知识库的健康状况"

**Steps:**

1. Read `wiki/_index.md` and `wiki/_graph.md`.
2. Run the following checks:

   **a. Broken links:** Scan all articles for `[[...]]` links that point to non-existent articles.

   **b. Orphan articles:** Find articles with no incoming or outgoing links.

   **c. Inconsistencies:** Read related articles and check for contradictory claims.
   Use the search script to find articles mentioning the same entities.

   **d. Coverage gaps:** Based on concepts mentioned but not having their own article.

   **e. Stale sources:** Check if any source summaries reference raw files that no longer exist.

   **f. Missing backlinks:** If article A references concept B, but B doesn't link back to A.

3. Generate a lint report:
   ```markdown
   # Wiki Health Report — {date}

   ## Summary
   - Total articles: N
   - Issues found: N
   - Health score: N/100

   ## Broken Links (N)
   - [[missing-concept]] referenced in [[article-a]], [[article-b]]

   ## Orphan Articles (N)
   - [[lonely-article]]: no links in or out

   ## Inconsistencies (N)
   - [[article-a]] says X, but [[article-b]] says Y

   ## Coverage Gaps (N)
   - "concept-x" mentioned 5 times but has no dedicated article

   ## Suggested Actions
   1. Create article for "concept-x"
   2. Add backlink from [[b]] to [[a]]
   3. Resolve contradiction between [[a]] and [[b]]
   ```

4. Ask user: "Should I auto-fix the issues I can fix? (broken links, missing backlinks, orphans)"
   - If yes: fix them and re-run lint to verify.

---

### 6. `output` — Generate Deliverables

**Usage:** `/llm-wiki output "topic" [format]` or "帮我根据知识库生成一份报告"

**Formats:**
- `report` (default): Markdown report in `output/reports/`
- `slides`: Marp-format slides in `output/slides/`
- `brief`: 1-page executive summary

**Steps:**

1. Use search + index to find all relevant articles for the topic.
2. Read relevant articles.
3. Generate the deliverable in the requested format.
4. Save to `output/{format}/{topic-slug}.md`.
5. Ask user: "Should I file key findings back into the wiki?"
   - If yes: create/update concept articles with the new synthesis.

**Marp slide format:**
```markdown
---
marp: true
theme: default
paginate: true
---

# {Title}

---

## {Section 1}

{content}

---

## {Section 2}

{content}
```

---

## Search Script

The skill includes a search engine for the wiki:

```bash
python3 ~/.claude/skills/llm-wiki/scripts/search.py \
  --wiki-dir wiki/ \
  --query "search terms" \
  --top-k 10
```

This returns a JSON list of matches with file paths, scores, and relevant snippets.
Use it to find relevant articles before reading them — saves context window.

## Wiki Conventions

See [references/wiki-conventions.md](references/wiki-conventions.md) for detailed format rules.

Key rules:
- All wiki files use `[[wiki-link]]` syntax for cross-references (Obsidian-compatible)
- Filenames: lowercase-kebab-case (e.g., `neural-network.md`)
- Every article starts with `# Title` followed by `> Auto-compiled by llm-wiki.`
- Source summaries always reference their raw file path
- Concept articles always list their sources
- `_index.md` and `_graph.md` are auto-maintained — never edit manually

## Tips for Users

1. **Start small:** Begin with 5-10 raw documents, run ingest, explore the wiki.
2. **Ask questions:** Every Q&A session enriches the wiki when you file answers back.
3. **Lint regularly:** Run lint after every few ingest cycles to keep quality high.
4. **Use Obsidian:** Open the wiki/ directory in Obsidian for the best reading experience.
5. **Don't edit the wiki manually:** Let the LLM own it. If you want to add information,
   put a new document in raw/ and run ingest.
