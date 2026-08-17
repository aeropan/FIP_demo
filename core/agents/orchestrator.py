"""core.agents.orchestrator —— 任务分配（Orchestrator）。"""

from __future__ import annotations

from core import config
from core.agents.base import Agent
from core.queries import get_query_template
from core.schemas import Intent, QueryContext


class Orchestrator(Agent):
    """根据意图选择查询模板，并处理实体兜底，产出 QueryContext。"""

    def run(self, intent: Intent, entities: list[str]) -> QueryContext:
        template = get_query_template(intent)

        # risk 意图未解析到药物实体时，回退到默认药物 GS-441524
        query_entities = list(entities)
        if intent == Intent.RISK and not query_entities:
            query_entities = list(config.RISK_DEFAULT_DRUG)

        return QueryContext(intent=intent, template=template, entities=query_entities)
