"""流水线端到端单测（需连接真实 Neo4j，连不上则跳过）。"""

from __future__ import annotations

import unittest

from core import config, db
from core.agents.intent_agent import IntentAgent
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
        # 实体解析为空 → 直接边界（用无医学实体的句子；
        # 注：「猫发热怎么办」会因别名扩展命中「发热→持续性发热」而不再走边界）
        r = self.pipeline.run("今天天气怎么样")
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
        # 用无医学实体的句子（「猫发热怎么办」现已命中发热别名，不再走边界）
        resp, trace = self.pipeline.run_with_trace("今天天气怎么样")
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


def _local_backend_available() -> bool:
    """本地 NetworkX 图谱是否可用（构造即构建图，无需 Neo4j）。"""
    try:
        from core.providers.factory import create_provider

        create_provider("local")
        return True
    except Exception:  # noqa: BLE001
        return False


# 六类细分意图：输入 / 期望意图 / 轨迹中文名 / 摘要关键子串 / 是否预期有风险标记
_SPECIAL_CASES = [
    {
        "input": "我的猫肚子大，可能是传腹吗？",
        "intent": Intent.DIAGNOSIS_INQUIRY,
        "display": "诊断可能性判断",
        "summary_sub": ["腹围增大", "疑似", "确诊"],
        "expect_risk": False,
    },
    {
        "input": "腹水是传腹的特征吗？",
        "intent": Intent.SYMPTOM_FEATURE,
        "display": "特征确认",
        "summary_sub": ["腹水", "依据"],
        "expect_risk": False,
    },
    {
        "input": "白球比0.5是传腹吗？",
        "intent": Intent.DIAGNOSTIC_TEST,
        "display": "指标解读",
        "summary_sub": ["白球比", "依据"],
        "expect_risk": False,
    },
    {
        "input": "什么会影响传腹康复？",
        "intent": Intent.RISK_FACTORS,
        "display": "风险因素查询",
        "summary_sub": ["病毒载量", "体重增加"],
        "expect_risk": True,
    },
    {
        "input": "传腹要和哪些病区分？",
        "intent": Intent.DIFFERENTIAL_DIAGNOSIS,
        "display": "鉴别诊断",
        "summary_sub": ["淋巴瘤", "细菌性腹膜炎"],
        "expect_risk": False,
    },
    {
        "input": "有什么药能治传腹？",
        "intent": Intent.DRUG_INFO,
        "display": "药物关联查询",
        "summary_sub": ["GS-441524", "瑞德西韦"],
        "expect_risk": False,
    },
]

# 原有四类医学意图（回归）：确认未被误送入细分意图轨迹格式
_REGRESSION_CASES = [
    {"input": "什么是猫传腹", "intent": Intent.CONCEPT},
    {"input": "湿性FIP怎么治疗", "intent": Intent.TREATMENT},
    {"input": "GS-441524有什么风险", "intent": Intent.RISK},
    {"input": "猫传腹怎么诊断？", "intent": Intent.DIAGNOSIS},
]


