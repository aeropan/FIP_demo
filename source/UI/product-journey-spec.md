# 产品说明页设计规范 · Interactive Product Journey（执行层 V2）

> 适用范围：`fip-causal-reasoning/source/design/design.html`（平台 Demo 中的「产品设计说明」子页面）  
> 最后更新：2026-08-19  
> 依赖：`design-system-spec.md`（方案 B · 暖杏奶油 V2）  
> 说明：本文档为执行层高权重规范，后续开发以此为准。与先前版本冲突处，以本文档为准。

---

## 1. 设计目标

页面需同时满足四个目标：

1. **快速理解**：用户进入后能迅速知道项目是什么、经历了哪些阶段、从调研到部署的大致过程。
2. **过程感**：9 个模块必须呈现为连续推进的过程 `01 → 02 → ... → 09`，而非孤立的 Tab。
3. **深度展示**：每个模块展示该阶段的思考、决策与核心产出（`Thinking → Core Artifact`）。
4. **可演示性**：提供 **Journey Auto Play**，让页面像自动演示一样从 Module 01 推进到 Module 09。

---

## 2. 核心认知转变

### 2.1 页面不是 9 个独立内容页

整个页面应理解为：

> **一个完整项目 Journey 中，9 个具有不同叙事任务的章节。**

整体 Journey：

```
产品设计阶段
│
├─ 01 产品与需求分析
├─ 02 产品需求验证
├─ 03 产品形态与方案设计
└─ 04 视觉设计
        ↓
工程设计阶段
│
├─ 05 数据设计
├─ 06 前端页面设计
└─ 07 开发实现
        ↓
验证与部署
│
├─ 08 测试与验证
└─ 09 部署与收尾
```

但在实际页面中，它们遵循：

> **统一 Journey + 统一模块框架 + 不同内容叙事方式。**

### 2.2 模块回答的问题链

9 个模块形成完整能力证明链：

**第一阶段 · 产品设计**

- 01 Why：从一个技术兴趣出发，最终收敛成一个可以验证的真实产品问题。
- 02 Is It True?：从假设到验证，关键假设如何被证实或推翻。
- 03 What Should It Become?：从需求到产品蓝图，产品形态如何确定。
- 04 How Does It Feel?：从产品原则到视觉语言，界面气质如何建立。

**第二阶段 · 工程设计**

- 05 How Is Knowledge Structured?：从知识到结构化系统，数据如何被组织。
- 06 How Does It Look?：从需求到可交互界面，页面如何被设计。
- 07 How Does It Run?：从设计到运行系统，工程如何实现。

**第三阶段 · 验证与部署**

- 08 Does It Work?：从功能到可靠性证明，系统是否按预期工作。
- 09 Can Others Actually Use It?：从本地项目到在线产品，如何交付并闭环。

---

## 3. 总体架构

页面只设计右侧主工作区（左侧为平台 Sidebar Placeholder）。

```
┌───────────────┬──────────────────────────────────────────────────────┐
│               │                                                      │
│   Platform    │   01 PROJECT HEADER                                  │
│   Sidebar     │   项目名称 / 项目简介 / Tags                         │
│   Placeholder │                                                      │
│               ├──────────────────────────────────────────────────────┤
│               │                                                      │
│               │   02 JOURNEY + AUTO PLAY                             │
│               │   产品设计 │ 工程设计 │ 验证与部署                   │
│               │   01 → 02 → 03 → 04 │ 05 → 06 → 07 │ 08 → 09        │
│               │        ⇢⇢⇢ 自动播放进度 ⇢⇢⇢                         │
│               │   [▶ Auto Play]     [5s ▾]                          │
│               │                                                      │
│               ├──────────────────────────────────────────────────────┤
│               │                                                      │
│               │   03 CURRENT MODULE HEADER                           │
│               │   MODULE 01                              01 / 09     │
│               │   产品与需求分析                                      │
│               │   One-line Thesis                                    │
│               │                                                      │
│               ├──────────────────────────────────────────────────────┤
│               │                                                      │
│               │   04 MODULE WORKSPACE                                │
│               │   ├──────────────┬─────────────────────────────────┤│
│               │   │              │                                 ││
│               │   │   THINKING   │      CORE ARTIFACT              ││
│               │   │              │      (Visualization /           ││
│               │   │  Why /       │       Screenshot /              ││
│               │   │  Decision /  │       Diagram /                 ││
│               │   │  Insight /   │       Gallery)                  ││
│               │   │  Key Output  │                                 ││
│               │   │              │                                 ││
│               │   └──────────────┴─────────────────────────────────┘│
│               │                                                      │
│               ├──────────────────────────────────────────────────────┤
│               │                                                      │
│               │   05 MODULE NAVIGATION                               │
│               │   ← Previous Module              Next Module →       │
│               │                                                      │
└───────────────┴──────────────────────────────────────────────────────┘
```

### 3.1 区域固定为 5 个

1. **01 Project Header** — 理解全局
2. **02 Journey Overview + Interactive Navigator** — 理解流程
3. **03 Current Module Header + Thesis** — 一句话核心观点
4. **04 Module Workspace** — 深入当前阶段
5. **05 Previous / Next Navigation** — 章节导航

### 3.2 模块统一骨架

虽然内容表现不同，但所有模块保持：

- **顶部**：Project Header（全局不变）
- **中部**：Journey Navigator（全局不变）
- **当前模块标题区**：Module Number / 模块名称 / One-line Thesis
- **工作区**：左侧 **Thinking** + 右侧 **Core Artifact**
- **底部**：Previous / Next

**关键变化**：左侧不再是固定的 `What I Did / Key Insight`，而是根据模块叙事任务变化的 **Thinking** 区域。统一的是「左侧负责讲思考与决策」，变化的是「每个模块用什么方式讲」。

---

## 4. 视觉系统引用

直接继承 `design-system-spec.md`（方案 B · 暖杏奶油 V2）的 token：

| Token                    | 色值        | 本页用途                                    |
| ------------------------ | --------- | --------------------------------------- |
| `--color-surface`        | `#FDFBF7` | 页面背景                                    |
| `--color-card`           | `#FFFFFF` | Journey Container、Artifact Canvas、Modal |
| `--color-header`         | `#FFF9F5` | 左侧 Sidebar Placeholder 背景               |
| `--color-text-main`      | `#3E3836` | 标题、正文                                   |
| `--color-text-secondary` | `#6F6763` | 辅助文字、阶段副标题                              |
| `--color-border`         | `#EDE5DD` | 分割线、边框、Journey 连接线                      |
| `--color-primary-900`    | `#6B5045` | 项目标题、当前模块标题、Key Insight 标题              |
| `--color-primary-700`    | `#8C6B5D` | 当前节点编号、小标签、Hover 文字、强调线                 |
| `--color-primary-500`    | `#C7A18E` | 箭头、装饰、Tag 描边、chevron                    |
| `--color-primary-100`    | `#FAF3EC` | 当前节点背景、Hover 背景、Key Insight 轻底          |

### 4.1 色彩比例

- **Neutral**：85–90%
- **Primary**：8–10%
- **Semantic**：≤ 2%

### 4.2 字体

- 中文主字体：`"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif`
- 等宽：`"JetBrains Mono", ui-monospace, monospace`（用于模块编号）

### 4.3 圆角与阴影

| 元素                | Radius  | Shadow                           |
| ----------------- | ------- | -------------------------------- |
| Journey Container | `16px`  | `0 1px 2px rgba(62,56,54,0.04)`  |
| Artifact Canvas   | `12px`  | `0 1px 2px rgba(62,56,54,0.04)`  |
| Modal / Expand    | `16px`  | `0 8px 24px rgba(62,56,54,0.10)` |
| Tag               | `999px` | 无                                |
| Button            | `8px`   | 无                                |

---

## 5. 01｜Project Header

### 5.1 设计原则

- 保持轻量，**不使用大型 Banner 或复杂 Hero**。
- 自然融入页面，不额外套大 Card。
- 推荐高度：**96–120px**。

### 5.2 内容

| 元素   | 内容                                                            | 样式                                      |
| ---- | ------------------------------------------------------------- | --------------------------------------- |
| 小标签  | `Product Journey`                                             | 字重 500，`#8C6B5D`，小型大写                   |
| 项目标题 | `从调研到设计到实现`                                                   | H2，`#6B5045`                            |
| 项目简介 | 展示一个宠物医疗问诊辅助工具，从问题识别、需求验证、方案设计，到工程实现、测试与部署的完整实践过程。            | Body，`#6F6763`，最多两行                     |
| Tags | `[ Product Design ] [ UX Research ] [ Data ] [ Engineering ]` | Tag 样式：`#8C6B5D` 文字 + `#FAF3EC` 背景，pill |

### 5.3 布局

- 左侧：项目标题 + Description
- 右侧：Tags / 项目状态
- 两端对齐，垂直居中。

---

## 6. 02｜Journey Overview + Interactive Navigator

这是页面最重要的交互区域，同时承担：流程概览、当前定位、模块跳转、自动播放进度展示。

### 6.1 三段结构

Journey 为一条横向时间线，分为三段：

- **产品设计阶段**：01 → 02 → 03 → 04
- **工程设计阶段**：05 → 06 → 07
- **验证与部署阶段**：08 → 09

三段之间通过**更大间距 + 细竖线 + 阶段标题**区分，不使用大色块。

