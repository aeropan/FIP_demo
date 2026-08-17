# app.py 与图数据库页面集成说明

> 供后续对话阅读，快速理解当前集成架构与关键代码位置。
> 最后更新：2026-08-17

## 1. 总体架构

app.py 是 Gradio 单页应用，通过**单个 `gr.HTML` 组件**承载全部前端。采用 **iframe 隔离方案**（方案 B）集成图数据库页面：

```
app.py（主应用 / 壳）
├── HOMEPAGE_HTML  —— 三栏首页 DOM（左导航 + 对话区 + 右侧时间线）
├── JS_CODE        —— 首页交互逻辑 + 导航路由（切换视图）
├── _GRADIO_CSS    —— 全局样式 + 图谱页视图显隐规则
├── respond()      —— 后端推理入口（server_functions 暴露给 JS）
└── 运行时注入 graph-demo.html → iframe srcdoc（懒加载）
```

## 2. 为什么用 iframe 而非 DOM 注入

app.py 的 `HOMEPAGE_HTML` 和 `graph-demo.html` **都用了 `.app-shell` 类名和各自独立的 `:root` CSS 变量**。如果直接 DOM 注入，CSS 互相覆盖。iframe srcdoc 方案零冲突，graph-demo.html 几乎不用改（只删了自带导航）。

## 3. 关键代码位置（app.py）

| 行号 | 内容 | 说明 |
|------|------|------|
| 278–279 | `<iframe id="pageGraph" class="page-graph" hidden>` | HOMEPAGE_HTML 内，app-shell 末尾，图谱页容器 |
| 284–285 | `window.__GRAPH_HTML__=__GRAPH_HTML_JSON__` | JS_CODE 第一行，占位符（运行时被替换为转义后的图谱 HTML） |
| 287–310 | 导航路由 IIFE | 点「图数据库」→ app-shell 加 `mode-graph` 类 + 懒加载 iframe srcdoc；点其他 → 移除该类 |
| 2377–2380 | Python 运行时注入 | 读取 `source/design/graph-demo.html`，JSON 转义后替换 `__GRAPH_HTML_JSON__` |
| 2385–2389 | 图谱页 CSS | `.mode-graph` 状态下隐藏 `.main-area` / `.right-sidebar`，显示 `.page-graph` |
| 2397–2445 | `respond()` | 后端推理入口，通过 `server_functions=[respond]` 暴露给前端 |

## 4. 关键代码位置（graph-demo.html）

| 位置 | 内容 | 说明 |
|------|------|------|
| 第 7 行 | G6 CDN script | `<head>` 内，iframe srcdoc 下正常加载 |
| 第 8 行 | 3d-force-graph / three-spritetext | 懒加载（点「3D」按钮时动态注入） |
| 242 行 | `<div class="app-shell">` | body 主体，仅含 `graph-main` + `right-panel`（导航已删除） |
| 内联 JS | `GRAPH_DATA` | 70 节点 / 65 边，已内嵌为 JSON 常量 |

## 5. 导航路由逻辑

```javascript
// app.py JS_CODE 第 287–310 行
navItems.forEach(function(item){
  item.addEventListener('click', function(e){
    e.preventDefault();
    var isGraph = item.textContent.indexOf('图数据库') >= 0;
    navItems.forEach(function(n){ n.classList.remove('active'); });
    item.classList.add('active');
    if(isGraph){
      appShell.classList.add('mode-graph');      // 隐藏首页，显示 iframe
      if(!pageGraph.dataset.loaded){
        pageGraph.srcdoc = window.__GRAPH_HTML__; // 首次点击才加载
        pageGraph.dataset.loaded = '1';
      }
    } else {
      appShell.classList.remove('mode-graph');     // 切回首页
    }
  });
});
```

## 6. 数据文件

| 文件 | 说明 |
|------|------|
| `source/design/graph-demo.html` | 图谱页高保真原型（2D G6 + 3D force-graph），已删除自带导航 |
| `source/design/graph-data.json` | 前端图数据（70 节点 / 65 边 / 四类节点映射） |
| `source/design/_gen_graph_data.py` | 数据生成脚本（含完整 ENTITY_TYPE_MAP） |
| `source/design/graph-page-spec.md` | 图谱页设计规范文档 |

## 7. 已知边界与后续接入点

### 已实现
- 2D 图谱渲染（G6 4.8.24，70 节点 / 65 边）
- 3D 全屏模式（3d-force-graph 懒加载，Esc 退出）
- 四类节点分类色、极性色、置信度展示
- 节点/关系点击详情、路径高亮（URL `?path=`）

### 未实现 / 后续接入
1. **对话→图谱联动**：对话推理结果中的路径高亮需要从父页面 postMessage 到 iframe（当前仅支持 iframe 内 URL `?path=` 自测）
2. **后端接入**：`core/db.py` 加 `get_full_graph()`；`core/config.py` 加 `ENTITY_TYPE_MAP`；`core/schemas.py` 的 `AgentResponse` 加 `path_nodes`
3. **3D 模式在 iframe srcdoc 内**：`import('https://esm.sh/three-spritetext')` 未实测，如异常需换加载方式
4. **其他导航页**：文献库、产品设计说明仍为占位，无页面内容

## 8. 备份

`app.py.bak` —— 改造前原始版本（2438 行），首页功能完整。