@unittest.skipUnless(_local_backend_available(), "本地 NetworkX 图谱不可用，跳过（需 networkx + data/knowledge_graph.json）")
class SpecialIntentTest(unittest.TestCase):
    """六类细分意图 + 原四类医学意图回归：响应层 + 轨迹面板适配。

    使用本地 NetworkX 后端（backend="local"），不依赖 Neo4j 连接。
    """

    def setUp(self) -> None:
        self.pipeline = Pipeline()

    def _steps_by_name(self, trace) -> dict:
        return {s.step_name: s for s in trace.steps}

    def test_special_intents_end_to_end(self) -> None:
        """六类新意图：响应结论正确 + 右侧轨迹七步显示符合适配规则。"""
        for case in _SPECIAL_CASES:
            with self.subTest(input=case["input"]):
                resp, trace = self.pipeline.run_with_trace(case["input"], backend="local")

                # —— 响应层 ——
                self.assertEqual(resp.status, ResponseStatus.OK)
                self.assertEqual(resp.intent, case["intent"])
                self.assertTrue(resp.summary, "摘要不应为空")
                for sub in case["summary_sub"]:
                    self.assertIn(sub, resp.summary, f"摘要应含关键内容：{sub}")

                # —— 轨迹层（保持七步，无边界处理第 8 步）——
                self.assertEqual(len(trace.steps), 7)
                steps = self._steps_by_name(trace)

                # 意图识别
                self.assertEqual(steps["意图识别"].status, "success")
                self.assertEqual(
                    steps["意图识别"].output_summary,
                    f"识别为{case['display']}（{case['intent'].value}）",
                )
                # 任务分配
                self.assertEqual(steps["任务分配"].status, "success")
                self.assertEqual(
                    steps["任务分配"].output_summary,
                    f"选择查询方法：query_{case['intent'].value}",
                )
                # 图查询（N=0 亦为 success）
                self.assertEqual(steps["图查询"].status, "success")
                self.assertRegex(steps["图查询"].output_summary, r"^命中 \d+ 条关系$")
                # 证据加工（专用意图无需分组）
                self.assertEqual(steps["证据加工"].status, "skipped")
                self.assertEqual(steps["证据加工"].skip_reason, "该意图无需证据分组")
                # 风险标记（保持原逻辑）
                risk = steps["风险标记"]
                if case["expect_risk"]:
                    self.assertEqual(risk.status, "success")
                    self.assertRegex(risk.output_summary, r"^识别到 \d+ 个风险标记$")
                else:
                    self.assertEqual(risk.status, "skipped")
                    self.assertEqual(risk.skip_reason, "无风险标记")
                # 响应生成
                self.assertEqual(steps["响应生成"].status, "success")
                self.assertEqual(steps["响应生成"].output_summary, f"生成{case['display']}回复")

    def test_original_intents_regression(self) -> None:
        """原四类医学意图：轨迹格式未被细分意图改造影响。"""
        for case in _REGRESSION_CASES:
            with self.subTest(input=case["input"]):
                resp, trace = self.pipeline.run_with_trace(case["input"], backend="local")

                self.assertEqual(resp.status, ResponseStatus.OK)
                self.assertEqual(resp.intent, case["intent"])
                self.assertTrue(resp.summary, "摘要不应为空")

                steps = self._steps_by_name(trace)
                # 意图识别仍走旧格式（非「识别为…（xxx）」）
                self.assertEqual(
                    steps["意图识别"].output_summary,
                    f"识别意图：{case['intent'].value}",
                )
                # 任务分配仍走通用模板
                self.assertTrue(steps["任务分配"].output_summary.startswith("选定查询模板："))
                # 原意图仍走证据分组（status=success，区别于细分意图的 skipped）
                self.assertEqual(steps["证据加工"].status, "success")
                # 响应生成成功
                self.assertEqual(steps["响应生成"].status, "success")


def _steps_by_name(trace) -> dict:
    """把轨迹步骤按中文名映射到步骤对象。"""
    return {s.step_name: s for s in trace.steps}


# 多跳推理场景：输入 / 期望意图（可为 None 表示仅验证间接关联文案）/ 起点 / 路径关键子串
_MULTIHOP_CASES = [
    {
        "input": "血管通透性增加是传腹的特征吗？",
        "intent": Intent.SYMPTOM_FEATURE,
        "path_sub": ["血管通透性 → 腹水 →", "湿性FIP"],
    },
    {
        "input": "内皮损伤是传腹的特征吗？",
        "intent": Intent.SYMPTOM_FEATURE,
        "path_sub": ["内皮损伤 → 血管通透性 → 腹水 →", "湿性FIP"],
    },
    {
        "input": "内皮损伤可能是传腹吗？",
        "intent": Intent.DIAGNOSIS_INQUIRY,
        "path_sub": ["内皮损伤 → 血管通透性 → 腹水 →", "湿性FIP"],
    },
]

