"""查询模板与数据访问单测（需连接真实 Neo4j，连不上则跳过）。"""

from __future__ import annotations

import unittest

from core import db
from core.queries import (
    CONCEPT_QUERY,
    DIAGNOSIS_QUERY,
    GENERAL_QUERY,
    RISK_QUERY,
    TREATMENT_QUERY,
    get_query_template,
)
from core.schemas import Intent, ReasoningStep


@unittest.skipUnless(db.test_connection()["ok"], "Neo4j 未连接，跳过")
class QueryTest(unittest.TestCase):
    """查询模板与 run_query。"""

    def test_templates_defined(self) -> None:
        for tpl in (CONCEPT_QUERY, DIAGNOSIS_QUERY, TREATMENT_QUERY, RISK_QUERY, GENERAL_QUERY):
            self.assertIn("RELATES", tpl)

    def test_get_query_template(self) -> None:
        self.assertEqual(get_query_template(Intent.RISK), RISK_QUERY)
        self.assertEqual(get_query_template("diagnosis"), DIAGNOSIS_QUERY)
        self.assertEqual(get_query_template("unknown"), GENERAL_QUERY)

    def test_run_query_counts(self) -> None:
        self.assertEqual(len(db.run_query(CONCEPT_QUERY, [])), 15)
        self.assertEqual(len(db.run_query(DIAGNOSIS_QUERY, [])), 25)
        self.assertEqual(len(db.run_query(TREATMENT_QUERY, [])), 21)
        self.assertEqual(len(db.run_query(RISK_QUERY, ["GS-441524"])), 4)
        self.assertEqual(len(db.run_query(GENERAL_QUERY, ["GS-441524"])), 4)

    def test_run_query_returns_steps(self) -> None:
        steps = db.run_query(RISK_QUERY, ["GS-441524"])
        self.assertTrue(all(isinstance(s, ReasoningStep) for s in steps))

    def test_empty_entities_returns_empty(self) -> None:
        # GENERAL_QUERY 需要实体，空实体应返回空列表
        self.assertEqual(db.run_query(GENERAL_QUERY, []), [])


if __name__ == "__main__":
    unittest.main()
