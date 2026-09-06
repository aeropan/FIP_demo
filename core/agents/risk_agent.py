"""core.agents.risk_agent —— 风险标记（RiskAgent）。"""

from __future__ import annotations

from core import config
from core.agents.base import Agent
from core.schemas import ReasoningGroup, RiskFlag, RiskKind


class RiskAgent(Agent):
    """标记低置信度关系，附注"证据有限，仅供参考"。

    设计原则：低置信度关系不回避，主动附注提示用户证据有限。
    负向极性（Negative）由输出层通过极性颜色标注，不在本层生成标记。
    """

    def run(self, groups: list[ReasoningGroup]) -> list[RiskFlag]:
        flags: list[RiskFlag] = []
        for group in groups:
            for idx, step in enumerate(group.steps):
                if step.confidence == "Low":
                    flags.append(
                        RiskFlag(
                            kind=RiskKind.LOW_CONFIDENCE,
                            note=config.LOW_CONFIDENCE_NOTE,
                            group_key=group.key,
                            step_index=idx,
                        )
                    )
        return flags
