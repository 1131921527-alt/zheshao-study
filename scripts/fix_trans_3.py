# -*- coding: utf-8 -*-
"""第14轮：修复第1/2批序号写错导致的误覆盖 + plume 漏修"""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
P = ROOT + r"\ielts\ielts_bank.json"
bank = json.load(io.open(P, encoding="utf-8"))
idx = {it["word"]: it for it in bank}

# 1) 误覆盖的 #2 恢复原译文；2) 污染 #3 补正确译文（序号 0 起）
FIX = {
    "swarm": (1, "当时，这是测试过的最大的机器人群。",
              2, "每次得分后后撤并调整状态，比挥舞着手臂一窝蜂乱冲要容易。"),
    "propulsion": (1, "推进器是由火箭发动机提供的，而不是螺旋桨和方向舵，这使得转向变得困难。",
                   2, "钓上一条当地的大海鲢或梭鱼，无疑会增添一股出乎意料的强劲推进力。"),
    "reel": (1, "该操作杆加倍弯曲，线轴发出刺耳的嗒嗒声。",
             2, "当然，有时砸重金签下一位大牌自由球员是划算的。"),
    "accessory": (1, "该公司为全国机动车售后市场提供各种配件和休闲车产品。",
                  2, "与其穿圆领 T 恤，不如选一件线条利落的浅色配饰。"),
}

n = 0
for w, (i_restore, cn_old, i_fix, cn_new) in FIX.items():
    it = idx.get(w)
    if not it:
        print("!! 找不到词:", w); continue
    exs = it["examples"]
    exs[i_restore]["cn"] = cn_old      # 恢复误覆盖
    exs[i_fix]["cn"] = cn_new          # 修真正的污染位
    n += 2

# plume #3 原句把词用在人名里，重写整条
it = idx.get("plume")
if it and len(it["examples"]) > 2:
    it["examples"][2]["en"] = "A plume of black smoke rose from the burning warehouse."
    it["examples"][2]["cn"] = "一股黑烟从燃烧的仓库升起。"
    n += 1

print("修复 %d 条" % n)
json.dump(bank, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("✅ 已写回，总词数 %d" % len(bank))
