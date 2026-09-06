"""
core.providers.base —— 图数据提供者统一接口（抽象基类）。

定义 GraphProvider 抽象基类，声明后续所有查询方法，确保本地（NetworkX）
与云端（Neo4j）两种数据源实现具有完全一致的方法签名，使 Pipeline 或
GraphQueryAgent 可以无差别调用，无需关心底层数据源。

本文件为纯接口：只声明方法签名与中文文档字符串，不包含任何实现细节，
也不引入 NetworkX / Neo4j 驱动，不从配置文件读取数据。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.schemas import ReasoningStep


class GraphProvider(ABC):
    """图数据提供者统一抽象基类。

    本地（LocalGraphProvider，基于 NetworkX 内存图）与云端（Neo4j）实现
    均应继承本类并实现全部抽象方法，保证方法签名一致、可无差别替换。
    """

    @abstractmethod
    def query_concept(self) -> list[ReasoningStep]:
        """查询概念 / 发病机制相关路径。

        从病原（如猫肠道冠状病毒 FECV）出发，沿 导致 / 表现为 / 影响 关系
        遍历至湿性 / 干性 FIP，并返回路径上的所有关系，同时包含诱因链。

        Returns:
            list[ReasoningStep]: 概念 / 机制相关的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_diagnosis(self) -> list[ReasoningStep]:
        """查询诊断决策相关路径。

        返回诊断意图所需的全部关系，包括症状表现、筛查指标、确诊金标准
        以及鉴别诊断（疑似 FIP → 排除其他疾病）。

        Returns:
            list[ReasoningStep]: 诊断相关的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_treatment(self) -> list[ReasoningStep]:
        """查询治疗方案与预后相关路径。

        返回治疗意图所需的全部关系，包括药物治疗、疾病预后、疗程支持
        以及治疗风险因素。

        Returns:
            list[ReasoningStep]: 治疗与预后相关的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_risk(self, entities: list[str]) -> list[ReasoningStep]:
        """查询药物风险证据。

        针对给定药物实体，返回疗效证据（极性 Positive 且置信度 High）与
        风险证据（置信度 Low 或极性 Negative）。未传入实体时默认查询
        GS-441524（由具体实现内部兜底）。

        Args:
            entities: 药物实体名列表。

        Returns:
            list[ReasoningStep]: 与药物风险 / 疗效相关的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_general(self, entities: list[str]) -> list[ReasoningStep]:
        """查询指定实体的一跳关联关系。

        围绕给定实体，返回其入向与出向的一跳关系（全量）。

        Args:
            entities: 实体名列表。

        Returns:
            list[ReasoningStep]: 与实体相关的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_diagnosis_inquiry(self, entities: list[str]) -> list[ReasoningStep]:
        """查询症状 / 体征指向疑似 FIP 的表现关系，用于症状可能性判断。

        围绕给定实体，返回「实体 --[表现为]--> 疑似*」以及「实体直接指向确诊
        FIP（湿性 / 干性）的 表现为 / 诊断于」关系，帮助回答「该症状是否可能
        是传腹」这类判断性问题。

        Args:
            entities: 用户问题中解析到的症状 / 体征实体名列表。

        Returns:
            list[ReasoningStep]: 症状可能性判断所需的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_symptom_feature(self, entities: list[str]) -> list[ReasoningStep]:
        """查询指定症状 / 指标与 FIP 之间的表现为 / 诊断于关系，用于特征确认。

        围绕给定实体，返回「实体 --[表现为|诊断于]--> 确诊 FIP 或 疑似*」关系，
        帮助回答「腹水是不是传腹的特征」这类特征确认问题。

        Args:
            entities: 用户问题中解析到的症状 / 指标实体名列表。

        Returns:
            list[ReasoningStep]: 特征确认所需的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_diagnostic_test(self, entities: list[str]) -> list[ReasoningStep]:
        """查询检查指标与疑似 / 确诊 FIP 之间的诊断关系，用于指标解读。

        围绕给定实体，返回「指标 --[诊断于]--> 疑似* 或 确诊 FIP」关系，帮助
        回答「白球比 0.5 是不是传腹」这类指标解读问题。

        Args:
            entities: 用户问题中解析到的检验 / 检查指标实体名列表。

        Returns:
            list[ReasoningStep]: 指标解读所需的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_risk_factors(self, entities: list[str]) -> list[ReasoningStep]:
        """查询影响康复 / 复发的风险因素关系。

        返回关系类型为 影响 / 导致，且目标为预后节点（康复 / 死亡 / 复发）或
        源为风险因素节点（体重增加 / 血脑屏障 / 病毒载量 / 长期免疫抑制 / 耐药性变异
        等）的边。entities 非空时优先返回与这些实体相关的风险边；为空时返回全量。

        Args:
            entities: 用户问题中解析到的实体名列表；为空表示返回全量风险因素。

        Returns:
            list[ReasoningStep]: 风险因素所需的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_differential_diagnosis(self, entities: list[str]) -> list[ReasoningStep]:
        """查询疑似 FIP 需要排除的其他疾病关系。

        返回源为疑似*节点、关系为 影响、目标以「排除」开头的边（即鉴别诊断中
        需排除的其他疾病）。本方法不依赖具体实体，可直接全量查询。

        Args:
            entities: 当前预留参数（本方法按全量鉴别诊断关系返回，不按实体过滤）。

        Returns:
            list[ReasoningStep]: 鉴别诊断所需的排除关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_drug_info(self, entities: list[str]) -> list[ReasoningStep]:
        """查询药物与 FIP 之间的治疗关系，用于药物关联信息。

        围绕给定实体：若实体为药物名（如 GS-441524），返回其出向 治疗于 边；
        若实体为疾病名，返回以该疾病为目标节点的 治疗于 边（对应药物）。

        Args:
            entities: 用户问题中解析到的实体名列表（可能为药物名或疾病名）。

        Returns:
            list[ReasoningStep]: 药物关联信息所需的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_disease_features(self, entities: list[str]) -> list[ReasoningStep]:
        """查询疾病有哪些特征/表现，方向为疾病 → 特征（反向查询 表现为/诊断于）。

        围绕给定疾病实体，返回「特征/症状/指标 --[表现为|诊断于]--> 该疾病」的入向边，
        帮助回答「传腹有哪些特征/表现/症状」这类疾病特征列举问题。

        Args:
            entities: 用户问题中解析到的疾病实体名列表。

        Returns:
            list[ReasoningStep]: 疾病特征列举所需的推理关系列表。
        """
        raise NotImplementedError

    @abstractmethod
    def query_disease_indicators(self, entities: list[str]) -> list[ReasoningStep]:
        """查询疾病有哪些检查指标异常，方向为疾病 → 指标（反向查询 诊断于）。

        围绕给定疾病实体，返回「指标 --[诊断于]--> 该疾病」的入向边，
        帮助回答「传腹有哪些指标异常」这类反向指标查询问题。与正向的
        query_diagnostic_test（指标 → 疾病）方向相反。

        Args:
            entities: 用户问题中解析到的疾病实体名列表。

        Returns:
            list[ReasoningStep]: 疾病指标异常列举所需的推理关系列表。
        """
        raise NotImplementedError

    def query_multihop_path(
        self, source: str, target: str, max_hops: int = 5
    ) -> list[ReasoningStep]:
        """查询 source 到 target 的多跳间接关联路径（默认空实现）。

        仅 LocalGraphProvider 实现了基于 NetworkX 简单路径 + 传递规则
        （core.config.TRANSITIVE_RULES / ALLOWED_PATH_RELATION_TYPES）的多跳推理；
        抽象基类提供默认空实现，便于其它后端（如 Neo4j）在尚未实现时调用不报错，
        调用方应将其作为「尽力而为」的间接推理补充，命中为空时回退到边界逻辑。

        Args:
            source: 起始实体名。
            target: 目标实体名。
            max_hops: 最大跳数，默认 3。

        Returns:
            list[ReasoningStep]: 多跳路径上的有序关系；默认实现返回空列表。
        """
        return []

    @abstractmethod
    def get_full_graph(self) -> dict[str, Any]:
        """返回全量图谱数据。

        供 2D / 3D 图谱视图使用，返回结构包含节点与边：
            - nodes: 每项为 {"id", "label", "type"}
            - edges: 每项为 {"source", "target", "label", "polarity",
                             "confidence", "evidence"}

        Returns:
            dict: 形如 {"nodes": [...], "edges": [...]} 的全量图谱数据。
        """
        raise NotImplementedError
