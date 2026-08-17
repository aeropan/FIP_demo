"""
core.db —— Neo4j 数据访问层。

负责从 .env 读取连接配置、创建驱动、执行 Cypher 查询，
并把原始记录转换为 core.schemas.ReasoningStep 强类型数据。

对外能力：
1. test_connection：测试 Neo4j 连接是否可用。
2. run_query：执行查询模板，返回去重后的推理步骤列表。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from core.schemas import ReasoningStep

# 显式指定 .env 位置（项目根目录），避免依赖当前工作目录
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# 延迟初始化的 Neo4j 驱动实例（进程内单例）
_driver: GraphDatabase.driver | None = None


def _get_driver() -> GraphDatabase.driver | None:
    """延迟初始化 Neo4j 驱动；缺少密码时不创建连接。"""
    global _driver
    if _driver is None and NEO4J_PASSWORD:
        _driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
            # 连接保活：减少长空闲后连接被服务端回收导致的连接/会话失效
            max_connection_lifetime=3600,
            keep_alive=True,
            connection_acquisition_timeout=30,
        )
    return _driver


def test_connection() -> dict[str, Any]:
    """测试 Neo4j 连接是否可用，返回 {"ok": bool, "error": str|None}。"""
    driver = _get_driver()
    if not driver:
        return {"ok": False, "error": "未配置 NEO4J_PASSWORD"}
    try:
        with driver.session() as session:
            session.run("RETURN 1 AS ok").single()
        return {"ok": True, "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


# 连接/会话失效类异常：命中时关闭旧驱动并重试一次
_RETRYABLE_EXCEPTIONS = (ServiceUnavailable, SessionExpired)


def _close_driver() -> None:
    """关闭并重置驱动单例，供下次 _get_driver 重新建立连接。"""
    global _driver
    if _driver is not None:
        try:
            _driver.close()
        except Exception:  # noqa: BLE001 关闭失败不阻断后续重试
            pass
        _driver = None


def _run_on_driver(
    driver: GraphDatabase.driver,
    query_template: str,
    entities: list[str],
) -> list[ReasoningStep]:
    """在给定驱动上执行查询并组装 ReasoningStep 列表。"""
    with driver.session() as session:
        result = session.run(query_template, entities=list(entities))
        steps: list[ReasoningStep] = []
        seen: set[tuple[str, str, str]] = set()
        for record in result:
            source = record.get("source", "?")
            rel = record.get("rel", "?")
            target = record.get("target", "?")
            key = (source, rel, target)
            if key in seen:
                continue
            seen.add(key)
            steps.append(
                ReasoningStep(
                    source=source,
                    rel=rel,
                    target=target,
                    polarity=record.get("polarity", "Neutral"),
                    confidence=record.get("confidence", "Medium"),
                    evidence=record.get("evidence", ""),
                )
            )
        return steps


def run_query(query_template: str, entities: list[str]) -> list[ReasoningStep]:
    """执行 Cypher 查询并返回结构化推理步骤列表。

    每条 ReasoningStep 代表一条关系：
        source      起始实体名
        rel         关系类型（导致 / 影响 / 表现为 / 诊断于 / 治疗于）
        target      目标实体名
        polarity    极性（Positive / Negative / Neutral）
        confidence  置信度（High / Medium / Low）
        evidence    支撑依据

    同一 (source, rel, target) 只保留首次命中，避免变长路径展开产生重复。

    Args:
        query_template: Cypher 模板字符串，可包含 $entities 参数。
        entities: 解析出的标准实体名列表。

    Returns:
        ReasoningStep 列表；连接未配置或查询异常时抛出异常（由调用方区分失败与空结果）。

    连接/会话失效（ServiceUnavailable / SessionExpired）时关闭旧驱动并重试一次，
    重试后仍失败则异常向上传播，交由调用方处理。
    """
    driver = _get_driver()
    if not driver:
        raise RuntimeError("Neo4j 未配置连接（缺少 NEO4J_PASSWORD）")

    try:
        return _run_on_driver(driver, query_template, entities)
    except _RETRYABLE_EXCEPTIONS:
        # 连接/会话失效：关闭旧驱动并重建，重试一次
        _close_driver()
        driver = _get_driver()
        if not driver:
            raise RuntimeError("Neo4j 未配置连接（缺少 NEO4J_PASSWORD）")
        return _run_on_driver(driver, query_template, entities)
