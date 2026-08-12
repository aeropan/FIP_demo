"""
FIP 知识推理后端工具模块。

已接入真实 Neo4j 连接（配置来自 .env），并保留意图识别 / 实体解析的占位实现。
前端 app.py 可直接通过本模块查询因果路径。
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# ---------------------------------------------------------------------------
# Neo4j 连接配置（从 .env 读取）
# ---------------------------------------------------------------------------
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

_driver: GraphDatabase.driver | None = None


def _get_driver() -> GraphDatabase.driver | None:
    """延迟初始化 Neo4j 驱动。"""
    global _driver
    if _driver is None and NEO4J_PASSWORD:
        _driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        )
    return _driver


# ---------------------------------------------------------------------------
# Cypher 查询模板（占位）
# ---------------------------------------------------------------------------
DIAGNOSIS_QUERY = """
// TODO: 根据实体查询诊断相关因果路径
MATCH path = (start)-[:CAUSES|RISK_FACTOR_FOR|PRESENTS_AS*1..3]->( Disease {name: '猫传腹' })
WHERE start.name IN $entities
RETURN path
LIMIT 10
""".strip()

TREATMENT_QUERY = """
// TODO: 根据实体查询治疗/用药相关路径
MATCH path = (d:Disease {name: '猫传腹'})-[:LEADS_TO|CAUSES*1..3]->(outcome)
RETURN path
LIMIT 10
""".strip()

SIDE_EFFECT_QUERY = """
// TODO: 根据实体查询副作用相关路径
MATCH path = (drug)-[:CAUSES|LEADS_TO*1..2]->(symptom)
WHERE drug.name IN $entities OR symptom.name IN $entities
RETURN path
LIMIT 10
""".strip()

GENERAL_QUERY = """
// TODO: 通用查询模板
MATCH path = (a)-[:CAUSES|RISK_FACTOR_FOR|PRESENTS_AS|LEADS_TO*1..3]->(b)
WHERE a.name IN $entities OR b.name IN $entities
RETURN path
LIMIT 10
""".strip()


# ---------------------------------------------------------------------------
# 实体与意图（前期存根）
# ---------------------------------------------------------------------------
def resolve_entities(user_input: str) -> list[str]:
    """
    从用户输入中解析标准实体名（当前为占位实现）。

    Args:
        user_input: 用户原始输入。

    Returns:
        匹配到的标准实体名列表；未实现时返回空列表。
    """
    # TODO: 接入同义词表 / LLM NER 进行实体链接。
    _ = user_input
    return []


def detect_intent(user_input: str) -> str:
    """
    识别用户 query 的意图（当前为占位实现）。

    Args:
        user_input: 用户原始输入。

    Returns:
        意图标签，取值 "diagnosis" | "treatment" | "side_effect" | "general"。
    """
    # TODO: 接入关键词或分类模型。
    _ = user_input
    return "general"


# ---------------------------------------------------------------------------
# 连接测试
# ---------------------------------------------------------------------------
def test_connection() -> dict[str, Any]:
    """测试 Neo4j 连接是否可用。"""
    driver = _get_driver()
    if not driver:
        return {"ok": False, "error": "未配置 NEO4J_PASSWORD"}
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS ok")
            result.single()
        return {"ok": True, "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# 查询执行
# ---------------------------------------------------------------------------
def run_query(query_template: str, entities: list[str]) -> list[dict[str, Any]]:
    """
    执行 Cypher 查询并返回结构化路径数据。

    Args:
        query_template: Cypher 模板字符串，可包含 $entities 参数。
        entities: 解析出的标准实体名列表。

    Returns:
        每个关系一步，字典包含 source, rel, target, polarity, confidence, evidence。
    """
    driver = _get_driver()
    if not driver:
        return []

    try:
        with driver.session() as session:
            result = session.run(query_template, entities=entities)
            steps: list[dict[str, Any]] = []
            for record in result:
                path = record.get("path")
                if not path:
                    continue
                nodes = list(path.nodes)
                rels = list(path.relationships)
                for idx, rel in enumerate(rels):
                    if idx + 1 >= len(nodes):
                        break
                    source = nodes[idx].get("name", "?")
                    target = nodes[idx + 1].get("name", "?")
                    steps.append(
                        {
                            "source": source,
                            "rel": rel.type,
                            "target": target,
                            "polarity": rel.get("polarity", "positive"),
                            "confidence": rel.get("confidence", 0.5),
                            "evidence": rel.get("evidence", ""),
                        }
                    )
            return steps
    except Exception as exc:  # noqa: BLE001
        # 前期先容错返回空结果；后续可改为向上抛异常并在前端展示错误
        print(f"Neo4j query failed: {exc}")
        return []


# ---------------------------------------------------------------------------
# 渲染辅助函数
# ---------------------------------------------------------------------------
def polarity_color(polarity: str) -> str:
    """返回极性对应的 Bootstrap 颜色类（占位）。"""
    mapping = {
        "positive": "success",
        "negative": "danger",
        "neutral": "secondary",
    }
    return mapping.get(polarity, "secondary")


def confidence_badge(confidence: float) -> str:
    """返回置信度对应的 Bootstrap 颜色类（占位）。"""
    if confidence >= 0.8:
        return "success"
    if confidence >= 0.5:
        return "warning"
    return "danger"


def format_reasoning_chain(chain: list[dict[str, Any]]) -> str:
    """
    将推理链渲染为 HTML/Markdown 字符串（占位）。

    Args:
        chain: run_query 返回的路径列表。

    Returns:
        可展示在右侧面板的 HTML/Markdown 文本。
    """
    if not chain:
        return "_暂无推理详情。_"
    lines = ["### 推理链详情", ""]
    for step in chain:
        source = step.get("source", "?")
        rel = step.get("rel", "?")
        target = step.get("target", "?")
        lines.append(f"- **{source}** → *{rel}* → **{target}**")
    return "\n".join(lines)
