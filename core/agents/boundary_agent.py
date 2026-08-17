"""core.agents.boundary_agent —— 边界兜底（BoundaryAgent）。"""

from __future__ import annotations

from core import config
from core.agents.base import Agent
from core.schemas import (
    AgentResponse,
    BoundaryReason,
    ClarificationOption,
    Intent,
    IntentResult,
    ResponseStatus,
)


class BoundaryAgent(Agent):
    """在实体缺失 / 无路径 / 意图不明确时生成兜底响应。"""

    def no_entities(self) -> AgentResponse:
        """实体解析为空 → 知识边界（跳过意图识别与后续流程）。"""
        return AgentResponse(
            status=ResponseStatus.BOUNDARY,
            boundary_reason=BoundaryReason.NO_ENTITIES,
            boundary_hint=config.BOUNDARY_MESSAGE,
        )

    def no_path(self, entities: list[str], intent: Intent | None = None) -> AgentResponse:
        """图谱无可用路径 → 知识边界。"""
        return AgentResponse(
            status=ResponseStatus.BOUNDARY,
            boundary_reason=BoundaryReason.NO_PATH,
            boundary_hint=config.BOUNDARY_MESSAGE,
            entities=list(entities),
            intent=intent,
        )

    def clarify(self, intent_result: IntentResult, entities: list[str]) -> AgentResponse:
        """意图不明确 → 返回澄清候选（选项 value 编码当前实体以恢复上下文）。"""
        options = self._build_options(intent_result.candidates, entities)
        return AgentResponse(
            status=ResponseStatus.CLARIFY,
            intent=None,
            entities=list(entities),
            clarify_options=options,
        )

    @staticmethod
    def _build_options(
        candidates: list[Intent], entities: list[str]
    ) -> list[ClarificationOption]:
        options: list[ClarificationOption] = []
        for intent in candidates:
            label = config.CLARIFICATION_LABELS.get(intent.value)
            if label:
                value = f"intent:{intent.value}"
                if entities:
                    value += f"|entities:{','.join(entities)}"
                options.append(ClarificationOption(label=label, value=value))
        return options