### 6.2 节点设计

每个节点包含：

```
01
产品与需求分析
```

| 状态      | 编号        | 标题        | 背景                     | 连接线              |
| ------- | --------- | --------- | ---------------------- | ---------------- |
| 默认      | `#6F6763` | `#6F6763` | 透明                     | `#EDE5DD`        |
| Hover   | `#8C6B5D` | `#6B5045` | `#FAF3EC`              | —                |
| Current | `#8C6B5D` | `#6B5045` | `#FAF3EC` + 下方 2px 强调线 | 前一段连接线 `#C7A18E` |
| 已完成     | `#8C6B5D` | `#6F6763` | 透明                     | `#C7A18E`        |

Current 节点不应做成大圆球，而是**精致的流程定位点**：

- 编号背景 `#FAF3EC`
- 编号下方 2px 强调线 `#8C6B5D`
- 标题 `#6B5045`

### 6.3 阶段标题

每个阶段上方显示阶段名：

```
产品设计
01 ─── 02 ─── 03 ─── 04
```

- 阶段标题：`#6F6763`，字重 500，字号 12px
- 阶段分隔：细竖线 `#EDE5DD`，高度与节点区域对齐

### 6.4 Auto Play Control

位于 Journey 区域右上角或右下角。

#### 6.4.1 按钮状态

| 状态      | 文字               | 样式                                   |
| ------- | ---------------- | ------------------------------------ |
| Playing | `⏸ Auto Playing` | `#FAF3EC` 背景，`#6B5045` 文字，8px radius |
| Paused  | `▶ Auto Play`    | Ghost Button，无边框，`#6B5045` 文字        |

#### 6.4.2 速度选择

提供固定档位：

| 档位 | 适合场景 |
| -- | ---- |
| 3s | 快速演示 |
| 5s | 默认   |
| 8s | 详细浏览 |

下拉选择器：`[ 5s ▾ ]`，Ghost 风格。

### 6.5 自动播放动效

播放时，一串小 chevron 沿 Journey 连接线从当前节点移动到下一个节点：

```
01    › › ›    02
```

动画行为：

1. 当前 Module 停留 5s（默认）。
2. chevron 从当前节点出发，沿连接线移动。
3. 到达下一节点时，下一节点激活，下方内容切换。
4. 停留计时重新开始。

箭头动画：

- 使用 3–5 个小 chevron（`›`）
- 沿连接线水平移动
- 单个 chevron 移动时长：**800–1200ms**
- 使用 `#C7A18E` 颜色

### 6.6 暂停规则

用户一旦主动操作，Auto Play 自动暂停：

- 点击任意 Module 节点
- 点击 Artifact 的 Expand / Preview
- 点击 Previous / Next
- 点击 Pause 按钮

**原则：自动演示是辅助，不抢夺用户控制权。**

---

## 7. 03｜Current Module Header

### 7.1 结构

```
MODULE 01                              01 / 09
产品与需求分析
One-line Thesis：从一个技术兴趣出发，最终收敛成一个可以验证的真实产品问题。
```

- 小标签：`MODULE 01`（`#8C6B5D`）
- 右侧：`01 / 09`（`#6F6763`）
- 标题：`产品与需求分析`（H3，`#6B5045`）
- **One-line Thesis**：一句话核心观点（`#6F6763`），替代原来的 Input/Output 结构

推荐高度：**90–110px**。

### 7.2 Thesis 规则

- 不是普通介绍，而是整个模块的**核心观点**。
- 控制在 30 字以内。
- 必须与模块叙事任务一致。

---

## 8. 04｜Module Workspace

### 8.1 布局

统一采用 **38% Left + 62% Right**。

```
┌─────────────────────────┬────────────────────────────┐
│                         │                            │
│      THINKING           │                            │
│                         │                            │
│      Block A Title      │      CORE ARTIFACT         │
│      Block A Content    │                            │
│                         │      (Artifact Canvas)     │
│      Block B Title      │                            │
│      Block B Content    │                            │
│                         │                            │
│      Block C Title      │                            │
│      Block C Content    │                            │
│                         │                            │
└─────────────────────────┴────────────────────────────┘
```

### 8.2 左侧 Thinking 区域

**核心原则**：左侧负责讲「思考与决策」，每个模块的 Block 标题各不相同。

示例：

| 模块 | Block A               | Block B              | Block C            |
| -- | --------------------- | -------------------- | ------------------ |
| 01 | THE STARTING POINT    | WHAT I NOTICED       | WHY FIP            |
| 02 | INITIAL ASSUMPTION    | WHAT CHANGED         | VALIDATED DECISION |
| 03 | THE PRODUCT PRINCIPLE | KEY DESIGN DECISIONS | WHY THIS SHAPE     |
| 04 | VISUAL DIRECTION      | DESIGN DECISIONS     | TOKEN SUMMARY      |
| 05 | SCHEMA PRINCIPLE      | KEY ENTITIES         | WHY THIS STRUCTURE |
| 06 | INTERFACE STRATEGY    | KEY PAGES            | WHY THIS FLOW      |
| 07 | ENGINEERING STRATEGY  | KEY COMPONENTS       | WHY THIS STACK     |
| 08 | VALIDATION FOCUS      | BOUNDARY CASES       | TEST CONCLUSION    |
| 09 | DELIVERY STRATEGY     | PROJECT CLOSURE      | NEXT STEPS         |

### 8.3 右侧 Core Artifact

统一容器 **Artifact Canvas**：

```
┌──────────────────────────────────────┐
│                                      │
│  RESEARCH ARTIFACT            ↗      │
│                                      │
│         CURRENT ARTIFACT             │
│                                      │
│                                      │
├──────────────────────────────────────┤
│  Artifact Caption                    │
└──────────────────────────────────────┘
```

- Background：`#FFFFFF`
- Border：`#EDE5DD`
- Radius：`12px`
- Padding：`24px`
- Shadow：`0 1px 2px rgba(62,56,54,0.04)`
- 类型标签：左上角小字，`#8C6B5D`
- Expand 按钮：右上角 `↗`，Ghost 风格

---

## 9. Artifact 实现类型规则

右侧统一称为 **Core Artifact**，但不强制同一种组件。建立三种实现类型：

### 9.1 Type A · 原生可视化

**适合**：时间线、架构图、Schema、流程、数据矩阵、测试结果

**使用**：HTML + CSS + SVG

**适用模块**：01、02、03、05、07、08、09

**特点**：

- 数据内嵌在 JS 中
- 支持 Hover / 点击交互
- 可随模块切换重绘
- 不依赖外部图片

### 9.2 Type B · 真实产物展示

**适合**：UI 截图、原型图、设计规范、真实页面

**使用**：前端容器 + 真实截图 + 点击放大

**适用模块**：04、06

**特点**：

- 图片内嵌 Base64 或相对路径
- 提供 Expand 查看大图
- 可叠加 Hotspot 标注

### 9.3 Type C · 混合型

**适合**：需要同时展示原生可视化与真实截图的复杂 Artifact

**使用**：HTML / SVG + 真实截图 + 动态 Hover

**适用模块**：04（视觉方向对比 → Gallery → 最终设计稿）

---

## 10. 9 个模块设计定位总表

| 模块 | 模块名称      | 核心叙事任务     | 左侧重点           | 右侧 Artifact              | 表现类型              |
| -- | --------- | ---------- | -------------- | ------------------------ | ----------------- |
| 01 | 产品与需求分析   | 从技术兴趣到产品机会 | 起点、观察、收敛       | Opportunity Evolution    | Story             |
| 02 | 产品需求验证    | 从假设到验证     | 假设变化、关键洞察      | Priority Shift           | Evidence          |
| 03 | 产品形态与方案设计 | 从需求到产品蓝图   | 产品决策、核心原则      | Product Blueprint        | Blueprint         |
| 04 | 视觉设计      | 从产品原则到视觉语言 | 视觉方向、设计决策      | Visual Direction Gallery | Gallery           |
| 05 | 数据设计      | 从知识到结构化系统  | Schema 决策、数据原则 | Knowledge Architecture   | Architecture      |
| 06 | 前端页面设计    | 从需求到可交互界面  | 页面设计方法、交互原则    | Interface Evolution      | Gallery / Process |
| 07 | 开发实现      | 从设计到运行系统   | 工程策略、实现方法      | System Build Stack       | Engineering       |
| 08 | 测试与验证     | 从功能到可靠性证明  | 验证重点、边界场景      | Test Proof Matrix        | Proof             |
| 09 | 部署与收尾     | 从本地项目到在线产品 | 交付策略、项目闭环      | Deployment Architecture  | Delivery          |

### 10.1 视觉节奏

```
01  Story
  ↓
02  Evidence
  ↓
03  Blueprint
  ↓
04  Visual
  ↓
05  Architecture
  ↓
06  Interface
  ↓
07  Engineering
  ↓
08  Proof
  ↓
09  Delivery
```

---

## 11. 模块详细规格（Module Specifications）

> **状态**：Module 01–03 为**设计定稿**（用户提供于 2026-08-19，标注【设计定稿 ✅】）；Module 04–09 为**草稿**（基于项目理解占位，待用户提供定稿后替换）。

### 11.0 模块开发基线（01–09 全部定稿）

#### 11.0.1 全局页面 Shell 约束（三模块共用）

