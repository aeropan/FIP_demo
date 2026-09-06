# 产品说明页 · 整页调整规范（终版）

> 适用文件：`fip-causal-reasoning/source/design/design.html`
> 父规范：`source/UI/product-journey-spec.md`（执行层 V2）
> 本文件为基于已落地 V2 版本的**整页结构调整规范**（终版），覆盖顶部信息区、Journey、Module 正文、左右区域与 Artifact 展示规则。
> 设计系统基线：方案 B · 暖杏奶油 V2。本轮**不推翻现有页面与风格**，只优化信息密度、层级关系与 9 个 Module 的视觉节奏。
> 本文件为开发中间过程文档，不纳入版本提交（见根 `.gitignore`）。

---

## 0. 改造目标与核心原则

当前页面核心问题不是风格错误，而是：顶部信息区与 Journey 占比偏大；Journey 与正文层级不够明确；左侧若持续统一卡片，9 个 Module 会产生重复感；左右不能简单固定比例或强制等高；Artifact 不应是「一张固定图」，而是灵活的成果展示区。

本轮遵循五条原则：

1. **顶部更轻**：Project Intro + Compact Journey 控制高度，让 Module 正文在第一屏尽可能露出。
2. **Journey 是导航，不是内容**：不再做成大型流程展示图。
3. **Narrative 与 Artifact 是两个内容系统**：左侧展示 Thinking / Decision / Process；右侧展示 Evidence / Output / Artifact。
4. **Artifact 是动态成果区域**：可一张大图、多张连续图、截图墙、图+数据、图+决策摘要，不固定成小图。
5. **9 个 Module 不使用同一种卡片结构**：保持设计系统统一，但让叙事方式、信息结构、Artifact 展示变化，形成「统一视觉语言 + 有节奏的阅读体验」。

---

## 1. 设计 token 速查（方案 B · 暖杏奶油 V2）

| 用途 | Token | 值 |
|---|---|---|
| Primary 900 | `--color-primary-900` | `#6B5045` |
| Primary 700 | `--color-primary-700` | `#8C6B5D` |
| Primary 500 | `--color-primary-500` | `#C7A18E` |
| Primary 100 | `--color-primary-100` | `#FAF3EC` |
| 文字主色 | `--color-text-main` | `#3E3836` |
| 文字次色 | `--color-text-secondary` | `#6F6763` |
| 边框 | `--color-border` | `#EDE5DD` |
| 表面底色 | `--color-surface` | `#FDFBF7` |

圆角：sm 6 / md 12 / lg 16 / pill 999。间距基准 4px 阶梯。

---

## 2. 页面整体结构

```
┌─────────────────────────────────────────────┐
│ Project Intro (PRODUCT JOURNEY / 标题 / 描述 / 标签) │
├─────────────────────────────────────────────┤
│ Compact Journey Navigation                    │
│ 01 — 02 — 03 — 04 — 05 — 06 — 07 — 08 — 09  │
├─────────────────────────────────────────────┤
│ Module Header                                 │
│ MODULE 01 · FROM INTEREST TO OPPORTUNITY     │
│ 产品与需求分析                          01 / 09 │
├──────────────────────┬──────────────────────┤
│   Narrative Area     │    Artifact Area      │
│   内容叙事区          │    成果展示区          │
├─────────────────────────────────────────────┤
│ Previous                               Next   │
└─────────────────────────────────────────────┘
```

左侧平台侧边栏保持现有设计，不参与本次调整。

---

## 3. Project Intro 调整

- 保留现有「PRODUCT JOURNEY + 项目标题」合并方式，**不新增独立 Journey 标题**（避免标题层级重复）。
- 结构：小标 `PRODUCT JOURNEY` → 项目标题 `可解释知识问答产品 · 设计实践` → 描述（一行项目说明）→ 分类 Tag 行（`Product Design` / `UX Research` / `Data` / `Engineering` / `Demo Ready`）。
- **高度控制：约 150–170px**，不再增加新标题或说明。

---

## 4. Journey Navigation 调整

### 4.1 背景与边界（无突兀色块）
- 主背景 `#FDFBF7`。
- Journey 区域使用**极浅渐变层次**（非色块）：
  ```css
  background: linear-gradient(180deg, rgba(250,243,236,0.35), rgba(253,251,247,0));
  ```
  目的：让用户自然感觉「顶部是导航层，下面进入内容层」，而非「这里有一大块色」。
- 底部分隔线：`border-bottom: 1px solid #EDE5DD`（轻但明确）。
- Journey 与正文之间：**24–32px 垂直留白**。
- **不使用**大面积灰底、深色背景、明显卡片容器。

### 4.2 高度压缩
- Journey 区域高度：**约 110–130px**（含 9 节点 + 当前状态 + Auto Play）。
- **不再额外增加阶段标题**（顶部大标题徽章已承担阶段/能力分类，功能重复，故去掉）。

