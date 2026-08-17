"""语义识别层纯规则单测（不依赖网络）。"""

from __future__ import annotations

import unittest

from core import config
from core.agents import EntityAgent, IntentAgent
from core.schemas import Intent


class EntityAgentTest(unittest.TestCase):
    """实体解析：别名映射、最长别名优先、边界。"""

    def setUp(self) -> None:
        self.agent = EntityAgent()

    def test_alias_fip(self) -> None:
        self.assertEqual(
            self.agent.run("猫传腹"),
            ["湿性猫传染性腹膜炎（湿性FIP）", "干性猫传染性腹膜炎（干性FIP）"],
        )

    def test_alias_drug_441(self) -> None:
        self.assertEqual(self.agent.run("441有什么副作用"), ["GS-441524"])

    def test_longest_alias_first(self) -> None:
        # "猫传染性腹膜炎病毒" 应命中 FIPV，而非被 "猫传染性腹膜炎" 抢先
        self.assertEqual(self.agent.run("猫传染性腹膜炎病毒"), ["猫传染性腹膜炎病毒（FIPV）"])
        # "gs-441524" 应命中 GS-441524，而非 "441"
        self.assertEqual(self.agent.run("gs-441524"), ["GS-441524"])

    def test_case_insensitive(self) -> None:
        self.assertEqual(self.agent.run("干性FIP"), ["干性猫传染性腹膜炎（干性FIP）"])

    def test_empty(self) -> None:
        self.assertEqual(self.agent.run("猫发热怎么办"), [])


class IntentAgentTest(unittest.TestCase):
    """意图识别：五类意图、澄清、兜底。"""

    def setUp(self) -> None:
        self.agent = IntentAgent()

    def test_concept(self) -> None:
        r = self.agent.run("猫传腹是怎么导致的？")
        self.assertEqual(r.intent, Intent.CONCEPT)
        self.assertFalse(r.need_clarify)

    def test_diagnosis(self) -> None:
        self.assertEqual(self.agent.run("猫传腹怎么诊断？").intent, Intent.DIAGNOSIS)

    def test_treatment(self) -> None:
        self.assertEqual(self.agent.run("猫传腹怎么治疗？").intent, Intent.TREATMENT)

    def test_risk(self) -> None:
        self.assertEqual(self.agent.run("441有什么副作用？").intent, Intent.RISK)

    def test_general_fallback(self) -> None:
        r = self.agent.run("GS-441524")
        self.assertEqual(r.intent, Intent.GENERAL)
        self.assertFalse(r.need_clarify)

    def test_clarify_tie(self) -> None:
        r = self.agent.run("猫传腹怎么治疗有什么风险")
        self.assertTrue(r.need_clarify)
        self.assertIsNone(r.intent)
        self.assertIn(Intent.TREATMENT, r.candidates)
        self.assertIn(Intent.RISK, r.candidates)

    def test_colloquial_treatment(self) -> None:
        # "怎么治" 口语化命中 treatment
        self.assertEqual(self.agent.run("湿性FIP怎么治").intent, Intent.TREATMENT)

    def test_colloquial_concept(self) -> None:
        # "什么是" 口语化命中 concept
        self.assertEqual(self.agent.run("什么是猫传腹？").intent, Intent.CONCEPT)

    def test_clarify_safety_and_cure(self) -> None:
        # "安全吗"（risk）与 "能治好吗"（treatment）各 10 分 → 触发澄清
        r = self.agent.run("441安全吗？能治好吗？")
        self.assertTrue(r.need_clarify)
        self.assertIn(Intent.RISK, r.candidates)
        self.assertIn(Intent.TREATMENT, r.candidates)

    def test_no_substring_double_count(self) -> None:
        # "安全吗" 命中后不应再重复命中 "安全"：risk 得分应为 10 而非 20
        r = self.agent.run("441安全吗")
        self.assertEqual(r.scores["risk"], 10)


class ConfigTest(unittest.TestCase):
    """配置数据完整性。"""

    def test_polarity_color(self) -> None:
        self.assertEqual(config.POLARITY_COLOR["Positive"], "green")
        self.assertEqual(config.POLARITY_COLOR["Negative"], "red")
        self.assertEqual(config.POLARITY_COLOR["Neutral"], "gray")

    def test_alias_sorted_longest_first(self) -> None:
        order = config.ALIASES_BY_LENGTH_DESC
        self.assertLess(order.index("gs-441524"), order.index("441"))
        self.assertLess(order.index("猫传染性腹膜炎病毒"), order.index("猫传染性腹膜炎"))


if __name__ == "__main__":
    unittest.main()
