"""流水线端到端单测（需连接真实 Neo4j，连不上则跳过）。"""

from __future__ import annotations

import unittest

from core import db
from core.pipeline import Pipeline
from core.schemas import BoundaryReason, Intent, ResponseStatus


@unittest.skipUnless(db.test_connection()["ok"], "Neo4j 未连接，跳过")
class PipelineTest(unittest.TestCase):
    """Pipeline 端到端：五意图 + 边界 + 澄清。"""

    def setUp(self) -> None:
        self.pipeline = Pipeline()

    def test_concept(self) -> None:
        r = self.pipeline.run("猫传腹是怎么导致的？")
        self.assertEqual(r.status, ResponseStatus.OK)
        self.assertEqual(r.intent, Intent.CONCEPT)

    def test_diagnosis(self) -> None:
        r = self.pipeline.run("猫传腹怎么诊断？")
        self.assertEqual(r.status, ResponseStatus.OK)
        self.assertEqual(r.intent, Intent.DIAGNOSIS)

    def test_treatment(self) -> None:
        r = self.pipeline.run("猫传腹怎么治疗？")
        self.assertEqual(r.status, ResponseStatus.OK)
        self.assertEqual(r.intent, Intent.TREATMENT)

    def test_risk(self) -> None:
        r = self.pipeline.run("441有什么副作用？")
        self.assertEqual(r.status, ResponseStatus.OK)
        self.assertEqual(r.intent, Intent.RISK)

    def test_boundary_no_entities(self) -> None:
        # 实体解析为空 → 直接边界，跳过意图识别
        r = self.pipeline.run("猫发热怎么办")
        self.assertEqual(r.status, ResponseStatus.BOUNDARY)
        self.assertEqual(r.boundary_reason, BoundaryReason.NO_ENTITIES)

    def test_clarify(self) -> None:
        r = self.pipeline.run("猫传腹怎么治疗有什么风险")
        self.assertEqual(r.status, ResponseStatus.CLARIFY)
        self.assertTrue(r.clarify_options)

    def test_clarify_option_encodes_entities(self) -> None:
        # 澄清选项的 value 应编码当前解析到的实体
        r = self.pipeline.run("441安全吗？能治好吗？")
        self.assertEqual(r.status, ResponseStatus.CLARIFY)
        self.assertEqual(r.entities, ["GS-441524"])
        for opt in r.clarify_options:
            self.assertIn("|entities:GS-441524", opt.value)

    def test_clarify_click_roundtrip(self) -> None:
        # 模拟点击澄清选项：value 回传后应恢复意图与实体并执行查询
        r = self.pipeline.run("441安全吗？能治好吗？")
        risk_opt = next(o for o in r.clarify_options if o.value.startswith("intent:risk"))
        clicked = self.pipeline.run(risk_opt.value)
        self.assertEqual(clicked.status, ResponseStatus.OK)
        self.assertEqual(clicked.intent, Intent.RISK)
        self.assertEqual(clicked.entities, ["GS-441524"])
        total = sum(len(g.steps) for g in clicked.groups)
        self.assertEqual(total, 4)

    def test_cards_render_ready(self) -> None:
        r = self.pipeline.run("441有什么副作用？")
        step = r.cards[0]["steps"][0]
        for key in ("source", "rel", "target", "polarity_color", "confidence_color", "flagged"):
            self.assertIn(key, step)

    def test_summary_not_statistical(self) -> None:
        # 摘要应为自然语言，不应包含「共 X 条」这类统计表达
        import re

        for q in ("猫传腹怎么治疗？", "猫传腹怎么诊断？", "猫传腹是怎么导致的？", "441有什么副作用？", "GS-441524"):
            r = self.pipeline.run(q)
            if r.status == ResponseStatus.OK:
                self.assertIsNone(
                    re.search(r"共\s*\d+\s*条", r.summary),
                    f"{q} 的摘要含统计表达：{r.summary}",
                )


