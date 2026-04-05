# 🏭 LLM Wiki

### Karpathy 都在用的 LLM 知识库方法论，我把它做成了一键工具

> **"用 LLM 构建个人知识库，越用越聪明"** — 灵感来自 [Andrej Karpathy 的最新分享](https://x.com/karpathy/status/2039805659525644595)

---

AI 大神 **Andrej Karpathy**（前 Tesla AI 总监、OpenAI 联合创始人）最近公开了他的个人工作流：不再只用 LLM 写代码，而是用 LLM **编译和管理知识**。

他说：

> *"There is room here for an incredible new product instead of a hacky collection of scripts."*

我们把这套方法论做成了 **Claude Code Skill**，开箱即用。

## 💡 一句话理解

你有没有过这种体验——收藏了 100 篇论文/文章，但从来没有系统整理过？

**LLM Wiki 做的事情就是：你把资料往文件夹里一丢，AI 帮你自动整理成一个知识库，然后你对这个知识库提问、出报告，而且越用越强。**

## 🔄 完整工作流

```
📄 你的资料               🤖 AI 编译              📚 知识库
论文/文章/代码/笔记  ──→  提炼概念+写摘要+建关联  ──→  结构化 wiki
                                                     │
          ┌──────────────────────────────────────────┘
          ↓
    💬 你提问 ──→ 🤖 AI 研究 ──→ 📊 输出报告/图表/幻灯片
                                      │
                                      ↓
                               📚 归档回知识库（越用越大！）
                                      │
                                      ↓
                          🔍 AI 自动巡检（找错·补缺·发现新关联）
```

**6 个环节，对应 Karpathy 原文：**

| 环节 | 做什么 | 你需要做的 |
|------|--------|-----------|
| ① 数据摄入 | 论文/文章/代码丢进 `raw/`，AI 编译成 wiki | 丢文件 |
| ② 浏览 | 用任意编辑器/Obsidian 查看 wiki | 看 |
| ③ 问答 | 对知识库提问，AI 研究后输出 | 问 |
| ④ 知识飞轮 | 输出自动归档回 wiki，越用越大 | 什么都不用做 |
| ⑤ 巡检 | AI 找矛盾、补缺、发现新关联 | 一键触发 |
| ⑥ 未来 | 一个问题 → 一支 AI 军团自动建库 | 敬请期待 |

> Karpathy: *"Way beyond a `.decode()`"*

## ❓ FAQ

**Q: 什么资料都能喂进去吗？**
A: 只要是文本能读的都行——`.md`、`.txt`、`.pdf`、`.py`、`.ipynb`、网页剪藏……论文、博客、代码、会议笔记、读书摘要，统统可以。

**Q: 必须用 Obsidian 吗？**
A: **不需要。** Karpathy 用 Obsidian 是因为它看 wiki 很漂亮。但我们的 skill 只操作 `.md` 文件，用 VS Code、Typora、甚至 `cat` 命令都能看。装了 Obsidian 体验更好（有图谱、链接跳转），但完全不是必须的。

**Q: 和 NotebookLM / RAG 有什么区别？**
A: NotebookLM 是只读的——你上传资料，它回答问题，完了。LLM Wiki 是**可生长的**——每次问答的产出会回流到知识库，越用越强。而且 Karpathy 说了，在 ~100 篇文档的规模下，根本不需要花哨的 RAG。

## 🚀 快速开始

### 安装

```bash
# 方法一：克隆 + 软链接（推荐，方便更新）
git clone https://github.com/chenly255/llm-wiki.git
ln -s $(pwd)/llm-wiki/llm-wiki ~/.claude/skills/llm-wiki

# 方法二：直接复制
cp -r llm-wiki/llm-wiki ~/.claude/skills/llm-wiki
```

### 使用

在 Claude Code 中：

```
/llm-wiki init my-research   # 初始化知识库项目
/llm-wiki digest             # 消化 inbox 里的新资料
/llm-wiki compile            # 编译 wiki（提取概念+实体+建关联）
/llm-wiki query "问题"          # 对知识库提问
/llm-wiki check           # 健康检查（找矛盾·补缺·修链接）
/llm-wiki export "主题"      # 生成报告/幻灯片
/llm-wiki trust            # 标记你信任的内容
```

或者直接用自然语言：

```
"帮我消化 inbox 里的新论文"
"编译一下知识库"
"知识库里关于 attention mechanism 有什么信息？"
"检查一下知识库的健康状况"
"根据知识库帮我生成一份关于 transformer 的报告"
"把知识飞轮那篇文章导出来"
```

## 📁 目录结构

```
your-project/
├── raw/
│   ├── inbox/              # 丢新资料到这里
│   └── sources/            # 已消化的原始文件（ingest 后自动移过来）
├── wiki/                   # AI 编译的知识库（别动！）
│   ├── _index.md           # 主索引
│   ├── _graph.md           # 关联图谱
│   ├── concepts/           # 概念文章（想法、方法、模式）
│   ├── entities/           # 实体文章（人物、工具、组织）
│   └── sources/            # 原文摘要
├── output/                 # AI 生成的交付物
├── trusted/               # 你审核通过的内容（你信任的知识）
└── .kf.md                  # 项目配置
```

## 🔧 内置工具

| 工具 | 用途 |
|------|------|
| `scripts/search.py` | BM25 搜索引擎，帮 AI 快速定位相关文章 |
| `scripts/index.py` | 自动生成索引和关联图谱 |

## 🎯 核心理念

引用 Karpathy 的原话：

> *"The LLM writes and maintains all of the data of the wiki, I rarely touch it directly."*

**知识库是 AI 的领地，不是你的。** 你只需要：
- 🗂️ 往 `raw/` 丢素材
- 💬 提出问题
- 👀 审阅输出

AI 负责全部脏活：编译、分类、链接、巡检、生长。

## 🌟 致谢

本项目完全基于 [Andrej Karpathy 的 LLM Knowledge Bases 方法论](https://x.com/karpathy/status/2039805659525644595)。如果你觉得这个想法很棒，请去给 Karpathy 的原帖点个赞。

## 📄 License

MIT
