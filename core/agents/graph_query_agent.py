"""core.agents.graph_query_agent —— 图查询执行（GraphQueryAgent）。"""

from __future__ import annotations

from core.agents.base import Agent
from core.providers.base import GraphProvider
from core.schemas import Intent, QueryContext, ReasoningStep


class GraphQueryAgent(Agent):
    """根据意图调用统一 GraphProvider 接口执行图查询，返回推理步骤列表。

    不再直接依赖 core.db / core.queries，改为面向 GraphProvider 抽象，
    使本地 NetworkX 与 Neo4j 两种后端可无差别切换。
    """

    def run(self, provider: GraphProvider, context: QueryContext) -> list[ReasoningStep]:
        """按意图路由到 Provider 的对应查询方法。

        provider: 统一的图数据提供者实例（由 Pipeline 注入）。
        context:  查询上下文，提供意图与参数实体。

        返回去重后的推理步骤列表；非医学意图（meta / emergency 等）
        不经过图查询，返回空列表。
        """
        intent = context.intent
        entities = context.entities
        if intent == Intent.CONCEPT:
            return provider.query_concept()
        if intent == Intent.DIAGNOSIS:
            return provider.query_diagnosis()
        if intent == Intent.TREATMENT:
            return provider.query_treatment()
        if intent == Intent.RISK:
            return provider.query_risk(entities)
        if intent == Intent.GENERAL:
            return provider.query_general(entities)
        # 其他意图（meta / emergency）不含图查询，返回空
        return []
