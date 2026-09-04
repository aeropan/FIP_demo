"""
core.providers.neo4j_graph_provider —— Neo4j 云端图数据提供者。

实现统一的 GraphProvider 接口，底层复用现有 core.db.run_query 与
core.queries 中的 Cypher 模板，使 Neo4j 方案与本地 NetworkX 方案拥有
完全一致的方法签名，供 Pipeline / GraphQueryAgent 无差别调用。

本文件不修改 core.db / core.queries 中的任何内容；全量图谱查询所需的
Cypher 直接定义在本文件内。节点类型分类逻辑与 LocalGraphProvider 保持一致
（此处为独立副本，后续建议统一收敛到 core.config）。
"""

from __future__ import annotations

from typing import Any

from core.providers.base import GraphProvider
from core.schemas import ReasoningStep
from core import db
from core import queries
# 复用 LocalGraphProvider 中定义的意图边匹配规则，确保两种数据源返回一致
from core.providers.local_graph_provider import (
    _match_diagnosis_inquiry,
    _match_symptom_feature,
    _match_diagnostic_test,
    _match_risk_factors,
    _match_differential_diagnosis,
    _match_drug_info,
)

# ---------------------------------------------------------------------------
# 全量图谱查询模板（不修改 core.queries，定义于本文件内）
# ---------------------------------------------------------------------------
FULL_GRAPH_QUERY = """
// 全量图谱：返回所有关系（供 2D/3D 图谱视图）
MATCH (a:Entity)-[r:RELATES]->(b:Entity)
RETURN a.name AS source, r.关系 AS rel, b.name AS target,
       r.极性 AS polarity, r.置信度 AS confidence, r.支撑依据 AS evidence
""".strip()

# ---------------------------------------------------------------------------
# 节点类型映射（四类）—— 与 LocalGraphProvider 一致的关键词优先级初版
# ---------------------------------------------------------------------------
NODE_TYPE_ETIOLOGY = "病因与病原"
NODE_TYPE_MECHANISM = "机制与过程"
NODE_TYPE_DIAGNOSIS = "诊断与检测"
NODE_TYPE_INTERVENTION = "干预与结局"

_DIAGNOSIS_KEYWORDS = [
    "试验", "组化", "细胞化学", "病理", "比值", "RT-PCR",
    "淀粉样蛋白", "糖蛋白", "排除", "疑似", "检测", "筛查",
]
_INTERVENTION_KEYWORDS = [
    "疗程", "支持治疗", "药物", "GS-441524", "GC376", "瑞德西韦",
    "莫努匹拉韦", "伊曲康唑", "康唑", "康复", "死亡", "复发",
    "血药浓度", "渗透", "尿结石", "淋巴瘤",
]
_ETIOLOGY_KEYWORDS = [
    "病毒", "基因", "感染", "环境", "应激", "复制", "载量",
    "清除不全", "耐药", "免疫抑制", "体重", "冠状病毒", "FECV", "FIPV", "FCoV",
]


def _classify_node(name: str) -> str:
    """根据实体名称关键词判断节点类型，无法判断时归为 机制与过程。"""
    for kw in _DIAGNOSIS_KEYWORDS:
        if kw in name:
            return NODE_TYPE_DIAGNOSIS
    for kw in _INTERVENTION_KEYWORDS:
        if kw in name:
            return NODE_TYPE_INTERVENTION
    for kw in _ETIOLOGY_KEYWORDS:
        if kw in name:
            return NODE_TYPE_ETIOLOGY
    return NODE_TYPE_MECHANISM


