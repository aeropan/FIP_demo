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
# Cypher 查询模板（匹配真实数据模型）
#
# 真实模型：节点 (n:Entity {name})，关系 (a)-[r:RELATES]->(b)，r 属性：
#   r.关系     中文语义，取值：导致 / 影响 / 表现为 / 诊断于 / 治疗于
#   r.极性     Positive / Negative / Neutral
#   r.置信度   High / Medium / Low
#   r.支撑依据 文献依据文本
# ---------------------------------------------------------------------------
DIAGNOSIS_QUERY = """
// 诊断：从输入实体出发，经 表现为/诊断于 关系定位疾病
MATCH path = (start:Entity)-[r:RELATES]->(disease:Entity)
WHERE start.name IN $entities
  AND r.关系 IN ['表现为', '诊断于']
RETURN path
ORDER BY r.置信度
LIMIT 20
""".strip()

TREATMENT_QUERY = """
// 治疗：药物/疗法（治疗于）与疾病的双向匹配
MATCH path = (drug:Entity)-[r:RELATES]->(disease:Entity)
WHERE (drug.name IN $entities OR disease.name IN $entities)
  AND r.关系 = '治疗于'
RETURN path
ORDER BY r.置信度
LIMIT 20
""".strip()

SIDE_EFFECT_QUERY = """
// 影响/副作用：经 影响/导致 关系，正向或反向匹配输入实体
MATCH path = (a:Entity)-[r:RELATES]->(b:Entity)
WHERE (a.name IN $entities OR b.name IN $entities)
  AND r.关系 IN ['影响', '导致']
RETURN path
ORDER BY r.置信度
LIMIT 20
""".strip()

GENERAL_QUERY = """
// 通用：任意 RELATES 关系，双向匹配输入实体
MATCH path = (a:Entity)-[r:RELATES]->(b:Entity)
WHERE a.name IN $entities OR b.name IN $entities
RETURN path
ORDER BY r.置信度
LIMIT 20
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
        其中 rel 为中文语义（导致/影响/...），polarity 取 Positive/Negative/Neutral，
        confidence 取 High/Medium/Low，evidence 为支撑依据文本。
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
                            "rel": rel.get("关系", rel.type),
                            "target": target,
                            "polarity": rel.get("极性", "Neutral"),
                            "confidence": rel.get("置信度", "Medium"),
                            "evidence": rel.get("支撑依据", ""),
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
    """返回极性对应的 Bootstrap 颜色类。

    真实数据极性取值为 Positive / Negative / Neutral。
    """
    mapping = {
        "Positive": "success",
        "Negative": "danger",
        "Neutral": "secondary",
    }
    return mapping.get(polarity, "secondary")


def confidence_badge(confidence: str) -> str:
    """返回置信度对应的 Bootstrap 颜色类。

    真实数据置信度取值为 High / Medium / Low。
    """
    mapping = {
        "High": "success",
        "Medium": "warning",
        "Low": "danger",
    }
    return mapping.get(confidence, "secondary")


def format_reasoning_chain(chain: list[dict[str, Any]]) -> str:
    """
    将推理链渲染为 HTML/Markdown 字符串。

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
        polarity = step.get("polarity", "Neutral")
        confidence = step.get("confidence", "Medium")
        evidence = step.get("evidence", "")
        lines.append(
            f"- **{source}** —{rel}→ **{target}**"
            f"（{confidence} · {polarity}）"
        )
        if evidence:
            lines.append(f"  - 依据：{evidence}")
    return "\n".join(lines)