- 现有左侧 Sidebar 仅保留 placeholder。
- 主内容使用暖杏奶油设计系统（方案 B · 暖杏奶油 V2）。
- 顶部横向 Journey 保持常驻。
- 同一时间只显示一个 active module 的内容区。
- 模块内容使用约 7:5（或 2:1）双栏布局：思考/决策在左，Core Artifact 在右。

#### 11.0.2 01–03 视觉节奏（连续产品决策链）

```
MODULE 01 ─── INTEREST → OBSERVATION → OPPORTUNITY → FIP MVP
MODULE 02 ─── ASSUMPTION → RESEARCH → EVIDENCE → PRIORITY SHIFT
MODULE 03 ─── VALIDATED NEED → PRODUCT PRINCIPLE → THREE CAPABILITIES → EXPLAINABLE PRODUCT
```

三者不是孤立章节，而是连续链：**我发现了一个值得解决的问题 → 我验证并修正了自己的判断 → 我将它定义成了一个真正可落地的产品。**

#### 11.0.3 给自动开发工具的前三模块总规则

- **MODULE 01**：Narrative / Opportunity Convergence。Artifact 应从宽泛技术兴趣视觉收窄到聚焦的 FIP MVP 机会。
- **MODULE 02**：Evidence / Assumption Shift。Artifact 应比较「研究前的假设」与「验证后的优先级」。视觉焦点是「改变了什么」，而不是「做了多少研究」。
- **MODULE 03**：Blueprint / Product System。Artifact 应展示 Conversation、Causal Graph、Evidence Library 如何构成一个可解释知识闭环。
- **统一要求**：
  - 三个模块均使用原生前端可视化（HTML + CSS + SVG），**不要使用生成式信息图图片**作为主 Artifact。
  - 避免重复的卡片布局。
  - Module 01 = 收敛叙事；Module 02 = 对比证据；Module 03 = 连接蓝图。
  - **Artifact 动画只在进入对应模块时播放一次**，不循环；Journey 自动播放控制模块间切换。
- **颜色基线**（严格执行）：
  - 页面背景 `#FDFBF7`；卡片/Artifact 表面 `#FFFFFF`；边框 `#EDE5DD`；主文字 `#3E3836`；次文字 `#6F6763`。
  - 选中/强调 `#8C6B5D`；强强调 `#6B5045`；选中/高亮背景 `#FAF3EC`。
  - Primary 用色克制；**除非表示真实语义状态，否则不使用 Semantic 色**。

#### 11.0.4 04–06 视觉节奏（从概念到可执行系统）

04–06 承接 03 DEFINE，证明「如何把一个产品概念变成可执行的设计系统、数据结构和具体界面」。三者采用明显不同的表现方式：

```
MODULE 04 ─── VISUAL DIRECTION → DESIGN SYSTEM
MODULE 05 ─── KNOWLEDGE → SCHEMA → GRAPH
MODULE 06 ─── REQUIREMENT → STRUCTURE → INTERFACE
```

从体验上：Module 04 像在看一个**视觉设计决策过程**；Module 05 像在看一个**知识系统架构**；Module 06 像真正进入**产品 Demo 展示**。即使仍沿用统一双栏框架，也不会产生连续阅读疲劳。

#### 11.0.5 给自动开发工具的 04–06 总规则

- **全局 Shell 不变**：左侧 Sidebar 仍为 placeholder；顶部 Journey 常驻；一次只显示一个 active module；左栏聚焦推理与决策，右栏为 Core Artifact；内容比例约 7:5 / 2:1（依视口）。
- **MODULE 04 — VISUAL DESIGN / Gallery**：三个紧凑视觉方向预览 + 一个最终选中方向 + 渐进过渡到设计系统预览。方向探索用原生前端 UI；可嵌入或预览真实设计系统 HTML 页面。
- **MODULE 05 — DATA DESIGN / Architecture**：Schema 可视化 + 四类节点 + 五种关系类型 + 三个关系元数据属性（polarity / confidence / evidence）+ 紧凑 live graph preview。原生 HTML + SVG；可交互节点与边检查。
- **MODULE 06 — FRONTEND PAGE DESIGN / Interface Showcase**：Conversation / Knowledge Graph / Literature Library；使用真实截图或真实渲染界面；Tab 切换；hotspot 标注；全尺寸预览 Modal。
- **VISUAL RHYTHM**：Module 04 = Gallery；05 = Architecture；06 = Interface Showcase。**不要用相同的卡片网格模式套所有模块。**
- **ANIMATION**：
  - Artifact entrance 动画只在模块激活时播放一次，不循环；module-level reveal 最长 2.5s；micro-interaction 150–300ms。
  - 遵守 `prefers-reduced-motion`：关闭时停止箭头位移、模块直接切换。
- **COLORS**：
  - Base：`#FDFBF7` / `#FFFFFF` / `#EDE5DD` / `#3E3836` / `#6F6763`。
  - Primary emphasis：`#FAF3EC` / `#8C6B5D` / `#6B5045`。
  - 图谱语义类别用克制的 accent border / indicator，而非满色卡片。
  - 维持：Neutral 85–90% / Primary 8–10% / Semantic ≤2%。
- **Avoid**：过度嵌套卡片、满宽彩色背景、高饱和技术渐变、无解释价值的装饰图表、用 AI 生成信息图作为技术 Artifact。

#### 11.0.6 07–09 视觉节奏（构建感 → 验证感 → 完成感）

07–09 承接 06 INTERFACE，强调「项目如何真正跑起来」，并保持统一骨架（Journey / Module Header / 左 Thinking + 右 Artifact / Input-Output），但进一步拉开视觉表现差异：

```
MODULE 07 ─── ARCHITECTURE → BUILD → INTEGRATION
MODULE 08 ─── COVERAGE → BOUNDARY → BEHAVIOR
MODULE 09 ─── DEPLOY → LIVE → DELIVER
```

从体验上：Module 07 像看工程拆解与系统构建（构建感）；Module 08 像看产品行为与边界验证（验证感）；Module 09 像真正交付可访问产品并收束闭环（完成感）。三者分别呈现 **构建感 → 验证感 → 完成感**。

#### 11.0.7 完整 9 模块视觉节奏（自动开发工具总览）

**9 个核心追问（浏览体验节奏）**：

```
MODULE 01  WHY THIS PRODUCT?
MODULE 02  IS THE NEED REAL?
MODULE 03  WHAT SHOULD IT BECOME?
MODULE 04  HOW SHOULD IT FEEL?
MODULE 05  HOW SHOULD KNOWLEDGE WORK?
MODULE 06  HOW DOES THE EXPERIENCE TAKE SHAPE?
MODULE 07  HOW IS IT BUILT?
MODULE 08  DOES IT BEHAVE CORRECTLY?
MODULE 09  CAN PEOPLE ACTUALLY USE IT?
```

**9 个模块 Artifact 表现总表（避免 9 个长得一样的说明卡片）**：

| Module       | Artifact 表现                                  | 模块类型               |
| ------------ | -------------------------------------------- | ------------------ |
| 01 产品与需求分析   | 项目起源 / Opportunity Map（收敛叙事）                 | Narrative          |
| 02 产品需求验证    | 用户洞察 / Priority Shift（对比证据）                  | Evidence           |
| 03 产品形态与方案设计 | Product Blueprint（连接蓝图）                      | Blueprint          |
| 04 视觉设计      | Design System / Visual Evolution（画廊）         | Gallery            |
| 05 数据设计      | Knowledge Schema / Graph Structure（架构）       | Architecture       |
| 06 前端页面设计    | Page Blueprint / Interface Composition（真实界面） | Interface Showcase |
| 07 开发实现      | System Architecture（分层工程）                    | Engineering        |
| 08 测试与验证     | Scenario Coverage Matrix（验证矩阵）               | Proof              |
| 09 部署与收尾     | Live Deployment Map（部署闭环）                    | Delivery           |

> 至此第 11 节 9 个模块全部为用户定稿，可直接进入开发执行层。

---

### 11.1 Module 01 · 产品与需求分析【设计定稿 ✅】

> 来源：用户提供于 2026-08-19。**阶段递进**：Module 01 Discover（发现问题）→ 02 Validate（验证问题）→ 03 Define（定义解决方案）。三者视觉叙事必须明显不同，不要做成三个相似的「左边文字 + 右边图表」。

#### 1. 模块定位

这一模块最重要的不是介绍「我研究了宠物行业」，而是让访问者看到一个完整的**产品机会收敛能力**：一个最初源于技术兴趣的想法，如何经过领域观察与问题筛选，最终收敛成一个可以实际验证的 MVP 产品。

核心叙事：**From Interest to Opportunity（从兴趣，到机会）**。

它直接展示产品思考：不是技术先决定产品，而是重新寻找技术适合解决的问题。

#### 2. 核心 Thesis

建议放在模块标题下方。

- **中文**：从对本体与因果图谱的兴趣出发，我没有直接寻找技术应用场景，而是先寻找一个真正需要"解释"的问题。
- **英文辅助标签**：`FROM INTEREST TO OPPORTUNITY`

#### 3. 左侧设计

Module 01 左侧不要做成传统的 `WHY / WHAT I DID / KEY INSIGHT`，因为本质是「逐步收敛」的故事。改为三个**连续区块**（区块间用 ↓ 连接）：

```
THE STARTING POINT
        ↓
WHAT I NOTICED
        ↓
WHY FIP
```

