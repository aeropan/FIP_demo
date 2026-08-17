"""
FIP 知识推理系统 —— 命令行核心测试脚本。

用法：
    python test_core.py          # 进入交互式问答
    python test_core.py demo     # 运行一组内置示例（含边界情况）

流程：
    用户输入 → Pipeline.run → 打印 摘要 / 分组推理链 / 边界提示 / 澄清候选。
"""

from __future__ import annotations

import sys

from core import db
from core.pipeline import Pipeline
from core.schemas import ResponseStatus

# 内置示例（覆盖五个意图 + 一个边界情况）
SELF_TEST_CASES = [
    "猫传腹是怎么导致的？",  # concept：发病机制
    "猫发热怎么办",  # 边界：实体解析为空 → 知识边界提示
    "441有什么副作用？",  # risk：默认药物 GS-441524
    "猫传腹怎么诊断？",  # diagnosis：诊断流程
    "猫传腹怎么治疗？",  # treatment：治疗与预后
    "GS-441524",  # general：围绕实体一跳全量查询
]

_pipeline = Pipeline()


def print_response(response) -> None:
    """按 AgentResponse 的 status 分派打印。"""
    if response.status == ResponseStatus.BOUNDARY:
        print(f"【结果】{response.boundary_hint}")
        return

    if response.status == ResponseStatus.CLARIFY:
        print("【结果】需要澄清（多个意图得分接近）：")
        for opt in response.clarify_options:
            print(f"    - {opt.label}  →  {opt.value}")
        return

    # ok：打印摘要 + 分组推理链
    print(f"【结果】{response.summary}")
    for card in response.cards:
        print(f"\n  [{card['label']}]")
        for step in card["steps"]:
            mark = " [低置信度]" if step["flagged"] else ""
            print(
                f"    {step['source']} —{step['rel']}→ {step['target']}  "
                f"[{step['polarity']} · {step['confidence']}]{mark}"
            )
            if step["evidence"]:
                print(f"      依据：{step['evidence']}")


def run_once(question: str) -> None:
    """执行一次完整推理并打印结果。"""
    print(f"\n【问题】{question}")
    response = _pipeline.run(question)
    print(f"【意图】{response.intent.value if response.intent else '未确定'}")
    print(f"【实体】{response.entities if response.entities else '未解析到已知实体'}")
    print_response(response)


def main() -> None:
    """命令行入口：支持交互式输入与内置示例。"""
    conn = db.test_connection()
    if conn["ok"]:
        print("Neo4j 连接正常。")
    else:
        print(f"Neo4j 连接异常：{conn['error']}")
        print("（将无法执行图查询，但实体解析 / 意图识别仍可测试）")

    # 以 "demo" 作为参数运行时，先跑一遍内置示例
    if len(sys.argv) > 1 and sys.argv[1].lower() == "demo":
        print("\n===== 内置示例 =====")
        for case in SELF_TEST_CASES:
            run_once(case)
        print("\n===== 示例结束，进入交互模式 =====")

    print("\n输入问题开始（输入 exit / 退出 结束，输入 demo 运行示例）")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit", "退出", "q"):
            print("再见。")
            break
        if question.lower() in ("demo", "示例"):
            for case in SELF_TEST_CASES:
                run_once(case)
            continue

        run_once(question)


if __name__ == "__main__":
    main()
