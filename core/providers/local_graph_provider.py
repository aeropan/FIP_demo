"""
core.providers.local_graph_provider —— 本地图数据提供者（NetworkX 内存图）。

作为 Neo4j 云端方案的本地替代（默认方案），从 data/knowledge_graph.json
读取三元组，用 networkx.DiGraph 构建有向内存图，并提供与 Neo4j 查询结果
一致的数据接口（核心查询方法均返回 list[ReasoningStep]）。

设计要点：
1. 使用 nx.DiGraph 承载图谱，支撑 all_simple_paths 等路径遍历；
2. 所有核心查询方法的返回结构与 core.db.run_query 对齐（按 source/rel/target
   去重），确保 Pipeline 上层无感知切换；
3. 知识图谱中存在少量"平行重复边"（同一 source→target，但 evidence 不同，
   例如 GS-441524→湿性FIP 有两条记录）。DiGraph 会自动合并平行边，但 2D/3D
   图谱视图需要展示全部三元组，因此额外保留 self._records（全量原始记录），
   供 get_full_graph 精确返回数据条数（nodes/edges 与源文件一致）。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

from core.providers.base import GraphProvider
from core.schemas import ReasoningStep

# ---------------------------------------------------------------------------
# 节点类型映射（四类）
#
# 采用"关键词优先 + 兜底归为 机制与过程"的简易规则。
# 说明：本映射为内置初版，后续建议统一收敛到 core.config 中维护。
# ---------------------------------------------------------------------------
NODE_TYPE_ETIOLOGY = "病因与病原"        # 病原、诱因、风险因素
NODE_TYPE_MECHANISM = "机制与过程"       # 病理机制、生理/病理过程
NODE_TYPE_DIAGNOSIS = "诊断与检测"       # 检验、检查、筛查、鉴别诊断
NODE_TYPE_INTERVENTION = "干预与结局"    # 药物/疗程/支持治疗、预后结局

# 关键词优先级：诊断与检测 > 干预与结局 > 病因与病原 > 机制与过程（兜底）
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

# CONCEPT 查询固定锚点与目标
_CONCEPT_START = "猫肠道冠状病毒（FECV）"
_CONCEPT_TARGETS = [
    "湿性猫传染性腹膜炎（湿性FIP）",
    "干性猫传染性腹膜炎（干性FIP）",
]
_CONCEPT_ALLOWED_REL = {"导致", "表现为", "影响"}
# CONCEPT 额外的诱因链（不与 FECV 主路径连通，需单独并入）
_CONCEPT_INDUCE_EDGES = [
    ("多猫环境", "猫冠状病毒（FCoV）感染"),
    ("应激", "病毒复制"),
]

# TREATMENT 查询相关的固定集合
_TREATMENT_OUTCOMES = ["康复", "死亡", "复发", "复发风险"]
_TREATMENT_RISK_SOURCES = {"病毒清除不全", "长期免疫抑制", "耐药性变异", "病毒载量"}
# 治疗风险因素精确边（source, target）白名单
_TREATMENT_RISK_FACTORS = {
    ("体重增加", "血药浓度"),
    ("血脑屏障", "药物渗透"),
    ("病毒清除不全", "复发"),
    ("长期免疫抑制", "复发"),
    ("耐药性变异", "死亡"),
    ("病毒载量", "康复"),
}


class LocalGraphProvider(GraphProvider):
    """基于 NetworkX 内存图的本地知识图谱数据提供者。"""

    def __init__(self, data_path: str = "data/knowledge_graph.json"):
        self.graph = nx.DiGraph()
        self._records: list[dict[str, Any]] = []  # 全量原始三元组（含平行重复边）
        self._load(data_path)

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------
    def _load(self, data_path: str) -> None:
        """读取 JSON 三元组并构建有向图。

        候选路径：先尝试 data_path 原样（相对当前工作目录），再回退到
        相对于本文件所在项目根目录的位置，提升从不同 cwd 启动时的健壮性。
        """
        base = Path(__file__).resolve().parent.parent
        candidates = [Path(data_path), base / data_path]
        raw: list[dict[str, Any]] | None = None
        for cand in candidates:
            if cand.exists():
                raw = json.loads(cand.read_text(encoding="utf-8"))
                break
        if raw is None:
            raise FileNotFoundError(f"未找到知识图谱文件：{data_path}")

        for rec in raw:
            src = rec["source"]
            tgt = rec["target"]
            rel = rec.get("rel", "?")
            polarity = rec.get("polarity", "Neutral")
            confidence = rec.get("confidence", "Medium")
            evidence = rec.get("evidence", "")

            # 节点及其类型（类型仅作为图谱视图展示用，不影响查询）
            self.graph.add_node(src, type=self._classify_node(src))
            self.graph.add_node(tgt, type=self._classify_node(tgt))
            # DiGraph 会自动合并平行边；查询方法内部仍按 (source,rel,target) 去重
            self.graph.add_edge(
                src, tgt,
                rel=rel,
                polarity=polarity,
                confidence=confidence,
                evidence=evidence,
            )
            # 保留全量原始记录，供 get_full_graph 精确返回 68 条边
            self._records.append({
                "source": src, "rel": rel, "target": tgt,
                "polarity": polarity, "confidence": confidence, "evidence": evidence,
            })

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------
    @staticmethod
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

    @staticmethod
    def _edge_to_step(u: str, v: str, data: dict[str, Any]) -> ReasoningStep:
        """将 NetworkX 边数据转换为 ReasoningStep。"""
        return ReasoningStep(
            source=u,
            rel=data.get("rel", "?"),
            target=v,
            polarity=data.get("polarity", "Neutral"),
            confidence=data.get("confidence", "Medium"),
            evidence=data.get("evidence", ""),
        )

    @staticmethod
    def _deduplicate(steps: list[ReasoningStep]) -> list[ReasoningStep]:
        """按 (source, rel, target) 去重，与 core.db.run_query 规则一致。"""
        seen: set[tuple[str, str, str]] = set()
        result: list[ReasoningStep] = []
        for step in steps:
            key = (step.source, step.rel, step.target)
            if key in seen:
                continue
            seen.add(key)
            result.append(step)
        return result

    # ------------------------------------------------------------------
    # 核心查询方法（均返回 list[ReasoningStep]）
    # ------------------------------------------------------------------
    def query_concept(self) -> list[ReasoningStep]:
        """概念/机制查询：从 FECV 出发经 导致/表现为/影响 遍历至湿性/干性FIP，
        同时并入诱因链（多猫环境→FCoV感染、应激→病毒复制）。"""
        steps: list[ReasoningStep] = []
        if self.graph.has_node(_CONCEPT_START):
            for target in _CONCEPT_TARGETS:
                if not self.graph.has_node(target):
                    continue
                for path in nx.all_simple_paths(
                    self.graph, _CONCEPT_START, target, cutoff=12
                ):
                    for u, v in zip(path[:-1], path[1:]):
                        data = self.graph[u][v]
                        if data.get("rel") in _CONCEPT_ALLOWED_REL:
                            steps.append(self._edge_to_step(u, v, data))
        # 并入独立的诱因链
        for u, v in _CONCEPT_INDUCE_EDGES:
            if self.graph.has_edge(u, v):
                steps.append(self._edge_to_step(u, v, self.graph[u][v]))
        return self._deduplicate(steps)

    def query_diagnosis(self) -> list[ReasoningStep]:
        """诊断查询：四类诊断关系（症状/筛查/金标准/鉴别诊断）。"""
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            rel = d.get("rel")
            if (
                (rel == "表现为" and v.startswith("疑似"))
                or (rel == "诊断于" and v.startswith("疑似"))
                or (rel in ("诊断于", "表现为") and v in _CONCEPT_TARGETS)
                or (u.startswith("疑似") and v.startswith("排除"))
            ):
                steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_treatment(self) -> list[ReasoningStep]:
        """治疗查询：药物治疗 / 疾病预后 / 疗程支持 / 治疗风险因素。"""
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            rel = d.get("rel")
            # 1) 药物治疗：药物 → 疾病（治疗于）
            if rel == "治疗于":
                steps.append(self._edge_to_step(u, v, d))
                continue
            # 2) 疾病预后：指向 康复/死亡/复发/复发风险，排除疗程与风险因素节点
            if (
                v in _TREATMENT_OUTCOMES
                and not (("疗程" in u) or (u == "对症支持治疗"))
                and u not in _TREATMENT_RISK_SOURCES
            ):
                steps.append(self._edge_to_step(u, v, d))
                continue
            # 3) 疗程支持：疗程 / 对症支持治疗 → 康复
            if (
                v == "康复"
                and (("疗程" in u) or (u == "对症支持治疗"))
                and rel == "影响"
            ):
                steps.append(self._edge_to_step(u, v, d))
                continue
            # 4) 治疗风险因素：精确边白名单
            if (u, v) in _TREATMENT_RISK_FACTORS:
                steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_risk(self, entities: list[str] | None = None) -> list[ReasoningStep]:
        """药物风险查询：疗效证据（Positive+High）与风险证据（Low 或 Negative）。"""
        if not entities:
            entities = ["GS-441524"]
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for drug in entity_set:
            if not self.graph.has_node(drug):
                continue
            for _, v, d in self.graph.out_edges(drug, data=True):
                polarity = d.get("polarity")
                confidence = d.get("confidence")
                # 疗效证据：极性 Positive 且置信度 High
                # 风险证据：置信度 Low 或极性 Negative
                if (
                    (polarity == "Positive" and confidence == "High")
                    or (confidence == "Low")
                    or (polarity == "Negative")
                ):
                    steps.append(self._edge_to_step(drug, v, d))
        return self._deduplicate(steps)

    def query_general(self, entities: list[str]) -> list[ReasoningStep]:
        """通用综合查询：围绕实体查询一跳内所有入向和出向关系。"""
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for entity in entity_set:
            if not self.graph.has_node(entity):
                continue
            # 出向边
            for _, v, d in self.graph.out_edges(entity, data=True):
                steps.append(self._edge_to_step(entity, v, d))
            # 入向边
            for u, _, d in self.graph.in_edges(entity, data=True):
                steps.append(self._edge_to_step(u, entity, d))
        return self._deduplicate(steps)

    # ------------------------------------------------------------------
    # 全量图谱（供 2D/3D 图谱视图）
    # ------------------------------------------------------------------
    def get_full_graph(self) -> dict[str, Any]:
        """返回全量节点与边。

        节点包含 id / label / type；边包含 source / target / label / polarity /
        confidence / evidence。边来自全量原始记录（self._records），确保与源文件
        的条数一致（平行重复边也保留）。
        """
        nodes = [
            {
                "id": n,
                "label": n,
                "type": self.graph.nodes[n].get("type", NODE_TYPE_MECHANISM),
            }
            for n in self.graph.nodes
        ]
        edges = [
            {
                "source": r["source"],
                "target": r["target"],
                "label": r["rel"],
                "polarity": r["polarity"],
                "confidence": r["confidence"],
                "evidence": r["evidence"],
            }
            for r in self._records
        ]
        return {"nodes": nodes, "edges": edges}
