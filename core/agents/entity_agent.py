"""core.agents.entity_agent —— 实体解析（EntityAgent）。"""

from __future__ import annotations

from core import config
from core.agents.base import Agent


class EntityAgent(Agent):
    """将用户口语解析为图谱标准实体名列表。

    规则：
    - 大小写不敏感；
    - 最长别名优先：按别名长度降序匹配，命中后将该区间用占位符覆盖，
      避免短别名重复命中长别名内部子串；
    - 返回标准实体名列表（去重，保留首次命中顺序）。
    """

    def run(self, user_input: str) -> list[str]:
        if not user_input:
            return []

        text = user_input.lower()
        result: list[str] = []
        seen: set[str] = set()

        for alias in config.ALIASES_BY_LENGTH_DESC:
            key = alias.lower()
            idx = text.find(key)
            while idx != -1:
                # 用占位符覆盖已匹配区间，防止短别名重复命中
                text = text[:idx] + "#" * len(key) + text[idx + len(key):]
                for entity in config.ALIAS_MAP[alias]:
                    if entity not in seen:
                        seen.add(entity)
                        result.append(entity)
                idx = text.find(key)

        return result