# 原有核心意图回归（本地后端）：输入 / 期望意图 / 是否完整七步
# meta / emergency 为短路意图，仅 4 步（实体解析、图查询均 skipped），其余完整七步
_CORE_REGRESSION_CASES = [
    {"input": "湿性FIP怎么治？", "intent": Intent.TREATMENT, "full": True},
    {"input": "GS-441524有副作用吗？", "intent": Intent.RISK, "full": True},
    {"input": "什么是猫传腹？", "intent": Intent.CONCEPT, "full": True},
    {"input": "你是谁？", "intent": Intent.META, "full": False},
    {"input": "谢谢", "intent": Intent.META, "full": False},
    {"input": "猫快不行了怎么办？", "intent": Intent.EMERGENCY, "full": False},
]


@unittest.skipUnless(_local_backend_available(), "本地 NetworkX 图谱不可用，跳过（需 networkx + data/knowledge_graph.json）")
class MultihopTest(unittest.TestCase):
    """多跳推理：直接查询为空时，通过 A→B→C 返回间接关联结论 + 轨迹适配。"""

    def setUp(self) -> None:
        self.pipeline = Pipeline()

    def test_multihop_indirect_association(self) -> None:
        """多跳场景：返回间接关联回复，摘要含完整推理链。"""
        for case in _MULTIHOP_CASES:
            with self.subTest(input=case["input"]):
                resp, trace = self.pipeline.run_with_trace(case["input"], backend="local")
                self.assertEqual(resp.status, ResponseStatus.OK)
                if case["intent"] is not None:
                    self.assertEqual(resp.intent, case["intent"])
                # 间接关联结论
                self.assertIn("间接关联", resp.summary)
                for sub in case["path_sub"]:
                    self.assertIn(sub, resp.summary, f"推理链应含：{sub}")

    def test_multihop_trace_adapts(self) -> None:
        """多跳发生时：图查询步骤显示「尝试多跳路径」，响应生成显示「生成间接关联回复」。"""
        resp, trace = self.pipeline.run_with_trace(
            "血管通透性增加是传腹的特征吗？", backend="local"
        )
        self.assertEqual(resp.status, ResponseStatus.OK)
        # 仍保持七步，无边界处理第 8 步
        self.assertEqual(len(trace.steps), 7)
        steps = _steps_by_name(trace)
        self.assertEqual(
            steps["图查询"].output_summary,
            "直接查询无结果，尝试多跳路径，命中 2 条",
        )
        self.assertEqual(steps["响应生成"].output_summary, "生成间接关联回复")
        # 证据加工仍 skipped（专用意图无需分组）
        self.assertEqual(steps["证据加工"].status, "skipped")
        self.assertEqual(steps["证据加工"].skip_reason, "该意图无需证据分组")

    def test_direct_query_no_multihop(self) -> None:
        """直接关系命中时：不走多跳，返回直接结论，轨迹显示「命中 N 条关系」。"""
        resp, trace = self.pipeline.run_with_trace("腹水是传腹的特征吗？", backend="local")
        self.assertEqual(resp.status, ResponseStatus.OK)
        self.assertEqual(resp.intent, Intent.SYMPTOM_FEATURE)
        steps = _steps_by_name(trace)
        # 直接命中 1 条，文案不含「多跳」
        self.assertEqual(steps["图查询"].output_summary, "命中 1 条关系")
        self.assertEqual(steps["响应生成"].output_summary, "生成特征确认回复")
        self.assertNotIn("间接关联", resp.summary)
        self.assertIn("是", resp.summary)

    def test_general_handles_unclassified_gracefully(self) -> None:
        """未归类为细分意图（如「会导致传腹吗」落 GENERAL）时，走通用查询、不报错、不误判多跳。"""
        resp, trace = self.pipeline.run_with_trace("内皮损伤会导致传腹吗？", backend="local")
        self.assertEqual(resp.status, ResponseStatus.OK)
        self.assertEqual(resp.intent, Intent.GENERAL)
        steps = _steps_by_name(trace)
        self.assertNotIn("尝试多跳路径", steps["图查询"].output_summary)


