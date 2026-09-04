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
    ReasoningGroup,
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

# 细分意图（精准度优化）：识别到这些意图时，绕过通用模板，直接调用 Provider
# 专用查询方法 + ResponseAgent 专用结论式回复，而非走 EvidenceAgent 分组路径。
_SPECIAL_INTENTS = {
    Intent.DIAGNOSIS_INQUIRY,
    Intent.SYMPTOM_FEATURE,
    Intent.DIAGNOSTIC_TEST,
    Intent.RISK_FACTORS,
    Intent.DIFFERENTIAL_DIAGNOSIS,
    Intent.DRUG_INFO,
    Intent.DISEASE_FEATURES,
}

# 细分意图 → 轨迹面板中文名称（意图识别 / 响应生成步骤显示用）
_INTENT_DISPLAY_NAME = {
    Intent.DIAGNOSIS_INQUIRY: "诊断可能性判断",
    Intent.SYMPTOM_FEATURE: "特征确认",
    Intent.DIAGNOSTIC_TEST: "指标解读",
    Intent.RISK_FACTORS: "风险因素查询",
    Intent.DIFFERENTIAL_DIAGNOSIS: "鉴别诊断",
    Intent.DRUG_INFO: "药物关联查询",
    Intent.DISEASE_FEATURES: "疾病特征列举",
}


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

        # 疾病特征列举的「主语歧义」智能改派：意图识别在实体解析之前、纯关键词
        # 无法区分「疾病主语」（传腹的特征是什么）与「症状主语」（腹水的特征是什么），
        # 两者都含「特征是什么」。若识别为 disease_features 但解析到的实体均非 FIP
        # 疾病节点（即主语其实是症状/指标），则改派回 symptom_feature，避免反向查询
        # 落空返回边界话术。
        if (
            intent_result.intent == Intent.DISEASE_FEATURES
            and entities
            and not any(
                ("猫传染性腹膜炎" in e) or ("FIP" in e) for e in entities
            )
        ):
            intent_result.intent = Intent.SYMPTOM_FEATURE

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
                    f"识别为{_INTENT_DISPLAY_NAME[intent_result.intent]}（{intent_result.intent.value}）"
                    if intent_result.intent in _SPECIAL_INTENTS
                    else f"识别意图：{intent_result.intent.value}"
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

        # 细分意图：专用查询 + 专用结论式回复（绕过通用模板与证据分组）
        if intent in _SPECIAL_INTENTS:
            return self._run_with_special_intent(intent, entities, trace, backend=backend)

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

    def _run_with_special_intent(
        self, intent: Intent, entities: list[str], trace: PipelineTrace, backend: str = "local"
    ) -> tuple[AgentResponse, PipelineTrace]:
        """细分意图专用路径：Provider 专用查询 + ResponseAgent 结论式回复。

        与 _run_with_intent 的区别：
        - 跳过 Orchestrator 通用模板与 EvidenceAgent 分组，直接调用 Provider 的
          专用查询方法（query_<intent>）获取 ReasoningStep 列表；
        - 直接调用 ResponseAgent 对应的 generate_<intent>_response 组装结论式回复；
        - 风险因素（risk_factors）为全局查询，不按实体过滤（传 []），
          以返回全部影响康复/复发的因素。
        """
        # 3. 任务分配：专用意图绕过通用模板，直接调用 Provider 专用查询方法
        trace.steps.append(
            TraceStep(
                step_id=3,
                step_name="任务分配",
                agent="Orchestrator",
                status="success",
                input_summary=f"意图：{intent.value}；实体：{', '.join(entities) if entities else '（无）'}",
                output_summary=f"选择查询方法：query_{intent.value}",
                detail={"intent": intent.value, "entities": list(entities), "mode": "specialized"},
            )
        )

        # 4. 图查询：调用对应专用查询方法
        used_disease_indicators = False
        try:
            provider = create_provider(backend)
            if intent == Intent.DIAGNOSIS_INQUIRY:
                steps = provider.query_diagnosis_inquiry(entities)
            elif intent == Intent.SYMPTOM_FEATURE:
                steps = provider.query_symptom_feature(entities)
            elif intent == Intent.DIAGNOSTIC_TEST:
                # 阶段二：优先正向（具体指标 → 疾病）；仅当正向为空且实体含疾病时，
                # 回退反向（疾病 → 指标）用于「传腹有哪些指标异常」这类泛指问法。
                # 这样「白球比0.5是传腹吗」仍返回针对性单条结论，而非全量指标列表。
                steps = provider.query_diagnostic_test(entities)
                if not steps and any(("猫传染性腹膜炎" in e) or ("FIP" in e) for e in entities):
                    steps = provider.query_disease_indicators(entities)
                    used_disease_indicators = bool(steps)
            elif intent == Intent.RISK_FACTORS:
                # 全局风险因素查询：不按实体过滤，返回全部影响因素
                steps = provider.query_risk_factors([])
            elif intent == Intent.DIFFERENTIAL_DIAGNOSIS:
                steps = provider.query_differential_diagnosis(entities)
            elif intent == Intent.DRUG_INFO:
                steps = provider.query_drug_info(entities)
            elif intent == Intent.DISEASE_FEATURES:
                steps = provider.query_disease_features(entities)
            else:  # pragma: no cover - 调用方已用 _SPECIAL_INTENTS 过滤
                steps = []
        except Exception as exc:  # noqa: BLE001
            error_msg = str(exc)
            trace.steps.append(
                TraceStep(
                    step_id=4,
                    step_name="图查询",
                    agent="GraphQueryAgent",
                    status="failed",
                    input_summary=f"执行专用查询（实体：{', '.join(entities) if entities else '（无）'}）",
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

        # 多跳推理分流：仅 symptom_feature / diagnosis_inquiry，直接查询为空时，
        # 尝试通过多跳路径（A→B→C）间接推理（A 为症状/指标实体，C 为 FIP 实体）。
        multihop = None  # (steps, source, target) 或 None
        if not steps and intent in (Intent.SYMPTOM_FEATURE, Intent.DIAGNOSIS_INQUIRY, Intent.DIAGNOSTIC_TEST):
            multihop = self._resolve_multihop(provider, entities)

        trace.steps.append(
            TraceStep(
                step_id=4,
                step_name="图查询",
                agent="GraphQueryAgent",
                status="success",
                input_summary=f"执行专用查询（实体：{', '.join(entities) if entities else '（无）'}）",
                output_summary=(
                    f"直接查询无结果，尝试多跳路径，命中 {len(multihop[0])} 条"
                    if multihop is not None
                    else f"命中 {len(steps)} 条关系"
                ),
                detail={
                    "steps": [
                        self._step_to_dict(s) for s in (multihop[0] if multihop is not None else steps)
                    ]
                },
            )
        )

        # 直接查询与多跳均无结果 → 边界兜底
        if not steps and multihop is None:
            self._add_skipped(trace, 5, 7, "图查询未命中路径（含多跳）")
            self._add_boundary(trace, "图查询命中 0 条", "未找到相关路径，返回边界提示", "no_path")
            return self.boundary_agent.no_path(entities, intent), trace

        # 实际用于后续风险标记 / 回复生成的步骤：多跳命中时用多跳路径，否则用直接查询
        use_steps = multihop[0] if multihop is not None else steps

        # 5. 证据加工：专用意图由 ResponseAgent 直接组装结论，无需证据分组
        trace.steps.append(
            TraceStep(
                step_id=5,
                step_name="证据加工",
                agent="EvidenceAgent",
                status="skipped",
                input_summary="",
                output_summary="",
                skip_reason="该意图无需证据分组",
            )
        )

        # 6. 风险标记：保持原逻辑，检查返回步骤中的低置信度关系
        risk_group = ReasoningGroup(key="specialized", label="专用结论", steps=use_steps)
        risks = self.risk_agent.run([risk_group])
        if risks:
            trace.steps.append(
                TraceStep(
                    step_id=6,
                    step_name="风险标记",
                    agent="RiskAgent",
                    status="success",
                    input_summary=f"{len(use_steps)} 条关系",
                    output_summary=f"识别到 {len(risks)} 个风险标记",
                    detail={
                        "risks": [
                            {"kind": r.kind.value, "group_key": r.group_key, "step_index": r.step_index, "note": r.note}
                            for r in risks
                        ]
                    },
                )
            )
        else:
            trace.steps.append(
                TraceStep(
                    step_id=6,
                    step_name="风险标记",
                    agent="RiskAgent",
                    status="skipped",
                    input_summary=f"{len(use_steps)} 条关系",
                    output_summary="",
                    skip_reason="无风险标记",
                )
            )

        # 7. 响应生成：调用对应专用结论式回复（多跳命中时生成间接关联回复）
        if multihop is not None:
            mh_source, mh_target = multihop[1], multihop[2]
            response = self.response_agent.generate_multihop_response(
                mh_source, mh_target, use_steps, intent=intent
            )
            response_action = "生成间接关联回复"
        elif intent == Intent.DIAGNOSIS_INQUIRY:
            response = self.response_agent.generate_diagnosis_inquiry_response(use_steps, entities)
            response_action = f"生成{_INTENT_DISPLAY_NAME[intent]}回复"
        elif intent == Intent.SYMPTOM_FEATURE:
            response = self.response_agent.generate_symptom_feature_response(use_steps)
            response_action = f"生成{_INTENT_DISPLAY_NAME[intent]}回复"
        elif intent == Intent.DIAGNOSTIC_TEST:
            if used_disease_indicators:
                response = self.response_agent.generate_disease_indicators_response(use_steps, entities)
            else:
                response = self.response_agent.generate_diagnostic_test_response(use_steps)
            response_action = f"生成{_INTENT_DISPLAY_NAME[intent]}回复"
        elif intent == Intent.RISK_FACTORS:
            response = self.response_agent.generate_risk_factors_response(use_steps)
            response_action = f"生成{_INTENT_DISPLAY_NAME[intent]}回复"
        elif intent == Intent.DIFFERENTIAL_DIAGNOSIS:
            response = self.response_agent.generate_differential_diagnosis_response(use_steps)
            response_action = f"生成{_INTENT_DISPLAY_NAME[intent]}回复"
        elif intent == Intent.DISEASE_FEATURES:
            response = self.response_agent.generate_disease_features_response(use_steps, entities)
            response_action = f"生成{_INTENT_DISPLAY_NAME[intent]}回复"
        else:  # DRUG_INFO
            response = self.response_agent.generate_drug_info_response(use_steps)
            response_action = f"生成{_INTENT_DISPLAY_NAME[intent]}回复"

        # 统一回显实体（专用回复方法内部 entities 可能为空）
        response.entities = list(entities)

        trace.steps.append(
            TraceStep(
                step_id=7,
                step_name="响应生成",
                agent="ResponseAgent",
                status="success",
                input_summary=f"{len(use_steps)} 条关系",
                output_summary=response_action,
                detail={"summary": response.summary, "cards": response.cards},
            )
        )

        return response, trace

    @staticmethod
    def _resolve_multihop(
        provider, entities: list[str]
    ) -> tuple[list, str, str] | None:
        """尝试从已解析实体中找出「症状源 → FIP 目标」的多跳间接路径。

        仅当实体同时包含「非 FIP 实体（症状 / 指标源）」与「FIP 实体（目标）」时尝试；
        逐对 (source, target) 调用 provider.query_multihop_path，返回第一条命中的路径
        （steps, source, target）。无命中返回 None，交由上层回退到边界逻辑。
        """
        fip_entities = [e for e in entities if ("猫传染性腹膜炎" in e) or ("FIP" in e)]
        source_candidates = [e for e in entities if e not in fip_entities]
        if not fip_entities or not source_candidates:
            return None
        for source in source_candidates:
            for target in fip_entities:
                path = provider.query_multihop_path(source, target, max_hops=5)
                if path:
                    return path, source, target
        return None

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
