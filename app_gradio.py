"""
猫传染性腹膜炎（FIP）知识推理系统 —— Gradio 前端（前期骨架版）。

当前仅完成三栏布局与基础组件展示：
- 左侧：功能导航（Radio 切换 4 个页面）
- 中间：对话区（Chatbot + 示例按钮 + 输入框）
- 右侧：默认隐藏的技术推理面板（Markdown 占位）

后端交互（实体解析、意图识别、Cypher 查询、按钮事件）暂缓实现。
运行命令：python app_gradio.py
"""

from __future__ import annotations

import gradio as gr

# ---------------------------------------------------------------------------
# 占位函数：从 utils.py 导入的接口目前只返回空结果
# ---------------------------------------------------------------------------
from utils import (
    DIAGNOSIS_QUERY,
    GENERAL_QUERY,
    SIDE_EFFECT_QUERY,
    TREATMENT_QUERY,
    detect_intent,
    resolve_entities,
    run_query,
)

# ---------------------------------------------------------------------------
# 页面常量
# ---------------------------------------------------------------------------
APP_TITLE = "🐱 猫传染性腹膜炎（FIP）知识推理系统"
NAV_OPTIONS = ["对话", "图谱数据", "产品设计理念", "补充说明"]
NAV_DEFAULT = "对话"

EXAMPLE_QUERIES = [
    "猫传腹如何诊断",
    "湿性FIP怎么治",
    "GS-441524有副作用吗",
    "猫发热怎么办",
]


# ---------------------------------------------------------------------------
# 左侧导航栏（宽度 scale=1）
# ---------------------------------------------------------------------------
def build_nav_column() -> gr.Column:
    """构建左侧导航栏。"""
    with gr.Column(scale=1, min_width=160) as col:
        gr.Markdown("## 功能导航")
        nav_radio = gr.Radio(
            choices=NAV_OPTIONS,
            value=NAV_DEFAULT,
            label="选择页面",
            interactive=True,
        )
        # 当前阶段： Radio 切换后由主内容区动态渲染，不绑定具体回调
        gr.Markdown("_提示：目前仅展示页面骨架，交互逻辑待后续补全。_")
    return col, nav_radio


# ---------------------------------------------------------------------------
# 中间对话栏（宽度 scale=4）
# ---------------------------------------------------------------------------
def build_chat_column() -> tuple[gr.Column, gr.Chatbot, gr.Textbox]:
    """构建中间对话主区域。"""
    with gr.Column(scale=4) as col:
        gr.Markdown(f"# {APP_TITLE}")

        chatbot = gr.Chatbot(
            label="对话历史",
            height=500,
        )

        # 示例问题按钮：当前只静态展示，后续绑定点击事件
        with gr.Row():
            for text in EXAMPLE_QUERIES:
                gr.Button(text, size="sm")

        # 用户输入框：当前只作为展示组件
        input_box = gr.Textbox(
            placeholder="请输入关于猫传腹的问题…",
            label="问题输入",
            show_label=False,
            lines=2,
            max_lines=4,
        )

        # 发送按钮（占位）
        send_btn = gr.Button("发送", variant="primary")
        _ = (send_btn, input_box, chatbot)  # 后续绑定事件用

    return col, chatbot, input_box


# ---------------------------------------------------------------------------
# 右侧技术推理面板（宽度 scale=2，默认隐藏）
# ---------------------------------------------------------------------------
def build_reasoning_column() -> tuple[gr.Column, gr.Markdown]:
    """构建右侧默认隐藏的技术推理面板。"""
    with gr.Column(scale=2, visible=False, elem_id="reasoning-panel") as col:
        gr.Markdown("## 技术推理详情")
        reasoning_md = gr.Markdown(
            value="_右侧面板将展示推理链、Cypher 语句及实体/意图匹配日志。_"
        )
    return col, reasoning_md


# ---------------------------------------------------------------------------
# 主内容区：根据左侧导航切换显示不同页面
# ---------------------------------------------------------------------------
def build_main_content() -> tuple[gr.Column, gr.Column, gr.Column, gr.Column]:
    """构建四个导航页面对应的内容容器。"""
    with gr.Column() as page_chat:
        chat_col, chatbot, input_box = build_chat_column()

    with gr.Column(visible=False) as page_graph:
        gr.Markdown("# 图谱数据")
        gr.Markdown("_此处将展示 Neo4j 图数据库统计信息、实体列表与关系概览。_")
        gr.Dataframe(
            headers=["实体名", "类型", "描述"],
            value=[],  # 前期占位
            label="实体列表",
            interactive=False,
        )

    with gr.Column(visible=False) as page_design:
        gr.Markdown("# 产品设计理念")
        gr.Markdown(
            """
            本项目基于**知识图谱**技术，将猫传染性腹膜炎（FIP）相关的病因、症状、
            诊断、治疗及预后知识组织为可推理的图结构，帮助用户通过自然语言问答
            获得结构化的医学知识提示。

            当前版本为前端骨架，后续将逐步接入：
            - 意图识别
            - 实体链接
            - Cypher 查询生成
            - 推理链可视化
            """
        )

    with gr.Column(visible=False) as page_notes:
        gr.Markdown("# 补充说明")
        gr.Markdown(
            """
            1. 本系统输出仅供学习参考，**不能替代执业兽医的诊断与治疗建议**。
            2. 知识库数据来源于公开文献与指南，持续更新中。
            3. 如猫咪出现疑似 FIP 症状，请及时就医。
            """
        )

    return page_chat, page_graph, page_design, page_notes, chat_col, chatbot, input_box


# ---------------------------------------------------------------------------
# 页面切换回调（占位）
# ---------------------------------------------------------------------------
def switch_page(selected: str) -> tuple:
    """根据左侧 Radio 选项切换主内容区可见性。"""
    return (
        gr.update(visible=(selected == "对话")),
        gr.update(visible=(selected == "图谱数据")),
        gr.update(visible=(selected == "产品设计理念")),
        gr.update(visible=(selected == "补充说明")),
    )


# ---------------------------------------------------------------------------
# 应用入口
# ---------------------------------------------------------------------------
def main() -> None:
    """构建并启动 Gradio 应用。"""
    with gr.Blocks(
        title="FIP 知识推理系统",
    ) as demo:
        with gr.Row(equal_height=False):
            # 左侧导航
            nav_col, nav_radio = build_nav_column()

            # 中间主内容区（包含 4 个可切换页面）
            (
                page_chat,
                page_graph,
                page_design,
                page_notes,
                chat_col,
                chatbot,
                input_box,
            ) = build_main_content()

            # 右侧技术推理面板
            reasoning_col, reasoning_md = build_reasoning_column()

        # 页面切换事件绑定
        nav_radio.change(
            fn=switch_page,
            inputs=nav_radio,
            outputs=[page_chat, page_graph, page_design, page_notes],
        )

        # TODO: 后续将绑定示例按钮、发送按钮与右侧推理面板显示逻辑
        _ = (chatbot, input_box, reasoning_col, reasoning_md)

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True,
        inbrowser=False,
        quiet=False,
        css="""
        #reasoning-panel { border-left: 2px solid #e0e0e0; padding-left: 1rem; }
        .example-btn { font-size: 0.85rem; }
        """,
    )


if __name__ == "__main__":
    main()