class Neo4jGraphProvider(GraphProvider):
    """基于 Neo4j 云端图数据库的图数据提供者，实现统一接口。"""

    def __init__(self):
        # 懒加载：连接由 core.db 内部驱动单例管理，此处无需额外初始化
        pass

    def query_concept(self) -> list[ReasoningStep]:
        """查询概念 / 发病机制相关路径（复用 CONCEPT_QUERY）。"""
        return db.run_query(queries.CONCEPT_QUERY, [])

    def query_diagnosis(self) -> list[ReasoningStep]:
        """查询诊断决策相关路径（复用 DIAGNOSIS_QUERY）。"""
        return db.run_query(queries.DIAGNOSIS_QUERY, [])

    def query_treatment(self) -> list[ReasoningStep]:
        """查询治疗方案与预后相关路径（复用 TREATMENT_QUERY）。"""
        return db.run_query(queries.TREATMENT_QUERY, [])

    def query_risk(self, entities: list[str]) -> list[ReasoningStep]:
        """查询药物风险证据（复用 RISK_QUERY）。

        未传入实体时兜底为 GS-441524，与 LocalGraphProvider 行为一致。
        """
        if not entities:
            entities = ["GS-441524"]
        return db.run_query(queries.RISK_QUERY, list(entities))

    def query_general(self, entities: list[str]) -> list[ReasoningStep]:
        """查询指定实体的一跳关联关系（复用 GENERAL_QUERY）。"""
        return db.run_query(queries.GENERAL_QUERY, list(entities))

    # ------------------------------------------------------------------
    # 细分意图查询方法
    #
    # 策略：复用 FULL_GRAPH_QUERY 获取全量关系（数据量小，无需维护多个 Cypher），
    # 再在 Python 中套用与 LocalGraphProvider 完全相同的 _match_* 规则过滤，
    # 保证两种数据源返回结构一致。ReasoningStep 已按 (source,rel,target) 去重。
    # ------------------------------------------------------------------
    def _fetch_all_steps(self) -> list[ReasoningStep]:
        """获取全量关系（已按 (source,rel,target) 去重）。"""
        return db.run_query(FULL_GRAPH_QUERY, [])

    @staticmethod
    def _dedupe(steps: list[ReasoningStep]) -> list[ReasoningStep]:
        """按 (source, rel, target) 去重，与 LocalGraphProvider._deduplicate 一致。"""
        seen: set[tuple[str, str, str]] = set()
        result: list[ReasoningStep] = []
        for s in steps:
            key = (s.source, s.rel, s.target)
            if key in seen:
                continue
            seen.add(key)
            result.append(s)
        return result

    def query_diagnosis_inquiry(self, entities: list[str]) -> list[ReasoningStep]:
        """症状可能性判断：症状 --[表现为]--> 疑似* 或 --[表现为|诊断于]--> 确诊FIP。"""
        entity_set = set(entities)
        return [
            s for s in self._fetch_all_steps()
            if s.source in entity_set
            and _match_diagnosis_inquiry(s.source, s.rel, s.target)
        ]

    def query_symptom_feature(self, entities: list[str]) -> list[ReasoningStep]:
        """特征确认：实体 --[表现为|诊断于]--> 确诊FIP / 疑似*。"""
        entity_set = set(entities)
        return [
            s for s in self._fetch_all_steps()
            if s.source in entity_set
            and _match_symptom_feature(s.source, s.rel, s.target)
        ]

    def query_diagnostic_test(self, entities: list[str]) -> list[ReasoningStep]:
        """指标解读：指标 --[诊断于]--> 确诊FIP / 疑似*。"""
        entity_set = set(entities)
        return [
            s for s in self._fetch_all_steps()
            if s.source in entity_set
            and _match_diagnostic_test(s.source, s.rel, s.target)
        ]

    def query_risk_factors(self, entities: list[str]) -> list[ReasoningStep]:
        """风险因素：影响/导致 且 目标预后 或 源风险源；entities 非空时按实体过滤。"""
        entity_set = set(entities)
        out: list[ReasoningStep] = []
        for s in self._fetch_all_steps():
            if not _match_risk_factors(s.source, s.rel, s.target):
                continue
            if entity_set and (s.source not in entity_set and s.target not in entity_set):
                continue
            out.append(s)
        return out

    def query_differential_diagnosis(self, entities: list[str]) -> list[ReasoningStep]:
        """鉴别诊断：疑似* --[影响]--> 排除*（不依赖具体实体，直接全量返回）。"""
        return [
            s for s in self._fetch_all_steps()
            if _match_differential_diagnosis(s.source, s.rel, s.target)
        ]

    def query_drug_info(self, entities: list[str]) -> list[ReasoningStep]:
        """药物关联：实体参与 治疗于 边（药物→疾病 或 疾病→药物 均覆盖）。"""
        entity_set = set(entities)
        out: list[ReasoningStep] = []
        for entity in entity_set:
            for s in self._fetch_all_steps():
                if _match_drug_info(s.source, s.rel, s.target, entity):
                    out.append(s)
        return self._dedupe(out)

    def query_disease_features(self, entities: list[str]) -> list[ReasoningStep]:
        """疾病特征列举：疾病 --[表现为|诊断于]--> 特征/症状/指标（入向边）。"""
        entity_set = set(entities)
        return [
            s for s in self._fetch_all_steps()
            if s.target in entity_set and s.rel in ("表现为", "诊断于")
        ]

    def query_disease_indicators(self, entities: list[str]) -> list[ReasoningStep]:
        """疾病指标异常列举：疾病 --[诊断于]--> 指标（入向边，反向于 query_diagnostic_test）。"""
        entity_set = set(entities)
        return [
            s for s in self._fetch_all_steps()
            if s.target in entity_set and s.rel == "诊断于"
        ]

    def get_full_graph(self) -> dict[str, Any]:
        """返回全量图谱数据（nodes / edges）。

        通过内部 FULL_GRAPH_QUERY 获取所有关系（ReasoningStep），
        再组装为 2D/3D 图谱视图所需的 dict 结构。
        """
        steps = db.run_query(FULL_GRAPH_QUERY, [])
        # 节点去重：收集所有 source / target 实体
        node_names: set[str] = set()
        edges: list[dict[str, Any]] = []
        for step in steps:
            node_names.add(step.source)
            node_names.add(step.target)
            edges.append({
                "source": step.source,
                "target": step.target,
                "label": step.rel,
                "polarity": step.polarity,
                "confidence": step.confidence,
                "evidence": step.evidence,
            })
        nodes = [
            {"id": n, "label": n, "type": _classify_node(n)}
            for n in node_names
        ]
        return {"nodes": nodes, "edges": edges}