### 4.3 节点样式（三态）
- **当前节点**：边框 Primary 700 `#8C6B5D`，数字 Primary 900 `#6B5045`，底部指示线 Primary 700。
- **已完成节点**：低强调但仍保持可读。
- **未完成节点**：进一步降低对比度；**不要使用强烈的「禁用灰」**，否则 Journey 前半段很重、后半段消失。
- 节点下方可显示当前模块短标签（如 `产品分析`）。

### 4.4 Auto Play（无时间选择器）
- 位置：Journey 条最右端，与 09 节点同行。
- 样式：弱化 ghost 按钮（`▷ Auto Play` / `❚❚ Playing`），无边框，次级文字色 `#6F6763`。
- **不放任何时间选择 UI**（如 `[5s ▾]`）。
- 交互：点击后出现移动小箭头沿 Journey 连线移动 → 到达下一节点 → 自动切换 Module → 切换后重置计时。不做复杂动画控制器。

---

## 5. Module Header 调整

- 每个 Module 统一 Header，结构：
  - 行 1：`MODULE 01 · FROM INTEREST TO OPPORTUNITY`（英文副标）
  - 行 2：中文标题 `产品与需求分析` + 进度 `01 / 09`
  - 行 3：一句模块说明
- 样式：`padding-bottom: 24px; border-bottom: 1px solid #EDE5DD;`
- **Module Header 不使用卡片**，使正文从顶部 Journey 中明确「切出来」。

---

## 6. 左右区域整体规则

- 不再理解为「左边内容 = 右边一张图」，而是 **Narrative Area + Artifact Area** 两个内容系统。
- 左侧负责：如何思考、做了什么、为什么这样决策。
- 右侧负责：最终形成什么成果、证据或结构。
- **宽度比例**：默认 `52 : 48` 或 `55 : 45`（不建议 60:40，Artifact 承担重要成果展示）。
  ```css
  grid-template-columns: minmax(0, 1.1fr) minmax(420px, 0.9fr);
  gap: 48px;
  ```
- **不强制左右内容完全等高**：通过 Artifact 展示方式让右侧自然长高（见第 7 节），而非硬性限制高度一致。

---

## 7. Artifact Area 展示规则

Artifact 是**成果容器系统**，不是固定图片框。每个 Module 按内容选类型：

| 类型 | 适用 | 形态 |
|---|---|---|
| **A 单个核心 Artifact** | 产品机会演化、系统架构、部署架构 | 一张 Large Diagram + Key Insight |
| **B 多个连续 Artifact** | 视觉设计、前端页面设计、测试验证 | 多张截图 / 方案 / Before-After 连续排列 |
| **C 图 + 结构化摘要** | 数据设计、开发实现、部署 | Diagram + OUTPUT 列表（如 `• 67 Causal Triples`） |
| **D 多张缩略图 / 成果墙** | 视觉设计、前端页面设计 | 2×N 缩略图网格，点击 Expand / Full View |

右侧不应只放一张 300px 图留大片空白；可用多 Artifact + 标题 + Decision/Result 让高度自然增长，与左侧接近平衡。

### 生成优先级
1. **HTML / CSS / SVG 绘制**（首选）：流程图、Schema、系统架构、测试结果、数据结构、优先级矩阵、部署结构——风格一致、清晰、响应式、复用 token、不模糊。
2. **真实页面截图**：视觉设计成果、前端页面、产品原型、运行界面。
3. **静态图片**（仅特殊场景）：AI 探索方案、特殊视觉效果、不需响应式的复杂图形。

原则：**结构化内容 → 前端绘制；真实产品成果 → 页面截图；特殊视觉 → 图片。**

---

## 8. 左侧 Narrative Area（不再全部使用卡片）

9 个 Module 全部用同一种大卡片会形成「9 张大卡片 + 内容不同」的重复疲劳。保留统一信息规范，但**不统一所有视觉容器**。

### 8.1 Vertical Narrative Rail（全局优化）
升级原来的小箭头分隔为统一竖向叙事轨：节点 `●` + 连续竖线 + 内容块。节点可置于内容块左侧，竖线贯穿。可根据 Module 内容变化为不同组织方式（不一定每步都包完整卡片）。

示例节奏：
- Module 01（Story Flow）：`● Interest │ ● Problem │ ● Opportunity`
- Module 02（Research Findings）：`01 Trust ─ Insight / 02 Risk ─ Insight / 03 Boundary ─ Insight`
- Module 03（Decision Tree）：`Problem → Option A × / Option B × / Option C ✓`

### 8.2 九个 Module 左侧表现方式（有意差异化）

| Module | 内容 | 左侧 Narrative 表现 |
|---|---|---|
| 01 | 产品与需求分析 | 垂直 Story Flow |
| 02 | 产品需求验证 | Research Findings |
| 03 | 产品形态与方案设计 | Decision Tree |
| 04 | 视觉设计 | Design Exploration |
| 05 | 数据设计 | Layered Schema |
| 06 | 前端页面设计 | Design-to-Prototype Flow |
| 07 | 开发实现 | Engineering Stack |
| 08 | 测试与验证 | Test Scenario Matrix |
| 09 | 部署与收尾 | Delivery Checklist |

