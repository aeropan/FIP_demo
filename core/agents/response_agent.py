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
