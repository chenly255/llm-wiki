# 🏭 LLM Wiki

### The LLM Knowledge Base workflow Karpathy uses — now a one-command tool

> **"Build personal knowledge bases with LLMs that get smarter the more you use them"** — Inspired by [Andrej Karpathy's latest post](https://x.com/karpathy/status/2039805659525644595)

---

**Andrej Karpathy** (former Tesla AI Director, OpenAI co-founder) recently shared his personal workflow: instead of using LLMs just to write code, he uses them to **compile and manage knowledge**.

He said:

> *"There is room here for an incredible new product instead of a hacky collection of scripts."*

We turned this methodology into a **Claude Code Skill** — ready to use out of the box.

## 💡 The Idea in One Sentence

Ever saved 100 papers/articles and never organized them?

**LLM Wiki: you dump files into a folder, AI organizes them into a knowledge base, then you ask questions and get reports — and the more you use it, the smarter it gets.**

## 🔄 The Full Workflow

```
📄 Your stuff               🤖 AI compiles             📚 Knowledge base
papers/articles/code/notes ──→ extracts concepts+links ──→ structured wiki
                                                           │
          ┌────────────────────────────────────────────────┘
          ↓
    💬 You ask ──→ 🤖 AI researches ──→ 📊 reports / charts / slides
                                             │
                                             ↓
                                      📚 archived back (grows!)
                                             │
                                             ↓
                                🔍 AI auto-lints (fix · fill · discover)
```

**6 stages, mapping to Karpathy's original post:**

| Stage | What happens | What you do |
|-------|-------------|-------------|
| ① Ingest | Papers/articles/code go into `raw/`, AI compiles into wiki | Drop files |
| ② Browse | View the wiki in any editor / Obsidian | Read |
| ③ Q&A | Ask questions, AI researches and outputs answers | Ask |
| ④ Flywheel | Outputs auto-archive back into wiki, it grows | Nothing |
| ⑤ Lint | AI finds contradictions, fills gaps, discovers connections | One click |
| ⑥ Future | One question → a team of AIs builds an entire knowledge base | Stay tuned |

> Karpathy: *"Way beyond a `.decode()`"*

## ❓ FAQ

**Q: What can I feed into it?**
A: Anything text-readable — `.md`, `.txt`, `.pdf`, `.py`, `.ipynb`, web clippings... Papers, blogs, code, meeting notes, book summaries, all welcome.

**Q: Do I need Obsidian?**
A: **No.** Karpathy uses Obsidian as a pretty wiki viewer. This skill only operates on `.md` files — VS Code, Typora, or even `cat` works. Obsidian is a nice bonus (graph view, link jumping) but not required.

**Q: How is this different from NotebookLM / RAG?**
A: NotebookLM is read-only — upload docs, ask questions, done. LLM Wiki **grows** — every Q&A output flows back into the wiki. And as Karpathy noted, at ~100 docs scale, you don't even need fancy RAG.

## 🚀 Quick Start

### Install

**Option 1: Just tell Claude Code (easiest)**

Open Claude Code and paste this:

```
Install the llm-wiki skill: clone https://github.com/chenly255/llm-wiki.git and symlink llm-wiki/llm-wiki to ~/.claude/skills/llm-wiki
```

Claude handles everything. You don't touch the terminal.

**Option 2: One-liner**

```bash
git clone https://github.com/chenly255/llm-wiki.git ~/.claude/skills/_llm-wiki-repo && \
ln -s ~/.claude/skills/_llm-wiki-repo/llm-wiki ~/.claude/skills/llm-wiki
```

**Option 3: Manual (custom location)**

```bash
git clone https://github.com/chenly255/llm-wiki.git /your/path/llm-wiki
ln -s /your/path/llm-wiki/llm-wiki ~/.claude/skills/llm-wiki
```

### Usage

After install, just use natural language — no need to memorize commands:

```
"Help me set up a knowledge base"
"Digest the new papers in inbox"
"Compile the knowledge base"
"What does the knowledge base say about attention mechanisms?"
"Run a health check on the wiki"
"Generate a report on transformers from the knowledge base"
"Trust the knowledge-flywheel article"
```

Or use slash commands:

```
/llm-wiki init my-research   # Initialize a project
/llm-wiki digest             # Digest new docs from inbox
/llm-wiki compile            # Build wiki (extract concepts + entities + links)
/llm-wiki query "question"   # Query the knowledge base
/llm-wiki check              # Health check
/llm-wiki export "topic"     # Export reports/slides
/llm-wiki trust              # Mark content as trusted
```

## 📁 Project Structure

```
your-project/
├── raw/
│   ├── inbox/              # Drop new materials here
│   └── sources/            # Processed originals (moved here after digest)
├── wiki/                   # AI-compiled knowledge base (don't touch!)
│   ├── _index.md           # Master index
│   ├── _graph.md           # Link graph
│   ├── concepts/           # Concept articles (ideas, methods, patterns)
│   ├── entities/           # Entity articles (people, tools, orgs)
│   └── sources/            # Source summaries
├── output/                 # AI-generated deliverables
├── trusted/               # Content you trust (human-verified)
└── .kf.md                  # Project config
```

## 🔧 Built-in Tools

| Tool | Purpose |
|------|---------|
| `scripts/search.py` | BM25 search engine — helps AI quickly find relevant articles |
| `scripts/index.py` | Auto-generates index and link graph |

## 🎯 Core Philosophy

In Karpathy's words:

> *"The LLM writes and maintains all of the data of the wiki, I rarely touch it directly."*

**The wiki is the AI's domain, not yours.** You only need to:
- 🗂️ Drop materials into `raw/`
- 💬 Ask questions
- 👀 Review outputs

The AI handles all the heavy lifting: compiling, categorizing, linking, linting, growing.

## 🌟 Credits

This project is entirely based on [Andrej Karpathy's LLM Knowledge Bases methodology](https://x.com/karpathy/status/2039805659525644595). If you find this idea compelling, please go like Karpathy's original post.

## 📄 License

MIT
