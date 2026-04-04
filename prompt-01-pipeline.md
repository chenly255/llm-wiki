# Prompt 01 — 全景流水线 "LLM Knowledge Factory"

## 画面核心故事

**一句话理解：** Karpathy 用 LLM 搭了一套"知识工厂"——把杂乱资料自动编译成 wiki 知识库，然后在上面做问答、出报告、自动巡检，形成闭环。

这张图是**全景地图**，让读者一眼看到整个系统的 6 个环节是如何串起来的。

## 画面布局（环形流水线 + 中心 Obsidian 窗口）

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│          ① raw/                                          │
│     📄📰💻📊🌐                                          │
│    (散乱的素材堆)                                         │
│          │                                               │
│          ▼                                               │
│     ② 🤖 LLM "compile"                                  │
│     (机器人在加工/编译)                                    │
│          │                                               │
│          ▼                                               │
│  ┌──── ③ wiki/ ─────┐        ┌─────────────┐            │
│  │  .md ←→ .md      │  ◄──── │ ⑥ 🔍 Lint   │            │
│  │  .md ←→ .md      │        │ 找错/补缺/   │            │
│  │  (概念文章+互联)   │        │ 发现新关联   │            │
│  └────────┬─────────┘        └─────────────┘            │
│           │                        ▲                     │
│           ▼                        │                     │
│    ④ 🖥️ Obsidian                   │                     │
│    (查看/浏览 wiki)                 │                     │
│           │                        │                     │
│           ▼                        │                     │
│    ⑤ 💬 Q&A ──→ 📊📑🎞️ Output ───┘                     │
│    (提问)    (报告/幻灯片/图表)                            │
│                    │                                     │
│                    └──→ 归档回 wiki ③ (飞轮!)             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**6 个环节一一对应 Karpathy 帖子：**

| 编号 | 环节 | 帖子原文对应 |
|------|------|------------|
| ① | raw/ 素材堆 | "Data ingest: I index source documents into a raw/ directory" |
| ② | LLM 编译 | "use an LLM to incrementally compile a wiki" |
| ③ | wiki/ 知识库 | ".md files in a directory structure, backlinks, concepts, articles" |
| ④ | Obsidian 查看 | "I use Obsidian as the IDE frontend" |
| ⑤ | Q&A + 输出 | "ask your LLM agent complex questions" + "render markdown, slides, matplotlib" |
| ⑥ | Linting 巡检 | "LLM health checks, find inconsistent data, impute missing data" |

## Prompt for nanobanana

> Hand-drawn whiteboard sketch, Excalidraw style, same character and line style as the reference image (cute round-head robot with antenna and dot eyes, casual imperfect black ink lines, white/cream background).
>
> **Layout: A circular/flow-chart pipeline with 6 clearly numbered stations, arranged in a clockwise flow on a whiteboard. The overall shape is roughly like an inverted "U" or a loop, so the viewer's eye follows a natural path.**
>
> **Station ① — "raw/" (top-left):** A messy pile of various source materials on a small desk or surface — scattered papers with text lines, a tiny browser window icon, a code snippet `</>`, a small chart, a photo thumbnail. Everything tilted and overlapping. A small folder icon labeled "raw/" sits nearby. Hand-drawn arrow pointing down to station ②.
>
> **Station ② — "LLM compile" (left-middle):** The cute robot character (same as reference image) standing at a workbench. The robot is actively processing — taking messy papers from the left and producing neat .md file icons on the right. Small gear icons or sparkle marks above the robot suggest "compiling/processing". Label: "LLM". Arrow pointing down to station ③.
>
> **Station ③ — "wiki/" (center-bottom):** A neat organized structure — like a small bookshelf, card catalog, or folder tree. Inside: 5-6 .md file icons arranged in a grid, with small curved bidirectional arrows between some of them showing backlinks/cross-references. This is visually the most organized and satisfying part of the image. Label: "wiki/". Two arrows leave this station: one going right to station ④, one receiving input from station ⑥.
>
> **Station ④ — "Obsidian" (right-bottom):** A screen/monitor icon showing a rendered view of the wiki — a clean document with headings, a small graph visualization (nodes and edges representing linked notes), maybe a sidebar with file list. This represents the "IDE frontend". The Obsidian diamond logo shape can be subtly included. Arrow pointing up to station ⑤.
>
> **Station ⑤ — "Q&A → Output" (right-middle):** A speech bubble with "?" represents a question being asked. Next to it, three small output icons: a document page (markdown report), a presentation slide, and a small bar chart (matplotlib). These represent diverse output formats. TWO arrows leave this station: one curves back to station ③ (labeled with a small recycling/loop icon — outputs get "filed back" into the wiki), and one goes up to station ⑥.
>
> **Station ⑥ — "Lint" (top-right):** The same robot character (or a smaller version) holding a magnifying glass, examining documents. Small checkmarks ✓ and a wrench icon nearby suggest "health check and fix". An arrow goes from here back into station ③, completing the loop.
>
> **Key visual elements:**
> - The arrows connecting stations should form a visible LOOP/CYCLE, making it obvious this is a self-reinforcing system
> - Station numbers ①②③④⑤⑥ are clearly visible as circled numbers
> - The wiki (station ③) is visually the CENTER and LARGEST element — everything flows through it
> - Two distinct loops are visible: the main pipeline (①→②→③→④→⑤→back to ③) and the maintenance loop (③→⑥→back to ③)
>
> **Style:** Hand-drawn imperfect lines, black ink dominant, soft blue for main flow arrows, warm orange for the feedback/loop-back arrows, light green for lint/check elements. No heavy shading, flat and sketchy. Cream/white background. Friendly and approachable. Minimal English labels only: "raw/", "LLM", "wiki/", "Obsidian", "Q&A", "Output", "Lint". Each label next to its station icon.
>
> **Aspect ratio: 3:4 (1080×1440)** for primary version.

## 这张图想表达什么

看图的人即使不知道 Karpathy 是谁，也应该一眼理解：

1. 有一堆乱七八糟的资料（论文、网页、代码……）
2. LLM 机器人把它们"编译"成结构化的 wiki 知识库
3. 你可以在 Obsidian 里漂亮地查看这个知识库
4. 你可以对知识库提问，LLM 帮你研究并输出报告/幻灯片/图表
5. 输出的内容又归档回知识库，**越用越丰富**
6. LLM 还会自动巡检知识库，找错、补缺、发现新关联

**核心冲击：这不是一次性的整理，而是一个自我增强的知识飞轮。**
