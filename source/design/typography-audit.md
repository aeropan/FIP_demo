# 左侧信息栏字体样式排查与统一方案（font-only）

> 范围：**仅字体样式**（文字的 font-family / font-size / font-weight / font-style / letter-spacing / text-transform / 文字前景色 text-color）。
> **不纳入**：背景色、边框色/边框样式、圆角、内边距、阴影、语义状态色（如 PASS 绿 / FAIL 红）。这些属于「组件样式」，本次排查明确排除，留给后续组件审计。
> 审计对象：`design.html` 中每个模块（M01–M09）的**左侧叙事栏（thinking 列）**，不含 module-header（顶部标题/描述），不含右侧 artifact 面板。

---

## 0. 设计令牌参考（颜色 → hex）

| Token | Hex | 用途 |
|---|---|---|
| `--c-text-main` | `#3E3836` | 正文主色（深） |
| `--c-text-secondary` | `#6F6763` | 次要/辅助文字（中灰） |
| `--c-primary-900` | `#6B5045` | 主色最深（暖棕） |
| `--c-primary-700` | `#8C6B5D` | 主色（标题/kicker/编号） |
| `--c-primary-500` | `#C7A18E` | 主色浅（点缀） |
| `--c-primary-100` | `#FAF3EC` | 主色极浅（杏底） |

字体族：默认 `sans`（`--f-sans`）；等宽 `mono`（`--f-mono`，用于编号/标签/代码类）。所有文字均为正常字重 400 或非斜体，除非特别标注。

---

## 1. 模块 → 左侧渲染器映射

| 模块 | leftType | 主要左侧渲染器 |
|---|---|---|
| M01 产品与需求分析 | narrative | `buildBlock` 通用块 |
| M02 需求验证 | evidence | `buildBlock` + 专用 |
| M03 形态设计 | decision-tree | `renderDecisionTree` |
| M04 视觉设计 | gallery | `buildBlock` + `t-dir`/`t-parts`/`gal` |
| M05 数据设计 | architecture | `buildBlock` + `t-rule`/`t-question`/`t-stat`/`t-flow`/`t-page` |
| M06 Agent 设计 | agent | `renderAgentArchitecture` 左栏 |
| M07 开发实现 | engineering | `renderEngineering`（`m07-*`/`eng-*`） |
| M08 测试验证 | proof | `pf-frame` + `t-dim`/`proof__*` |
| M09 部署与运维 | deploy-ops | `renderDeployOpsNarrative`（`dep-*`） |

---

## 2. 字体样式清单（按语义角色分组）

> 列：样式类 ｜ 字体族 ｜ 字号 ｜ 字重 ｜ 斜体 ｜ 文字色 ｜ 出现模块·位置 ｜ 示例文字 ｜ 组件样式备注（已排除）｜ 合并/重用建议
> 文字色括号内为主色 token 名。

### ① 一级 / 区块标题（eyebrow / block title）

| 样式类 | 字体族 | 字号 | 字重 | 斜体 | 文字色 | 模块·位置 | 示例 | 组件备注 | 合并建议 |
|---|---|---|---|---|---|---|---|---|---|
| `.t-block__title` | sans | 12 | 600 | 否 | `#8C6B5D` | M01–M05 通用块标题 | "THE STARTING POINT" | 无 | 作为统一一级标题基准 |
| `.pf-frame .t-block__title` | sans | 14 | 700 | 否 | `#8C6B5D` | M08 覆盖 | "TESTED PLAN · 验证维度" | 无 | 与下两项统一规格 |
| `.dep-title` | sans | 14 | 700 | 否 | `#8C6B5D` | M09 | "DEPLOYMENT" | `::after` 下划线（组件） | ↑ |
| `.agent-section__label` | sans | 12 | 600 | 否 | `#8C6B5D` | M06 区标 | "CONCEPT · 设计理念" | 无 | 与 `.t-block__title` 同为 12/600，合并 |
| `.m07-sec__title` | sans | 14 | 600 | 否 | `#8C6B5D` | M07 区头 | "PROCESS · 开发流程" | 无 | 与 14/700 变体统一为区头 |

**小结**：文字色完全一致（`#8C6B5D`）。差异仅在字号（12 vs 14）与字重（600 vs 700），以及是否大写（前两项 uppercase + 1.5px 字距，后三项 `text-transform:none`）。属同一字体的轻微变体，应合并为一个令牌，用「是否大写 + 字号」区分层级。

### ② 二级 / 子标题

