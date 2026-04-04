# Prompt 02 — 知识飞轮 "The Knowledge Flywheel"

## 画面核心故事

**一句话理解：** 知识库不是整理完就吃灰——你每次用它，它就长大一点。

**视觉策略：** 不画抽象循环图，改成**时间线叙事**——同一个书架在三个时间点越来越满，旁边画出是什么让它长大的。像漫画分镜一样，从上到下讲一个成长故事。

## 画面布局（三格漫画：从上到下）

```
┌────────────────────────────────────┐
│                                    │
│  【第一格：刚建好】                  │
│                                    │
│   📚 小书架（3-4本 .md，半空）       │
│   🤖 机器人站旁边，刚放好几本        │
│   旁注: "Day 1"                    │
│                                    │
├────────────────────────────────────┤
│                                    │
│  【第二格：用了一阵】                │
│                                    │
│   💬 左边：人问了个问题 "?"          │
│   🤖 中间：机器人在研究+写报告       │
│   📊 右边：产出了报告/图表           │
│        ↘                           │
│   📚 书架变大了！(6-7本 .md)        │
│   一个箭头把报告塞回书架             │
│   🔍 机器人拿放大镜检查书架          │
│       找到一个❌标记，修好变✓         │
│   旁注: "Day 30"                   │
│                                    │
├────────────────────────────────────┤
│                                    │
│  【第三格：知识库成熟】              │
│                                    │
│   📚📚 大书架！塞满了 .md            │
│   文件之间密密麻麻的连线(backlinks)  │
│   🤖 机器人很轻松，翘着脚            │
│   💬 旁边一个复杂问题               │
│   📊📑🎞️ 输出了一整套：              │
│       报告 + 幻灯片 + 图表          │
│   💡 机器人头顶冒出新问题灯泡        │
│   旁注: "Day 100"                  │
│                                    │
│   底部: wiki 从小到大的成长曲线       │
│         一条向上弯的弧线 📈          │
│                                    │
└────────────────────────────────────┘
```

## Prompt for nanobanana

> Hand-drawn whiteboard sketch, Excalidraw style, same character and line style as the previous images (cute round-head robot with antenna and dot eyes, casual imperfect black ink lines, white/cream background).
>
> **Layout: A vertical 3-panel comic strip, separated by light hand-drawn horizontal divider lines. Each panel shows the SAME bookshelf at a different stage of growth. Read from top to bottom like a story.**
>
> **PANEL 1 — "Day 1" (top, smallest panel ~25% height):**
> A small bookshelf with only 3-4 .md file icons on it, half the shelf is empty. The cute robot character stands next to it, placing the last file on the shelf, looking proud but the shelf looks sparse. A small label "Day 1" in the corner. The vibe is: just getting started, a fresh new wiki.
>
> **PANEL 2 — "Day 30" (middle, largest panel ~40% height):**
> The same bookshelf is now noticeably BIGGER with 7-8 .md files. This panel shows WHY it grew — two activities happening simultaneously:
> - LEFT SIDE: A person icon with a "?" speech bubble asks a question. The robot is in the middle researching (flipping through pages). On the right, output artifacts appear: a small report document, a bar chart, a presentation slide. A curved arrow takes these outputs and puts them BACK onto the bookshelf (with a small "+" sign on the arrow).
> - BOTTOM-RIGHT: A smaller version of the robot holds a magnifying glass examining the bookshelf. It found a small "✗" error mark on one file and is fixing it to "✓". A small wrench icon nearby.
> - Label: "Day 30"
>
> **PANEL 3 — "Day 100" (bottom, ~35% height):**
> The bookshelf is now LARGE and FULL, packed with .md files. Small curved lines between the files show dense interconnections/backlinks — it's a rich knowledge web now. The robot is relaxed and confident (maybe leaning back or giving a thumbs up). Next to it: a complex question in a speech bubble, and a full set of polished outputs — a report, slides, and charts all neatly arranged. A lightbulb icon above the robot's head suggests it's discovering new questions on its own. At the very bottom, a small hand-drawn growth curve (simple upward arc with a dotted line) reinforces the "compounding growth" message. Label: "Day 100"
>
> **Key visual progression the viewer should immediately feel:**
> - Panel 1: shelf is SMALL and SPARSE
> - Panel 2: shelf is MEDIUM, and you can SEE the actions feeding it
> - Panel 3: shelf is BIG and RICH, robot is confident, outputs are impressive
>
> **Style:** Same hand-drawn Excalidraw style. Black ink lines, soft blue for Q&A arrows, warm orange for Lint/fix elements, light green for the lightbulb/discovery. Cream/white background. Minimal English labels: "Day 1", "Day 30", "Day 100", "wiki/", "Q&A", ".md". No Chinese text.
>
> **Aspect ratio: 3:4 (1080×1440)**

## 这张图想表达什么

看图的人即使完全没有上下文，也应该一眼看懂：

1. **第一格**：刚开始，知识库还很小很空
2. **第二格**：使用过程中，提问产出的东西会回流到知识库，机器人还会检查修复，知识库在变大
3. **第三格**：时间久了，知识库变得又大又密，能回答复杂问题，还能自己发现新方向

**核心冲击：这是一个有"复利效应"的系统——你的每一次使用都在给它增值。**
