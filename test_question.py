# batch_test_questions.py

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.pipeline import Pipeline

# 初始化 Pipeline（默认本地模式）
p = Pipeline()

# 测试问题列表：覆盖方向混淆、意图重叠、指标解读、特征列举、药物、多跳、边界、系统保护等
test_questions = [
    # 方向性混淆类
    "猫传腹的症状是什么？",
    "传腹有什么表现？",
    "腹水是传腹的症状吗？",
    "传腹有腹水症状吗？",
    "血管通透性增加会表现为传腹吗？",
    "传腹早期有什么症状？",
    "发热是传腹的表现吗？",
    "传腹有哪些指标异常？",

    # 意图重叠竞争类
    "治疗传腹用什么药？",
    "传腹怎么判断？",
    "白球比低有什么表现？",
    "有哪些风险因素会影响康复？",
    "什么药能治传腹？",
    "传腹要和哪些病区分？",
    "猫可能是传腹吗？",
    "怎么确认是不是传腹？",

    # 指标解读类
    "白球比0.5是传腹吗？",
    "Rivalta阳性代表什么？",
    "SAA高说明什么？",
    "腹水蛋白高是传腹吗？",
    "PCR阳性一定是传腹吗？",
    "白球比低需要怀疑传腹吗？",

    # 疾病特征与概念边界类
    "猫传腹有什么症状？",
    "什么是猫传腹？",
    "猫传腹的发病机制是什么？",
    "猫传腹的典型表现有哪些？",

    # 药物与治疗边界类
    "传腹吃什么药？",
    "传腹怎么治疗？",
    "GS-441524能治传腹吗？",
    "441是什么药？",

    # 多跳与间接关联类
    "血管通透性增加是传腹的特征吗？",
    "内皮损伤会导致传腹吗？",
    "免疫复合物是传腹的特征吗？",
    "血管炎是传腹的表现吗？",

    # 非标准口语类
    "猫肚子大，可能是传腹吗？",
    "猫发烧，会不会是传腹？",
    "猫抽风，是传腹症状吗？",
    "猫没精神，和传腹有关系吗？",
    "猫呼吸快，是不是传腹？",
    "猫眼睛发炎，会不会是干性传腹？",

    # 边界与系统保护类
    "猫感冒了怎么办？",
    "狗会得传腹吗？",
    "今天天气怎么样？",
    "你是谁？",
    "猫快不行了怎么办？",
    "谢谢",

    # 澄清后选项完整性类
    "传腹是什么原因？",
    "腹水是什么？",
    "白球比低是什么？",
    "这药安全吗能治吗？",
]

# 迭代测试
for q in test_questions:
    print("=" * 60)
    print("问题:", q)

    try:
        result = p.run(q)

        print("状态:", result.status)
        print("意图:", result.intent)

        if hasattr(result, "meta_subtype") and result.meta_subtype:
            print("meta子类型:", result.meta_subtype)

        # 打印摘要，截取前100个字符
        if result.summary:
            summary_preview = result.summary[:100].replace("\n", " ")
            print("摘要:", summary_preview, "..." if len(result.summary) > 100 else "")

        # 如果触发澄清，打印选项
        if result.clarify_options:
            print("澄清选项:")
            for opt in result.clarify_options:
                print(f"  - {opt.label} ({opt.value})")

        # 如果触发边界，打印提示
        if result.boundary_hint:
            print("边界提示:", result.boundary_hint)

        # 打印实体（可选）
        if result.entities:
            print("实体:", result.entities)

    except Exception as e:
        print("执行出错:", e)

    print()