| 样式类 | 字体族 | 字号 | 字重 | 斜体 | 文字色 | 模块·位置 | 示例 | 组件备注 | 合并建议 |
|---|---|---|---|---|---|---|---|---|---|
| `.t-block__subtitle` | sans | 18 | 700 | 否 | `#6B5045` | M02 块副标题 | "验证需求是否真实存在" | 无 | 作为"大副标题"基准 |
| `.t-dim__tag` | sans | 14 | 600 | 否 | `#3E3836` | M08 维度名 | "可解释性" | 无 | 归二级标题族 |
| `.agent-concept__title` | sans | 14 | 600 | 否 | `#6B5045` | M06 概念条 | "圆点+标题" | 无 | ↑ |
| `.agent-decision__trigger` | sans | 14 | 600 | 否 | `#3E3836` | M06 决策触发 | "触发条件" | 无 | ↑ |
| `.eng-sec__label` | mono | 14 | 600 | 否 | `#6B5045` | M07 工程标签 | "模型协作策略：" | 下边框（组件） | 带边框版，保留或统一 |
| `.m07-sub__title` | sans | 14 | 600 | 否 | `#3E3836` | M07 子块 | "模型协作策略" | 无 | 与 14/600 合并 |
| `.dep-sub__title` | sans | 13 | 600 | 否 | `#3E3836` | M09 子块 | "部署方案" | 无 | 升到 14 与其他二级统一 |
| `.t-rule__tag` | sans | 13 | 600 | 否 | `#6B5045` | M05 规则标签 | "规则名" | 无 | ↑ |
| `.t-parts__tag` | sans | 14 | 600 | 否 | `#6B5045` | M04 部件标签 | "部件名" | 无 | ↑ |
| `.t-dir__name` | sans | 14 | 600 | 否 | `#6B5045` | M04 方向名 | "方向名" | 无 | ↑ |
| `.t-signal-box__title` | sans | 13 | 600 | 否 | `#6B5045` | M02 | "信号标题" | 无 | ↑ |
| `.t-loop__tag` | sans | 13 | 600 | 否 | `#6B5045` | M01 循环标签 | "循环名" | 无 | ↑ |
| `.t-case__decision` | sans | 14 | 600 | 否 | `#6B5045` | M02 案例结论 | "结论" | 无 | ↑ |
| `.dt-problem__title` | sans | 14 | 600 | 否 | `#6B5045` | M03 问题标题 | "问题" | 无 | ↑ |
| `.dt-option__tag` | sans | 13 | 600 | 否 | `#6B5045` | M03 选项标签 | "选项" | 无 | ↑ |
| `.dt-option__name` | sans | 14 | 600 | 否 | `#3E3836` | M03 选项名 | "选项名" | 无 | ↑ |
| `.af-point__head` | sans | 12.5 | 600 | 否 | `#3E3836` | M06 | "要点头" | 无 | ↑ |
| `.agent-sec__name` | sans | 13 | 600 | 否 | `#3E3836` | M06 | "节名" | 无 | ↑ |
| `.agent-future__sub` | sans | 12 | 600 | 否 | `#8C6B5D` | M06 | "子标题" | 无 | ↑ |
| `.af-principle__head` | sans | 12 | 600 | 否 | `#6B5045` | M06 | "原则头" | 无 | ↑ |
| `.gal__dir-name` | sans | 13 | 600 | 否 | `#6B5045`（off=`#9E918A`） | M04 方向名 | "方向" | 无 | off 态异色应并入 |

**小结**：碎片化严重——字号 12/12.5/13/14/18，文字色 `#3E3836` 与 `#6B5045` 混用，家族 sans 与 mono 各一处。应统一为 `--title-2`（建议 14px / 600 / `#3E3836`，区头强调用 `#6B5045`），仅 `.t-block__subtitle`（18/700）作为"大副标题"单独令牌。

### ③ 正文 / 辅助说明

