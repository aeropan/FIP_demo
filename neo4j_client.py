"""Neo4j 连接与因果路径查询封装。"""

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


@dataclass
class ConnectionConfig:
    uri: str
    username: str
    password: str

    def valid(self) -> bool:
        return bool(self.uri and self.username and self.password)


class FIPCausalClient:
    """封装 Neo4j 驱动，提供因果图查询能力。"""

    def __init__(self, config: ConnectionConfig | None = None):
        self.config = config or self._default_config()
        self.driver = None
        if self.config.valid():
            self.driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password),
            )

    @staticmethod
    def _default_config() -> ConnectionConfig:
        return ConnectionConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", ""),
        )

    def is_ready(self) -> bool:
        return self.driver is not None

    def test_connection(self) -> dict[str, Any]:
        if not self.driver:
            return {"ok": False, "error": "缺少连接配置（URI / 用户名 / 密码）"}
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS ok")
                result.single()
            return {"ok": True, "error": None}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    def get_all_nodes(self) -> list[dict[str, Any]]:
        """返回图中所有因果节点的名称、标签与描述，用于下拉选择。"""
        if not self.driver:
            return []
        query = """
        MATCH (n)
        RETURN labels(n)[0] AS label, n.name AS name, n.description AS description
        ORDER BY label, n.name
        """
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]

    def find_causal_paths(
        self,
        start_name: str,
        end_name: str,
        max_hops: int = 4,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        查找从 start_name 到 end_name 的所有有向因果路径。

        返回每条路径的节点序列和关系序列。
        """
        if not self.driver:
            return []
        query = """
        MATCH path = (start {name: $start_name})-[:CAUSES|RISK_FACTOR_FOR|PRESENTS_AS|LEADS_TO*1..%d]->(end {name: $end_name})
        WITH path
        LIMIT $limit
        RETURN [n IN nodes(path) | {name: n.name, label: labels(n)[0], description: n.description}] AS nodes,
               [r IN relationships(path) | {type: type(r), description: r.description}] AS rels,
               length(path) AS hops
        ORDER BY hops
        """ % max_hops
        with self.driver.session() as session:
            result = session.run(query, start_name=start_name, end_name=end_name, limit=limit)
            return [dict(record) for record in result]

    def find_outward_paths(
        self,
        start_name: str,
        max_hops: int = 3,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """从指定节点出发，查找其下游因果影响路径。"""
        if not self.driver:
            return []
        query = """
        MATCH path = (start {name: $start_name})-[:CAUSES|RISK_FACTOR_FOR|PRESENTS_AS|LEADS_TO*1..%d]->(end)
        WITH path, end
        LIMIT $limit
        RETURN [n IN nodes(path) | {name: n.name, label: labels(n)[0], description: n.description}] AS nodes,
               [r IN relationships(path) | {type: type(r), description: r.description}] AS rels,
               length(path) AS hops
        ORDER BY hops
        """ % max_hops
        with self.driver.session() as session:
            result = session.run(query, start_name=start_name, limit=limit)
            return [dict(record) for record in result]

    def close(self):
        if self.driver:
            self.driver.close()


def nodes_to_networkx(
    paths: list[dict[str, Any]],
) -> tuple[set[tuple[str, str, str, str]], set[tuple[str, str, str]]]:
    """
    把路径列表转换成用于可视化的节点和边集合。

    返回 (nodes, edges)，其中 nodes 元素为 (id, label, name, description)，
    edges 元素为 (source, target, type, description)。
    """
    nodes: set[tuple[str, str, str, str]] = set()
    edges: set[tuple[str, str, str, str]] = set()
    for path in paths:
        path_nodes = path["nodes"]
        path_rels = path.get("rels", [])
        for node in path_nodes:
            node_id = node["name"]
            nodes.add((node_id, node["label"], node["name"], node.get("description", "")))
        for idx, rel in enumerate(path_rels):
            if idx + 1 < len(path_nodes):
                source = path_nodes[idx]["name"]
                target = path_nodes[idx + 1]["name"]
                edges.add((source, target, rel["type"], rel.get("description", "")))
    return nodes, edges
