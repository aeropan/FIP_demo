"""core.agents.graph_query_agent —— 图查询执行（GraphQueryAgent）。"""

from __future__ import annotations

from core import db
from core.agents.base import Agent
from core.schemas import QueryContext, ReasoningStep


class GraphQueryAgent(Agent):
    """执行 Cypher 查询，返回去重后的推理步骤列表。"""

    def run(self, context: QueryContext) -> list[ReasoningStep]:
        return db.run_query(context.template, context.entities)
