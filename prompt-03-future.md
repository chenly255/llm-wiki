# Prompt 03 — 未来愿景 "From One Question to a Knowledge Army"

## 画面核心故事

**一句话理解：** 现在是你+一个 LLM 慢慢搭知识库，未来是你问一个问题，一支 LLM 军团自动帮你从零建好一整个知识库并交付报告。

**视觉策略：** 左右对比，"现在的小作坊" vs "未来的自动化工厂"，对比越强烈越好。

## Karpathy 原文对应

> "In the natural extrapolation, you could imagine that every question to a frontier grade LLM spawns a team of LLMs to automate the whole thing: iteratively construct an entire ephemeral wiki, lint it, loop a few times, then write a full report. Way beyond a .decode()."

## 画面布局（左右对比）

```
┌──────────────────────┬──────────────────────────┐
│                      │                          │
│    【左: Now 现在】   │    【右: Future 未来】    │
│                      │                          │
│                      │                          │
│   👤 一个人           │   👤 一个人               │
│   +                  │   发出一个问题 💬          │
│   🤖 一个机器人       │        │                 │
│                      │        ▼                 │
│   两人面对面          │   ┌─────────┐            │
│   中间一个小书架      │   │ 🤖🤖🤖🤖│            │
│   📚 (wiki还不大)     │   │ 搜 编 审 报│           │
│                      │   │ 索 译 核 告│           │
│   手工作坊的感觉      │   └────┬────┘            │
│   慢但在进步          │        │                 │
│                      │        ▼                 │
│                      │   📚 完整 wiki            │
│                      │   +                      │
│                      │   📊📑🎞️ 全套报告         │
│                      │                          │
│                      │   自动工厂的感觉           │
│                      │   快且完整                │
│                      │                          │
├──────────────────────┴──────────────────────────┤
│                                                  │
│    中间大箭头: ───────────────────►               │
│    .decode() ──────────► Knowledge Factory        │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Prompt for nanobanana

> Hand-drawn whiteboard sketch, Excalidraw style, same character and line style as the previous images (cute round-head robot with antenna and dot eyes, casual imperfect black ink lines, white/cream background).
>
> **Layout: Left-right comparison split by a vertical dashed line in the middle. Left side is "Now", right side is "Future". A large hand-drawn horizontal arrow at the bottom spans the full width pointing from left to right, showing the evolution.**
>
> **LEFT SIDE — "Now":**
> A cozy small workshop scene. One person (simple stick figure with hair, distinct from the robot) and one robot character sitting together at a small desk. Between them is a modest bookshelf with a few .md files on it — the wiki is still small. The robot is writing/organizing files while the person watches or points at something. The mood is friendly but manual — they're working together one step at a time. A small label "Now" in the top-left corner. Maybe a small clock or calendar suggesting this takes time. The scene feels warm but LIMITED — just two characters doing their best.
>
> **RIGHT SIDE — "Future":**
> A dramatically different scene. The same person stands at the top, speaking a single question into a speech bubble with "?" — just ONE question. Below the speech bubble, the question branches out into 4-5 small robots in a row, each doing a different job. Each robot has a tiny icon above its head showing its role:
> - Robot 1: magnifying glass (Search)
> - Robot 2: gear/wrench (Compile)
> - Robot 3: checkmark/magnifying glass (Lint/Review)
> - Robot 4: document/pen (Write Report)
> - Robot 5 (optional): lightbulb (Discover new questions)
>
> These robots are all working simultaneously (motion lines showing activity). Below them, their work converges (arrows pointing down and merging) into TWO impressive outputs at the bottom: a LARGE full bookshelf packed with .md files (a complete wiki), AND next to it a polished stack of deliverables — a report, slides, charts, all neatly arranged. A small label "Future" in the top-right corner. The scene feels POWERFUL and FAST — one question in, a whole knowledge base out.
>
> **BOTTOM ARROW:** Spanning the full width at the very bottom, a large hand-drawn arrow pointing from left to right. On the left end of the arrow, small text: ".decode()". On the right end: "Knowledge Factory". This references Karpathy's original quote about going "way beyond a .decode()".
>
> **Key visual contrast the viewer should immediately feel:**
> - Left: SMALL scale, 2 characters, small shelf, slow and manual
> - Right: BIG scale, many robots, huge output, fast and automated
> - The person is the SAME on both sides — but their power is multiplied
>
> **Style:** Same hand-drawn Excalidraw style. Black ink lines. Left side uses muted/softer tones. Right side uses slightly more vibrant accent colors (blue, orange, green) to feel more energetic and exciting. Cream/white background. Minimal English labels: "Now", "Future", ".decode()", "Knowledge Factory", and small role icons above robots. No Chinese text.
>
> **Aspect ratio: 3:4 (1080×1440)**

## 这张图想表达什么

看图的人一眼就能理解：

1. **左边（现在）**：一个人 + 一个 AI 助手，慢慢攒知识库，像小作坊
2. **右边（未来）**：同一个人只需要问一个问题，一群 AI 自动分工——搜索、编译、审核、写报告——直接交付一整个知识库 + 全套报告
3. **底部箭头**：从简单的 `.decode()`（LLM 只会吐文本）进化到 Knowledge Factory（知识工厂）

**核心冲击：同样一个人，杠杆从 1 个 AI 变成了一支 AI 军团。**
