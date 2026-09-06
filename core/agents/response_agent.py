"""core.agents.response_agent —— 输出组装（ResponseAgent）。"""

from __future__ import annotations

from core import config
from core.agents.base import Agent
from core.schemas import (
    AgentResponse,
    Intent,
    ReasoningGroup,
    ResponseStatus,
    RiskFlag,
)

# 确诊 FIP 节点集合（与 core.providers.local_graph_provider._FIP_CONFIRMED 保持一致，
# 用于 diagnosis_inquiry 在命中"疑似"步骤之外的兜底判断）。
_FIP_CONFIRMED = {
    "湿性猫传染性腹膜炎（湿性FIP）",
    "干性猫传染性腹膜炎（干性FIP）",
    "复发性猫传染性腹膜炎",
}

# 置信度展示排序权重（High > Medium > Low），用于"选置信度最高一条"。
_CONFIDENCE_RANK = {"High": 3, "Medium": 2, "Low": 1}


class ResponseAgent(Agent):
    """生成自然语言摘要与推理链卡片，组装最终 AgentResponse。

    摘要基于「意图 + 规则模板」，从分组的推理步骤（ReasoningGroup）中确定性提取
    关键信息（药物、疗程、风险因素、症状、筛查指标、金标准、疗效、风险事件等），
    不使用任何统计型表达（如「共 X 条」），不调用任何大模型。
    卡片为「渲染就绪」的结构化数据。
    """

    def run(
        self,
        intent: Intent,
        groups: list[ReasoningGroup],
        risks: list[RiskFlag],
        entities: list[str],
    ) -> AgentResponse:
        summary = self._build_summary(intent, groups, entities)
        cards = self._build_cards(groups, risks)
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=groups,
            cards=cards,
            risks=risks,
            entities=list(entities),
            intent=intent,
        )

    # ------------------------------------------------------------------
    # meta 意图：预设回复（不依赖图谱查询）
    # ------------------------------------------------------------------
    def generate_meta_response(self, meta_subtype: str | None) -> AgentResponse:
        """生成 meta 意图的预设回复。

        meta 意图不依赖图谱查询，直接根据子场景类型返回固定文案。
        子场景类型包括：
            identity   身份介绍
            capability 能力说明
            usage      使用引导
            greeting   问候响应
        """
        from core.schemas import ResponseStatus

        responses = {
            "identity": (
                "我是猫传腹知识推理助手，一个不依赖大模型的确定性问答系统。\n"
                "我会通过知识图谱展示完整的推理链，让每一步都有依据可查。"
            ),
            "capability": (
                "我可以回答猫传腹相关的问题，例如：\n"
                "· 猫传腹如何诊断？\n"
                "· 湿性FIP怎么治疗？\n"
                "· GS-441524有副作用吗？\n"
                "· 什么是猫传腹？\n"
                "并且会展示完整的推理路径、证据来源和置信度。"
            ),
            "usage": (
                "你可以直接在下方输入猫传腹相关问题，例如：\n"
                "“猫传腹如何诊断？”\n"
                "“湿性FIP怎么治？”\n"
                "我会给出回答，并展示推理链与执行轨迹。"
            ),
            "greeting": (
                "你好，我在这里。\n"
                "你可以尝试问我：\n"
                "“猫传腹如何诊断？”\n"
                "“湿性FIP怎么治疗？”\n"
                "我会展示完整的推理过程。"
            ),
            "farewell": "不客气，祝你和猫咪健康。如果还有其他问题，随时可以问我。",
        }

        summary = responses.get(
            meta_subtype or "",
            responses["greeting"],
        )

        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=[],
            risks=[],
            entities=[],
            intent=Intent.META,
            meta_subtype=meta_subtype,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    # ------------------------------------------------------------------
    # 紧急求助：预设回复（不依赖图谱查询，最高优先级）
    # ------------------------------------------------------------------
    def generate_emergency_response(self) -> AgentResponse:
        """生成 emergency 意图的预设回复。

        emergency 意图不依赖图谱查询，直接返回立即就医提示。
        """
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=(
                "请立即联系附近的兽医或前往最近的宠物医院。\n"
                "如果猫咪正在抽搐、呼吸困难、无法站立或已经失去意识，请不要等待。"
            ),
            groups=[],
            cards=[],
            risks=[],
            entities=[],
            intent=Intent.EMERGENCY,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    # ------------------------------------------------------------------
    # 细分意图：结论式回复（不依赖图谱分组，直接从 ReasoningStep 抽取）
    #
    # 以下六个方法接收 Provider 专用查询方法返回的 list[ReasoningStep]，
    # 基于规则生成具有明确结论的回答（不调用大模型）。回复中的关系类型与实体
    # 名称均来自图谱数据，不编造。
    # ------------------------------------------------------------------
    @staticmethod
    def _confidence_rank(step) -> int:
        """置信度展示排序权重（High > Medium > Low）。"""
        return _CONFIDENCE_RANK.get(getattr(step, "confidence", ""), 0)

    @staticmethod
    def _steps_to_cards(steps: list) -> list[dict]:
        """把 list[ReasoningStep] 渲染为与现有 _build_cards 一致的卡片结构。"""
        step_dicts = []
        for s in steps:
            step_dicts.append(
                {
                    "source": s.source,
                    "rel": s.rel,
                    "target": s.target,
                    "polarity": s.polarity,
                    "polarity_color": config.POLARITY_COLOR.get(s.polarity, "gray"),
                    "confidence": s.confidence,
                    "confidence_color": config.CONFIDENCE_COLOR.get(s.confidence, "gray"),
                    "evidence": s.evidence,
                    "flagged": False,
                }
            )
        return [{"key": "reasoning", "label": "推理链路", "steps": step_dicts}]

    def generate_diagnosis_inquiry_response(
        self, steps: list, entities: list[str]
    ) -> AgentResponse:
        """症状可能性判断：从步骤中找 表现为→疑似*，给出"可能"/"确诊"结论。"""
        suspected = [s for s in steps if s.rel == "表现为" and s.target.startswith("疑似")]
        if suspected:
            symptoms = self._dedup([s.source for s in suspected])
            types = self._dedup([s.target for s in suspected])
            detail = "；".join(f"{s.source}表现为{s.target}" for s in suspected)
            summary = (
                f"你提到的{'、'.join(symptoms)}，在现有知识图谱中与猫传腹"
                f"（尤其是{'、'.join(types)}）有关联。\n其中，{detail}。"
                f"\n建议进一步结合白球比、Rivalta试验等指标确诊。"
            )
        elif steps:
            # 命中确诊 FIP 直接关联（表现为 / 诊断于 → 确诊FIP）
            symptoms = self._dedup([s.source for s in steps])
            types = self._dedup([s.target for s in steps])
            summary = (
                f"你提到的{'、'.join(symptoms)}，在现有知识图谱中直接表现为"
                f"{'、'.join(types)}。\n建议结合白球比、Rivalta试验等进一步确诊。"
            )
        else:
            summary = (
                "根据当前知识库，你描述的症状暂未直接对应猫传腹的典型表现。"
                "建议咨询兽医进行完整检查。"
            )
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=list(entities),
            intent=Intent.DIAGNOSIS_INQUIRY,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_diagnosis_inquiry_guidance(self) -> AgentResponse:
        """诊断可能性判断（无具体症状/体征实体）：返回引导性回复。

        当用户只提到疾病（如「猫可能是传腹吗」）而未描述任何具体症状/体征时，
        图谱无法定位症状源实体，无法给出针对性关联，故引导用户补充观察信息。
        状态为 OK（非边界），因为已给出有效引导。
        """
        summary = (
            "猫传腹的确诊需要结合具体症状和检查。"
            "你观察到猫咪有哪些异常表现？比如发烧、肚子大、精神差、呼吸快等。"
        )
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=[],
            risks=[],
            entities=[],
            intent=Intent.DIAGNOSIS_INQUIRY,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_symptom_feature_response(self, steps: list) -> AgentResponse:
        """特征确认：选择置信度最高的一条 表现为/诊断于→确诊FIP/疑似*。"""
        if steps:
            best = max(steps, key=self._confidence_rank)
            summary = f"是的，{best.source}是{best.target}的典型{best.rel}。\n依据：{best.evidence}"
            if best.confidence in ("Medium", "Low"):
                summary += "\n证据有限，仅供参考。"
        else:
            summary = "当前知识库未显示该症状/指标与猫传腹存在直接特征关联。"
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=[],
            intent=Intent.SYMPTOM_FEATURE,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_diagnostic_test_response(self, steps: list) -> AgentResponse:
        """指标解读：提取指标与 FIP 的关联（表现为/诊断于 均覆盖）与依据。"""
        matched = [s for s in steps if s.rel in ("诊断于", "表现为")]
        if matched:
            best = max(matched, key=self._confidence_rank)
            summary = f"{best.source}在现有知识图谱中与{best.target}相关。\n依据：{best.evidence}"
            if best.target.startswith("疑似"):
                summary += "\n建议结合其他检查进一步确诊。"
        else:
            summary = "当前知识库未收录该指标的诊断信息，建议咨询兽医。"
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=[],
            intent=Intent.DIAGNOSTIC_TEST,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_risk_factors_response(self, steps: list) -> AgentResponse:
        """风险因素：按目标（结局）分组，列出 因素→结果（证据）。

        过滤掉"源实体为确诊FIP疾病节点"的步骤（如 湿性FIP→导致死亡），
        这类描述的是疾病自身预后，并非外部风险因素，避免误导用户。
        """
        if not steps:
            summary = "当前知识库暂无相关风险因素信息。"
        else:
            # 仅保留外部风险因素（源实体不是确诊FIP疾病节点）
            factor_steps = [s for s in steps if s.source not in _FIP_CONFIRMED]
            groups_map: dict[str, list] = {}
            for s in factor_steps:
                groups_map.setdefault(s.target, []).append(s)
            # 不利结局优先展示，康复置后
            priority = ["复发", "死亡", "复发风险", "血药浓度", "药物渗透", "康复"]
            ordered = sorted(
                groups_map.keys(),
                key=lambda t: next((i for i, p in enumerate(priority) if p in t), len(priority)),
            )
            lines = []
            for t in ordered:
                for s in groups_map[t]:
                    lines.append(f"· {s.source} → {s.rel}{t}（证据：{s.evidence}）")
            if lines:
                summary = (
                    "根据知识图谱，以下因素可能影响猫传腹的康复或复发：\n"
                    + "\n".join(lines)
                )
            else:
                summary = "当前知识库暂无相关风险因素信息。"
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=[],
            intent=Intent.RISK_FACTORS,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_differential_diagnosis_response(self, steps: list) -> AgentResponse:
        """鉴别诊断：提取 疑似*→影响→排除* 的排除疾病列表。"""
        matched = [
            s for s in steps
            if s.source.startswith("疑似") and s.rel == "影响" and s.target.startswith("排除")
        ]
        if matched:
            diseases = self._dedup([s.target[len("排除"):] for s in matched])
            summary = (
                "猫传腹在诊断时需要与其他疾病进行鉴别，包括："
                + "、".join(diseases) + "。"
            )
        else:
            summary = "当前知识库暂无鉴别诊断信息。"
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=[],
            intent=Intent.DIFFERENTIAL_DIAGNOSIS,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_drug_info_response(self, steps: list) -> AgentResponse:
        """药物关联：提取 治疗于 边，按药物聚合适应症。"""
        matched = [s for s in steps if s.rel == "治疗于"]
        if matched:
            by_drug: dict[str, list[str]] = {}
            for s in matched:
                by_drug.setdefault(s.source, []).append(s.target)
            lines = [
                f"· {drug}：治疗{'、'.join(self._dedup(diseases))}"
                for drug, diseases in by_drug.items()
            ]
            summary = (
                "根据知识图谱，以下药物可用于治疗猫传腹：\n" + "\n".join(lines)
            )
        else:
            summary = "当前知识库暂无相关药物信息。"
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=[],
            intent=Intent.DRUG_INFO,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_disease_features_response(self, steps: list, entities: list[str]) -> AgentResponse:
        """疾病特征列举：从 steps 提取源节点（特征），按目标 FIP 类型分组列举。

        steps 为 query_disease_features 返回的入向边（特征 --[表现为|诊断于]--> 疾病），
        源节点即疾病特征/表现。按目标 FIP 节点（湿性/干性）分组，便于用户区分。
        """
        if not steps:
            summary = "当前知识库暂未收录该疾病的特征信息。"
        else:
            by_target: dict[str, list[str]] = {}
            for s in steps:
                by_target.setdefault(s.target, []).append(s.source)
            lines = [
                f"· {target}：{'、'.join(self._dedup(sources))}"
                for target, sources in by_target.items()
            ]
            summary = (
                "根据知识图谱，猫传腹（FIP）的常见特征/表现包括：\n"
                + "\n".join(lines)
            )
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=list(entities),
            intent=Intent.DISEASE_FEATURES,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    def generate_disease_indicators_response(self, steps: list, entities: list[str]) -> AgentResponse:
        """疾病指标异常列举：从 steps 提取源节点（指标），列举该疾病的常见异常指标。

        steps 为 query_disease_indicators 返回的入向边（指标 --[诊断于]--> 疾病），
        源节点即该疾病的异常指标。空 → 提示未收录。
        """
        if not steps:
            summary = "当前知识库暂未收录该疾病的异常指标信息。"
        else:
            indicators = self._dedup([s.source for s in steps])
            summary = (
                "根据知识图谱，猫传腹（FIP）常见的异常指标包括：\n"
                + "、".join(indicators) + "。"
            )
        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=list(entities),
            intent=Intent.DIAGNOSTIC_TEST,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    # ------------------------------------------------------------------
    # 多跳推理：间接关联回复（不依赖分组，直接从有序 ReasoningStep 抽取）
    #
    # 用于直接查询失败、转多跳路径命中后的结论式回复。source 为用户询问的
    # 起始实体，target 为用户想确认关联的目标实体，steps 为路径上的有序边。
    # 文案基于 steps 真实数据，不编造节点或关系；置信度提示从路径关系数据提取。
    # intent 可选：第四步接入分流时传入真实意图；缺省为 GENERAL。
    # ------------------------------------------------------------------
    def generate_multihop_response(
        self,
        source: str,
        target: str,
        steps: list,
        intent: Intent | None = None,
    ) -> AgentResponse:
        """多跳/直接路径的结论式回复，展示完整推理链与依据。"""
        resolved_intent = intent if intent is not None else Intent.GENERAL

        # steps 为空：未找到直接或间接关联，返回边界提示
        if not steps:
            return AgentResponse(
                status=ResponseStatus.BOUNDARY,
                summary=(
                    f"当前知识库未显示{source}与{target}存在直接或间接关联。"
                ),
                groups=[],
                cards=[],
                risks=[],
                entities=[source, target],
                intent=resolved_intent,
                boundary_reason="no_multihop_path",
                boundary_hint="建议咨询兽医或进行进一步检查。",
                clarify_options=[],
                error_message="",
            )

        # 路径文本：A → B → C → ...（按 steps 顺序拼接节点）
        path_nodes = [steps[0].source] + [s.target for s in steps]
        path_text = " → ".join(path_nodes)
        # 关系描述：A rel B；B rel C；...
        rel_desc = "；".join(f"{s.source}{s.rel}{s.target}" for s in steps)

        if len(steps) == 1:
            # 单条边：直接关系
            summary = (
                f"{source}与{target}存在直接关联。\n依据：{rel_desc}。"
            )
        else:
            # 多条边：间接关联
            summary = (
                f"{source}与{target}存在间接关联。\n"
                f"推理链：{path_text}\n"
                f"依据：{rel_desc}。"
            )

        # 路径上存在低置信度关系时追加提示（证据有限，仅供参考）
        if any(getattr(s, "confidence", "") == "Low" for s in steps):
            summary += f"\n{config.LOW_CONFIDENCE_NOTE}"

        return AgentResponse(
            status=ResponseStatus.OK,
            summary=summary,
            groups=[],
            cards=self._steps_to_cards(steps),
            risks=[],
            entities=[source, target],
            intent=resolved_intent,
            boundary_reason=None,
            boundary_hint=None,
            clarify_options=[],
            error_message="",
        )

    # ------------------------------------------------------------------
    # 自然语言摘要（意图分派 + 规则模板）
    # ------------------------------------------------------------------
    def _build_summary(
        self, intent: Intent, groups: list[ReasoningGroup], entities: list[str]
    ) -> str:
        if not groups:
            return "暂未找到相关信息，详情见卡片。"

        if intent == Intent.CONCEPT:
            return self._summary_concept(groups)
        if intent == Intent.DIAGNOSIS:
            return self._summary_diagnosis(groups)
        if intent == Intent.TREATMENT:
            return self._summary_treatment(groups)
        if intent == Intent.RISK:
            return self._summary_risk(groups)
        return self._summary_general(groups, entities)

    # ---- concept：固定科普文本 ----
    def _summary_concept(self, groups: list[ReasoningGroup]) -> str:
        # 机制与诱因描述为固定文本；其中关键实体名与图谱标准名称一致：
        # 猫肠道冠状病毒（FECV）/ 多猫环境 / 应激（见 core.config.ALIAS_MAP）。
        return (
            "猫传腹（FIP）是由猫肠道冠状病毒（FECV）发生基因突变后，"
            "病毒在巨噬细胞内大量复制并引发全身性血管炎，"
            "最终导致胸腹腔积液（湿性）或肉芽肿（干性）的严重疾病。"
            "多猫环境和应激可能增加感染和发病风险。详细机制路径见卡片。"
        )

    # ---- treatment ----
    def _summary_treatment(self, groups: list[ReasoningGroup]) -> str:
        drugs = self._extract_sources_by_key(groups, "drug_treatment")
        regimens = self._extract_sources_by_key(groups, "regimen")
        risks = self._extract_risk_factors(groups)

        if not (drugs or regimens or risks):
            return "暂未找到相关治疗信息。"

        parts: list[str] = ["猫传腹的治疗以抗病毒药物为主"]
        if drugs:
            parts.append(f"，常用药物包括{'、'.join(drugs)}")
        parts.append("。")
        if regimens:
            parts.append(f"通常建议完成{'或'.join(regimens)}，")
        parts.append("规范治疗下多数患猫可以康复（康复率可达80-100%），但若不治疗死亡率接近100%。")
        if risks:
            parts.append(f"治疗期间需特别注意{'、'.join(risks)}。")
        parts.append("具体药物、疗程与预后关系详见推理链卡片。")
        return "".join(parts)

    # ---- diagnosis ----
    def _summary_diagnosis(self, groups: list[ReasoningGroup]) -> str:
        symptoms = self._extract_sources_by_label(groups, "症状", 4)
        screening = self._extract_sources_by_label(groups, "筛查", 3)
        gold = self._extract_sources_by_label(groups, "确诊", 3)

        if not (symptoms or screening or gold):
            return "暂未找到相关诊断信息。"

        parts = ["猫传腹的诊断需结合症状、实验室检查和确诊金标准。"]
        detail: list[str] = []
        if symptoms:
            detail.append(f"常见症状包括{'、'.join(symptoms)}")
        if screening:
            detail.append(f"筛查时关注{'、'.join(screening)}")
        if gold:
            detail.append(f"最终确诊依赖{'、'.join(gold)}")
        if detail:
            parts.append("；".join(detail) + "。")
        parts.append("同时需与淋巴瘤、细菌性腹膜炎等疾病鉴别。完整诊断决策链见卡片。")
        return "".join(parts)

    # ---- risk ----
    def _summary_risk(self, groups: list[ReasoningGroup]) -> str:
        drugs, diseases = self._extract_efficacy(groups)
        risks = self._extract_risk_events(groups)

        if not (drugs and diseases) and not risks:
            return "暂未找到相关药物风险信息。"

        parts: list[str] = []
        if drugs and diseases:
            parts.append(
                f"{'、'.join(drugs)}对{'、'.join(diseases)}有显著疗效，是当前的核心治疗药物。"
            )
        if risks:
            parts.append(f"但需注意，极少数病例报告了{'、'.join(risks)}等风险（证据有限）。")
        parts.append("总体而言，其治疗获益远大于风险，但需在兽医指导下权衡。疗效与风险对比见卡片。")
        return "".join(parts)

    # ---- general ----
    def _summary_general(
        self, groups: list[ReasoningGroup], entities: list[str]
    ) -> str:
        all_names: list[str] = []
        for g in groups:
            for s in g.steps:
                all_names.append(s.source)
                all_names.append(s.target)
        related = [e for e in self._dedup(all_names) if e not in entities]
        if related:
            user = "、".join(entities) if entities else "该实体"
            return f"关于{user}，知识图谱显示其与{'、'.join(related[:5])}等存在关联。详情见卡片。"
        return "已找到相关关联信息，详情见卡片。"

    # ------------------------------------------------------------------
    # 提取辅助函数
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_sources_by_key(
        groups: list[ReasoningGroup], key: str
    ) -> list[str]:
        """按 group.key 取所有 source，去重。"""
        g = ResponseAgent._find_by_key(groups, key)
        if not g:
            return []
        return ResponseAgent._dedup([s.source for s in g.steps])

    @staticmethod
    def _extract_sources_by_label(
        groups: list[ReasoningGroup], keyword: str, limit: int | None
    ) -> list[str]:
        """按 group.label 含关键词取所有 source，去重，可选截断。"""
        g = ResponseAgent._find_by_label(groups, keyword)
        if not g:
            return []
        sources = ResponseAgent._dedup([s.source for s in g.steps])
        return sources[:limit] if limit else sources

    @staticmethod
    def _extract_risk_factors(groups: list[ReasoningGroup]) -> list[str]:
        """从 risk_factor 组优先选 High / Negative 的前 2 条，拼成「源+关系+目标」。"""
        g = ResponseAgent._find_by_key(groups, "risk_factor")
        if not g:
            return []
        high = [s for s in g.steps if s.confidence == "High"]
        negative = [s for s in g.steps if s.confidence != "High" and s.polarity == "Negative"]
        selected = (high + negative)[:2]
        return [f"{s.source}{s.rel}{s.target}" for s in selected]

    @staticmethod
    def _extract_efficacy(
        groups: list[ReasoningGroup],
    ) -> tuple[list[str], list[str]]:
        """从疗效组收集药物（source）与疾病（target），去重。"""
        g = ResponseAgent._find_by_label(groups, "疗效")
        if not g:
            return [], []
        drugs = ResponseAgent._dedup([s.source for s in g.steps])
        diseases = ResponseAgent._dedup([s.target for s in g.steps])
        return drugs, diseases

    @staticmethod
    def _extract_risk_events(groups: list[ReasoningGroup]) -> list[str]:
        """从风险组收集风险事件名（target），去重。"""
        g = ResponseAgent._find_by_label(groups, "风险")
        if not g:
            return []
        return ResponseAgent._dedup([s.target for s in g.steps])

    # ------------------------------------------------------------------
    # 通用辅助
    # ------------------------------------------------------------------
    @staticmethod
    def _find_by_key(
        groups: list[ReasoningGroup], key: str
    ) -> ReasoningGroup | None:
        for g in groups:
            if g.key == key:
                return g
        return None

    @staticmethod
    def _find_by_label(
        groups: list[ReasoningGroup], keyword: str
    ) -> ReasoningGroup | None:
        for g in groups:
            if keyword in g.label:
                return g
        return None

    @staticmethod
    def _dedup(items: list[str]) -> list[str]:
        """保序去重。"""
        seen: set[str] = set()
        result: list[str] = []
        for it in items:
            if it not in seen:
                seen.add(it)
                result.append(it)
        return result

    # ------------------------------------------------------------------
    # 推理链卡片（渲染就绪）
    # ------------------------------------------------------------------
    def _build_cards(
        self, groups: list[ReasoningGroup], risks: list[RiskFlag]
    ) -> list[dict]:
        # 风险标记定位集合：(group_key, step_index)
        flagged = {(r.group_key, r.step_index) for r in risks}

        cards: list[dict] = []
        for group in groups:
            steps = []
            for idx, s in enumerate(group.steps):
                steps.append(
                    {
                        "source": s.source,
                        "rel": s.rel,
                        "target": s.target,
                        "polarity": s.polarity,
                        "polarity_color": config.POLARITY_COLOR.get(s.polarity, "gray"),
                        "confidence": s.confidence,
                        "confidence_color": config.CONFIDENCE_COLOR.get(s.confidence, "gray"),
                        "evidence": s.evidence,
                        "flagged": (group.key, idx) in flagged,
                    }
                )
            cards.append({"key": group.key, "label": group.label, "steps": steps})
        return cards