> **说明**：差异化是**有意设计**，目的是减少阅读疲劳、形成节奏。必须用统一 token 约束（统一字体阶梯、统一间距标尺、统一强调色用法、统一节点/卡片组件库），使变化呈现为「有节奏的变奏」而非「无规则的杂乱」。

---

## 9. 统一 Key Decision / Key Insight 组件

9 个 Module 均保留一个统一组件，建立全局统一性：

```
KEY DECISION
不追求"覆盖所有宠物疾病"，而是选择一个足够聚焦、同时能完整体现核心能力的 MVP 场景。
```

样式：
```css
background: #FAF3EC;
border-left: 3px solid #8C6B5D;
border-radius: 0 12px 12px 0;
```
或非常浅暖底（3–5% opacity）。作用：每段都有一个明确的「产品判断」，突出产品能力。

---

## 10. 统一视觉规则

- **背景**：Main Background `#FDFBF7`，不使用大面积明显色块。
- **区域边界**：优先用「留白 + 1px `#EDE5DD` 分割线 + 极浅暖色层次」，而非深色背景 / 大面积渐变 / 大阴影 / 厚卡片。
- **卡片使用原则**：卡片不再作为所有内容的默认容器。仅当满足以下情况才用：表达独立对象、独立成果、强调决策、承载截图 / Artifact。纯文字叙事、流程、列表、时间线可直接存在于页面中。

---

## 11. 推荐前端结构与数据模型

```
ProductJourneyPage
├── ProjectIntro
├── JourneyNavigation
│   ├── JourneyNode × 9
│   └── AutoPlayControl
├── ModuleContainer
│   ├── ModuleHeader
│   ├── NarrativeArea  (Module-specific Layout)
│   └── ArtifactArea
│       ├── ArtifactItem × N
│       └── KeyOutput
└── ModuleNavigation (Previous / Next)
```

Module 数据层通过 `narrativeType` / `artifactType` 加载不同组件，而非所有 Module 用同一个大卡片模板：

```js
{
  id: 1,
  title: "产品与需求分析",
  subtitle: "FROM INTEREST TO OPPORTUNITY",
  category: "Product Design",
  narrativeType: "vertical-story",
  artifactType: "opportunity-evolution",
  keyDecision: "...",
  artifacts: [ { type: "html-diagram", id: "opportunity-evolution" } ]
}
```

---

## 12. 禁止事项（anti-patterns）

- ❌ Journey 使用明显色块背景（如整块 `#FAF3EC`）
- ❌ Auto Play 使用时间选择器（如 `[5s ▾]`）
- ❌ Journey 额外增加阶段标题（与顶部徽章重复）
- ❌ 左右强制等高 / 固定 60:40
- ❌ Artifact 固定为「一张小图」
- ❌ 9 个 Module 全部使用同一种大卡片结构
- ❌ 左侧用 `↓` 小箭头弱分隔（改用 Vertical Narrative Rail）
- ❌ 未完成 Journey 节点使用强烈「禁用灰」
- ❌ 节点文字因图片缩放模糊（结构化内容优先前端绘制）

---

## 13. 验收要点

- [ ] **顶部更轻**：Project Intro ≤170px + Journey ≤130px，Module 正文首屏可见。
- [ ] **Journey 分层**：极浅渐变 + 1px 底线 + 24–32px 留白，无突兀色块；三态节点清晰但后半段不消失。
- [ ] **Auto Play**：右端弱化 ghost 按钮、无时间选择器、点击沿连线推进并切 Module。
- [ ] **Module Header**：统一、无卡片、底部 1px 线。
- [ ] **左右平衡**：约 52:48 + gap 48px，右侧随 Artifact 自然长高，不强制等高。
- [ ] **Artifact**：按 A/B/C/D 灵活展示，结构化内容前端绘制。
- [ ] **左侧节奏**：9 个 Module 叙事方式差异化但 token 统一，无重复疲劳。
- [ ] **Key Decision**：每 Module 统一组件，暖杏底 + 左条。

---

## 14. 备注（交给实现时）

- 本规范覆盖整页调整，取代此前仅针对 Journey/时间线的局部修订（原 V3「Journey 布局」范围已扩展）。
- **待你自查项**（用户实机评估，不改文档）：
  - Journey 极浅渐变在不同屏幕/亮度下的可见度与干净度；
  - 9 种叙事 layout 实际渲染后的节奏感是否达成「变奏」而非「杂乱」；
  - 左右 52:48 在目标屏宽下的内容容量与平衡。
- 本文件为开发中间过程文档，已加入根 `.gitignore`，不 commit / 不 push。
