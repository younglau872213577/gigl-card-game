# -*- coding: utf-8 -*-
"""
GI/GL 食物卡牌分类游戏 —— 纯逻辑层（可独立测试，无 GUI 依赖）
"""
import random
import card_data as cd


def get_box_labels(level_type):
    """返回某关卡类型对应的分类框标签列表。"""
    mapping = {
        "gi3": ["低GI", "中GI", "高GI"],
        "gl3": ["低GL", "中GL", "高GL"],
        "dual4": ["可少量吃", "放心多吃", "不能乱吃", "严格少吃"],
    }
    return mapping.get(level_type, [])


def get_answer(card, level_type):
    """返回卡牌在该关卡类型下的标准答案标签。"""
    if level_type == "gi3":
        return card["gi_level"]
    if level_type == "gl3":
        return card["gl_level"]
    if level_type == "dual4":
        return card["dual_class"]
    return None


def draw_cards(level, seed=None):
    """从关卡卡牌池随机抽取 num_cards 张卡（按名称去重）。"""
    rng = random.Random(seed)
    seen = set()
    pool = []
    for pool_name in level["pools"]:
        for c in cd.get_pool(pool_name):
            key = c["name"]
            if key not in seen:
                seen.add(key)
                pool.append(c)
    n = min(level["num_cards"], len(pool))
    return rng.sample(pool, n)


def judge(card, box_label, level_type):
    """判断卡牌放入 box_label 是否正确。"""
    return get_answer(card, level_type) == box_label


if __name__ == "__main__":
    # 自测：校验数据完整性
    print("== 数据自测 ==")
    for lv in cd.LEVELS:
        if lv["type"] in ("gi3", "gl3", "dual4"):
            cards = draw_cards(lv)
            labels = get_box_labels(lv["type"])
            ok = all(get_answer(c, lv["type"]) in labels for c in cards)
            print(f"关卡{lv['id']} {lv['name']}: 抽卡{len(cards)}张, "
                  f"答案均在框内={ok}, 分类框={labels}")
    print("自测完成")
