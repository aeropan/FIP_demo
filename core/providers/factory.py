"""core.providers.factory —— Provider 工厂。

根据 core.config.GRAPH_BACKEND 选择对应的图数据提供者：
- "neo4j" → Neo4jGraphProvider（云端图数据库）
- 其他（默认 "local"）→ LocalGraphProvider（本地 NetworkX 内存图）

新增后端只需在此处扩展分支，Pipeline 调用方无需感知具体实现。
"""

from __future__ import annotations

from core import config
from core.providers.base import GraphProvider
from core.providers.local_graph_provider import LocalGraphProvider
from core.providers.neo4j_graph_provider import Neo4jGraphProvider


def get_graph_provider() -> GraphProvider:
    """返回当前配置对应的图数据提供者实例。

    默认使用本地 NetworkX 图（无需连接 Neo4j）；
    设置环境变量 GRAPH_BACKEND=neo4j 时切换为云端图数据库。
    """
    if config.GRAPH_BACKEND == "neo4j":
        return Neo4jGraphProvider()
    return LocalGraphProvider()


def create_provider(backend: str) -> GraphProvider:
    """根据后端标识创建新的 Provider 实例，不使用全局缓存。

    用于单次查询按用户选择的后端（"local" / "neo4j"）动态获取数据源，
    与 get_graph_provider()（读取全局 GRAPH_BACKEND）的区别在于：
    本函数完全无状态，每次调用都返回全新实例，便于在会话内按需切换
    数据源，而无需修改全局配置或环境变量。

    backend 为 "neo4j" 时返回云端图数据库提供者，其余一律返回本地 NetworkX 提供者。
    """
    if backend == "neo4j":
        return Neo4jGraphProvider()
    return LocalGraphProvider()
