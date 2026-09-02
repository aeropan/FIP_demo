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
