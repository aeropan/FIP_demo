// 清空已有数据
MATCH (n) DETACH DELETE n;

// 创建节点
CREATE (fcov:Factor {name: '猫冠状病毒感染', en: 'Feline coronavirus infection', description: '猫肠道冠状病毒（FCoV）感染是发生FIP的前提条件。'})
CREATE (mut:Factor {name: '病毒突变', en: 'Viral mutation', description: 'FCoV在猫体内发生突变，获得感染巨噬细胞的能力。'})
CREATE (stress:Factor {name: '应激', en: 'Stress', description: '环境变化、手术、换粮等应激可抑制免疫。'})
CREATE (young:Factor {name: '幼龄', en: 'Young age', description: '2岁以下猫咪免疫发育不完善，发病率更高。'})
CREATE (multi:Factor {name: '多猫环境', en: 'Multi-cat environment', description: '多猫家庭或猫舍更易传播FCoV。'})
CREATE (immune:Factor {name: '细胞免疫缺陷', en: 'Cell-mediated immunity failure', description: '机体无法有效清除被感染的巨噬细胞。'})
CREATE (fip:Disease {name: '猫传腹', en: 'Feline infectious peritonitis', description: '由突变FCoV引起的免疫介导性血管炎。'})
CREATE (fever:Symptom {name: '发热', en: 'Fever', description: '持续性或间歇性发热，对抗生素反应差。'})
CREATE (wtloss:Symptom {name: '消瘦', en: 'Weight loss', description: '食欲下降与代谢亢进导致体重减轻。'})
CREATE (ascites:Symptom {name: '腹水', en: 'Ascites', description: '湿性FIP典型表现，腹腔积液。'})
CREATE (neuro:Symptom {name: '神经症状', en: 'Neurological signs', description: '共济失调、抽搐、行为异常等干性FIP表现。'})
CREATE (ocul:Symptom {name: '眼部炎症', en: 'Ocular inflammation', description: '葡萄膜炎、虹膜变色等。'})
CREATE (death:Outcome {name: '死亡', en: 'Death', description: '未经治疗的传统预后极差。'})
CREATE (recovery:Outcome {name: '临床治愈', en: 'Clinical recovery', description: '及时进行GS-441524等抗病毒治疗可缓解。'})

// 创建关系
CREATE (fcov)-[:CAUSES {description: '感染导致病毒在肠道复制'}]->(mut)
CREATE (multi)-[:CAUSES {description: '增加病毒暴露与传播机会'}]->(fcov)
CREATE (stress)-[:CAUSES {description: '抑制免疫系统功能'}]->(immune)
CREATE (young)-[:RISK_FACTOR_FOR {description: '免疫系统尚未成熟'}]->(fip)
CREATE (multi)-[:RISK_FACTOR_FOR {description: '高病毒载量环境'}]->(fip)
CREATE (mut)-[:CAUSES {description: '突变为FIPV后感染巨噬细胞'}]->(immune)
CREATE (immune)-[:CAUSES {description: '无法清除病毒，触发血管炎'}]->(fip)
CREATE (fip)-[:PRESENTS_AS {description: '全身炎症反应'}]->(fever)
CREATE (fip)-[:PRESENTS_AS {description: '代谢消耗增加'}]->(wtloss)
CREATE (fip)-[:PRESENTS_AS {description: '血管渗漏形成腹水'}]->(ascites)
CREATE (fip)-[:PRESENTS_AS {description: '病毒侵袭中枢神经系统'}]->(neuro)
CREATE (fip)-[:PRESENTS_AS {description: '病毒侵袭眼部组织'}]->(ocul)
CREATE (fip)-[:LEADS_TO {description: '未经治疗预后不良'}]->(death)
CREATE (fip)-[:LEADS_TO {description: '抗病毒治疗可达成'}]->(recovery);
