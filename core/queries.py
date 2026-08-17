"""
core.queries —— Cypher 查询模板与意图映射。

定义五个查询模板（对应五类意图），以及意图 → 模板的映射。
每个模板统一返回以下字段（每条记录代表一条关系）：
    source / rel / target / polarity / confidence / evidence

说明：
- CONCEPT 使用固定锚点实体，不依赖 $entities 参数；
- DIAGNOSIS / TREATMENT 全量返回，不依赖 $entities 参数；
- RISK / GENERAL 使用 $entities 参数（列表），由 db.run_query 传入。
"""

from __future__ import annotations

from core.schemas import Intent

CONCEPT_QUERY = """
// 概念 / 机制查询（意图：concept）
// 业务逻辑：
//   1) 从"猫肠道冠状病毒（FECV）"出发，沿 导致 / 表现为 / 影响 关系
//      遍历至 湿性 / 干性 FIP，返回路径上的所有关系（供后续筛选最长路径各一条）。
//   2) 同时返回诱因链：多猫环境 → 猫冠状病毒（FCoV）感染；应激 → 病毒复制。
// 说明：本模板锚点实体固定，不依赖 $entities 参数。
MATCH path = (start:Entity {name: "猫肠道冠状病毒（FECV）"})-[:RELATES*1..12]->(fip:Entity)
WHERE fip.name IN ["湿性猫传染性腹膜炎（湿性FIP）", "干性猫传染性腹膜炎（干性FIP）"]
  AND ALL(r IN relationships(path) WHERE r.关系 IN ["导致", "表现为", "影响"])
WITH relationships(path) AS rels, nodes(path) AS ns
UNWIND range(0, size(rels) - 1) AS i
RETURN ns[i].name AS source,
       rels[i].关系 AS rel,
       ns[i + 1].name AS target,
       rels[i].极性 AS polarity,
       rels[i].置信度 AS confidence,
       rels[i].支撑依据 AS evidence

UNION

// 诱因链：多猫环境 → FCoV 感染；应激 → 病毒复制
MATCH (a:Entity)-[r:RELATES]->(b:Entity)
WHERE (a.name = "多猫环境" AND b.name = "猫冠状病毒（FCoV）感染")
   OR (a.name = "应激" AND b.name = "病毒复制")
RETURN a.name AS source,
       r.关系 AS rel,
       b.name AS target,
       r.极性 AS polarity,
       r.置信度 AS confidence,
       r.支撑依据 AS evidence
""".strip()


DIAGNOSIS_QUERY = """
// 诊断查询（意图：diagnosis）
// 业务逻辑：查询四类诊断关系（全量返回，前端分组展示）：
//   1) 症状表现：表现为 → 疑似 FIP
//   2) 筛查指标：诊断于 → 疑似 FIP
//   3) 确诊金标准：诊断于 / 表现为 → 确诊 FIP（湿性 / 干性）
//   4) 鉴别诊断：疑似 FIP → 排除 淋巴瘤 / 细菌性腹膜炎 / 充血性心力衰竭 等
// 说明：本模板全量返回，不依赖 $entities 参数。
MATCH (a:Entity)-[r:RELATES]->(b:Entity)
WHERE
  // 1) 症状表现：表现为 → 疑似 FIP
  (r.关系 = "表现为" AND b.name STARTS WITH "疑似")
  OR
  // 2) 筛查指标：诊断于 → 疑似 FIP
  (r.关系 = "诊断于" AND b.name STARTS WITH "疑似")
  OR
  // 3) 确诊金标准：诊断于 / 表现为 → 确诊 FIP（湿性 / 干性）
  (r.关系 IN ["诊断于", "表现为"]
     AND b.name IN ["湿性猫传染性腹膜炎（湿性FIP）", "干性猫传染性腹膜炎（干性FIP）"])
  OR
  // 4) 鉴别诊断：疑似 FIP → 排除 其他疾病
  (a.name STARTS WITH "疑似" AND b.name STARTS WITH "排除")
RETURN a.name AS source,
       r.关系 AS rel,
       b.name AS target,
       r.极性 AS polarity,
       r.置信度 AS confidence,
       r.支撑依据 AS evidence
""".strip()


