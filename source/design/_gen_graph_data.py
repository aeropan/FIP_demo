import re
import json
from collections import Counter

txt = open('source/neo4j/FIP_data.txt', encoding='utf-8').read()
pat = re.compile(r'\{h:"(.*?)", r:"(.*?)", t:"(.*?)", p:"(.*?)", c:"(.*?)", e:"(.*?)"\}')
rows = [m.groups() for m in pat.finditer(txt)]

seen = set()
edges = []
for h, r, t, p, c, e in rows:
    if (h, r, t) in seen:
        continue
    seen.add((h, r, t))
    edges.append({'h': h, 'r': r, 't': t, 'p': p, 'c': c, 'e': e})

# ---- 四类节点映射（按设计文档 6.1 规则） ----
TYPE_ETIOLOGY = "病因与病原"      # 病毒、基因、环境诱因、风险因素
TYPE_MECH = "机制与过程"          # 病理生理过程、中间环节、疾病本体
TYPE_DIAG = "诊断与检测"          # 症状、体征、实验室检查、鉴别诊断
TYPE_INTERV = "干预与结局"        # 药物、疗程、治疗结果、风险事件

ENTITY_TYPE_MAP = {}

for n in [
    "猫肠道冠状病毒（FECV）", "猫传染性腹膜炎病毒（FIPV）", "I型猫冠状病毒",
    "II型猫冠状病毒", "猫冠状病毒（FCoV）感染", "3c基因", "S基因突变",
    "多猫环境", "应激", "耐药性变异",
]:
    ENTITY_TYPE_MAP[n] = TYPE_ETIOLOGY

for n in [
    "病毒复制", "巨噬细胞", "全身性扩散", "免疫复合物", "血管炎", "内皮损伤",
    "血管通透性", "腹水", "慢性炎症", "肉芽肿", "病毒清除不全", "长期免疫抑制",
    "血脑屏障", "药物渗透", "血药浓度", "病毒载量", "体重增加",
    "湿性猫传染性腹膜炎（湿性FIP）", "干性猫传染性腹膜炎（干性FIP）",
    "复发性猫传染性腹膜炎",
]:
    ENTITY_TYPE_MAP[n] = TYPE_MECH

for n in [
    "持续性发热", "腹围增大", "呼吸困难", "葡萄膜炎", "共济失调", "癫痫发作",
    "白球比（A:G比值）", "白球比（A:G比值）低于0.6", "血清淀粉样蛋白A（SAA）",
    "血清淀粉样蛋白A（SAA）显著升高", "Rivalta试验", "Rivalta试验阳性",
    "积液中猫冠状病毒RT-PCR阳性", "免疫组化（IHC）", "组织病理学（肉芽肿）",
    "免疫细胞化学（ICC）", "α-1酸性糖蛋白（AGP）", "淋巴细胞减少",
    "粘稠草黄色积液", "渗出液高蛋白（>35g/L）", "疑似猫传染性腹膜炎",
    "疑似湿性猫传染性腹膜炎", "疑似干性猫传染性腹膜炎",
    "排除淋巴瘤", "排除细菌性腹膜炎", "排除充血性心力衰竭",
]:
    ENTITY_TYPE_MAP[n] = TYPE_DIAG

for n in [
    "GS-441524", "瑞德西韦", "莫努匹拉韦", "GC376", "伊曲康唑",
    "84天标准疗程", "42天短疗程", "对症支持治疗", "康复", "死亡", "复发",
    "复发风险", "大细胞淋巴瘤", "尿结石",
]:
    ENTITY_TYPE_MAP[n] = TYPE_INTERV

# ---- 组装 nodes ----
nodes_set = set()
for e in edges:
    nodes_set.add(e['h'])
    nodes_set.add(e['t'])

missing = [n for n in nodes_set if n not in ENTITY_TYPE_MAP]
if missing:
    print("!! 未归类节点:", missing)

nodes = []
for n in sorted(nodes_set):
    nodes.append({
        "id": n,
        "label": n,
        "type": ENTITY_TYPE_MAP.get(n, TYPE_MECH),
    })

edges_out = []
for e in edges:
    edges_out.append({
        "source": e['h'],
        "target": e['t'],
        "rel": e['r'],
        "polarity": e['p'],
        "confidence": e['c'],
        "evidence": e['e'],
    })

data = {"nodes": nodes, "edges": edges_out}
with open('source/design/graph-data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print("nodes:", len(nodes), "edges:", len(edges_out))
print("type dist:", Counter(n['type'] for n in nodes))
print("pol dist:", Counter(e['polarity'] for e in edges_out))
print("conf dist:", Counter(e['confidence'] for e in edges_out))