| 样式类 | 字体族 | 字号 | 字重 | 斜体 | 文字色 | 模块·位置 | 示例 | 组件备注 | 合并建议 |
|---|---|---|---|---|---|---|---|---|---|
| `.t-block__body` | sans | 15 | 400 | 否 | `#3E3836` | 全局基础正文 | 段落 | 无 | 正文基准 `--body` |
| `.t-point` | sans | 15 | 400 | 否 | `#3E3836` | M01 要点 | 列表项 | 无 | 与 body 合并 |
| `.t-assumption__text` | sans | 14 | 400 | 否 | `#3E3836` | M01 | 假设文 | 无 | ↑ |
| `.t-decision__desc` | sans | 14 | 400 | 否 | `#6F6763` | M01 | 决策描述 | 无 | 偏次要，归 `--body-sm` |
| `.t-signal-row__label` | sans | 13 | 400 | 否 | `#3E3836` | M02 | 标签 | 无 | ↑ |
| `.t-parts__desc` | sans | 13 | 400 | 否 | `#6F6763` | M04 | 部件描述 | 无 | `--body-sm` |
| `.t-question__text` | sans | 14 | 400 | 否 | `#3E3836` | M05 | 问题文 | 无 | `--body` |
| `.t-page` | sans | 14 | 400 | 否 | `#3E3836` | M05 页码 | 页面名 | 无 | `--body` |
| `.t-rule__desc` | sans | 13 | 400 | 否 | `#6F6763` | M05 规则描述 | 描述 | 无 | `--body-sm` |
| `.t-dim__desc` | sans | 13 | 400 | 否 | `#6F6763` | M08 维度描述 | 描述 | 无 | `--body-sm` |
| `.t-deliv__desc` | sans | 13 | 400 | 否 | `#6F6763` | M02 交付描述 | 描述 | 无 | `--body-sm` |
| `.agent-concept__desc` | sans | 13 | 400 | 否 | `#6F6763` | M06 | 概念描述 | 无 | `--body-sm` |
| `.agent-decision__desc` | sans | 13 | 400 | 否 | `#6F6763` | M06 | 决策描述 | 无 | `--body-sm` |
| `.m07-sub__desc` | sans | 12 | 400 | 否 | `#6F6763` | M07 | 子描述 | 无 | `--body-sm` |
| `.m07-concept` | sans | 13 | 400 | 否 | `#3E3836` | M07 | 概念文 | 无 | `--body` |
| `.eng-map__input` | sans | 13 | 400 | 否 | `#3E3836` | M07 | 输入 | 无 | `--body` |
| `.eng-dotlist__d` | sans | 13 | 400 | 否 | `#3E3836` | M07 | 说明 | 无 | `--body` |
| `.eng-intg__d` | sans | 12 | 400 | 否 | `#6F6763` | M07 | 集成说明 | 无 | `--body-sm` |
| `.m07-dotlist__d` | sans | 13 | 400 | 否 | `#3E3836` | M07 | 说明 | 无 | `--body` |
| `.m07-card__d` | sans | 11 | 400 | 否 | `#6F6763` | M07 | 卡片说明 | 无 | `--body-sm`（或最小号） |
| `.m07-tag__d` | sans | 12 | 400 | 否 | `#6F6763` | M07 | 标签说明 | 无 | `--body-sm` |
| `.m07-pipe__d` | sans | 11 | 400 | 否 | `#6F6763` | M07 | 管线说明 | 无 | `--body-sm` |
| `.m07-table__duty` | sans | 12 | 400 | 否 | `#6F6763` | M07 | 职责 | 无 | `--body-sm` |
| `.dep-table__plan` | sans | 13 | 400 | 否 | `#6F6763` | M09 | 部署说明 | 无 | `--body-sm` |
| `.dep-ops__d` | sans | 11 | 400 | 否 | `#6F6763` | M09 | 运维描述 | 无 | `--body-sm` |
| `.agent-future__note` | sans | 13 | 400 | 否 | `#6F6763` | M06 | 备注 | 无 | `--body-sm` |
| `.af-principle__d` | sans | 11 | 400 | 否 | `#6F6763` | M06 | 原则说明 | 无 | `--body-sm` |
| `.proof__row-input` | sans | 12 | 400 | 否 | `#6F6763` | M08 | 输入 | 无 | `--body-sm` |
| `.proof__acc-row` | sans | 12 | 400 | 否 | `#3E3836` | M08 展开行 | 明细 | 无 | `--body` |
| `.t-block__en` | sans | 11 | 400 | 否 | `#6F6763` | 块英文副标 | "EN" | 无 | `--body-sm`（大写变体） |
| `.t-loop__desc` | sans | 12 | 400 | 否 | `#6F6763` | M01 | 描述 | 无 | `--body-sm` |
| `.t-decision-a` | sans | 14 | 400 | 否 | `#6F6763` | M01 | 答案 | 无 | `--body` |
| `.t-case__before`,`.t-case__after` | sans | 14 | 400 | 否 | `#3E3836` | M02 | 案例文 | 无 | `--body` |
| `.dt-option__reason` | sans | 13 | 400 | 否 | `#6F6763` | M03 | 理由 | 无 | `--body-sm` |
| `.dt-decompose__note` | sans | 12 | 400 | 否 | `#6F6763` | M03 | 备注 | 无 | `--body-sm` |
| `.dt-objective` | sans | 14 | 400 | 否 | `#3E3836` | M03 | 目标 | 无 | `--body` |
| `.dt-problem__body` | sans | 14 | 400 | 否 | `#3E3836` | M03 | 问题文 | 无 | `--body` |