**A. THE STARTING POINT**

- 内容：最初的兴趣并不是宠物医疗，而是一个更基础的问题——能否用本体与图谱组织复杂知识，让系统不仅给出答案，还能解释答案从哪里来。
- 辅助说明：与传统关键词检索或直接生成答案相比，更关注知识之间的结构、因果关系以及推理路径。
- **设计约束**：
  - 不使用卡片。
  - 结构为：`01`（编号）+ `THE STARTING POINT`（标签）+ 正文 + 强调短语「本体论 + 因果图谱」。
  - 「本体论 + 因果图谱」使用 `#6B5045`，且字号略高于正文。

**B. WHAT I NOTICED**

- 这是 Module 01 最重要的左侧内容。
- 内容：在寻找适合落地的领域时，把注意力转向了宠物健康场景。
- 使用**三个短句**（非一大段）：
  ```
  宠物主需要快速获得判断
                  ↓
  但医疗问题天然存在不确定性
                  ↓
  "给出答案"远远不够
  ```
- **Highlight 块**（关键句）：真正的问题不是"信息够不够"，而是用户不知道这个答案为什么值得相信。
  - 样式：`#FAF3EC` 浅背景；左侧 `3px` Primary 700 `#8C6B5D` 指示线；不做完整卡片；内边距 `16px 20px`。

**C. WHY FIP**

- 体现 MVP 收敛能力。不要简单列出三个 Bullet，设计为三个**轻量 Decision Item**：
  - `01 · CLEAR BOUNDARY` 疾病范围明确 —— 知识边界相对清晰，可以控制 MVP 的数据规模。
  - `02 · CAUSAL STRUCTURE` 天然具备因果链 —— 病因、症状、诊断、治疗与风险之间存在明确关联，适合图谱表达。
  - `03 · SMALL BUT COMPLETE` 小规模也能跑通完整闭环 —— 无需构建庞大医学知识库，也能验证：知识结构化 → 图谱查询 → 推理解释 → 前端呈现。
- **KEY DECISION 总结**：不追求"覆盖所有宠物疾病"，而是选择一个足够聚焦、同时能完整体现产品核心能力的场景。使用 Primary 100 `#FAF3EC` 背景即可。

#### 4. 右侧 Core Artifact

- **Artifact 名称**：Opportunity Evolution
- **副标题**：How an initial technical interest became a testable product opportunity.
- **推荐表现**：**Opportunity Funnel（机会演化路径）**，横向逐步收敛。**不建议使用传统时间轴**，因为这是「问题不断收敛」，不是「时间发生顺序」。
- **结构（5 个阶段，容器逐步缩小）**：
  ```
  TECH INTEREST → KNOWLEDGE STRUCTURE → EXPLAINABLE AI → PET HEALTH → FIP MVP
  ```
  容器随过程推进逐渐缩小，形成「大范围兴趣 → 更具体问题 → 明确产品机会」的视觉隐喻。
- **最终节点 FIP MVP 重点突出**：
  - 背景 `#FAF3EC`；边框 `#8C6B5D`；右上角标签 `PRODUCT OPPORTUNITY`。
  - 文案：A focused environment to validate explainable knowledge reasoning.
- **类型**：Type A（原生 HTML + SVG）。

#### 5. 交互设计

- **Hover 每个阶段**：当前节点上浮 `2px`；Border → Primary 700 `#8C6B5D`；显示一句补充说明（如 `PET HEALTH` → "A domain where information quality and explainability directly affect trust."）。
- **Auto Play 进入 Module 01**：左侧内容淡入；Artifact 从顶部开始逐级收敛；每个节点间隔 `300–450ms`；最终停留在 FIP MVP；FIP MVP 出现一次非常轻微的强调动画。整体不超过 `1.8s`。

#### 6. 开发关键词

```
module-type: narrative
left-layout: stacked editorial sections
artifact: native HTML + SVG
visual: opportunity convergence
interaction: hover details, sequential reveal
avoid: traditional long timeline, large cards, dense paragraphs
```

---

### 11.2 Module 02 · 产品需求验证【设计定稿 ✅】

> 与 Module 01 明显不同：Module 01 是「我发现了一个机会」，Module 02 是「我发现自己的判断并不完全正确」。这一点比「调研验证了我的想法」更能体现产品能力。

#### 1. 模块定位

展示关键假设如何被验证或修正：最初认为用户需要治疗方案，但验证后发现用户更迫切需要理解诊断逻辑。重点是「哪些判断需要被改变」，而非「调研验证了多少」。

#### 2. 核心 Thesis

- **中文**：真正有价值的调研，不是证明原来的判断正确，而是找到哪些判断需要被改变。
- **英文**：`ASSUMPTION → EVIDENCE → ADJUSTMENT`

#### 3. 左侧设计

整体结构明显不同于 Module 01：

```
INITIAL ASSUMPTION
        ↓
WHAT USERS SAID
        ↓
WHAT CHANGED
```

**A. INITIAL ASSUMPTION**

- 使用一个非常轻量的 Assumption List，**不要使用完整 Card**。
- 每项采用 `编号 + assumption + 分隔线` 的列表结构：
  ```
  01      assumption
  ────────────────────
  02      assumption
  ────────────────────
  03      assumption
  ```
- 三项内容：
  1. 用户最需要诊断与治疗信息
  2. 风险提示可能增加理解成本
  3. 知识边界可能降低产品体验

**B. WHAT USERS SAID**

- **不建议使用词云**（信息价值低）。更建议使用 **Research Signal（调研信号列表）**：
  - `HIGH FREQUENCY`（高频关注）：诊断路径、治疗方案
  - `HIGH TRUST CONCERN`（高信任关切）：证据来源、风险提示
  - `HIGH ACCEPTANCE`（高接受度）：不确定性、知识边界
- 旁边显示一个非常轻量的 **Interview Note**：
  - 引语："告诉我不知道，比假装知道更容易接受。"
  - **注意**：不要表现成真实引用某个具体用户；标记为 `Synthesized Research Insight`（整理后的调研结论）。

**C. WHAT CHANGED**

- 这是整个 Module 02 的重点。设计为 **Priority Shift**（优先级重排）。
- 使用 **Priority Bars**（不要简单使用星级）：
  ```
  DIAGNOSIS        █████
  TREATMENT        █████
  RISK             ████
  KNOWLEDGE LIMIT  ████
  ```
  - 默认颜色 `#EDE5DD`；强调颜色 `#8C6B5D`。
- 展示 BEFORE（诊断/治疗/风险/知识边界 初始优先级）与 AFTER（验证后优先级变化）。

#### 4. 右侧 Core Artifact

- **Artifact 名称**：Assumption Shift
- **副标题**：What changed after speaking with real users.
- **核心视觉**：**Before / After Matrix**（不要做普通箭头流程图）：
  ```
  ┌── BEFORE ──┐    ┌── AFTER ───┐
  │ Diagnosis  A │    │ Diagnosis  A │
  │ Treatment  A │    │ Treatment  A │
  │ Risk       C │    │ Risk       B │
  │ Knowledge  C │    │ Boundary   B │
  └─────────────┘    └─────────────┘
  ```
  - 中间**不要使用粗箭头**，使用一条细连接线：`ASSUMPTION ──────────────→ VALIDATION`。
- **最关键的视觉效果**：Risk 和 Knowledge Boundary 在 Before 使用低权重 `#F5F2EF`；在 After 提升到 `#FAF3EC` 背景 + `#C7A18E` 边框，并出现 `PRIORITY ↑` 标签。让用户一眼看到「调研带来了什么改变」。
- **类型**：Type A（原生 HTML + SVG）。

#### 5. Artifact Key Insight（底部）

- 英文：Trust was not reduced by uncertainty. It was reduced when the system could not explain its uncertainty.
- 中文（实际页面显示）：用户并不排斥"不确定"，真正影响信任的，是系统无法解释为什么不确定。
- 这是 Module 02 最值得强调的一句话。

#### 6. 交互设计

- **Hover** Before / After 的条目：显示 `WHAT CHANGED`，例如 `Risk disclosure moved from secondary → core experience.`
- **Auto Play 进入 Module 02** 动画顺序：BEFORE 出现 → Research Signals 逐条出现 → After（Risk / Boundary 上升）→ Key Insight Highlight。动画总时长 `1.5–2.0s`。

#### 7. 开发关键词

```
module-type: evidence
left-layout: assumption list, research signals, priority change
artifact: native HTML + SVG
visual: before-after comparison, priority elevation
avoid: word cloud, fake survey charts, excessive statistics
```

---

### 11.3 Module 03 · 产品形态与方案设计【设计定稿 ✅】

> 产品设计阶段最有「成品感」的模块：01 发现机会 → 02 验证与修正 → 03 定义产品。

#### 1. 模块定位

需求本身不会自动变成产品。真正的设计工作，是决定哪些能力必须共同出现，才能形成完整体验。Module 03 应成为产品设计阶段最有「成品感」的模块。

#### 2. 核心 Thesis

- **中文**：需求本身不会自动变成产品。真正的设计工作，是决定哪些能力必须共同出现，才能形成完整体验。
- **英文**：`FROM VALIDATED NEEDS TO PRODUCT SYSTEM`

#### 3. 左侧设计

Module 03 左侧不采用连续故事，采用更像正式产品设计模块的结构：

