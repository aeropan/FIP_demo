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

from core import config
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

# ---------------------------------------------------------------------------
# 细分意图查询：固定集合与边匹配规则
#
# 以下常量与 _match_* 函数为 Local / Neo4j 两套 Provider 共用的"结构过滤规则"，
# 确保同一意图在两种数据源下返回一致的关系集合（仅数据来源不同）。
# 节点名以知识图谱 data/knowledge_graph.json 中的实际命名为准：
#   - "疑似*" 节点：疑似猫传染性腹膜炎 / 疑似湿性猫传染性腹膜炎 / 疑似干性猫传染性腹膜炎
#   - 确诊 FIP：湿性猫传染性腹膜炎（湿性FIP）/ 干性猫传染性腹膜炎（干性FIP）/ 复发性猫传染性腹膜炎
#   - 预后节点：康复 / 死亡 / 复发 / 复发风险
# ---------------------------------------------------------------------------
_FIP_CONFIRMED = {
    "湿性猫传染性腹膜炎（湿性FIP）",
    "干性猫传染性腹膜炎（干性FIP）",
    "复发性猫传染性腹膜炎",
}
_PROGNOSTIC_OUTCOMES = {"康复", "死亡", "复发", "复发风险"}
# 影响康复 / 复发的风险因素源节点
_RISK_FACTOR_SOURCES = {
    "体重增加", "血脑屏障", "病毒载量", "长期免疫抑制", "耐药性变异", "病毒清除不全",
}
# 已知药物实体（用于 drug_info 判断实体是药物还是疾病）
_DRUG_NAMES = {"GS-441524", "GC376", "瑞德西韦", "莫努匹拉韦"}

# 置信度排序权重（用于多跳路径择优：跳数相同时总分高优先）
_CONF_RANK = {"High": 3, "Medium": 2, "Low": 1}


def _match_diagnosis_inquiry(source: str, rel: str, target: str) -> bool:
    """症状可能性判断：实体 --[表现为]--> 疑似*，或实体 --[表现为|诊断于]--> 确诊FIP。"""
    if rel == "表现为" and target.startswith("疑似"):
        return True
    if rel in ("表现为", "诊断于") and target in _FIP_CONFIRMED:
        return True
    return False


def _match_symptom_feature(source: str, rel: str, target: str) -> bool:
    """特征确认：实体 --[表现为|诊断于]--> 确诊FIP 或 疑似*。"""
    return rel in ("表现为", "诊断于") and (
        target in _FIP_CONFIRMED or target.startswith("疑似")
    )


def _match_diagnostic_test(source: str, rel: str, target: str) -> bool:
    """指标解读：指标 --[诊断于|表现为]--> 确诊FIP 或 疑似*。

    部分指标（如 Rivalta试验阳性）以 表现为 直接连到确诊FIP，放宽关系类型
    以覆盖此类边，避免「Rivalta阳性代表什么」误走边界。
    """
    return rel in ("诊断于", "表现为") and (target in _FIP_CONFIRMED or target.startswith("疑似"))


def _match_risk_factors(source: str, rel: str, target: str) -> bool:
    """风险因素：影响/导致 且 目标为预后节点 或 源为风险源节点。"""
    if rel not in ("影响", "导致"):
        return False
    return target in _PROGNOSTIC_OUTCOMES or source in _RISK_FACTOR_SOURCES


def _match_differential_diagnosis(source: str, rel: str, target: str) -> bool:
    """鉴别诊断：疑似* --[影响]--> 排除*。"""
    return source.startswith("疑似") and rel == "影响" and target.startswith("排除")


