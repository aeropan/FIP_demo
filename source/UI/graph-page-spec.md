# 猫传腹因果图谱页面 · 设计规范与实现记录

> 归属：fip-causal-reasoning 项目「图数据库」页面
> 视觉体系：暖杏奶油 V2（详见 design-system-spec.md）
> 状态：**高保真原型已完成**（graph-demo.html），后端接入待开发

---

## 1. 设计定位

图数据库核心工作台，用于浏览、理解、追踪猫传腹因果知识。延续首页暖杏奶油视觉，以暖白 + 中性色为基础，通过有限的分类色区分节点类型，用透明度与层级突出当前节点及关联关系。

核心目标：
- 展示推理链、极性与置信度
- 支持从对话系统跳转并高亮特定推理路径
- 提供节点/关系详情查看，展示支撑依据

## 2. 三栏布局

| 栏 | 宽度 | 内容 |
|----|------|------|
| 左侧导航 | 280px | Logo / 新建任务 / 图数据库(选中) / 文献库 / 产品设计说明 / 最近对话 |
| 中间图谱 | 自适应(最大) | 标题 + 四类图例 + 全屏按钮 + 因果图谱画布 |
| 右侧详情 | 380px | 节点详情 / 关系详情 / 空态(含极性·置信度图例) |

## 3. 视觉规范

### 3.1 基础色
- 页面底色 `#FDFBF7`；点阵 `#EDE5DD`(约 3% 透明度)
- 标题 `#3E3836`；次级文字 `#6F6763`
- 导航选中背景 `#FAF3EC`；选中文字 `#6B5045`
- 卡片 `#FFFFFF`；分割线/边框 `#EDE5DD`

### 3.2 节点分类色（四类，仅用于识别，不表达状态）

| 类型 | 主色 | 浅背景 | 边框 | 缩写 |
|------|------|--------|------|------|
| 病因与病原 | `#B86B5B` | `#FCF4F1` | `#E9CEC5` | 病 |
| 机制与过程 | `#8C6B5D` | `#FAF3EC` | `#E2D5CD` | 机 |
| 诊断与检测 | `#6D8795` | `#F2F6F8` | `#D7E2E8` | 诊 |
| 干预与结局 | `#6F8A6A` | `#F4F7F1` | `#D6E2CF` | 治 |

### 3.3 极性（关系线）
- Positive `#5B8C5A`（正向/有利）
- Negative `#C25E5E`（负向/风险）
- Neutral `#8C8C8C`（中性/机制）

### 3.4 置信度（徽章）
- High `#5B8C5A` / Medium `#D9A13B` / Low `#C25E5E`

### 3.5 圆角/阴影/动效
- 按钮 6px / 卡片 12px / 大面板 16px / Tag 999px
- 阴影暖灰 `rgba(62,56,54,x)`，不用冷黑
- 动效 150–300ms，hover 轻微缩放 + 透明度过渡

## 4. 节点与关系样式

- 节点：圆形主体(默认 44px) + 中心类型缩写 + 下方名称(超长自动换行)
  - Hover 46px(+5%) / Selected 52–54px + 外围 4–6px 浅色焦点环
- 关系线：极性色，默认透明度 0.6、线宽 1.2px，细箭头
  - Hover/选中显示标签「关系类型 · 置信度」，线宽增至 2–2.5px，不透明度 1.0

## 5. 交互

- **Hover 节点**：当前放大约 5%；一度邻居清晰；非关联降到 opacity 0.25；关联线高亮、非关联线 0.15
- **点击节点（聚焦）**：当前最大 + 焦点环；一度全显；二度 0.5；无关 0.12–0.2；线同理
- **点击关系线**：该线最高层级，两端节点清晰，其余弱化；右栏切「关系详情」
- **路径高亮**：URL `?path=` 或对话「查看图谱」跳转，高亮路径节点/边，非路径降到 0.12–0.15，自动居中

## 6. 数据接口与后端接入点（待开发）

当前原型用静态数据 `graph-data.json`（由 `_gen_graph_data.py` 从 `source/neo4j/FIP_data.txt` 生成）。

后端接入三件事：
1. **`core/config.py` 新增 `ENTITY_TYPE_MAP`**：70 个实体 → 四类映射（已在 `_gen_graph_data.py` 中完成并全覆盖，可直接迁移）。
2. **`core/db.py` 新增 `get_full_graph()`**：返回全量节点+关系（Cypher 见设计文档 12.1）。
3. **`core/schemas.py` 的 `AgentResponse` 新增 `path_nodes`**：`ResponseAgent` 提取推理链节点名（有序），前端跳转图谱页时经 URL 传参。

## 7. 实现优先级（对齐设计文档 14）

1. 节点类型映射与样式 ✅（原型已完成）
2. 关系线与极性/置信度展示 ✅（原型已完成）
3. 推理链路径高亮 ✅（原型已完成，URL ?path= 已通）
4. 右侧详情面板 ✅（原型已完成）
5. 交互优化 ✅（Hover/点击聚焦/动画已实现）

## 8. 交付物清单

| 文件 | 说明 |
|------|------|
| `graph-demo.html` | 高保真可交互原型（AntV G6 4.8.24，内嵌 70 节点/65 边，单文件可独立打开） |
| `graph-data.json` | 前端图数据（nodes 含 type，edges 含 polarity/confidence/evidence） |
| `_gen_graph_data.py` | 数据生成脚本（含完整 `ENTITY_TYPE_MAP`，可复现） |

## 9. 3D 模式（新增）

- 顶部「全屏」旁新增「3D」按钮，点击进入**全屏 3D 覆盖层**（`position:fixed; inset:0`，覆盖三栏），Esc 或「返回 2D」退出并恢复 2D。
- 复用同一份 `GRAPH_DATA`（70 节点 / 65 边），不新增数据源。
- 技术栈：
  - `3d-force-graph@1.80.0`（unpkg UMD，1.3MB **已内置 Three.js**，单 script 引入，无需另引 three）
  - `three-spritetext`（esm.sh 动态 `import()`，canvas 生成中文文字 sprite）
- 节点 = 分类色球体（`nodeColor` + `nodeVal`）+ 上方文字标签（`nodeThreeObject` 返回 `SpriteText`，`nodeThreeObjectExtend(true)` 叠加）；边 = 极性色 + 置信度粒子箭头。
- 交互：hover 显示 `nodeLabel` tooltip；点击节点/边弹出浮层详情（复用 2D 详情数据）；继承 2D 的路径高亮（`nodeColor` + `linkVisibility`）。
- 生命周期：`enter3D()` 懒加载（CDN script + esm.sh import）→ `init3D()`；`exit3D()` 调 `g3d._destructor()` 释放 WebGL 上下文并清空容器。
- 注意：3d-force-graph 无 `nodeHoverColor` API；销毁必须用 `_destructor()` 释放 WebGL。