**小结**：正文分两档——`#3E3836`（主）与 `#6F6763`（次要），字号 11–15px 散布。应收敛为两个令牌：`--body`（15/400/`#3E3836`，用作段落与多数说明）与 `--body-sm`（13/400/`#6F6763`，用作辅助/次要说明）；11px 极小号统一归入 `--body-sm` 或单独 `--body-xs`。

### ④ 强调块 callout（仅记文字字体属性；左条/杏底为组件样式，已排除）

| 样式类 | 字体族 | 字号 | 字重 | 斜体 | 文字色 | 模块·位置 | 示例 | 组件备注(排除) | 合并建议 |
|---|---|---|---|---|---|---|---|---|---|
| `.t-highlight` | sans | 15 | 400 | 否 | `#3E3836` | M01 | 高亮句 | 左条+杏底 | callout 基准 |
| `.t-key-insight`/`.key-decision` | sans | 15 | 600 | 否 | `#6B5045` | M01/M02 | KEY DECISION | 左条+杏底 | 合并为强调 callout |
| `.dt-problem` | sans | 14 | 400 | 否 | `#3E3836` | M03 | Objectives | 左条+杏底 | ↑ |
| `.agent-future__position` | sans | 12.5 | 400 | 否 | `#3E3836` | M06 | 定位句 | 左条 | ↑ |
| `.nti__update-summary` | sans | 14 | 600 | 否 | `#6B5045` | M02 | 总结 | 左条+杏底 | ↑ |

**小结**：文字字体属性差异小（14–15px、400/600、`#3E3836`/`#6B5045`），组件外观（左条+杏底）统一。应合并为一个 `--callout` 令牌，强调版用 600/`#6B5045`。

### ⑤ 编号 / 标签（mono）

| 样式类 | 字体族 | 字号 | 字重 | 斜体 | 文字色 | 模块·位置 | 示例 | 组件备注(排除) | 合并建议 |
|---|---|---|---|---|---|---|---|---|---|
| `.t-start__idx` | mono | 13 | 600 | 否 | `#8C6B5D` | M01 | "01" | 无 | 统一 mono 编号令牌 |
| `.t-decision__idx` | mono | 13 | 600 | 否 | `#8C6B5D` | M01 | "01" | 无 | ↑ |
| `.t-parts__idx` | mono | 13 | 600 | 否 | `#8C6B5D` | M04 | "01" | 无 | ↑ |
| `.agent-decision__idx` | mono | 13 | 600 | 否 | `#8C6B5D` | M06 | "01" | 无 | ↑ |
| `.agent-sec__idx` | mono | 13 | 600 | 否 | `#8C6B5D` | M06 | "01" | 无 | ↑ |
| `.t-deliv__idx` | mono | 13 | 600 | 否 | `#8C6B5D` | M02 | "01" | 无 | ↑ |
| `.t-dim__idx` | mono | 13 | 600 | 否 | **`#C7A18E`** | M08 | "01" | 无 | **异色！应改为 `#8C6B5D`** |
| `.t-assumption__idx` | mono | 13 | 600 | 否 | **`#6F6763`** | M01 | "01" | 无 | **异色！应改为 `#8C6B5D`** |
| `.t-question__q` | mono | 13 | 700 | 否 | `#8C6B5D` | M05 | "Q" | 无 | 字重差异，可并入 600 |
| `.t-flow__seg` | mono | 13 | 600 | 否 | `#3E3836` | M05 | 流程段 | 边框+底色（组件） | 带框版保留 |
| `.t-stat__k` | mono | 20 | 600 | 否 | `#6B5045` | M05 | "94%" | 无 | 大数字，单独令牌 `--num-lg` |
| `.acg__name` | mono | 12 | 600 | 否 | `#6B5045` | M06 | 角色名 | 边框+底色（组件） | 组件内文字，字体归 mono 标签 |

