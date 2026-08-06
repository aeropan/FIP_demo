---
title: FIP 知识推理系统
emoji: 🐱
colorFrom: warmGray
colorTo: amber
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# 猫传染性腹膜炎（FIP）知识推理系统

基于 **Gradio + Neo4j** 的猫传染性腹膜炎（FIP，猫传腹）知识推理前端。
当前版本为前端骨架：展示三栏布局（左侧导航 / 中间对话 / 右侧隐藏技术面板），
后端自然语言理解、实体链接、Cypher 查询生成等逻辑将在后续迭代中补全。

## 功能

- 左侧功能导航：切换「对话 / 图谱数据 / 产品设计理念 / 补充说明」四个页面
- 中间对话区：Chatbot 交互展示区 + 示例问题按钮 + 问题输入框
- 右侧技术面板：默认隐藏，后续将展示推理链、Cypher 语句、实体/意图匹配日志
- 响应式布局：适配桌面与移动端浏览器访问

## 项目结构

```
fip-causal-reasoning/
├── app.py              # Gradio 前端主程序（Hugging Face Spaces 入口）
├── utils.py            # 后端接口存根（意图识别 / 实体解析 / Cypher 查询）
├── neo4j_client.py     # Neo4j 连接与因果路径查询封装（可复用）
├── seed_data.cypher    # 示例因果图数据
├── .env.example        # 环境变量示例
├── requirements.txt
├── README.md
└── .gitignore
```

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Neo4j（可选，当前后端逻辑未接入）

复制环境变量示例并填写凭据：

```bash
cp .env.example .env
```

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### 3. 启动

```bash
python app.py
```

打开浏览器访问 `http://127.0.0.1:7860`。

## 部署到 Hugging Face Spaces

1. 在 [Hugging Face](https://huggingface.co/spaces) 新建 Space，选择 **Gradio SDK**。
2. 选择 **关联 GitHub 仓库**：`aeropan/FIP_demo`。
3. Spaces 会自动读取仓库根目录的 `app.py`（已在 README YAML 元数据中通过 `app_file: app.py` 指定）。
4. 推送代码到 GitHub 后，Spaces 将自动构建并发布。
5. 构建完成后，通过 `https://huggingface.co/spaces/<你的用户名>/<space名>` 访问。

### 前后端一体说明

- Gradio 应用即前端 UI，同时 `utils.py` / `neo4j_client.py` 作为后端逻辑运行在同一个容器内。
- 如需查询真实 Neo4j 图谱，数据库需要可被 Hugging Face 容器访问（推荐 [Neo4j Aura](https://neo4j.com/cloud/aura/) 等云实例，或具有公网地址的 Neo4j 服务）。
- 当前 `utils.py` 中 `run_query()` 为占位实现，未真正连接数据库；补全后将通过环境变量读取 `NEO4J_URI` / `NEO4J_USERNAME` / `NEO4J_PASSWORD`。

## 移动设备与展示效果

- Gradio 生成的页面在移动端浏览器中会自动缩放适配，基础布局（三栏）在小屏幕下会变为纵向堆叠。
- 页面动效/图表类复杂特效需要额外引入 CSS/JS 或第三方库（如 D3、ECharts）实现，Gradio 原生组件以表单和静态展示为主。

## 免责声明

本系统输出内容仅供学习参考，**不能替代执业兽医的诊断与治疗建议**。
如猫咪出现疑似 FIP 症状，请及时就医。
