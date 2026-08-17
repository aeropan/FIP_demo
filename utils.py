"""
FIP 知识推理系统 —— utils 兼容层。

本模块的功能已迁移至 core 包（config / queries / db / schemas / agents / pipeline）。
此处保留向后兼容的导出与薄封装，确保旧的 `from utils import ...` 引用不断。

新代码请直接使用：
    from core.pipeline import Pipeline
    from core import config, queries, db, schemas
"""

from __future__ import annotations

from typing import Any

from core.agents import (
    Agent,
    BoundaryAgent,
    EntityAgent,
    EvidenceAgent,
    GraphQueryAgent,
    IntentAgent,
    Orchestrator,
    ResponseAgent,
    RiskAgent,
)
from core.config import (
    ALIAS_MAP,
    ALIASES_BY_LENGTH_DESC,
    BOUNDARY_MESSAGE,
    CLARIFICATION_LABELS,
    CLARIFY_THRESHOLD,
    CONFIDENCE_COLOR,
    INTENT_KEYWORDS,
    INTENT_KEYWORD_WEIGHT,
    LOW_CONFIDENCE_NOTE,
    POLARITY_COLOR,
    RISK_DEFAULT_DRUG,
)
from core.db import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME, run_query, test_connection
from core.pipeline import Pipeline
from core.queries import (
    CONCEPT_QUERY,
    DIAGNOSIS_QUERY,
    GENERAL_QUERY,
    INTENT_TO_QUERY,
    RISK_QUERY,
    TREATMENT_QUERY,
    get_query_template,
)
from core.schemas import (
    AgentResponse,
    BoundaryReason,
    ClarificationOption,
    Intent,
    IntentResult,
    QueryContext,
    ReasoningGroup,
    ReasoningStep,
    ResponseStatus,
    RiskFlag,
    RiskKind,
)


# ---------------------------------------------------------------------------
# 薄封装：保留最初需求中的函数名与返回格式，向后兼容
# ---------------------------------------------------------------------------
def resolve_entities(user_input: str) -> list[str]:
    """兼容封装：实体解析（委托 EntityAgent）。返回标准实体名列表。"""
    return EntityAgent().run(user_input)


def detect_intent(user_input: str) -> dict[str, Any]:
    """兼容封装：意图识别（委托 IntentAgent）。

    返回旧版字典格式：
        {"intent": str|None, "need_clarify": bool, "scores": {...},
         可选 "candidates": [str, ...]}
    """
    result = IntentAgent().run(user_input)
    data: dict[str, Any] = {
        "intent": result.intent.value if result.intent else None,
        "need_clarify": result.need_clarify,
        "scores": result.scores,
    }
    if result.need_clarify:
        data["candidates"] = [c.value for c in result.candidates]
    return data


def get_clarification_options(candidates: list[str]) -> list[dict[str, str]]:
    """兼容封装：将候选意图标识转换为澄清按钮选项（旧版 dict 格式）。"""
    options: list[dict[str, str]] = []
    for key in candidates:
        label = CLARIFICATION_LABELS.get(key)
        if label:
            options.append({"label": label, "value": f"intent:{key}"})
    return options


def normalize_entities_for_intent(intent: str | Intent, entities: list[str]) -> list[str]:
    """兼容封装：risk 意图缺省药物时兜底为 GS-441524。"""
    intent_key = intent.value if isinstance(intent, Intent) else intent
    if intent_key == "risk" and not entities:
        return list(RISK_DEFAULT_DRUG)
    return list(entities)


__all__ = [
    # 薄封装
    "resolve_entities",
    "detect_intent",
    "get_clarification_options",
    "normalize_entities_for_intent",
    # 模板与映射
    "CONCEPT_QUERY",
    "DIAGNOSIS_QUERY",
    "TREATMENT_QUERY",
    "RISK_QUERY",
    "GENERAL_QUERY",
    "INTENT_TO_QUERY",
    "get_query_template",
    # 数据访问
    "run_query",
    "test_connection",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
    # 配置
    "ALIAS_MAP",
    "ALIASES_BY_LENGTH_DESC",
    "INTENT_KEYWORDS",
    "INTENT_KEYWORD_WEIGHT",
    "CLARIFY_THRESHOLD",
    "CLARIFICATION_LABELS",
    "RISK_DEFAULT_DRUG",
    "POLARITY_COLOR",
    "CONFIDENCE_COLOR",
    "BOUNDARY_MESSAGE",
    "LOW_CONFIDENCE_NOTE",
    # Agent 与 Pipeline
    "Pipeline",
    "Agent",
    "IntentAgent",
    "EntityAgent",
    "Orchestrator",
    "GraphQueryAgent",
    "EvidenceAgent",
    "RiskAgent",
    "ResponseAgent",
    "BoundaryAgent",
    # schemas
    "AgentResponse",
    "BoundaryReason",
    "ClarificationOption",
    "Intent",
    "IntentResult",
    "QueryContext",
    "ReasoningGroup",
    "ReasoningStep",
    "ResponseStatus",
    "RiskFlag",
    "RiskKind",
]