@unittest.skipUnless(_local_backend_available(), "本地 NetworkX 图谱不可用，跳过（需 networkx + data/knowledge_graph.json）")
class CoreIntentRegressionTest(unittest.TestCase):
    """原有核心意图回归：本地后端下意图识别与正常流程不受影响。"""

    def setUp(self) -> None:
        self.pipeline = Pipeline()

    def test_core_intents(self) -> None:
        for case in _CORE_REGRESSION_CASES:
            with self.subTest(input=case["input"]):
                resp, trace = self.pipeline.run_with_trace(case["input"], backend="local")
                self.assertEqual(resp.status, ResponseStatus.OK)
                self.assertEqual(resp.intent, case["intent"])
                # 完整意图七步；meta/emergency 为短路意图，仅 4 步
                self.assertEqual(len(trace.steps), 7 if case["full"] else 4)
                self.assertTrue(resp.summary, "摘要不应为空")


class IntentClarifyFixTest(unittest.TestCase):
    """澄清修复回归：细分意图与泛化意图得分接近不再误澄清。

    覆盖精准度优化 Step1 引入的 6 个细分意图与 concept/diagnosis/treatment
    之间的典型冲突问法。本地后端即可运行，不依赖 Neo4j。
    """

    def setUp(self) -> None:
        self.agent = IntentAgent()

    def _classify(self, text: str):
        r = self.agent.run(text)
        return (r.intent.value if r.intent else None), r.need_clarify

    def test_special_intent_cases(self) -> None:
        # (输入, 期望意图, 是否触发澄清)
        cases = [
            ("腹水的特征是什么", "symptom_feature", False),
            ("腹水是传腹的特征吗", "symptom_feature", False),
            ("什么是猫传腹", "concept", False),
            ("猫可能是传腹吗", "diagnosis_inquiry", False),
            ("猫传腹怎么诊断", "diagnosis", False),
            ("白球比0.5是传腹吗", "diagnostic_test", False),
            ("什么会影响传腹康复", "risk_factors", False),
            ("传腹要和哪些病区分", "differential_diagnosis", False),
            ("有什么药能治传腹", "drug_info", False),
            ("湿性FIP怎么治", "treatment", False),
        ]
        for text, exp_intent, exp_clarify in cases:
            with self.subTest(input=text):
                intent, clarify = self._classify(text)
                self.assertEqual(intent, exp_intent)
                self.assertEqual(clarify, exp_clarify)

    def test_clarification_labels_complete(self) -> None:
        # 全部意图（含 6 个细分意图）都应有中文标签，避免澄清时单一/空白选项
        for intent in [
            "treatment", "risk", "concept", "diagnosis", "general",
            "diagnosis_inquiry", "symptom_feature", "diagnostic_test",
            "risk_factors", "differential_diagnosis", "drug_info",
        ]:
            with self.subTest(intent=intent):
                self.assertIn(intent, config.CLARIFICATION_LABELS)
                self.assertTrue(config.CLARIFICATION_LABELS[intent])

    def test_clarify_still_complete_when_tied(self) -> None:
        # 真正歧义（概念 vs 特征问法）仍会澄清，但两意图均有标签 → 选项≥2 且不空白
        intent, clarify = self._classify("猫传腹的特征和区别")
        self.assertTrue(clarify)
        self.assertIsNone(intent)
        # 通过 Pipeline 走边界，确认澄清候选标签完整（修复前 symptom_feature 无标签会单一化）
        resp, _ = Pipeline().run_with_trace("猫传腹的特征和区别", backend="local")
        self.assertEqual(resp.status, ResponseStatus.CLARIFY)
        self.assertTrue(len(resp.clarify_options) >= 2)
        for opt in resp.clarify_options:
            self.assertTrue(opt.label, "澄清选项标签不应为空")


if __name__ == "__main__":
    unittest.main()