**小结**：绝大多数 mono 编号为 13/600/`#8C6B5D`，高度一致。**两处文字色硬伤**：`.t-dim__idx`（`#C7A18E`）与 `.t-assumption__idx`（`#6F6763`）应改正为 `#8C6B5D`。`.t-stat__k`（20px）作为大数字单独令牌。

### ⑥ 引用 / 斜体

| 样式类 | 字体族 | 字号 | 字重 | 斜体 | 文字色 | 模块·位置 | 示例 | 组件备注(排除) | 合并建议 |
|---|---|---|---|---|---|---|---|---|---|
| `.t-note` | sans | 14 | 400 | **是** | `#3E3836` | M04 | 能力闭环 | 虚线边框+底色（组件） | 统一斜体引用令牌 |
| `.t-quote-pair__quote` | sans | 14 | 400 | **是** | `#6F6763` | M02 | "用户原话" | 无 | ↑（颜色统一） |
| `.key-insight__en` | sans | 14 | 600 | **是** | `#6B5045` | M02 | 英文洞察 | 无 | ↑（字重/颜色统一） |

**小结**：三处斜体引用均为 14px，但文字色（`#3E3836`/`#6F6763`/`#6B5045`）与字重（400/600）不一致。合并为一个 `--quote` 令牌（14px / italic / `#6F6763`，强调版 600/`#6B5045`）。

### ⑦ 徽章 / 胶囊（仅记内部文字字体属性；背景/边框/状态色为组件样式，已排除）

| 样式类 | 字体族 | 字号 | 字重 | 斜体 | 文字色 | 模块·位置 | 示例 | 组件备注(排除) | 合并建议 |
|---|---|---|---|---|---|---|---|---|---|
| `.dep-capsule` | sans | 12 | 600 | 否 | biz `#6B5045` / ops `#8C6B5D` | M09 | 业务/运营 | 底色 `#FAF3EC`/`#FFF`、边框（组件） | 内部文字色两态差异，建议统一为单一 token |
| `.af-pill` | sans | 10.5 | 400 | 否 | `#FFFFFF` | M06 | 技术预留 | 底色 `#C7A18E`、边框（组件） | pill 令牌（小号） |
| `.eng-dep__pill` | sans | 13 | 400 | 否 | `#3E3836` | M07 | 依赖 | 底色 `#FAF3EC`、边框（组件） | pill 令牌 |
| `.proof__status` | sans | 12 | 600 | 否 | 状态色(pass/info/warn) | M08 | PASS | 底色+边框=语义状态（组件） | 状态徽章单独令牌，字体仅 12/600 |
| `.t-signal__chip` | sans | 13 | 400 | 否 | `#3E3836` | M02 | 信号值 | 底色 primary-100（组件） | 归 pill 家族 |
| `.t-flow-chain__item` | mono | 12 | 600 | 否 | `#6B5045` | M01 | 链路项 | 底色 primary-100（组件） | mono 标签 |
| `.matrix__priority` | sans | 10 | 600 | 否 | `#6B5045` | M05 | 优先级 | 底色 primary-100、边框（组件） | 小徽章 |
| `.gal__sel` | sans | 10 | 600 | 否 | `#6B5045` | M04 | 选中 | 边框（组件） | 小徽章 |
| `.t-dir__sel` | sans | 10 | 600 | 否 | `#6B5045` | M04 | 选中 | 边框（组件） | 小徽章 |

**说明**：本类所有"背景色 A vs 背景色 B""边框色差异""状态色差异"均为**组件样式**，不在字体排查范围，不据此合并。仅内部文字字体属性纳入：字号 10–13px、字重 400–600、文字色 `#3E3836`/`#6B5045`/`#8C6B5D`/`#fff`/状态色。建议徽章内文字统一使用一个主色 token（如 `#6B5045` 或 `#8C6B5D`），语义状态色（proof__status）除外。

---

## 3. 文字类型角色评估（语义归类）

左侧栏实际出现的语义角色可归为 8 类：

1. **一级/区块标题**：eyebrow 式小标签（12–14px，主色）。
2. **二级/子标题**：区块内小节标题（13–14px，深棕/主色）。
3. **正文**：段落与多数说明（14–15px，`#3E3836`）。
4. **辅助/次要说明**：注释、备注、表格次要列（11–13px，`#6F6763`）。
5. **强调块 callout**：左条+杏底的高亮句（14–15px）。
6. **编号/标签 mono**：序号、Q、流程段、大数字（mono 13px 为主）。
7. **引用/斜体**：用户原话、英文洞察（14px italic）。
8. **徽章/胶囊**：内部文字（10–13px，组件外观另计）。

