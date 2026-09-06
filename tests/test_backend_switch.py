"""后端数据源切换：create_provider 与 Pipeline.run(backend=...) 的本地验证。

不依赖 Neo4j：local 模式完全离线；neo4j 模式仅校验工厂返回类型（不触发真实连接）。
"""

from __future__ import annotations

import unittest

from core.pipeline import Pipeline
from core.providers.base import GraphProvider
from core.providers.factory import create_provider
from core.schemas import Intent, ResponseStatus


class CreateProviderTest(unittest.TestCase):
    """工厂函数：按后端标识返回对应 Provider 类型。"""

    def test_local(self) -> None:
        from core.providers.local_graph_provider import LocalGraphProvider

        self.assertIsInstance(create_provider("local"), LocalGraphProvider)

    def test_neo4j_type_only(self) -> None:
        # 仅校验类型，不触发真实连接（Neo4jGraphProvider 懒加载）
        from core.providers.neo4j_graph_provider import Neo4jGraphProvider

        prov = create_provider("neo4j")
        self.assertIsInstance(prov, Neo4jGraphProvider)
        self.assertIsInstance(prov, GraphProvider)

    def test_unknown_falls_back_to_local(self) -> None:
        from core.providers.local_graph_provider import LocalGraphProvider

        self.assertIsInstance(create_provider("whatever"), LocalGraphProvider)


class PipelineBackendSwitchTest(unittest.TestCase):
    """Pipeline.run 透传 backend 参数（默认 local，不修改全局配置）。"""

    def setUp(self) -> None:
        self.pipeline = Pipeline()

    def test_default_is_local(self) -> None:
        r = self.pipeline.run("猫传腹怎么诊断")
        self.assertEqual(r.status, ResponseStatus.OK)
        self.assertEqual(r.intent, Intent.DIAGNOSIS)

    def test_explicit_local(self) -> None:
        r = self.pipeline.run("猫传腹怎么治疗", backend="local")
        self.assertEqual(r.status, ResponseStatus.OK)
        self.assertEqual(r.intent, Intent.TREATMENT)

    def test_backend_shortcuts_untouched(self) -> None:
        # meta / emergency 在图查询前已短路，与 backend 无关
        self.assertEqual(self.pipeline.run("你好").intent, Intent.META)
        self.assertEqual(self.pipeline.run("快不行了救救它").intent, Intent.EMERGENCY)

    def test_full_graph_via_create_provider(self) -> None:
        full = create_provider("local").get_full_graph()
        self.assertEqual(len(full["nodes"]), 70)
        self.assertEqual(len(full["edges"]), 68)


if __name__ == "__main__":
    unittest.main()
