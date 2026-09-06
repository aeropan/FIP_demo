"""core.agents.base —— Agent 基类。"""

from __future__ import annotations


class Agent:
    """所有 Agent 的基类：提供统一标识与日志入口。

    子类实现 run(...) 方法，输入输出遵循 core.schemas 定义的数据结构。
    各 Agent 保持无状态、无副作用，便于单元测试与流水线编排。
    """

    @property
    def name(self) -> str:
        """Agent 名称（类名），用于日志标识。"""
        return type(self).__name__

    def log(self, message: str) -> None:
        """打印带 Agent 名称前缀的日志。"""
        print(f"[{self.name}] {message}")