---

## 4. 合并 / 重用方案（收敛为约 10 个字体令牌）

| 建议令牌 | 规格（字体族/字号/字重/文字色） | 吸纳的现存样式 |
|---|---|---|
| `--title-1`（一级标题） | sans / 12 / 600 / `#8C6B5D`（大写+1.5px 字距） | `.t-block__title`、`.agent-section__label` |
| `--title-1--lg`（区头变体） | sans / 14 / 700 / `#8C6B5D` | `.pf-frame .t-block__title`、`.dep-title`、`.m07-sec__title`（统一字重与大小写） |
| `--title-2`（二级标题） | sans / 14 / 600 / `#3E3836` | `.t-dim__tag`、`.agent-concept__title`、`.agent-decision__trigger`、`.m07-sub__title`、`.t-rule__tag`、`.t-parts__tag`、`.t-dir__name`、`.t-signal-box__title`、`.t-loop__tag`、`.t-case__decision`、`.dt-problem__title`、`.dt-option__tag`、`.dt-option__name`、`.af-point__head`、`.agent-sec__name`、`.af-principle__head`、`.gal__dir-name`、`.dep-sub__title`（升 14） |
| `--subtitle-lg`（大副标题） | sans / 18 / 700 / `#6B5045` | `.t-block__subtitle` |
| `--body`（正文） | sans / 15 / 400 / `#3E3836` | `.t-block__body`、`.t-point`、`.t-assumption__text`、`.t-question__text`、`.t-page`、`.m07-concept`、`.eng-map__input`、`.eng-dotlist__d`、`.m07-dotlist__d`、`.proof__acc-row`、`.t-decision-a`、`.t-case__before/after`、`.dt-objective`、`.dt-problem__body` |
| `--body-sm`（次要） | sans / 13 / 400 / `#6F6763` | ③类全部 `#6F6763` 项（含 `#9A938E` 异色纠正 → `#6F6763`） |
| `--callout` | sans / 15 / 400 / `#3E3836`（强调版 600 / `#6B5045`） | `.t-highlight`、`.t-key-insight`、`.key-decision`、`.dt-problem`、`.agent-future__position`、`.nti__update-summary` |
| `--mono-idx`（编号） | mono / 13 / 600 / `#8C6B5D` | `.t-start__idx` 等（**`.t-dim__idx` 改 `#8C6B5D`、`.t-assumption__idx` 改 `#8C6B5D`**） |
| `--num-lg`（大数字） | mono / 20 / 600 / `#6B5045` | `.t-stat__k` |
| `--quote`（斜体引用） | sans / 14 / italic / `#6F6763`（强调版 600 / `#6B5045`） | `.t-note`、`.t-quote-pair__quote`、`.key-insight__en` |
| `--pill` / `--badge` | sans / 12 / 600 / 主色 token（状态色除外） | `.dep-capsule`、`.af-pill`、`.eng-dep__pill`、`.proof__status`、`.t-signal__chip`、`.matrix__priority`、`.gal__sel`、`.t-dir__sel` |

---

## 5. 已知字体硬伤（文字色不一致，优先修）

1. **`.t-dim__idx`**：mono 编号文字色为 `#C7A18E`（primary-500），与其他 mono 编号的 `#8C6B5D` 不一致 → 改为 `#8C6B5D`。
2. **`.t-assumption__idx`**：mono 编号文字色为 `#6F6763`（text-secondary），应改为 `#8C6B5D`。
3. **`.dep-capsule-note`**：文字色 `#9A938E`（游离灰），应并入 `#6F6763`（`--body-sm`）。
4. **`.gal__dir--off` 的 `.gal__dir-name`/`kw`**：off 态用 `#9E918A`/`#B5AAA3` 游离灰，on 态用主色，建议 off 态并入 `#6F6763`。

> 注：以上"硬伤"均为**文字前景色**问题，属字体排查范围；其所在组件的背景/边框不在此列。

---

## 6. 执行备注

- 本文件为只读排查与方案，**不修改 `design.html`**。
- 组件样式（背景/边框/圆角/阴影/语义状态色）不在本次范围，待后续「组件样式一致性」任务处理（含右侧 artifact 面板）。
- 落地时建议：先在 `:root` 定义上述令牌变量，再逐类替换 class 内的 font-* 与 color，最后删除冗余 class 或保留别名。
