<<<<<<< HEAD
# 猫传腹因果推理 Web 应用

基于 Streamlit 与 Neo4j 的猫传染性腹膜炎（FIP，猫传腹）因果推理可视化应用。用户可输入起始节点与目标节点，查询并展示两者之间的因果路径。

## 功能

- 连接本地或远程 Neo4j 图数据库
- 根据用户选择的起点 / 终点查询因果路径
- 支持设置最大路径长度（跳数）
- 以交互式网络图和表格形式展示结果
- 内置示例数据（Cypher 脚本），方便快速体验

## 项目结构

```
fip-causal-reasoning/
├── app.py              # Streamlit 主程序
├── neo4j_client.py     # Neo4j 连接与查询封装
├── seed_data.cypher    # 示例因果图数据
├── requirements.txt
├── README.md
└── .gitignore
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备 Neo4j

启动 Neo4j 数据库，然后使用浏览器或 `cypher-shell` 执行 `seed_data.cypher` 导入示例数据：

```bash
cypher-shell -u neo4j -p <密码> -f seed_data.cypher
```

或在 Neo4j Browser 中直接复制粘贴脚本内容执行。

### 3. 配置连接

创建 `.env` 文件（或在 Streamlit 侧边栏中填写）：

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### 4. 运行应用

```bash
streamlit run app.py
```

## Git 版本管理

项目已初始化为 Git 仓库。常用命令：

```bash
git status
git add .
git commit -m "描述修改内容"
```

## 因果图模型

- **节点**：Factor（危险因素）、Symptom（症状）、Disease（疾病）、Outcome（结局）
- **关系**：CAUSES（导致）、RISK_FACTOR_FOR（危险因素）、PRESENTS_AS（表现为）、LEADS_TO（发展为）
=======
# FIP_demo
>>>>>>> origin/main