def _match_drug_info(source: str, rel: str, target: str, entity: str) -> bool:
    """药物关联：实体参与 治疗于 边（实体为药物或疾病均覆盖）。"""
    if rel != "治疗于":
        return False
    return source == entity or target == entity


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
    # 多跳推理查询方法
    # ------------------------------------------------------------------
    def query_multihop_path(
        self, source: str, target: str, max_hops: int = 3
    ) -> list[ReasoningStep]:
        """多跳推理：直接关系不存在时，查找符合传递规则的多跳路径。

        仅读取本地图数据，不修改任何现有逻辑。返回从 source 到 target 的合法
        路径上的所有 ReasoningStep（有序）。找不到合法路径则返回空列表。

        规则（来自 core.config）：
          - 路径每一步的关系类型须在 ALLOWED_PATH_RELATION_TYPES 中；
          - 每对连续关系 (rel_i, rel_{i+1}) 须在 TRANSITIVE_RULES 中且 allowed=True。
        多条合法路径时：跳数最少优先；跳数相同则关系置信度总和最高优先。
        """
        if not (self.graph.has_node(source) and self.graph.has_node(target)):
            return []

        # 1) 直接边：存在则直接返回（不受多跳白名单限制）
        if self.graph.has_edge(source, target):
            return [self._edge_to_step(source, target, self.graph[source][target])]

        # 2) 查找所有简单路径（跳数 <= max_hops）
        try:
            all_paths = list(
                nx.all_simple_paths(
                    self.graph, source=source, target=target, cutoff=max_hops
                )
            )
        except nx.NodeNotFound:
            return []

        valid_paths: list[list[str]] = []
        for path in all_paths:
            rels = [
                self.graph[path[i]][path[i + 1]].get("rel", "?")
                for i in range(len(path) - 1)
            ]
            # 每步关系类型必须在白名单内
            if not all(rel in config.ALLOWED_PATH_RELATION_TYPES for rel in rels):
                continue
            # 每对连续关系必须可传递
            if len(rels) >= 2 and not all(
                config.TRANSITIVE_RULES.get((rels[i], rels[i + 1]), {}).get(
                    "allowed", False
                )
                for i in range(len(rels) - 1)
            ):
                continue
            valid_paths.append(path)

        if not valid_paths:
            return []

        # 3) 选最优：跳数最少 → 关系置信度总和最高
        def _path_score(path: list[str]) -> tuple[int, int]:
            total = 0
            for i in range(len(path) - 1):
                d = self.graph[path[i]][path[i + 1]]
                total += _CONF_RANK.get(d.get("confidence", "Medium"), 2)
            return (len(path), -total)  # 跳数少优先；同跳数总分高优先

        best = min(valid_paths, key=_path_score)

        steps: list[ReasoningStep] = []
        for i in range(len(best) - 1):
            u, v = best[i], best[i + 1]
            steps.append(self._edge_to_step(u, v, self.graph[u][v]))
        return steps

    # ------------------------------------------------------------------
    # 细分意图查询方法
    # ------------------------------------------------------------------
    def query_diagnosis_inquiry(self, entities: list[str]) -> list[ReasoningStep]:
        """症状可能性判断：症状 --[表现为]--> 疑似* 或 --[表现为|诊断于]--> 确诊FIP。"""
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            if u in entity_set and _match_diagnosis_inquiry(u, d.get("rel"), v):
                steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_symptom_feature(self, entities: list[str]) -> list[ReasoningStep]:
        """特征确认：实体 --[表现为|诊断于]--> 确诊FIP / 疑似*。"""
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            if u in entity_set and _match_symptom_feature(u, d.get("rel"), v):
                steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_diagnostic_test(self, entities: list[str]) -> list[ReasoningStep]:
        """指标解读：指标 --[诊断于]--> 确诊FIP / 疑似*。"""
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            if u in entity_set and _match_diagnostic_test(u, d.get("rel"), v):
                steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_risk_factors(self, entities: list[str]) -> list[ReasoningStep]:
        """风险因素：影响/导致 且 目标预后 或 源风险源；entities 非空时按实体过滤。"""
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            if not _match_risk_factors(u, d.get("rel"), v):
                continue
            # entities 非空时，仅保留与该实体相关的风险边（源或目标命中）
            if entity_set and (u not in entity_set and v not in entity_set):
                continue
            steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_differential_diagnosis(self, entities: list[str]) -> list[ReasoningStep]:
        """鉴别诊断：疑似* --[影响]--> 排除*（不依赖具体实体，直接全量返回）。"""
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            if _match_differential_diagnosis(u, d.get("rel"), v):
                steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_drug_info(self, entities: list[str]) -> list[ReasoningStep]:
        """药物关联：实体参与 治疗于 边（药物→疾病 或 疾病→药物 均覆盖）。"""
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for entity in entity_set:
            if not self.graph.has_node(entity):
                continue
            # 实体为药物：出向 治疗于
            for _, v, d in self.graph.out_edges(entity, data=True):
                if _match_drug_info(entity, d.get("rel"), v, entity):
                    steps.append(self._edge_to_step(entity, v, d))
            # 实体为疾病：入向 治疗于
            for u, _, d in self.graph.in_edges(entity, data=True):
                if _match_drug_info(u, d.get("rel"), entity, entity):
                    steps.append(self._edge_to_step(u, entity, d))
        return self._deduplicate(steps)

    def query_disease_features(self, entities: list[str]) -> list[ReasoningStep]:
        """疾病特征列举：疾病 --[表现为|诊断于]--> 特征/症状/指标（入向边）。

        围绕给定疾病实体，返回目标节点为该疾病、关系为 表现为/诊断于 的边，
        源节点即该疾病的特征/表现。与 query_symptom_feature 方向相反。
        """
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            if v in entity_set and d.get("rel") in ("表现为", "诊断于"):
                steps.append(self._edge_to_step(u, v, d))
        return self._deduplicate(steps)

    def query_disease_indicators(self, entities: list[str]) -> list[ReasoningStep]:
        """疾病指标异常列举：疾病 --[诊断于]--> 指标（入向边，反向于 query_diagnostic_test）。

        围绕给定疾病实体，返回目标节点为该疾病、关系为 诊断于 的边，
        源节点即该疾病的异常指标。用于「传腹有哪些指标异常」这类反向指标查询。
        """
        entity_set = set(entities)
        steps: list[ReasoningStep] = []
        for u, v, d in self.graph.edges(data=True):
            if v in entity_set and d.get("rel") == "诊断于":
                steps.append(self._edge_to_step(u, v, d))
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
