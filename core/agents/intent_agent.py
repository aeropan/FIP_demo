"""core.agents.intent_agent —— 意图识别（IntentAgent）。"""

from __future__ import annotations

from core import config
from core.agents.base import Agent
from core.schemas import Intent, IntentResult


class IntentAgent(Agent):
    """基于关键词加权打分识别用户意图，返回 IntentResult。

    逻辑：
    1. 输入转小写，统计每个意图命中的关键词并累加权重。
       - 医学意图使用 INTENT_KEYWORD_WEIGHT（10）。
       - meta 意图使用 META_KEYWORD_WEIGHT（5），确保医学意图优先。
       - risk_factors 使用 RISK_FACTORS_WEIGHT（13），压过 treatment 的「康复」重叠。
       匹配采用"最长关键词优先 + 覆盖"：长关键词命中后覆盖该区间，
       避免短关键词重复命中长关键词内部子串（如 "安全" vs "安全吗"）。
    1.5 基础打分后应用 SPECIAL_PATTERNS 精确短语加成（每细分意图最多 +5 一次），
       使具体意图在典型问法下压过泛化意图（概念/诊断/治疗等），减少误澄清。
    2. 最高分为 0 → 返回 general。
    3. 最高分与次高分差值 ≤ 阈值 → 意图不明确，返回候选意图。
    4. 否则返回最高分意图。若为 meta，则进一步匹配子场景。
    """

    def run(self, user_input: str) -> IntentResult:
        text = user_input.lower()

        scores: dict[str, int] = {}
        for intent_key, keywords in config.INTENT_KEYWORDS_BY_LENGTH_DESC.items():
            # 权重：emergency 最高，meta 最低，其余医学意图居中
            if intent_key == "emergency":
                weight = config.EMERGENCY_KEYWORD_WEIGHT
            elif intent_key == "meta":
                weight = config.META_KEYWORD_WEIGHT
            elif intent_key == "risk_factors":
                weight = config.RISK_FACTORS_WEIGHT
            else:
                weight = config.INTENT_KEYWORD_WEIGHT

            score = 0
            # 每组独立的工作副本，供"最长关键词优先 + 覆盖"匹配
            work = text
            for kw in keywords:
                idx = work.find(kw)
                while idx != -1:
                    # 用占位符覆盖已匹配区间，避免短关键词重复命中
                    work = work[:idx] + "#" * len(kw) + work[idx + len(kw):]
                    score += weight
                    idx = work.find(kw)
            scores[intent_key] = score

        # 特殊短语加成：在基础打分之后、排序之前，对命中精确短语的细分意图
        # 追加一次加权（每意图最多 +SPECIAL_PATTERN_BONUS 一次），使具体意图
        # 在典型问法下压过较泛化的意图，减少误澄清。不影响 meta / emergency。
        for sp_intent, phrases in config.SPECIAL_PATTERNS.items():
            if scores.get(sp_intent, 0) > 0 and any(p in text for p in phrases):
                scores[sp_intent] += config.SPECIAL_PATTERN_BONUS

        # 按得分降序排列；同分时按 INTENT_PRIORITY 优先（更具体的细分意图靠前），
        # 并保障 emergency 优先、meta 置后。
        _priority_map = {k: i for i, k in enumerate(config.INTENT_PRIORITY)}
        ranked = sorted(
            scores.items(),
            key=lambda kv: (
                -kv[1],
                kv[0] != "emergency",
                _priority_map.get(kv[0], 100),
                kv[0] == "meta",
            ),
        )
        top_key, top_score = ranked[0]
        second_score = ranked[1][1]

        if top_score == 0:
            return IntentResult(
                intent=Intent.GENERAL,
                need_clarify=False,
                scores=scores,
            )

        # 阶段五：强意图直判 —— 对 4 个高频细分意图，若输入命中其 SPECIAL_PATTERNS
        # 强模式、且其得分与最高分差值 <= CLARIFY_THRESHOLD，则直接选择该意图，
        # 跳过澄清。不影响 emergency / meta（由权重与短路逻辑单独处理）。
        _STRONG_DIRECT_INTENTS = {
            "disease_features", "diagnosis_inquiry", "symptom_feature", "diagnostic_test",
        }
        strong_candidates = [
            k for k in _STRONG_DIRECT_INTENTS
            if scores.get(k, 0) > 0 and any(p in text for p in config.SPECIAL_PATTERNS.get(k, []))
        ]
        if strong_candidates:
            best_strong = max(
                strong_candidates,
                key=lambda k: (scores[k], -_priority_map.get(k, 100)),
            )
            if top_score - scores[best_strong] <= config.CLARIFY_THRESHOLD:
                return IntentResult(
                    intent=Intent(best_strong),
                    need_clarify=False,
                    scores=scores,
                )

        if top_score - second_score <= config.CLARIFY_THRESHOLD:
            candidates = [Intent(key) for key, s in ranked if s > 0][:3]
            return IntentResult(
                intent=None,
                need_clarify=True,
                candidates=candidates,
                scores=scores,
            )

        # 正常返回最高分意图
        meta_subtype: str | None = None
        if top_key == "meta":
            meta_subtype = self._detect_meta_subtype(text)

        return IntentResult(
            intent=Intent(top_key),
            need_clarify=False,
            scores=scores,
            meta_subtype=meta_subtype,
        )

    @staticmethod
    def _detect_meta_subtype(text: str) -> str | None:
        """根据 meta 子场景关键词匹配具体类型。"""
        for subtype, keywords in config.META_SUBTYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return subtype
        return None