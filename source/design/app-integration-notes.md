# app.py 与子页面集成说明

> 供后续对话阅读，快速理解当前集成架构与关键代码位置。
> 最后更新：2026-08-17（新增文献库 / 产品设计说明空页面；导航路由改为 document 事件委托）

## 1. 总体架构

app.py 是 Gradio 单页应用，通过**单个 `gr.HTML` 组件**承载全部前端。采用 **iframe 隔离方案**（方案 B）集成子页面（图数据库 / 文献库 / 产品设计说明）：

```
app.py（主应用 / 壳）
├── HOMEPAGE_HTML  —— 三栏首页 DOM（左导航 + 对话区 + 右侧时间线 + 三个 iframe）
├── JS_CODE        —— 首页交互逻辑 + 导航路由（document 事件委托，切换视图）
├── _GRADIO_CSS    —— 全局样式 + 页面视图显隐规则
├── respond()      —— 后端推理入口（server_functions 暴露给 JS）
└── 运行时注入三个页面 HTML → 对应 iframe srcdoc（懒加载）
```

## 2. 为什么用 iframe 而非 DOM 注入

app.py 的 `HOMEPAGE_HTML` 和 `graph-demo.html` **都用了 `.app-shell` 类名和各自独立的 `:root` CSS 变量**。如果直接 DOM 注入，CSS 互相覆盖。iframe srcdoc 方案零冲突，graph-demo.html 几乎不用改（只删了自带导航）。

## 3. 关键代码位置（app.py）

| 行号（当前） | 内容 | 说明 |
|------|------|------|
| 281–285 | 三个 iframe：`pageGraph` / `pageDocs` / `pageDesign` | HOMEPAGE_HTML 内 app-shell 末尾，三个页面的容器（懒加载 srcdoc） |
| 291–294 | `window.__GRAPH_HTML__ / __DOCS_HTML__ / __DESIGN_HTML__` | JS_CODE 开头占位符，运行时替换为转义后的页面 HTML |
| 295–338 | 导航路由 IIFE（document 事件委托） | 点「图数据库 / 文献库 / 产品设计说明」→ 加对应 `mode-*` 类 + 懒加载 srcdoc；其他 → 回首页 |
| 1381–1397 | 新建任务 / 最近对话委托 | document 委托处理 `.new-task-btn` / `.collapsed-tool` / `.chat-item`，先退出页面模式再执行功能 |
| 2546–2554 | Python 运行时注入 | 读取 graph-demo.html / docs.html / design.html，JSON 转义后替换占位符 |
| 2555–2570 | 页面视图 CSS | `mode-graph` / `mode-docs` / `mode-design` 隐藏 main-area / right-sidebar，显示对应 iframe |
| 2580+ | `respond()` | 后端推理入口，通过 `server_functions=[respond]` 暴露给前端 |

> ⚠️ 行号随代码改动会漂移，定位时以「内容」列的关键词搜索为准。

## 4. 关键代码位置（graph-demo.html）

| 位置 | 内容 | 说明 |
|------|------|------|
| 第 7 行 | G6 CDN script | `<head>` 内，iframe srcdoc 下正常加载 |
| 第 8 行 | 3d-force-graph / three-spritetext | 懒加载（点「3D」按钮时动态注入） |
| 242 行 | `<div class="app-shell">` | body 主体，仅含 `graph-main` + `right-panel`（导航已删除） |
| 内联 JS | `GRAPH_DATA` | 70 节点 / 65 边，已内嵌为 JSON 常量 |

## 5. 导航路由逻辑

> 已从「一次性 forEach 绑定」改为「document 事件委托」（约 295–338 行），避免 Gradio 重渲染导致监听丢失。新建任务 / 最近对话同样用委托（约 1381–1397 行），且会先退出页面模式再执行功能（否则 main-area 被隐藏看不到反馈）。

```javascript
// app.py JS_CODE（document 事件委托，约 295–338 行）
document.addEventListener('click', function(e){
  var item = e.target && e.target.closest && e.target.closest('.nav-menu .nav-item');
  if (!item) return;
  e.preventDefault();
  var text = item.textContent;
  document.querySelectorAll('.nav-menu .nav-item').forEach(function(n){ n.classList.remove('active'); });
  item.classList.add('active');
  if (text.indexOf('图数据库') >= 0) {
    appShell.classList.add('mode-graph');
    appShell.classList.remove('mode-docs', 'mode-design');
    if (!pageGraph.dataset.loaded) { pageGraph.srcdoc = window.__GRAPH_HTML__; pageGraph.dataset.loaded = '1'; }
  } else if (text.indexOf('文献库') >= 0) {
    appShell.classList.add('mode-docs');
    appShell.classList.remove('mode-graph', 'mode-design');
    if (!pageDocs.dataset.loaded) { pageDocs.srcdoc = window.__DOCS_HTML__; pageDocs.dataset.loaded = '1'; }
  } else if (text.indexOf('产品设计说明') >= 0) {
    appShell.classList.add('mode-design');
    appShell.classList.remove('mode-graph', 'mode-docs');
    if (!pageDesign.dataset.loaded) { pageDesign.srcdoc = window.__DESIGN_HTML__; pageDesign.dataset.loaded = '1'; }
  } else {
    appShell.classList.remove('mode-graph', 'mode-docs', 'mode-design');  // 回首页
  }
});
```

## 6. 数据文件

| 文件 | 说明 |
|------|------|
| `source/design/graph-demo.html` | 图谱页高保真原型（2D G6 + 3D force-graph），已删除自带导航 |
| `source/design/docs.html` | 文献库空页面（独立文件，填充内容只改此文件） |
| `source/design/design.html` | 产品设计说明空页面（独立文件，填充内容只改此文件） |
| `source/design/graph-data.json` | 前端图数据（70 节点 / 65 边 / 四类节点映射） |
| `source/design/_gen_graph_data.py` | 数据生成脚本（含完整 ENTITY_TYPE_MAP） |
| `source/design/graph-page-spec.md` | 图谱页设计规范文档 |

## 7. 已知边界与后续接入点

### 已实现
- 2D 图谱渲染（G6 4.8.24，70 节点 / 65 边）
- 3D 全屏模式（3d-force-graph 懒加载，Esc 退出；esm.sh 的 three-spritetext 已实测可用）
- 四类节点分类色、极性色、置信度展示
- 节点/关系点击详情、路径高亮（URL `?path=`）
- 三页面路由：图数据库 / 文献库 / 产品设计说明（后两者空页面占位，独立文件）
- 左侧导航全部用 document 事件委托（nav-item / 新建任务 / 最近对话），不受 Gradio 重渲染影响

### 未实现 / 后续接入
1. **对话→图谱联动**：对话推理结果中的路径高亮需要从父页面 postMessage 到 iframe（当前仅支持 iframe 内 URL `?path=` 自测）
2. **后端接入**：`core/db.py` 加 `get_full_graph()`；`core/config.py` 加 `ENTITY_TYPE_MAP`；`core/schemas.py` 的 `AgentResponse` 加 `path_nodes`
3. **文献库 / 产品设计说明页面内容**：已建空页面（docs.html / design.html），填充内容只改对应文件即可，无需动 app.py 路由

## 8. 备份

`app.py.bak` —— 改造前原始版本（2438 行），首页功能完整。
