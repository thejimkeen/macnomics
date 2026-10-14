"""The economics curriculum: every order teaches one lesson.

Each lesson: title, the one-line principle, the McDonald's evidence, and the
takeaway for life. Lessons are picked by rules in pick_lesson(), based on what
the optimizer actually did -- the lesson always explains YOUR order.
"""
from __future__ import annotations

LESSONS = {
    "anchoring": {
        "title": "价格锚定：套餐的'立省'是算出来的",
        "principle": "人们判断贵不贵，不看绝对价格，看参照物。商家只要定好参照物，就定好了你的感受。",
        "evidence": "巨无霸三件套 ¥37.5，单点总和 ¥50（巨无霸26.5+中薯14+可乐9.5），'立省12.5'。拿掉可乐的¥9.5锚，只省¥3——76%的优惠感来自成本最低的饮料。",
        "takeaway": "下次看到'立省XX元'，先问：省，是相对哪个锚省的？",
    },
    "marginal_cost": {
        "title": "边际成本：可乐为什么是锚",
        "principle": "边际成本越低的东西，越适合做价格锚——定价可以远高于成本，全部变成'优惠感'的弹药。",
        "evidence": "一杯可乐的糖浆+水+杯，成本约¥1.5，菜单价¥9.5，毛利率84%。用¥1.5的成本，制造了¥9.5的 perceived value，杠杆6倍。",
        "takeaway": "凡是边际成本趋近于零的东西（饮料、酱包、APP会员），都是天然的价格锚。",
    },
    "unit_economics": {
        "title": "单位经济学：每块钱买多少热量/蛋白质",
        "principle": "没有度量就没有优化。把'划算'翻译成数字：kcal/元， protein(g)/元。",
        "evidence": "实测：中薯买一送一 42.8 kcal/元全场第一；那么大鸡排 1.71g蛋白/元双料冠军。派29kcal/元看着高，但全是糖——度量要选对分子。",
        "takeaway": "任何消费决策，先定义你的效用函数，再度量。否则'划算'只是感觉。",
    },
    "constrained_optimization": {
        "title": "约束优化：人生就是背包问题",
        "principle": "预算有限、欲望无限——这就是0/1背包问题。Macnomics用动态规划给你精确最优解，不靠感觉。",
        "evidence": "给定¥40预算，算法在116个商品中算出蛋白最大组合。这不是推荐，是数学：在约束下，没有比这更好的解。",
        "takeaway": "承认约束，精确求解，比'差不多就行'更接近理性。",
    },
    "diminishing_marginal_utility": {
        "title": "边际效用递减：第二份薯条不香",
        "principle": "同样一件事，重复做的快乐递减。第二份薯条的快乐远小于第一份——但价格一样。",
        "evidence": "买一送一多出的那份薯条，对你边际效用≈0（吃不掉），对路边阿姨边际效用极高。同样一份薯条，效用取决于在谁手里。",
        "takeaway": "识别自己效用递减的点，把剩余转移给效用更高的人——这是套利，不是浪费。",
    },
    "opportunity_cost": {
        "title": "机会成本：省下的¥11是什么",
        "principle": "选择的成本，是你放弃的次优选项。省钱不是目的，省下来的钱能买什么才是。",
        "evidence": "理性套餐（巨无霸+冰水）比三件套省¥11——这¥11是一杯9.9的冰美式（券后），或3天后的另一顿鸡排。'省'的价值由它的去处决定。",
        "takeaway": "每次省钱时，明确写下这笔钱的去处，否则省下来的钱会以另一种方式花掉。",
    },
    "utility_arbitrage": {
        "title": "效用套利：把促销变成善意",
        "principle": "商家促销创造'剩余'（多出的一份），剩余在你手里价值低，在别人手里价值高——转移它，就是套利。",
        "evidence": "买一送一多的一份薯条：你的效用≈0，小哥的一句'谢谢'=你一天的好心情。商家的让利，经你手变成了人情，ROI最高的一单。",
        "takeaway": "最高级的'划算'，不是把便宜占尽，而是让每一分优惠都落在效用最高的地方——包括别人的效用。",
    },
}

ORDER = ["anchoring", "marginal_cost", "unit_economics", "constrained_optimization",
         "diminishing_marginal_utility", "opportunity_cost", "utility_arbitrage"]


def pick_lesson(bundle: list[dict], summary: dict, goal: str) -> dict:
    """Pick the lesson that explains THIS order."""
    names = " ".join(it["name"] for it in bundle)
    # coupon used -> diminishing marginal utility / arbitrage
    if any(it.get("coupon") for it in bundle):
        return LESSONS["diminishing_marginal_utility"]
    # no combo in a bundle that could have used one -> anchoring
    if "三件套" not in names and "套餐" not in names:
        return LESSONS["anchoring"]
    if goal == "protein":
        return LESSONS["unit_economics"]
    return LESSONS["constrained_optimization"]
