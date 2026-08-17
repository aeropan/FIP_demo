"""core.agents.evidence_agent —— 证据标准化与分组（EvidenceAgent）。"""

from __future__ import annotations

from core.agents.base import Agent
from core.schemas import Intent, ReasoningGroup, ReasoningStep

# 确诊 FIP 实体（湿性 / 干性），用于区分"确诊金标准"与"疑似"关系
_CONFIRMED_FIP = {"湿性猫传染性腹膜炎（湿性FIP）", "干性猫传染性腹膜炎（干性FIP）"}

# 治疗风险因素节点（与 TREATMENT_QUERY 第 4 部分保持一致）
_TREATMENT_RISK_FACTORS = {
    "体重增加", "血脑屏障", "病毒清除不全", "长期免疫抑制", "耐药性变异", "病毒载量",
}

# concept 意图的诱因链起点（与 CONCEPT_QUERY 诱因部分保持一致）
_CONCEPT_TRIGGERS = {"多猫环境", "应激"}


class EvidenceAgent(Agent):
    """将扁平的推理步骤按意图分组，供前端分组展示。

    分组规则与各查询模板的业务分类保持镜像，保证结果可追溯到
    "症状表现 / 筛查指标 / 确诊金标准 / 鉴别诊断" 等语义类别。
    """

    def run(self, intent: Intent, steps: list[ReasoningStep]) -> list[ReasoningGroup]:
        if intent == Intent.DIAGNOSIS:
            return self._group_diagnosis(steps)
        if intent == Intent.TREATMENT:
            return self._group_treatment(steps)
        if intent == Intent.RISK:
            return self._group_risk(steps)
        if intent == Intent.CONCEPT:
            return self._group_concept(steps)
        # general：一跳关系，单组返回
        return [ReasoningGroup(key="relations", label="关联关系", steps=list(steps))]

    # ------------------------------------------------------------------
    # diagnosis：症状表现 / 筛查指标 / 确诊金标准 / 鉴别诊断
    # ------------------------------------------------------------------
    def _group_diagnosis(self, steps: list[ReasoningStep]) -> list[ReasoningGroup]:
        groups = [
            ReasoningGroup(key="symptoms", label="症状表现", steps=[]),
            ReasoningGroup(key="screening", label="筛查指标", steps=[]),
            ReasoningGroup(key="gold_standard", label="确诊金标准", steps=[]),
            ReasoningGroup(key="differential", label="鉴别诊断", steps=[]),
        ]
        for s in steps:
            if s.target.startswith("排除"):
                groups[3].steps.append(s)
            elif s.target in _CONFIRMED_FIP:
                groups[2].steps.append(s)
            elif s.rel == "表现为":
                groups[0].steps.append(s)
            elif s.rel == "诊断于":
                groups[1].steps.append(s)
        return [g for g in groups if g.steps]

    # ------------------------------------------------------------------
    # treatment：药物治疗 / 疾病预后 / 疗程支持 / 治疗风险因素
    # ------------------------------------------------------------------
    def _group_treatment(self, steps: list[ReasoningStep]) -> list[ReasoningGroup]:
        groups = [
            ReasoningGroup(key="drug_treatment", label="药物治疗", steps=[]),
            ReasoningGroup(key="prognosis", label="疾病预后", steps=[]),
            ReasoningGroup(key="regimen", label="疗程支持", steps=[]),
            ReasoningGroup(key="risk_factor", label="治疗风险因素", steps=[]),
        ]
        for s in steps:
            if s.rel == "治疗于":
                groups[0].steps.append(s)
            elif s.source in _TREATMENT_RISK_FACTORS:
                groups[3].steps.append(s)
            elif s.source.endswith("疗程") or s.source == "对症支持治疗":
                groups[2].steps.append(s)
            else:
                groups[1].steps.append(s)
        return [g for g in groups if g.steps]

    # ------------------------------------------------------------------
    # risk：疗效证据 / 风险证据
    # ------------------------------------------------------------------
    def _group_risk(self, steps: list[ReasoningStep]) -> list[ReasoningGroup]:
        groups = [
            ReasoningGroup(key="efficacy", label="疗效证据", steps=[]),
            ReasoningGroup(key="risk_evidence", label="风险证据", steps=[]),
        ]
        for s in steps:
            if s.polarity == "Positive" and s.confidence == "High":
                groups[0].steps.append(s)
            else:
                groups[1].steps.append(s)
        return [g for g in groups if g.steps]

    # ------------------------------------------------------------------
    # concept：发病机制 / 诱因链
    # ------------------------------------------------------------------
    def _group_concept(self, steps: list[ReasoningStep]) -> list[ReasoningGroup]:
        mechanism: list[ReasoningStep] = []
        trigger: list[ReasoningStep] = []
        for s in steps:
            if s.source in _CONCEPT_TRIGGERS:
                trigger.append(s)
            else:
                mechanism.append(s)
        groups: list[ReasoningGroup] = []
        if mechanism:
            groups.append(ReasoningGroup(key="mechanism", label="发病机制", steps=mechanism))
        if trigger:
            groups.append(ReasoningGroup(key="trigger", label="诱因链", steps=trigger))
        return groups