```
PRODUCT PRINCIPLE
        ↓
THE THREE PARTS
        ↓
KEY DECISIONS
```

**A. PRODUCT PRINCIPLE**

- 顶部突出能力闭环：**Answer → Explain → Verify**
  - `ANSWER`：快速回答问题
  - `EXPLAIN`：展示因果关系与推理路径
  - `VERIFY`：提供文献与证据来源
- 使用三个**紧凑的横向文字 Block**，而不是 Card。

**B. THE THREE PARTS**

- `01 CONVERSATION`：让用户自然提问
- `02 CAUSAL GRAPH`：让用户理解答案如何得出
- `03 EVIDENCE LIBRARY`：让用户追溯知识来源
- **重点强调**：不是三个独立页面，而是一个完整的 **Explainable Knowledge Loop**（可解释知识闭环）。

**C. KEY DECISIONS**

只保留三个最能体现判断力的决策：

- **Why not a pure chatbot?** 因为只有答案，无法形成可信度。
- **Why show execution trace?** 让系统内部的确定性推理过程对用户可见。
- **Why no LLM in the demo?** 主动控制演示环境的不确定性，把重点放在知识图谱推理本身（体现「不是不会用大模型，而是有意识地决定在哪个阶段不用」）。

#### 4. 右侧 Core Artifact

- **Artifact 名称**：Explainable Product Blueprint
- **副标题**：Answer, explain and verify — in one connected experience.
- **推荐结构**：**产品能力闭环**（不要做成普通三模块架构图，也不要做成传统技术架构图）：
  ```
  USER QUESTION
        │
        ▼
  CONVERSATION
        │
        ▼
  KNOWLEDGE QUERY
     ╱         ╲
    ╱           ╲
   ▼             ▼
  CAUSAL GRAPH   EVIDENCE
  EXPLAIN         VERIFY
     ╲         ╱
      ╲       ╱
        ▼
  TRUSTED ANSWER
  ```
- **视觉层级**：
  - 中心 `USER QUESTION`：白色卡片。
  - 下方 `CONVERSATION`：Primary 100 `#FAF3EC`。
  - 两侧 `CAUSAL GRAPH` / `EVIDENCE LIBRARY`：白色 + 边框。
  - 最终 `EXPLAINABLE ANSWER`：背景 `#FAF3EC` + 边框 `#8C6B5D` + 小标签 `PRODUCT CORE`。
- **微型 Interface Preview**（Blueprint Preview，非正式截图）：Artifact 底部加入简化三栏 UI：
  ```
  ┌──────┬─────────────────────┬──────────┐
  │ Nav  │ Conversation        │ Trace    │
  │      │   Answer            │ Step 01  │
  │      │                     │ Step 02  │
  └──────┴─────────────────────┴──────────┘
  ```
  作用是告诉访问者：前面的产品架构最终真的会变成一个可操作的界面。
- **类型**：Type A（原生 HTML + SVG）。

#### 5. 交互设计

- **Hover 三个模块**：
  - `Conversation` 高亮：Ask naturally
  - `Causal Graph` 高亮：See why
  - `Evidence` 高亮：Trace the source
- Hover 后其他模块轻微降低到 `opacity: 0.45`，让用户理解三个能力不是平行堆叠，而是围绕同一个问题协同工作。

#### 6. 自动播放动画

进入 Module 03：USER QUESTION 出现 → Conversation 连接 → Causal Graph + Evidence 从两侧展开 → Explainable Answer 最终汇聚。最后整个 Blueprint 保持静止，**不要循环播放 Artifact 本身**。持续时间 `1.8–2.2s`。Artifact 只在模块切换时执行一次 Entrance Animation（顶部 Journey 已存在自动播放逻辑）。

#### 7. 开发关键词

```
module-type: blueprint
left-layout: product principle, three-part capability, key decisions
artifact: native HTML + SVG
visual: connected product loop, not technical architecture
interaction: module focus, relationship highlight
avoid: generic feature cards, standard flowchart appearance, large technical diagram
```

---

### 11.4 Module 04 · 视觉设计（Gallery）

> 状态：**定稿**（用户 2026-08-19 提供）

#### 1. 模块定位

Module 04 不应只是展示「我选了一个暖杏奶油色」，真正应展示的是：**如何从多个视觉方向中进行选择，并最终建立一套可以约束整个产品的视觉系统**。最需要体现的能力是 **Visual Exploration → Design Decision → Design System**，而不是单纯展示最终设计稿。

在 Journey 中的角色：从「定义产品」(03 DEFINE) 推进到「建立视觉语言」(04 VISUALIZE)。

#### 2. 核心 Thesis

> 视觉设计不是为页面选择一种"好看的风格"，而是为产品建立一套能够持续指导设计与开发的规则。

英文辅助标签：**FROM VISUAL DIRECTION TO DESIGN SYSTEM**

#### 3. 左侧内容结构（Thinking）

Module 04 左侧采用三个递进层级，相比 Module 01–03 的连续叙事，这里更像一次设计决策过程：

```
EXPLORE
   ↓
CHOOSE
   ↓
SYSTEMIZE
```

**A. EXPLORE — EXPLORE THE DIRECTION**

直接提炼成三个视觉方向（不详细介绍三版方案）：

- **Direction 01 · Clinical & Rational** — 强调专业、清晰、理性。问题：容易接近传统医疗产品，情绪距离较远。
- **Direction 02 · Tech & Intelligent** — 强调 AI、图谱与技术感。问题：视觉表达过强，容易削弱医疗场景需要的温和与可信。
- **Direction 03 · Natural & Trustworthy** — 暖白、米杏与低饱和自然色。优势：在专业感之外，降低医疗问答的心理距离。

**B. CHOOSE — THE FINAL CHOICE**

采用 Key Decision Highlight（非完整卡片）：

> **THE FINAL CHOICE — Warm Almond Cream**  
> 最终没有选择典型的医疗蓝，也没有强化 AI 科技感，而是建立了一套更克制的自然暖色体系。

最重要的一句总结：

> 专业感来自信息秩序，而不是冷色与科技符号。

**C. SYSTEMIZE — THREE PRINCIPLES**

展示三个原则（不逐条展示所有 Design Token）：

- **01 · COLOR AS HIERARCHY** — 颜色主要用于建立信息层级、标记当前状态、表达有限的语义，而不是装饰页面。
- **02 · CONSISTENCY AS CONSTRAINT** — 将色彩、字体、间距、圆角、阴影、组件状态整理成统一规则。
- **03 · DESIGN AS DEVELOPMENT INPUT** — 最终规范同时也是前端实现的输入约束，把视觉设计与开发实现直接连接。

#### 4. Core Artifact 设计

- **Artifact 名称**：Visual Direction → System
- **副标题**：From exploring visual personality to defining reusable rules.
- **类型**：Type C（原生 UI + 真实 Design System 预览）—— 上半部分 HTML/CSS 原生构建，下半部分可嵌入真实设计规范页面或截图。
- **核心形式**：Gallery Layout，Artifact 内部分上下两部分：

```
┌──────────────────────────────────────┐
│  VISUAL EXPLORATION                  │
│  [ Direction 01 ] [ Direction 02 ]   │
│  [ Direction 03 · Selected ]         │
├──────────────────────────────────────┤
│  DESIGN SYSTEM                       │
│  Color   Type   Spacing   Components │
└──────────────────────────────────────┘
```

**Part 01 · Visual Exploration**：展示三张紧凑的「视觉方向样本」，每个方向只展示一个迷你页面片段 + 3~4 个代表性色块 + 一个关键词。

```
[ 01 ] CLINICAL          [ 02 ] TECH            [ 03 ✓ ] NATURAL
Rational / Clear         Structured/Intelligent    Warm / Trustworthy
```

- 前两个方案：降低饱和度，opacity ≈ 0.55，不展示完整真实设计稿。
- 最终方案：白色表面；`#FAF3EC` 轻背景；`#8C6B5D` 作为 Selected Indicator。

**Part 02 · Design System**：用户点击 / Hover Direction 03 后，下方展示最终设计系统。只展示四组最有代表性的内容：

- **COLOR**：`#FDFBF7` / `#FFFFFF` / `#8C6B5D` / `#6B5045`
- **TYPOGRAPHY**：Display 28px / Heading 20px / Body 15px
- **SPACING**：4 · 8 · 16 · 24 · 32
- **COMPONENT**：Button / Card / Tag

#### 5. 实现方式与视觉表现

- 上半部分：Native HTML/CSS 原生构建视觉方向样本。
- 下半部分：放真实设计规范 HTML 页面缩略图，或点击「View Design System」弹出 Modal。
- Modal 内推荐**直接嵌入完整 HTML Design System 页面**（而非截图），因为设计规范本身是真实成果。
- 视觉重点：「Selected Direction」与「渐进式 refinement」，而非一堆色卡。Primary 仅用于 Selected Indicator，不铺满。

#### 6. 交互设计

- **Hover 三个视觉方向**：当前方向 opacity 1；其他方向 opacity 0.55；下方出现一句 Design Rationale（如 `NATURAL & TRUSTWORTHY` → "Designed to reduce the emotional distance between users and medical knowledge."）。
- **Auto Play 进入 Module 04**：Direction 01 出现 → Direction 02 出现 → Direction 03 出现并被选中 → Design System 从下方展开。总时长 1.8–2.2s，不过于复杂。

#### 7. 开发规则

