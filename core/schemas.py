"""
core.schemas —— 层间数据契约。

定义 Pipeline 各层 Agent 之间传递的强类型数据结构。
所有 Agent 的输入输出都遵循本模块定义，便于单元测试与后续接入前端。

流水线关键约定（Pipeline 实现时必须遵循）：
1. 实体解析结果为空 → 直接返回 boundary（reason=NO_ENTITIES），
   跳过意图识别与后续查询流程。
2. 意图不明确（need_clarify）→ 返回 clarify（附 clarify_options）。
3. 查询无可用路径 → 返回 boundary（reason=NO_PATH）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Intent(str, Enum):
    """系统支持的五类意图。"""

    CONCEPT = "concept"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    RISK = "risk"
    GENERAL = "general"


class ResponseStatus(str, Enum):
    """Pipeline 最终响应的状态。"""

    OK = "ok"              # 正常返回推理链
    CLARIFY = "clarify"    # 意图不明确，需用户澄清
    BOUNDARY = "boundary"  # 知识边界（实体缺失 / 无路径）
    ERROR = "error"        # 异常


class BoundaryReason(str, Enum):
    """触发边界兜底的原因。"""

    NO_ENTITIES = "no_entities"  # 实体解析为空
    NO_PATH = "no_path"          # 图谱无可用路径


class RiskKind(str, Enum):
    """风险标记类型。"""

    LOW_CONFIDENCE = "low_confidence"    # 置信度 Low
    NEGATIVE = "negative"                 # 负向极性（不利结局 / 风险）
    CONTROVERSIAL = "controversial"       # 争议点（证据有限）


@dataclass
class ReasoningStep:
    """单条推理关系，对应知识图谱中的一条 RELATES 边。"""

    source: str
    rel: str
    target: str
    polarity: str = "Neutral"    # Positive / Negative / Neutral
    confidence: str = "Medium"   # High / Medium / Low
    evidence: str = ""


@dataclass
class IntentResult:
    """意图识别结果。"""

    intent: Intent | None = None
    need_clarify: bool = False
    candidates: list[Intent] = field(default_factory=list)
    scores: dict[str, int] = field(default_factory=dict)


@dataclass
class QueryContext:
    """查询上下文：意图 + 选定的 Cypher 模板 + 参数实体。"""

    intent: Intent
    template: str
    entities: list[str] = field(default_factory=list)


@dataclass
class ClarificationOption:
    """澄清按钮选项（供前端渲染）。

    value 为复合编码，格式：
        intent:{意图}
        intent:{意图}|entities:{实体1},{实体2}
    其中 entities 为触发澄清时已解析到的实体（逗号分隔），
    供用户点击按钮后恢复上下文并直接执行对应查询。
    """

    label: str
    value: str                  # 形如 "intent:risk|entities:GS-441524"


@dataclass
class RiskFlag:
    """低置信度 / 负向极性 / 争议点的风险标注。

    通过 group_key + step_index 定位到某个分组内的某条关系。
    """

    kind: RiskKind
    note: str = ""
    group_key: str = ""          # 所属分组键
    step_index: int = 0          # 分组内下标


@dataclass
class ReasoningGroup:
    """一组推理关系，供前端按主题分组展示。"""

    key: str                    # 分组键，如 "drug_treatment"
    label: str                  # 分组中文名，如 "药物治疗"
    steps: list[ReasoningStep] = field(default_factory=list)


@dataclass
class AgentResponse:
    """Pipeline 统一出口，前端只消费这一结构。"""

    status: ResponseStatus
    summary: str = ""                                        # 自然语言摘要
    groups: list[ReasoningGroup] = field(default_factory=list)
    cards: list[dict] = field(default_factory=list)          # 推理链卡片数据
    risks: list[RiskFlag] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)        # 回显解析出的实体
    intent: Intent | None = None
    boundary_reason: BoundaryReason | None = None
    boundary_hint: str | None = None                         # 边界话术
    clarify_options: list[ClarificationOption] = field(default_factory=list)
    error_message: str = ""                                  # 异常信息（status=error 时非空）


@dataclass
class TraceStep:
    """执行轨迹中的单个步骤（供前端分级展示：一级缩略 + 二级详情）。

    status 取值约定（字符串字面量，便于 JSON 序列化）：
        "success"  成功
        "skipped"  跳过（配合 skip_reason 说明原因）
        "failed"   失败
    """

    step_id: int                # 链路顺序 1~7，边界处理为 8
    step_name: str              # "实体解析"/"意图识别"/"任务分配"/"图查询"/"证据加工"/"风险标记"/"响应生成"/"边界处理"
    agent: str                  # 对应 Agent 类名，如 "EntityAgent"
    status: str                 # "success" / "skipped" / "failed"
    input_summary: str          # 一级缩略输入
    output_summary: str         # 一级缩略输出
    detail: Any = None          # 二级详情（结构化 dict/list，第一版前端文本渲染）
    skip_reason: str = ""       # 仅 status="skipped" 时非空


@dataclass
class PipelineTrace:
    """一次 Pipeline 执行的完整轨迹（供右侧栏展示）。"""

    user_input: str             # 原始输入
    input_type: str             # "普通文本" / "复合澄清输入"
    steps: list[TraceStep] = field(default_factory=list)
