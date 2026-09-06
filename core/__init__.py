"""
core —— FIP 知识推理系统的确定性多 Agent 流水线。

本包遵循「编排-执行-适配」思想，不依赖任何大语言模型，
所有推理均通过规则与 Neo4j 图查询完成。

目录结构：
- schemas.py   层间数据契约（dataclass / Enum）
- config.py    别名表 / 意图关键词 / 极性·置信度映射
- queries.py   五个 Cypher 查询模板
- db.py        Neo4j 连接与查询执行
- agents/      各 Agent 实现
- pipeline.py  流水线编排入口
"""

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

__version__ = "0.2.0"

__all__ = [
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
    "__version__",
]
