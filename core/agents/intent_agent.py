"""core.agents.intent_agent —— 意图识别（IntentAgent）。"""

from __future__ import annotations

from core import config
from core.agents.base import Agent
from core.schemas import Intent, IntentResult


class IntentAgent(Agent):
    """基于关键词加权打分识别用户意图，返回 IntentResult。

    逻辑：
    1. 输入转小写，统计每个意图命中的关键词并累加权重（每词权重 10）。
       匹配采用"最长关键词优先 + 覆盖"：长关键词命中后覆盖该区间，
       避免短关键词重复命中长关键词内部子串（如 "安全" vs "安全吗"）。
    2. 最高分为 0 → 返回 general。
    3. 最高分与次高分差值 ≤ 阈值 → 意图不明确，返回候选意图。
    4. 否则返回最高分意图。
    """

    def run(self, user_input: str) -> IntentResult:
        text = user_input.lower()

        scores: dict[str, int] = {}
        for intent_key, keywords in config.INTENT_KEYWORDS_BY_LENGTH_DESC.items():
            score = 0
            # 每组独立的工作副本，供"最长关键词优先 + 覆盖"匹配
            work = text
            for kw in keywords:
                idx = work.find(kw)
                while idx != -1:
                    # 用占位符覆盖已匹配区间，避免短关键词重复命中
                    work = work[:idx] + "#" * len(kw) + work[idx + len(kw):]
                    score += config.INTENT_KEYWORD_WEIGHT
                    idx = work.find(kw)
            scores[intent_key] = score

        # 按得分降序排列（排序稳定，同分时保持定义顺序）
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_key, top_score = ranked[0]
        second_score = ranked[1][1]

        if top_score == 0:
            return IntentResult(intent=Intent.GENERAL, need_clarify=False, scores=scores)

        if top_score - second_score <= config.CLARIFY_THRESHOLD:
            candidates = [Intent(key) for key, s in ranked if s > 0][:3]
            return IntentResult(intent=None, need_clarify=True, candidates=candidates, scores=scores)

        return IntentResult(intent=Intent(top_key), need_clarify=False, scores=scores)
