# 🏭 Knowledge Factory

### The LLM Knowledge Base workflow Karpathy uses — now a one-command tool

> **"Build personal knowledge bases with LLMs that get smarter the more you use them"** — Inspired by [Andrej Karpathy's latest post](https://x.com/karpathy/status/2039805659525644595)

---

**Andrej Karpathy** (former Tesla AI Director, OpenAI co-founder) recently shared his personal workflow: instead of using LLMs just to write code, he uses them to **compile and manage knowledge**.

He said:

> *"There is room here for an incredible new product instead of a hacky collection of scripts."*

We turned this methodology into a **Claude Code Skill** — ready to use out of the box.

## 💡 Karpathy's Core Methodology

<p align="center">
  <img src="images/01-pipeline.png" width="500" alt="Knowledge Factory Pipeline"/>
</p>

1. **Data Ingest** — Papers, articles, code, data go into `raw/`, LLM auto-compiles them into an interlinked wiki
2. **Obsidian as IDE** — Use Obsidian as the "frontend" to browse the entire knowledge base
3. **Q&A** — Ask questions against the wiki, LLM researches and outputs reports, slides, charts
4. **Knowledge Flywheel** — Outputs get filed back into the wiki, creating compound growth
5. **Linting** — LLM auto-checks: finds contradictions, fills gaps, discovers new connections
6. **Future** — One question spawns a team of LLMs that auto-build a full knowledge base

### The Knowledge Flywheel: Gets Smarter Over Time

<p align="center">
  <img src="images/02-flywheel.png" width="500" alt="Knowledge Flywheel"/>
</p>

### Future: From Solo to LLM Army

<p align="center">
  <img src="images/03-future.png" width="400" alt="Now vs Future"/>
</p>

> Karpathy: *"Way beyond a `.decode()`"*

## 🚀 Quick Start

### Install

Copy the `knowledge-factory/` directory to your Claude Code skills directory:

```bash
# Option 1: Clone + symlink (recommended, easy to update)
git clone https://github.com/chenly255/knowledge-factory.git
ln -s $(pwd)/knowledge-factory/knowledge-factory ~/.claude/skills/knowledge-factory

# Option 2: Direct copy
cp -r knowledge-factory/knowledge-factory ~/.claude/skills/knowledge-factory
```

### Usage

In Claude Code:

```
/knowledge-factory init          # Initialize a knowledge factory
/knowledge-factory ingest        # Compile raw/ documents into the wiki
/knowledge-factory qa "question" # Ask the knowledge base
/knowledge-factory lint          # Health check
/knowledge-factory output "topic"# Generate reports/slides
/knowledge-factory compile       # Full recompilation
```

Or use natural language:

```
"Organize my papers in raw/ into the knowledge base"
"What does the knowledge base say about attention mechanisms?"
"Run a health check on the wiki"
"Generate a report on transformers from the knowledge base"
```

## 📁 Project Structure

```
your-project/
├── raw/                    # Your source materials (papers, articles, code...)
├── wiki/                   # LLM-compiled knowledge base (auto-maintained)
│   ├── _index.md           # Master index: all articles + one-line summaries
│   ├── _graph.md           # Backlink graph
│   ├── concepts/           # Concept articles (auto-categorized)
│   └── sources/            # Source summaries (one per raw document)
├── output/                 # Generated deliverables
│   ├── reports/            # Markdown reports
│   ├── slides/             # Marp slides
│   └── charts/             # Charts
└── .kf.md                  # Project config
```

## 🔧 Built-in Tools

| Tool | Purpose |
|------|---------|
| `scripts/search.py` | BM25 search engine with CLI and JSON output |
| `scripts/index.py` | Auto-generates index and backlink graph |

## 🎯 Design Philosophy

In Karpathy's words:

> *"The LLM writes and maintains all of the data of the wiki, I rarely touch it directly."*

**The wiki is the LLM's domain.** You only need to:
- Feed raw materials into `raw/`
- Ask questions
- Review outputs

The LLM handles: compiling, organizing, linking, linting, and growing the knowledge base.

## 🌟 Credits

This project is entirely based on [Andrej Karpathy's LLM Knowledge Bases methodology](https://x.com/karpathy/status/2039805659525644595). If you find this idea compelling, please go like Karpathy's original post.

## 📄 License

MIT