```
module-type: gallery
left-layout: explore / choose / systemize
artifact: native HTML/CSS visual direction gallery + real design system screenshot or embedded preview
visual: selected direction / progressive refinement / design token preview
avoid: showing all design tokens / large color palettes / repeating full screenshots / overusing cards
```

---

### 11.5 Module 05 · 数据设计（Architecture）

> 状态：**定稿**（用户 2026-08-19 提供）

#### 1. 模块定位

Module 05 是整个 Journey 中第一次真正进入**底层能力展示**。前面主要证明产品判断、设计能力；这里要开始证明：**数据建模能力、系统抽象能力、对领域知识结构化的能力**。视觉上从 Story / Gallery 转变为 Architecture。

在 Journey 中的角色：从「建立视觉语言」(04 VISUALIZE) 推进到「构建知识结构」(05 STRUCTURE)。

#### 2. 核心 Thesis

> 界面可以展示知识，但只有结构化的数据模型，才能让系统真正理解知识之间的关系。

英文：**FROM MEDICAL KNOWLEDGE TO QUERYABLE STRUCTURE**

#### 3. 左侧内容结构（Thinking）

Module 05 不建议三个连续段落，而使用更工程化的结构：

```
THE MODEL
   ↓
THE RULES
   ↓
THE RESULT
```

**A. THE MODEL — STRUCTURE BEFORE EXTRACTION**

重点：先定义系统需要理解什么，再进行知识抽取与数据导入。

```
KNOWLEDGE → SCHEMA → EXTRACTION
```

Key Insight：**先定义规则，再生产数据。**

**B. THE RULES**

四类节点（定义知识实体所在的语义位置，而非单纯按页面分类）：

- **CAUSE & PATHOGEN** — 病因与病原
- **MECHANISM & PROCESS** — 机制与过程
- **DIAGNOSIS & DETECTION** — 诊断与检测
- **INTERVENTION & OUTCOME** — 干预与结局

关系类型（重点展示实体如何连接）：**导致 / 表现为 / 诊断于 / 治疗于 / 影响**。

**C. THE RESULT**

- **67 CAUSAL TRIPLES**
- **Neo4j AuraDB** — Cloud Graph Database
- 辅助：从非结构化医学知识，转化为可查询、可追踪的因果关系网络。

#### 4. Core Artifact 设计

- **Artifact 名称**：Knowledge Architecture
- **副标题**：A schema designed before knowledge extraction.
- **类型**：Type A（原生 HTML + SVG）
- **核心结构**：Schema + Graph Preview，分两层，不是普通技术架构图。

**上层 · Schema Layer**（小型网络，非严格树状）：

```
Cause & Pathogen ──leads to──> Mechanism & Process
Mechanism ├─manifests as─> Diagnosis
         └─influences──> Intervention
```

**下层 · Relationship Metadata**：三个属性连接到一个 RELATION —— 直接体现图谱不仅有 Node 和 Edge，还对正负向、不确定性、证据来源进行了建模：

- **POLARITY**（正负向）
- **CONFIDENCE**（不确定性）
- **EVIDENCE**（证据来源）

**Graph Preview · LIVE DATA PREVIEW**：Schema 下方展示 8–12 个节点形成真实小型因果图谱（Mini Knowledge Graph，不铺开 67 条）：

```
FIP
 ├── caused by → Feline Coronavirus
 ├── manifests as → Fever
 ├── diagnosed by → PCR
 └── treated with → GS-441524
```

#### 5. 视觉表现（节点色彩语义）

严格继承图谱节点设计规则。节点主体仍为 `#FFFFFF`，语义色仅用于 Border / 小型 Icon / 左侧色条 / Connection Highlight，不铺满：

| 节点类别  | 建议色  |
| ----- | ---- |
| 病因与病原 | 暖陶土  |
| 机制与过程 | 蜂蜜琥珀 |
| 诊断与检测 | 雾蓝   |
| 干预与结局 | 鼠尾草绿 |

整体仍符合暖杏奶油系统，Semantic 色克制使用。

#### 6. 交互设计

- **Hover 节点**：高亮当前节点 + 相关关系 + 相邻节点；其他节点 opacity 0.25。
- **Hover 关系**：轻量浮层显示 `LEADS TO` / `Polarity: Positive` / `Confidence: High` / `Evidence: Literature-supported`。
- **Auto Play 进入 Module 05**：四类节点逐个出现 → 关系线依次连接 → POLARITY / CONFIDENCE / EVIDENCE → Mini Graph 逐步生成。整体 2.0–2.5s（前三阶段里可稍微更有「技术感」的一个 Artifact）。

#### 7. 开发规则

```
module-type: architecture
left-layout: model / rules / result
artifact: native HTML + SVG
visual: schema first / graph second
interaction: node hover / relationship inspection
avoid: generic database diagrams / large technical tables / showing all 67 triples / dense Neo4j screenshots
```

---

### 11.6 Module 06 · 前端页面设计（Interface Showcase）

> 状态：**定稿**（用户 2026-08-19 提供）

#### 1. 模块定位

Module 06 的核心不是「我画了几个页面」，而是展示：**如何把产品需求、信息架构和视觉规范，逐步转换成可以直接开发的界面**。它不应再做流程图，也不应只是堆放页面截图——而应成为整个 Journey 中**最具作品集展示感**的模块。

在 Journey 中的角色：从「构建知识结构」(05 STRUCTURE) 推进到「设计具体体验」(06 INTERFACE)。

#### 2. 核心 Thesis

> 界面不是设计过程的起点，而是产品需求、信息结构与视觉规则共同收敛后的结果。

英文：**FROM PRODUCT LOGIC TO INTERFACE**

#### 3. 左侧内容结构（Thinking）

```
DEFINE
  ↓
STRUCTURE
  ↓
MATERIALIZE
```

**A. DEFINE — START WITH THE PAGE PURPOSE**

在画界面之前，先明确每个页面解决什么问题、用户在页面中需要完成什么操作。展示三个问题：

- What is the user trying to do?
- What information is needed?
- What should happen next?

**B. STRUCTURE — TURN REQUIREMENTS INTO STRUCTURE**

根据功能目标确定信息层级、核心组件、交互状态与异常情况。

```
Requirement → Information Architecture → Interaction Logic
```

Highlight：**先定义结构，再进入视觉细节。**

**C. MATERIALIZE — TURN STRUCTURE INTO INTERFACE**

在统一设计规范约束下，将页面需求转化为具体的布局与组件。展示三个主要页面（细节由右侧 Artifact 直接呈现）：

- **Conversation**
- **Knowledge Graph**
- **Literature Library**

#### 4. Core Artifact 设计

- **Artifact 名称**：Interface Evolution
- **副标题**：From page purpose to working interface.
- **类型**：Type B（真实产物展示 / 真实渲染界面预览）
- **形式**：主展示区 + 页面切换器（Tab）

```
┌───────────────────────────────────────┐
│ Conversation  Graph  Literature        │
│ ───────────                           │
│                                        │
│         LARGE INTERFACE PREVIEW        │
│                                        │
└───────────────────────────────────────┘
```

- 推荐使用**真实页面截图**（不建议 AI 生成），因为 Module 06 是真实作品展示。
- 用户可点击 Tab 切换三个页面、Hover 页面中的重点区域。
- **为什么这样设计**：前序模块（01 机会收敛 / 02 判断变化 / 03 产品蓝图 / 04 视觉系统 / 05 数据结构）让用户终于看到真正的产品——因此让页面本身成为 Artifact，不要重新设计一个「解释前端设计的图」，真实页面就是最好的成果。

**三个页面的 Artifact 标注：**

- **Conversation（默认）**：真实 UI 缩略图 + 三个轻量标记 ①NAVIGATION ②CONVERSATION ③EXECUTION TRACE。Hover ① 突出左侧导航；② 突出中间对话；③ 突出右侧执行轨迹；其他区域 opacity 0.2。
- **Knowledge Graph**：真实截图 + Hover 标注 ①LEGEND ②GRAPH CANVAS ③DETAIL PANEL。重点展示图谱可与问答、节点详情产生关联。
- **Literature Library**：真实截图 + Hover 标注 ①SEARCH & FILTER ②LITERATURE COLLECTION ③EVIDENCE DETAIL。点击文献卡片可打开 Artifact Preview Modal 展示更大真实页面。

#### 5. 视觉表现

- 大图居中展示，最小注解（仅轻量 hotspot 标记）。
- 不一次展示多张完整截图，不堆满小缩略图。
- 真实截图即 Artifact，不重绘为图示。

#### 6. 交互设计

- **Tab 切换**：Conversation / Graph / Literature；切换动画 150–200ms opacity + translateY(4px)；不使用左右大幅滑动、Carousel、自动滚动截图。
- **点击「View Full Interface」**：打开 Modal，最大宽度约 90vw / 高度 90vh，支持关闭，图片支持滚动。
- **Auto Play 进入 Module 06**：
  - 默认展示 Conversation；约 1.5s 后切到 Graph；再 1.5s 切到 Literature，最后停留。
  - **关键例外**：若 Journey 单模块停留时间 ≤ 5s（短档位），则 Module 06 内部**不启用自动切换**，默认只展示 Conversation，由用户手动切换。仅当 Journey 单模块停留 ≥ 7s 时才启用内部页面自动 Preview。避免「页面自动播放 + Artifact 自动播放」同时发生导致注意力混乱。

