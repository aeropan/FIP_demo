"""core.pipeline —— 流水线编排入口。"""

from __future__ import annotations

from core.agents import (
    BoundaryAgent,
    EntityAgent,
    EvidenceAgent,
    GraphQueryAgent,
    IntentAgent,
    Orchestrator,
    ResponseAgent,
    RiskAgent,
)
from core.providers.factory import create_provider, get_graph_provider
from core.schemas import (
    AgentResponse,
    Intent,
    PipelineTrace,
    ResponseStatus,
    TraceStep,
)

# 完整链路元信息：步骤 id、中文名、对应 Agent 类名（边界处理为第 8 步，单独处理）
_PIPELINE_STAGES = [
    (1, "实体解析", "EntityAgent"),
    (2, "意图识别", "IntentAgent"),
    (3, "任务分配", "Orchestrator"),
    (4, "图查询", "GraphQueryAgent"),
    (5, "证据加工", "EvidenceAgent"),
    (6, "风险标记", "RiskAgent"),
    (7, "响应生成", "ResponseAgent"),
]


def _parse_composite_input(user_input: str) -> tuple[Intent, list[str]] | None:
    """解析澄清按钮回传的复合输入。

    格式：intent:{意图}[|entities:{实体1},{实体2}]
    返回 (intent, entities)；非复合输入（不以 "intent:" 开头）返回 None。
    """
    text = user_input.strip()
    if not text.startswith("intent:"):
        return None

    intent_str: str | None = None
    entities: list[str] = []

    for part in text.split("|"):
        part = part.strip()
        if part.startswith("intent:"):
            intent_str = part[len("intent:"):].strip()
        elif part.startswith("entities:"):
            raw = part[len("entities:"):].strip()
            if raw:
                entities = [e.strip() for e in raw.split(",") if e.strip()]

    if intent_str is None:
        return None
    try:
        intent = Intent(intent_str)
    except ValueError:
        return None
    return intent, entities