TREATMENT_QUERY = """
// 治疗查询（意图：treatment）
// 业务逻辑：查询四类治疗关系（全量返回，前端分组展示）：
//   1) 药物治疗：药物 → 疾病（治疗于）
//   2) 疾病预后：疾病 / 因素 → 康复 / 死亡 / 复发 / 复发风险（排除疗程与风险因素）
//   3) 疗程支持：疗程 → 康复
//   4) 治疗风险因素：体重增加 → 血药浓度；血脑屏障 → 药物渗透；
//                   病毒清除不全 → 复发；长期免疫抑制 → 复发；
//                   耐药性变异 → 死亡；病毒载量 → 康复
// 说明：本模板全量返回，不依赖 $entities 参数。
// 1) 药物治疗：药物 → 疾病
MATCH (drug:Entity)-[r:RELATES]->(disease:Entity)
WHERE r.关系 = "治疗于"
RETURN drug.name AS source, r.关系 AS rel, disease.name AS target,
       r.极性 AS polarity, r.置信度 AS confidence, r.支撑依据 AS evidence

UNION

// 2) 疾病预后：指向 康复 / 死亡 / 复发 / 复发风险 的结局关系
//    排除疗程/支持治疗节点，并排除风险因素节点，避免与第4部分重叠
MATCH (a:Entity)-[r:RELATES]->(b:Entity)
WHERE b.name IN ["康复", "死亡", "复发", "复发风险"]
  AND NOT (a.name CONTAINS "疗程" OR a.name = "对症支持治疗")
  AND NOT (a.name IN ["病毒清除不全", "长期免疫抑制", "耐药性变异", "病毒载量"])
RETURN a.name AS source, r.关系 AS rel, b.name AS target,
       r.极性 AS polarity, r.置信度 AS confidence, r.支撑依据 AS evidence

UNION

// 3) 疗程支持：疗程 / 对症支持治疗 → 康复
MATCH (regimen:Entity)-[r:RELATES]->(outcome:Entity)
WHERE outcome.name = "康复"
  AND (regimen.name CONTAINS "疗程" OR regimen.name = "对症支持治疗")
RETURN regimen.name AS source, r.关系 AS rel, outcome.name AS target,
       r.极性 AS polarity, r.置信度 AS confidence, r.支撑依据 AS evidence

UNION

// 4) 治疗风险因素：体重增加 → 血药浓度；血脑屏障 → 药物渗透；
//                   病毒清除不全 → 复发；长期免疫抑制 → 复发；
//                   耐药性变异 → 死亡；病毒载量 → 康复
MATCH (factor:Entity)-[r:RELATES]->(effect:Entity)
WHERE (factor.name = "体重增加" AND effect.name = "血药浓度")
   OR (factor.name = "血脑屏障" AND effect.name = "药物渗透")
   OR (factor.name = "病毒清除不全" AND effect.name = "复发")
   OR (factor.name = "长期免疫抑制" AND effect.name = "复发")
   OR (factor.name = "耐药性变异" AND effect.name = "死亡")
   OR (factor.name = "病毒载量" AND effect.name = "康复")
RETURN factor.name AS source, r.关系 AS rel, effect.name AS target,
       r.极性 AS polarity, r.置信度 AS confidence, r.支撑依据 AS evidence
""".strip()


RISK_QUERY = """
// 药物风险查询（意图：risk）
// 业务逻辑：查询指定药物的两类证据（全量返回）：
//   1) 疗效证据：药物 → 疾病，极性 Positive 且置信度 High
//   2) 风险证据：药物 → 风险事件，置信度 Low 或极性 Negative
// 默认药物为 GS-441524（由调用方通过 $entities 传入，为空时兜底为 ["GS-441524"]）。
MATCH (drug:Entity)-[r:RELATES]->(target:Entity)
WHERE drug.name IN $entities
  AND (
    // 疗效证据：极性 Positive 且置信度 High
    (r.极性 = "Positive" AND r.置信度 = "High")
    OR
    // 风险证据：置信度 Low 或极性 Negative
    (r.置信度 = "Low" OR r.极性 = "Negative")
  )
RETURN drug.name AS source, r.关系 AS rel, target.name AS target,
       r.极性 AS polarity, r.置信度 AS confidence, r.支撑依据 AS evidence
""".strip()


GENERAL_QUERY = """
// 通用综合查询（意图：general）
// 业务逻辑：围绕指定实体查询一跳内所有入向和出向关系（全量返回）。
MATCH (a:Entity)-[r:RELATES]->(b:Entity)
WHERE a.name IN $entities OR b.name IN $entities
RETURN a.name AS source, r.关系 AS rel, b.name AS target,
       r.极性 AS polarity, r.置信度 AS confidence, r.支撑依据 AS evidence
""".strip()


# 意图 → 查询模板 映射（供 Orchestrator 使用）
INTENT_TO_QUERY: dict[Intent, str] = {
    Intent.CONCEPT: CONCEPT_QUERY,
    Intent.DIAGNOSIS: DIAGNOSIS_QUERY,
    Intent.TREATMENT: TREATMENT_QUERY,
    Intent.RISK: RISK_QUERY,
    Intent.GENERAL: GENERAL_QUERY,
}


def get_query_template(intent: Intent | str) -> str:
    """根据意图返回对应的查询模板，未知意图回退到通用查询。

    Args:
        intent: Intent 枚举或对应的字符串值（如 "risk"）。

    Returns:
        对应的 Cypher 模板字符串。
    """
    if isinstance(intent, str):
        try:
            intent = Intent(intent)
        except ValueError:
            return GENERAL_QUERY
    return INTENT_TO_QUERY.get(intent, GENERAL_QUERY)
