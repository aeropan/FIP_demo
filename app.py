"""猫传腹因果推理 Streamlit 主程序。"""

import os

import streamlit as st
import streamlit.components.v1 as components
from neo4j_client import ConnectionConfig, FIPCausalClient, nodes_to_networkx
from pyvis.network import Network

# ---------------- 页面配置 ----------------
st.set_page_config(
    page_title="猫传腹因果推理",
    page_icon="🐱",
    layout="wide",
)

# ---------------- 主题样式 ----------------
st.markdown(
    """
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem; }
    .subtitle { color: #666; font-size: 1rem; margin-bottom: 1.5rem; }
    .metric-card { background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

LABEL_COLORS = {
    "Factor": "#4A90D9",
    "Symptom": "#F5A623",
    "Disease": "#D0021B",
    "Outcome": "#7ED321",
}

# ---------------- 状态管理 ----------------
@st.cache_resource(show_spinner="连接 Neo4j...")
def get_client(uri: str, username: str, password: str) -> FIPCausalClient:
    return FIPCausalClient(ConnectionConfig(uri=uri, username=username, password=password))


@st.cache_data(ttl=30, show_spinner="加载节点列表...")
def load_node_options(_client: FIPCausalClient) -> list[dict]:
    return _client.get_all_nodes()


# ---------------- 侧边栏：连接配置 ----------------
with st.sidebar:
    st.header("🔗 Neo4j 连接")
    neo4j_uri = st.text_input(
        "URI",
        value=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        help="例如：bolt://localhost:7687 或 neo4j+s://xxx.databases.neo4j.io",
    )
    neo4j_user = st.text_input(
        "用户名",
        value=os.getenv("NEO4J_USERNAME", "neo4j"),
    )
    neo4j_pass = st.text_input(
        "密码",
        type="password",
        value=os.getenv("NEO4J_PASSWORD", ""),
    )

    client = get_client(neo4j_uri, neo4j_user, neo4j_pass)

    conn_status = client.test_connection()
    if conn_status["ok"]:
        st.success("连接成功")
    else:
        st.error(f"连接失败：{conn_status['error']}")

    st.divider()
    st.info(
        "请先运行 `seed_data.cypher` 导入示例数据，\n"
        "或在 .env 中配置 NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD。"
    )

# ---------------- 主体 ----------------
st.markdown('<div class="main-title">🐱 猫传腹因果推理</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">基于 Neo4j 图数据库的 FIP 因果路径可视化探索</div>',
    unsafe_allow_html=True,
)

if not client.is_ready():
    st.warning("请在左侧填写完整的 Neo4j 连接信息。")
    st.stop()

node_options = load_node_options(client)
if not node_options:
    st.warning("数据库中未找到任何节点，请先导入 seed_data.cypher。")
    st.stop()

names = [n["name"] for n in node_options]
name_to_meta = {n["name"]: n for n in node_options}

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_node = st.selectbox("起始节点", options=names, index=0)
with col2:
    end_node = st.selectbox(
        "目标节点",
        options=names,
        index=names.index("猫传腹") if "猫传腹" in names else min(1, len(names) - 1),
    )
with col3:
    max_hops = st.slider("最大跳数", min_value=1, max_value=6, value=3)

mode = st.radio(
    "查询模式",
    ["双向路径：起点 → 终点", "单向影响：从起点出发的所有下游路径"],
    horizontal=True,
)

run_query = st.button("🔍 查询因果路径", type="primary", use_container_width=True)


def build_pyvis_html(nodes: set, edges: set, height: int = 500) -> str:
    """使用 PyVis 生成可在 Streamlit 中嵌入的 HTML。"""
    net = Network(
        height=f"{height}px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#333333",
        notebook=False,
    )
    net.toggle_physics(True)
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=120)

    for node_id, label, name, description in nodes:
        color = LABEL_COLORS.get(label, "#979797")
        title = f"类别：{label}\n名称：{name}\n描述：{description or '无'}"
        net.add_node(node_id, label=name, title=title, color=color, size=28 if label == "Disease" else 22)

    for source, target, rel_type, description in edges:
        title = f"关系：{rel_type}\n描述：{description or '无'}"
        net.add_edge(source, target, title=title, arrows="to", color="#888888")

    return net.generate_html()


def render_paths(paths: list[dict]):
    if not paths:
        st.info("未找到符合条件的因果路径。")
        return

    st.markdown(f"**共找到 {len(paths)} 条因果路径**")
    nodes, edges = nodes_to_networkx(paths)

    tab_graph, tab_list = st.tabs(["🕸 交互网络图", "📋 路径列表"])

    with tab_graph:
        html = build_pyvis_html(nodes, edges, height=550)
        components.html(html, height=560, scrolling=False)

    with tab_list:
        for i, path in enumerate(paths, 1):
            steps = path["nodes"]
            rels = path.get("rels", [])
            with st.expander(f"路径 {i}（{path['hops']} 跳）", expanded=i == 1):
                step_texts = []
                for idx, node in enumerate(steps):
                    step_texts.append(f"**{node['name']}** ({node['label']})")
                    if idx < len(rels):
                        rel = rels[idx]
                        step_texts.append(
                            f"➡️ *{rel['type']}*" + (f"：{rel['description']}" if rel.get("description") else "")
                        )
                st.markdown(" → ".join(step_texts))

                # 表格形式
                rows = []
                for idx, node in enumerate(steps):
                    rows.append(
                        {
                            "顺序": idx + 1,
                            "节点": node["name"],
                            "类别": node["label"],
                            "描述": node.get("description", ""),
                        }
                    )
                st.dataframe(rows, use_container_width=True, hide_index=True)


if run_query:
    if start_node == end_node and mode.startswith("双向"):
        st.warning("起始节点与目标节点不能相同。")
    else:
        with st.spinner("查询中..."):
            if mode.startswith("双向"):
                paths = client.find_causal_paths(start_node, end_node, max_hops=max_hops)
            else:
                paths = client.find_outward_paths(start_node, max_hops=max_hops)
        render_paths(paths)

st.divider()
with st.expander("ℹ️ 图例与说明"):
    legend_html = ""
    for label, color in LABEL_COLORS.items():
        legend_html += f'<span style="display:inline-block;width:12px;height:12px;background:{color};margin-right:6px;border-radius:50%;"></span>{label} '
    st.markdown(legend_html, unsafe_allow_html=True)
    st.markdown(
        """
        - **Factor（危险因素）**：诱发疾病的因素或上游原因
        - **Symptom（症状）**：疾病表现出来的临床征象
        - **Disease（疾病）**：猫传腹（FIP）本体
        - **Outcome（结局）**：疾病导致的结果
        """
    )