#### 7. 开发规则

```
module-type: interface showcase
left-layout: define / structure / materialize
artifact: real interface screenshots or real rendered interface preview
visual: large central interface / minimal annotation / tab switching
interaction: page tab switch / hotspot highlight / full-size preview modal
avoid: redrawing screenshots as diagrams / showing multiple full screenshots at once / small unreadable thumbnails / excessive annotations
```

---

### 11.7 Module 07 · 开发实现（Engineering）

> 状态：**定稿**（用户 2026-08-19 提供）

#### 1. 模块定位

- 模块名称：**Module 07 · Development**／中文「开发实现」。
- 一句话定位：将前面的产品、数据与页面设计，逐层转化为真正可运行的系统。
- 最需要展示的不是「我写了多少代码」，而是：**如何把一个产品方案拆解成可控的工程模块，并逐步实现**。视觉重点：**Architecture · Build · Integration**。
- 在 Journey 中的角色：从「设计具体体验」(06 INTERFACE) 推进到「系统如何被搭建起来」(07 BUILD)。

#### 2. 核心 Thesis

> Good implementation is not about generating more code. It's about reducing uncertainty one layer at a time.

中文辅助：开发过程不是一次性生成完整系统，而是将复杂问题拆解为可验证的模块，在每一层确认行为正确后再继续向上构建。

#### 3. 左侧内容结构（Thinking）

左侧不使用普通时间线（会与 Module 01 叙事重复），改用 **Build Strategy Stack / Engineering Manifesto**：编号 + 垂直 Build Line，编号用 `#6B5045`（Primary 900），连接线 `#EDE5DD`，节点小圆点 `background:#FAF3EC; border:1px solid #C7A18E`。

**A. WHAT I DID — BUILD PRINCIPLES**

- **01 · Layered Architecture**：先定义系统层级，再实现具体功能。拆成 Data Access / Rule Routing / Agent Layer / Pipeline / Frontend，避免所有逻辑堆积在单一应用文件。
- **02 · Module-first Development**：每个模块独立实现，再逐步连接。开发顺序 Data ↓ Routing ↓ Agent ↓ Pipeline ↓ Interface，每完成一个层级即验证该层行为。
- **03 · Continuous Verification**：不等待全部完成后再测试。每个模块完成后立即 Run / Check / Fix / Integrate，降低后期集中调试成本。

**B. KEY INSIGHT**（相对独立的突出区域，背景 `#FAF3EC`，仅非常浅的暖杏色，不整块使用 Primary）

> Good implementation is not about generating more code. It's about reducing uncertainty one layer at a time.

中文辅助：开发与前端工程不是一次性生成完整系统，而是将复杂问题拆解为可验证模块，逐层确认行为正确后再向上构建。下方标注：`Modular Build Philosophy`。

#### 4. Core Artifact 设计

- **Artifact 名称**：System Architecture
- **顶部信息**：`SYSTEM ARCHITECTURE` ＋ 5 Layers ↓ Modular Build ↓ Continuous Validation
- **类型**：Type A（原生 HTML + SVG 分层架构图），**不使用代码截图**
- **结构**（自上而下 5 层，靠微弱背景差异 + Layer Label + Connector 形成结构，不铺大面积彩色）：

```
FRONTEND          (白色卡片)   Chat · Graph · Literature
      │
PIPELINE          (Primary 100) Semantic → Task → Query
      │
AGENT LAYER       (白色)        Intent · Entity · Evidence
      │
DATA ACCESS       (#FDFBF7)      Query Templates · Dedup
      │
NEO4J             (白色)         Causal Knowledge Graph
```

- 连接线：`#C7A18E` 细线 + 小箭头（`↓ · · · ↓`），不用粗箭头，保持精致。
- 右上角：`● IMPLEMENTED` Success Tag（background `#F4F7F1`，color `#53664F`；绿色有明确语义：已完成并运行）。

#### 5. 交互设计

- **Layer Hover** 显示 Floating Detail（Tooltip）：Layer Name / Responsibility / Core Files。例如 `PIPELINE` → Responsibility: Orchestrate the complete reasoning flow；Core: `core/pipeline.py`。不真正跳转代码。
- Auto Play 进入 Module 07：层级自上而下逐级出现，时长 ≤ 2.2s。

#### 6. Input / Output Flow

底部不使用复杂流程：

```
INPUT   Product Architecture / Design System / Data Schema
  ↓ (Build 使用 #8C6B5D 强调)
BUILD   Layer by Layer / Module by Module
  ↓
OUTPUT  A Working Knowledge System
```

其余文字保持 Neutral。

#### 7. 开发规则

```
module-type: engineering
left-layout: build principles (vertical stack) + standalone key insight
artifact: native layered system architecture (no code screenshots)
visual: 5 subtle layers / connector lines / implemented success tag
interaction: layer hover tooltip (name / responsibility / core files)
avoid: timeline reuse / dark tech style / large color blocks / code screenshots
```

---

### 11.8 Module 08 · 测试与验证（Verification Matrix）

> 状态：**定稿**（用户 2026-08-19 提供）

#### 1. 模块定位

- 关键词：**Coverage · Boundary · Behavior**。
- 不能只是「7 项测试全部通过」式的项目汇报。真正应展示：**验证的不是代码是否运行，而是产品设计原则是否真的被实现**。
- 与 Module 07 拉开差异：Module 07 = Architecture；Module 08 = Verification Matrix。
- 在 Journey 中的角色：从「系统如何被搭建」(07 BUILD) 推进到「系统是否真的可靠」(08 VERIFY)。

#### 2. 核心 Thesis

> The most important tests are often the cases where the system should not answer.

中文：对于知识型系统而言，真正重要的不只是「能否正确回答」，还包括「是否知道什么时候不应该回答」——直接呼应知识边界、上下文保护、澄清机制、可解释性。

#### 3. 左侧内容结构（Thinking）

**A. WHAT I TESTED — VALIDATION DIMENSIONS**（5 个维度，不用时间线；数字 color `#C7A18E`，标题 `#3E3836`，不用 5 种颜色）

- **01 Intent Recognition** — Does the system understand what the user asks?
- **02 Entity Resolution** — Can it identify and reuse the correct context?
- **03 Clarification** — Does ambiguity trigger clarification instead of guessing?
- **04 Knowledge Boundary** — Can the system refuse unsupported knowledge safely?
- **05 Recovery** — Can the system recover from connection interruptions?

**B. KEY INSIGHT**

> The most important tests are often the cases where the system should not answer.

中文：对于知识型系统，真正重要的不只是「能否正确回答」，还包括「是否知道什么时候不应该回答」。

#### 4. Core Artifact 设计

- **Artifact 名称**：Scenario Coverage Matrix
- **类型**：Type A（原生可视化），**不要做成普通 `<table>` / Excel 样式**
- **结构**（轻量卡片式场景列表，每行：Scenario 名 + 简短输入 + 状态 Tag）：

```
SCENARIO COVERAGE
─────────────────────────────
Diagnosis          猫传腹如何诊断            ✓ Passed
Knowledge Boundary 猫发热怎么办        Boundary Triggered
Clarification      441安全吗？              Clarification
Context Inheritance 什么是传腹 → 怎么治疗   ✓ Passed
Topic Switch       今天天气怎么样          ✓ Passed
Recovery           Idle DB connection        ✓ Passed
```

- **状态设计不要全部使用绿色**，用 Semantic Color 表达真实语义：
  - `✓ Passed` → Success Tag
  - `Boundary Triggered` → **Info Tag**（蓝灰语义：进入知识边界）
  - `Clarification` → **Warning Tag**（橙语义：需要进一步确认；**Warning 不代表失败**）
- **顶部 Summary（非常轻量，不要 Dashboard）**：`TEST SUMMARY` ＋ `7 / 7 Core Tests Passed` ＋ `＋ 8 Critical User Scenarios`。关键数字 `font-size:28px; font-family:JetBrains Mono; color:#6B5045`；只保留两个关键数字。

#### 5. 交互设计

- 每个 Scenario 行可点击展开（**Accordion**，不需要 Modal），展开显示：
  - `INPUT`：猫发热怎么办？
  - `EXPECTED`：Do not reuse previous FIP context
  - `ACTUAL`：Knowledge boundary triggered
  - `RESULT`：✓ Matched Expected Behavior
- 访客可快速扫一眼结果，对感兴趣的测试再查看细节。

#### 6. Input / Output Flow

```
INPUT   System Logic / Interaction Rules / Product Principles
  ↓
VALIDATE  Automated Tests + Manual Scenarios
  ↓
OUTPUT  Verified Behavior Across Core Boundaries
```

注意 OUTPUT 写 **Verified Behavior**（而非 Verified System）——测试对象是「系统行为是否符合设计」。

#### 7. 开发规则

```
module-type: proof
left-layout: validation dimensions (5) + key insight
artifact: scenario coverage matrix (card rows, not excel table)
visual: semantic status tags (success / info / warning) / light summary
interaction: accordion expand row (input / expected / actual / result)
avoid: dashboard / all-green status / dense table / modal for row detail
```

---

### 11.9 Module 09 · 部署与收尾（Delivery）

> 状态：**定稿**（用户 2026-08-19 提供）

#### 1. 模块定位

