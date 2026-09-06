"""Neo4j Aura 保活心跳脚本。

通过执行一个极轻量的写查询（MERGE + SET），让 Aura Free 实例识别为"有活动"，
避免连续 72 小时无写入后被自动 pause。

运行方式：
- GitHub Actions：由 .github/workflows/aura-heartbeat.yml 调度执行，从仓库 Secrets 读取凭据。
- 本地调试：
  set NEO4J_URI=<...>
  set NEO4J_USERNAME=<...>
  set NEO4J_PASSWORD=<...>
  python scripts/aura_heartbeat.py
"""

from __future__ import annotations

import os
import sys

from neo4j import GraphDatabase


def run_heartbeat() -> None:
    """连接 Neo4j 并写入一个心跳节点。"""
    uri = os.environ["NEO4J_URI"]
    username = os.environ["NEO4J_USERNAME"]
    password = os.environ["NEO4J_PASSWORD"]

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session() as session:
            result = session.run(
                """
                MERGE (h:Heartbeat {id: 'keepalive'})
                SET h.last_check = datetime(),
                    h.count = coalesce(h.count, 0) + 1
                RETURN h.last_check AS last_check, h.count AS count
                """
            )
            record = result.single()
            if record is None:
                print("Heartbeat returned no record.")
                sys.exit(1)
            print(
                f"Heartbeat OK: last_check={record['last_check']}, "
                f"count={record['count']}"
            )
    finally:
        driver.close()


if __name__ == "__main__":
    run_heartbeat()
