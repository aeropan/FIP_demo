"""collect_seed.py —— 一键采集 3 组 system_default 默认对话（含真实多轮回答 + 完整链路）。

做法：直接调用后端确定性 Pipeline.run_with_trace，对预置的多轮提问序列跑一遍，
把每轮的「用户提问 → 真实回答 + 意图 + 执行轨迹（PipelineTrace）」连同多轮结构
落盘为 asset/seed_conversations.json。前端 loadHistory 在「首次/清 cookie」时读取
该数组播种 3 条 system_default 对话（点击即可查看完整多轮 + 每轮轨迹）。

- 多轮实体继承：上一轮解析到的实体作为下一轮的 context_entities 传入，还原真实连贯对话。
- 数组顺序即 [组1, 组2, 组3]，前端正序遍历 + insertBefore(firstChild) → 组1 显示在最下方。
- backend 默认 local（NetworkX 本地镜像，不连 Neo4j）。
"""

import sys
import os
import json
from datetime import datetime
from dataclasses import asdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from core.pipeline import Pipeline  # noqa: E402

# 3 组对话，每组按对话顺序排列的多轮用户提问（顺序即 1→2→3）
GROUPS = [
    # 组1
    [
        "我的猫肚子大，可能是传腹吗？",
        "猫发热怎么办？",
        "猫快不行了怎么办？",
    ],
    # 组2
    [
        "猫传腹怎么诊断？",
        "湿性FIP怎么治？",
        "有什么药能治传腹？",
        "GS-441524有副作用吗？",
        "传腹要和哪些病区分？",
    ],
    # 组3
    [
        "腹水是传腹的特征吗？",
        "血管通透性增加是传腹的特征吗？",
        "白球比0.5是传腹吗",
        "什么会影响传腹康复？",
        "谢谢",
    ],
]


def trace_to_dict(trace):
    """PipelineTrace → 前端 renderTrace 期望的 JSON 结构（逐字段一致）。"""
    return {
        "user_input": trace.user_input,
        "input_type": trace.input_type,
        "steps": [asdict(s) for s in trace.steps],
    }


def main():
    pipe = Pipeline()
    out = []
    for gi, questions in enumerate(GROUPS, start=1):
        ctx = []
        msgs = []
        last_trace = None
        for qi, q in enumerate(questions, start=1):
            resp, trace = pipe.run_with_trace(q, ctx if ctx else None, backend="local")
            # user 消息
            msgs.append({"role": "user", "text": q})
            # bot 消息：回答文本取 summary / boundary_hint；意图；完整 trace
            bot_text = resp.summary or resp.boundary_hint or ""
            intent = resp.intent.value if resp.intent else None
            bt = trace_to_dict(trace)
            msgs.append(
                {"role": "bot", "text": bot_text, "intent": intent, "trace": bt}
            )
            last_trace = bt
            # 继承实体到下一轮（仅当本轮解析到实体）
            if resp.entities:
                ctx = list(resp.entities)
            print(
                f"  [组{gi} 轮{qi}] intent={intent} status={resp.status.value} "
                f"entities={resp.entities} steps={len(trace.steps)}"
            )
        convo = {
            "id": f"seed_{gi}",
            "kind": "system_default",
            "title": questions[0],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "msgs": msgs,
            "contextEntities": [],
            "lastTrace": last_trace,
        }
        out.append(convo)
        print(f"组{gi} 完成：{len(msgs)} 条消息")

    dest = os.path.join(HERE, "data", "seed_conversations.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"已写入 {len(out)} 组默认对话 -> {dest}")


if __name__ == "__main__":
    main()