class Pipeline:
    """确定性多 Agent 流水线，串起语义识别 → 任务分配 → 决策 → 证据加工 → 输出。

    关键约定（与 core.schemas 文档一致）：
    - 实体解析结果为空 → 若意图明确（非 general）且传入上下文实体则继承，否则返回边界话术；
    - 意图不明确 → 返回澄清候选（选项 value 编码实体，点击后可恢复上下文）；
    - 输入为复合格式（intent:...|entities:...）→ 跳过实体/意图解析直接执行；
    - 识别为 meta 意图（系统自身意图）→ 跳过实体解析与图查询，直接返回预设回复，
      trace 中实体解析 / 图查询标记为 skipped（不触发边界处理）；
    - 图谱无路径 → 返回边界话术；
    - 查询异常 → 返回 error。
    """

    def __init__(self) -> None:
        self.entity_agent = EntityAgent()
        self.intent_agent = IntentAgent()
        self.orchestrator = Orchestrator()
        self.graph_agent = GraphQueryAgent()
        self.evidence_agent = EvidenceAgent()
        self.risk_agent = RiskAgent()
        self.response_agent = ResponseAgent()
        self.boundary_agent = BoundaryAgent()
        # 图数据提供者：根据 GRAPH_BACKEND 选择本地 NetworkX 或 Neo4j 后端，
        # 供 GraphQueryAgent 调用（默认 local，无需连接 Neo4j）。
        self.graph_provider = get_graph_provider()

    def run(
        self,
        user_input: str,
        context_entities: list[str] | None = None,
        backend: str = "local",
    ) -> AgentResponse:
        """执行一次完整推理，返回统一响应结构（不携带 trace）。

        context_entities 为上一轮成功解析的实体（上下文），本轮实体解析为空时用于继承。
        backend 为本次查询使用的数据源（"local" / "neo4j"），默认本地；
        仅影响本次调用，不修改全局 GRAPH_BACKEND 配置。
        """
        response, _ = self.run_with_trace(user_input, context_entities, backend=backend)
        return response

    def run_with_trace(
        self,
        user_input: str,
        context_entities: list[str] | None = None,
        backend: str = "local",
    ) -> tuple[AgentResponse, PipelineTrace]:
        """执行一次完整推理，同时返回统一响应与执行轨迹。

        context_entities 为上一轮成功解析的实体（上下文）；本轮实体解析为空且
        意图明确（非 general）时继承该上下文，实现连续对话的实体省略补全。
        backend 为本次查询使用的数据源（"local" / "neo4j"），默认本地。
        """
        trace = PipelineTrace(user_input=user_input, input_type="普通文本")
        context_entities = context_entities or []

        # 0. 复合输入识别：澄清按钮回传（intent:...|entities:...）
        parsed = _parse_composite_input(user_input)
        if parsed is not None:
            intent, entities = parsed
            trace.input_type = "复合澄清输入"
            trace.steps.append(
                TraceStep(
                    step_id=1,
                    step_name="实体解析",
                    agent="EntityAgent",
                    status="skipped",
                    input_summary="",
                    output_summary="",
                    skip_reason=f"复合澄清输入已指定实体：{', '.join(entities) if entities else '（无）'}",
                )
            )
            trace.steps.append(
                TraceStep(
                    step_id=2,
                    step_name="意图识别",
                    agent="IntentAgent",
                    status="skipped",
                    input_summary="",
                    output_summary="",
                    skip_reason=f"复合澄清输入已指定意图：{intent.value}",
                )
            )
            return self._run_with_intent(intent, entities, trace, backend=backend)

        # 1. 意图识别（优先执行，用于 emergency / meta 意图短路判断）
        intent_result = self.intent_agent.run(user_input)

        # --- emergency 意图短路（最高优先级）：跳过实体解析与图查询，直接返回就医提示 ---
        if intent_result.intent == Intent.EMERGENCY:
            trace.steps.append(
                TraceStep(
                    step_id=2,
                    step_name="意图识别",
                    agent="IntentAgent",
                    status="success",
                    input_summary=f"用户输入：{user_input}",
                    output_summary="识别为紧急求助",
                    detail={"scores": intent_result.scores},
                )
            )
            trace.steps.append(
                TraceStep(
                    step_id=1,
                    step_name="实体解析",
                    agent="EntityAgent",
                    status="skipped",
                    input_summary=f"用户输入：{user_input}",
                    output_summary="",
                    skip_reason="紧急场景，直接返回就医提示",
                )
            )
            trace.steps.append(
                TraceStep(
                    step_id=4,
                    step_name="图查询",
                    agent="GraphQueryAgent",
                    status="skipped",
                    input_summary="",
                    output_summary="",
                    skip_reason="紧急场景，直接返回就医提示",
                )
            )
            response = self.response_agent.generate_emergency_response()
            trace.steps.append(
                TraceStep(
                    step_id=7,
                    step_name="响应生成",
                    agent="ResponseAgent",
                    status="success",
                    input_summary="紧急求助",
                    output_summary="返回立即就医提示",
                    detail={"summary": response.summary},
                )
            )
            return response, trace

        # --- meta 意图短路：跳过实体解析与图查询，直接生成预设回复 ---
        if intent_result.intent == Intent.META:
            trace.steps.append(
                TraceStep(
                    step_id=2,
                    step_name="意图识别",
                    agent="IntentAgent",
                    status="success",
                    input_summary=f"用户输入：{user_input}",
                    output_summary="识别为 meta 意图",
                    detail={
                        "scores": intent_result.scores,
                        "meta_subtype": intent_result.meta_subtype,
                    },
                )
            )
            trace.steps.append(
                TraceStep(
                    step_id=1,
                    step_name="实体解析",
                    agent="EntityAgent",
                    status="skipped",
                    input_summary=f"用户输入：{user_input}",
                    output_summary="",
                    skip_reason="meta 意图无需实体解析",
                )
            )
            trace.steps.append(
                TraceStep(
                    step_id=4,
                    step_name="图查询",
                    agent="GraphQueryAgent",
                    status="skipped",
                    input_summary="",
                    output_summary="",
                    skip_reason="meta 意图无需图查询",
                )
            )
            response = self.response_agent.generate_meta_response(intent_result.meta_subtype)
            meta_label = {
                "identity": "返回系统自我介绍",
                "capability": "返回能力说明",
                "usage": "返回使用引导",
                "greeting": "返回问候引导",
            }.get(intent_result.meta_subtype or "", "返回问候引导")
            trace.steps.append(
                TraceStep(
                    step_id=7,
                    step_name="响应生成",
                    agent="ResponseAgent",
                    status="success",
                    input_summary=f"meta 子场景：{intent_result.meta_subtype or '（未识别）'}",
                    output_summary=meta_label,
                    detail={"summary": response.summary, "meta_subtype": response.meta_subtype},
                )
            )
            return response, trace

        # 2. 实体解析（meta 已短路返回，以下仅非 meta 流程，保持原逻辑不变）
        entities = self.entity_agent.run(user_input)

        # 3. 实体为空 → 判断是否继承上一轮上下文实体
        if not entities:
            intent = intent_result.intent
            # 继承条件：意图明确（非 general、非 None）+ 上下文实体非空
            if intent is not None and intent != Intent.GENERAL and context_entities:
                entities = list(context_entities)
                entity_output = f"未解析到实体，继承上一轮实体：{', '.join(entities)}"
                entity_detail: dict = {"entities": entities, "inherited": True}
            else:
                entity_output = "未解析到实体"
                entity_detail = {"entities": []}
        else:
            entity_output = f"解析到实体：{', '.join(entities)}"
            entity_detail = {"entities": list(entities)}

        trace.steps.append(
            TraceStep(
                step_id=1,
                step_name="实体解析",
                agent="EntityAgent",
                status="success",
                input_summary=f"用户输入：{user_input}",
                output_summary=entity_output,
                detail=entity_detail,
            )
        )
        trace.steps.append(
            TraceStep(
                step_id=2,
                step_name="意图识别",
                agent="IntentAgent",
                status="success",
                input_summary=f"用户输入：{user_input}",
                output_summary=(
                    f"识别意图：{intent_result.intent.value}"
                    if intent_result.intent
                    else "意图不明确，需澄清"
                ),
                detail={
                    "scores": intent_result.scores,
                    "candidates": [c.value for c in intent_result.candidates],
                },
            )
        )

        # 4. 实体仍为空（未继承）→ 边界兜底
        if not entities:
            self._add_skipped(trace, 3, 7, "实体解析为空")
            self._add_boundary(trace, "实体解析为空", "实体缺失，返回知识边界提示", "no_entities")
            return self.boundary_agent.no_entities(), trace

        # 5. 意图不明确 → 澄清
        if intent_result.need_clarify:
            self._add_skipped(trace, 3, 7, "意图不明确，等待用户澄清")
            self._add_boundary(trace, "意图不明确", "返回澄清候选选项", "clarify")
            return self.boundary_agent.clarify(intent_result, entities), trace

        intent = intent_result.intent
        assert intent is not None  # need_clarify=False 时 intent 必非 None

        return self._run_with_intent(intent, entities, trace, backend=backend)

    def _run_with_intent(
        self, intent: Intent, entities: list[str], trace: PipelineTrace, backend: str = "local"
    ) -> tuple[AgentResponse, PipelineTrace]:
        """从已知意图 + 实体继续执行：任务分配 → 决策 → 证据加工 → 输出。"""
        # 3. 任务分配：选模板 + 实体兜底
        context = self.orchestrator.run(intent, entities)
        trace.steps.append(
            TraceStep(
                step_id=3,
                step_name="任务分配",
                agent="Orchestrator",
                status="success",
                input_summary=f"意图：{intent.value}；实体：{', '.join(context.entities) if context.entities else '（无）'}",
                output_summary=f"选定查询模板：{intent.value.upper()}_QUERY",
                detail={"intent": intent.value, "entities": list(context.entities), "template": context.template},
            )
        )

        # 4. 图查询：按本次 backend 创建 Provider 实例并执行（失败则记 failed 并返回 error）
        # 使用 create_provider(backend) 而非 self.graph_provider，确保会话内可自由切换数据源，
        # 且不修改全局 GRAPH_BACKEND 配置；meta / emergency 等已在前面短路，不会到达此处。
        try:
            provider = create_provider(backend)
            steps = self.graph_agent.run(provider, context)
        except Exception as exc:  # noqa: BLE001
            error_msg = str(exc)
            trace.steps.append(
                TraceStep(
                    step_id=4,
                    step_name="图查询",
                    agent="GraphQueryAgent",
                    status="failed",
                    input_summary=f"执行图查询（实体：{', '.join(context.entities) if context.entities else '（无）'}）",
                    output_summary=f"查询异常：{error_msg}",
                    detail={"error": error_msg},
                )
            )
            self._add_skipped(trace, 5, 7, "图查询失败")
            response = AgentResponse(
                status=ResponseStatus.ERROR,
                error_message=error_msg,
                entities=list(entities),
                intent=intent,
            )
            return response, trace

        trace.steps.append(
            TraceStep(
                step_id=4,
                step_name="图查询",
                agent="GraphQueryAgent",
                status="success",
                input_summary=f"执行图查询（实体：{', '.join(context.entities) if context.entities else '（无）'}）",
                output_summary=f"命中 {len(steps)} 条关系",
                detail={"steps": [self._step_to_dict(s) for s in steps]},
            )
        )

        # 无路径 → 边界兜底
        if not steps:
            self._add_skipped(trace, 5, 7, "图查询未命中路径")
            self._add_boundary(trace, "图查询命中 0 条", "未找到相关路径，返回边界提示", "no_path")
            return self.boundary_agent.no_path(entities, intent), trace

        # 5. 证据加工：分组
        groups = self.evidence_agent.run(intent, steps)
        trace.steps.append(
            TraceStep(
                step_id=5,
                step_name="证据加工",
                agent="EvidenceAgent",
                status="success",
                input_summary=f"{len(steps)} 条关系",
                output_summary=f"分组：{'、'.join(f'{g.label} {len(g.steps)} 条' for g in groups)}",
                detail={"groups": [{"key": g.key, "label": g.label, "count": len(g.steps)} for g in groups]},
            )
        )

        # 6. 风险标记
        risks = self.risk_agent.run(groups)
        trace.steps.append(
            TraceStep(
                step_id=6,
                step_name="风险标记",
                agent="RiskAgent",
                status="success",
                input_summary=f"{len(groups)} 组证据",
                output_summary=(f"识别到 {len(risks)} 个低置信度风险" if risks else "未发现低置信度关系"),
                detail={
                    "risks": [
                        {"kind": r.kind.value, "group_key": r.group_key, "step_index": r.step_index, "note": r.note}
                        for r in risks
                    ]
                },
            )
        )

        # 7. 响应生成
        response = self.response_agent.run(intent, groups, risks, entities)
        trace.steps.append(
            TraceStep(
                step_id=7,
                step_name="响应生成",
                agent="ResponseAgent",
                status="success",
                input_summary=f"{len(groups)} 组证据，{len(risks)} 个风险",
                output_summary=response.summary,
                detail={"summary": response.summary, "cards": response.cards},
            )
        )

        return response, trace

    @staticmethod
    def _add_skipped(
        trace: PipelineTrace, start_id: int, end_id: int, reason: str
    ) -> None:
        """批量填充 start_id~end_id 区间内的步骤为 skipped（附原因）。"""
        for step_id, name, agent in _PIPELINE_STAGES:
            if start_id <= step_id <= end_id:
                trace.steps.append(
                    TraceStep(
                        step_id=step_id,
                        step_name=name,
                        agent=agent,
                        status="skipped",
                        input_summary="",
                        output_summary="",
                        skip_reason=reason,
                    )
                )

    @staticmethod
    def _add_boundary(
        trace: PipelineTrace, input_summary: str, output_summary: str, reason: str
    ) -> None:
        """追加第 8 步「边界处理」（success）。"""
        trace.steps.append(
            TraceStep(
                step_id=8,
                step_name="边界处理",
                agent="BoundaryAgent",
                status="success",
                input_summary=input_summary,
                output_summary=output_summary,
                detail={"reason": reason},
            )
        )

    @staticmethod
    def _step_to_dict(step) -> dict:
        """把 ReasoningStep 转成可 JSON 序列化的字典。"""
        return {
            "source": step.source,
            "rel": step.rel,
            "target": step.target,
            "polarity": step.polarity,
            "confidence": step.confidence,
            "evidence": step.evidence,
        }