- 关键词：**Deploy · Live · Deliver**。
- 整个 Journey 的最后一步，要把项目收束成一个完整闭环——不能只是「我部署了 Gradio 和 Neo4j」，否则结尾会很弱。
- 在 Journey 中的角色：从「系统是否真的可靠」(08 VERIFY) 推进到「项目如何真正跑起来」(09 LIVE)。

#### 2. 核心 Thesis

> A prototype proves an idea. A live product proves it can be experienced.

中文：原型证明想法是否成立，真正可访问的产品才让别人能够验证它。

#### 3. 左侧内容结构（Thinking）

**A. WHAT I DELIVERED**（不再使用「What I Did」，最后一步更强调交付；Deliverable List）

- **01 Live Application** — A browser-accessible product demo.
- **02 Cloud Knowledge Graph** — A continuously available Neo4j instance.
- **03 Automated Heartbeat** — Scheduled checks to maintain availability.
- **04 Project Documentation** — A complete walkthrough of the design and implementation process.

**B. KEY INSIGHT**

> A project is not complete until others can use it.

中文：原型证明想法是否成立，真正可访问的产品才让别人能够验证它。

#### 4. Core Artifact 设计

- **Artifact 名称**：Live Deployment Map
- **类型**：Type A（原生 HTML + SVG），不做普通流程图（Module 07 已有 Architecture）
- **结构**：

```
        ┌─────────────┐
        │   Visitor   │
        └──────┬──────┘
               ↓
      ┌────────────────────┐
      │ Web Application     │   Gradio
      └─────────┬──────────┘
                ↓
      ┌────────────────────┐
      │ Python Core         │   Pipeline + Agents
      └─────────┬──────────┘
                ↓
      ┌────────────────────┐
      │ Neo4j AuraDB       │   Knowledge Graph
      └─────────▲──────────┘
                │
   ┌────────────┴───────────┐
   │  GitHub Actions        │   Daily Heartbeat
   └────────────────────────┘
```

- **视觉层级**：
  - 主路径 Visitor ↓ Application ↓ Core Logic ↓ Database：`border:#EDE5DD; background:#FFFFFF`。
  - 辅助路径 GitHub Actions：`background:#FDFBF7; border-style:dashed`，连接到 Neo4j 用虚线——表示 Supporting Infrastructure，与主产品访问链路不在同一层级。

#### 5. 视觉表现与交互

- 右侧 Artifact 应成为 Module 09 最有「完成感」的区域。加入轻量 `● LIVE` 状态标签（background `#F4F7F1`，color `#53664F`）；**不要闪烁动画**，可有一个非常慢的 opacity breathing（约 3s 循环），`prefers-reduced-motion` 时关闭。
- **Artifact 底部 · Project Outcome**：

```
PROJECT OUTCOME
✓ Designed
✓ Structured
✓ Implemented
✓ Tested
● LIVE  (Deployed)
A complete product journey.
```

前 4 个 `✓` 使用 **Primary 700**；最后一个 `● LIVE` 使用 **Success**（只有「Live」属于明确运行状态）。不全部做成 Success Green。

- Hover 组件显示职责（可选 Modal）；Auto Play 结束时停留在 Module 09。

#### 6. Input / Output（FROM → TO）

最后一步不再使用传统 Input / Output，因为已是 Journey 终点：

```
FROM   Local Prototype / Personal Environment / Static Demonstration
  ↓
TO     Live Application / Cloud Infrastructure / Independent Access
```

底部收束文案：**The journey ends here. The product starts here.**

#### 7. 开发规则

```
module-type: delivery
left-layout: what i delivered (deliverable list) + key insight
artifact: live deployment map (main path solid / infra dashed)
visual: live status tag / breathing (reduced-motion off) / outcome checklist
interaction: component hover / autoplay ends here
avoid: weak ending / generic flowchart reuse / all-green outcome
```

---

## 12. 05｜Previous / Next Navigation

底部轻量章节导航：

```
← Module 01                                  Module 03 →
Previous                                     Next
```

- 文字：`#6F6763`，Hover 时 `#6B5045`
- 箭头：Hover 时微移动
  - `←` 左移 4px
  - `→` 右移 4px
- 时长：200ms
- 当前处于 Module 01 时，Previous 禁用；处于 Module 09 时，Next 禁用。

---

## 13. 首屏规则

用户进入第一屏必须看到：

1. Project Header
2. Journey
3. Current Module Header
4. Workspace 的顶部区域

**禁止**首屏只到 Module Header，需要滚动才能看到内容。

### 13.1 建议高度

| 区域             | 建议高度      |
| -------------- | --------- |
| Project Header | 96–120px  |
| Journey        | 110–140px |
| Module Header  | 90–110px  |

这样在普通桌面端首屏至少能看到 Thinking 与 Artifact 顶部。

---

## 14. 响应式规则

### 14.1 Desktop ≥ 1440px

- Journey 完整展开，显示完整模块名称。
- Workspace：`38% │ 62%`

### 14.2 Medium 1024–1439px

- Journey 保留 9 个节点，名称缩短，使用 Tooltip 展示完整名称。
- Workspace：`40% │ 60%`

### 14.3 Small < 1024px

- Journey 改为横向滚动或压缩节点：
  ```
  01 → 02 → 03 → 04 → 05 → ...
  ```
- 当前模块名称完整显示。
- Workspace：单栏，Thinking 在上，Artifact 在下。
- Auto Play 控制继续保留。

---

## 15. 动效规则

| 动效              | 时长         | 用途            |
| --------------- | ---------- | ------------- |
| Node Hover      | 150–200ms  | Hover 背景/文字变化 |
| Journey Arrow   | 800–1200ms | 节点间移动         |
| Module Content  | 200–300ms  | 内容切换          |
| Previous / Next | 150–200ms  | 箭头微移动         |
| Card Hover      | 150–200ms  | 阴影加深          |
| Auto Play Pause | 即时         | 用户控制          |

### 15.1 内容切换动画

```
Opacity: 1 → 0
TranslateY: 0 → -8px

然后：

Opacity: 0 → 1
TranslateY: 8px → 0
```

时长：200–300ms，easing：`ease-out`。

### 15.2 可访问性

所有动效必须支持 `prefers-reduced-motion`：

- 关闭 Journey Arrow 动画
- 模块直接切换，无位移动画
- 保留基本透明度过渡或瞬间切换

---

## 16. 数据文件结构建议

为便于开发与维护，建议将 9 个模块数据组织为单一 JS 对象：

```javascript
window.MODULES = [
  {
    id: 1,
    phase: 'product-design',
    phaseLabel: '产品设计阶段',
    title: '产品与需求分析',
    thesis: '从一个技术兴趣出发，最终收敛成一个可以验证的真实产品问题。',
    thinking: [
      { title: 'THE STARTING POINT', content: '...' },
      { title: 'WHAT I NOTICED', content: '...' },
      { title: 'WHY FIP', content: '...' }
    ],
    artifact: {
      type: 'A',
      name: 'Opportunity Evolution',
      caption: '从产品兴趣到可验证机会的收敛过程',
      data: { ... }
    }
  },
  // ... 02–09
];
```

---

## 17. 与 app.py 集成注意事项

根据 `source/design/app-integration-notes.md`：

- `design.html` 通过 iframe srcdoc 注入到 `app.py` 中。
- 页面必须是**单文件 HTML**（HTML + CSS + JS 内联）。
- 样式使用 `:root` CSS 变量，但需注意与父页面 `app.py` 的变量隔离（iframe 已隔离）。
- 页面宽度应占满 iframe，高度建议 `min-height: 100vh`。
- 不需要左侧 Sidebar，页面右侧主工作区占满可用宽度。

---

## 18. 文件输出

| 文件   | 路径                                  | 说明              |
| ---- | ----------------------------------- | --------------- |
| 设计规范 | `source/UI/product-journey-spec.md` | 本文档             |
| 页面实现 | `source/design/design.html`         | 单文件 HTML/CSS/JS |

---

## 19. 开发任务顺序建议

1. **准备模块数据**：按第 16 节结构整理 9 个模块的 JSON 数据。
2. **搭建页面骨架**：Project Header、Journey、Module Header、Workspace、Navigation。
3. **实现 Journey 与 Auto Play**：三段式导航 + chevron 动画 + 播放控制。
4. **实现 Module Workspace**：动态渲染左侧 Thinking + 右侧 Artifact Canvas。
5. **逐个实现 9 个 Artifact**：按 Type A/B/C 分别实现。
6. **响应式与动效收尾**：三档响应式 + prefers-reduced-motion。
7. **集成验证**：在 iframe srcdoc 环境中测试页面表现。

---

## 20. 验收清单

- [ ] 首屏可见 Project Header + Journey + Module Header + Workspace 顶部
- [ ] Journey 三段式结构清晰，当前节点高亮正确
- [ ] Auto Play 能自动从 01 推进到 09，chevron 动画流畅
- [ ] 用户点击节点/Previous/Next/Expand 时 Auto Play 暂停
- [ ] 9 个模块内容完整，Thinking 区块标题各不相同
- [ ] Artifact 按 Type A/B/C 正确实现，支持 Expand
- [ ] 响应式在 1440px / 1024px / <1024px 下布局正常
- [ ] 支持 `prefers-reduced-motion`
- [ ] 单文件 HTML，无外部 CSS/JS 文件依赖
- [ ] 模块数据以 JSON 内嵌，便于维护