@unittest.skipUnless(db.test_connection()["ok"], "Neo4j 未连接，跳过")
class PipelineTraceTest(unittest.TestCase):
    """run_with_trace 执行轨迹：完整成功 / 短路 / 澄清 / 复合输入。"""

    def setUp(self) -> None:
        self.pipeline = Pipeline()

    def _status_by_name(self, trace, step_name: str) -> str | None:
        for s in trace.steps:
            if s.step_name == step_name:
                return s.status
        return None

    def test_full_success(self) -> None:
        resp, trace = self.pipeline.run_with_trace("猫传腹怎么治疗？")
        self.assertEqual(resp.status, ResponseStatus.OK)
        self.assertEqual(len(trace.steps), 7)  # 7 步全 success，无边界处理
        self.assertTrue(all(s.status == "success" for s in trace.steps))

    def test_boundary_short_circuit(self) -> None:
        resp, trace = self.pipeline.run_with_trace("猫发热怎么办")
        self.assertEqual(resp.status, ResponseStatus.BOUNDARY)
        self.assertEqual(self._status_by_name(trace, "实体解析"), "success")
        # 实体为空也执行意图识别（用于判断是否继承上下文），识别为 general
        self.assertEqual(self._status_by_name(trace, "意图识别"), "success")
        self.assertEqual(self._status_by_name(trace, "任务分配"), "skipped")
        self.assertEqual(self._status_by_name(trace, "边界处理"), "success")

    def test_context_inheritance(self) -> None:
        """连续对话：实体为空 + 意图明确 + 有上下文 → 继承实体。"""
        ctx = ["湿性猫传染性腹膜炎（湿性FIP）", "干性猫传染性腹膜炎（干性FIP）"]
        resp, trace = self.pipeline.run_with_trace("怎么治疗", context_entities=ctx)
        self.assertEqual(resp.status, ResponseStatus.OK)
        self.assertEqual(resp.intent, Intent.TREATMENT)
        self.assertEqual(resp.entities, ctx)
        entity_step = next(s for s in trace.steps if s.step_name == "实体解析")
        self.assertIn("继承上一轮实体", entity_step.output_summary)

    def test_general_no_inherit(self) -> None:
        """实体为空 + 意图 general → 不继承上下文，返回边界。"""
        ctx = ["湿性猫传染性腹膜炎（湿性FIP）", "干性猫传染性腹膜炎（干性FIP）"]
        resp, trace = self.pipeline.run_with_trace("今天天气怎么样", context_entities=ctx)
        self.assertEqual(resp.status, ResponseStatus.BOUNDARY)
        self.assertEqual(self._status_by_name(trace, "意图识别"), "success")

    def test_clarify_skips_rest(self) -> None:
        resp, trace = self.pipeline.run_with_trace("441安全吗？能治好吗？")
        self.assertEqual(resp.status, ResponseStatus.CLARIFY)
        self.assertEqual(self._status_by_name(trace, "意图识别"), "success")
        self.assertEqual(self._status_by_name(trace, "任务分配"), "skipped")
        task_step = next(s for s in trace.steps if s.step_name == "任务分配")
        self.assertEqual(task_step.skip_reason, "意图不明确，等待用户澄清")

    def test_composite_input_skips_parsing(self) -> None:
        resp, trace = self.pipeline.run_with_trace("intent:risk|entities:GS-441524")
        self.assertEqual(resp.status, ResponseStatus.OK)
        self.assertEqual(trace.input_type, "复合澄清输入")
        entity_step = next(s for s in trace.steps if s.step_name == "实体解析")
        self.assertEqual(entity_step.status, "skipped")
        self.assertEqual(entity_step.skip_reason, "复合澄清输入已指定实体：GS-441524")
        intent_step = next(s for s in trace.steps if s.step_name == "意图识别")
        self.assertEqual(intent_step.status, "skipped")
        self.assertEqual(intent_step.skip_reason, "复合澄清输入已指定意图：risk")

    def test_run_backward_compatible(self) -> None:
        # run() 仍返回 AgentResponse，与 run_with_trace 的结果一致
        r1 = self.pipeline.run("441有什么副作用？")
        r2, _ = self.pipeline.run_with_trace("441有什么副作用？")
        self.assertEqual(r1.status, r2.status)
        self.assertEqual(r1.intent, r2.intent)


if __name__ == "__main__":
    unittest.main()
