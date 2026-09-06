# -*- coding: utf-8 -*-
"""
第14轮收尾修复：
1) 8 个过短/跑题例句重写（thermal/immune/ratify/amplify/apply/accompany/occupy/liability）
2) 1 处语法错误 parents -> parents'
3) 4 处中文标点/拼写修复
"""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
P = ROOT + r"\ielts\ielts_bank.json"
bank = json.load(io.open(P, encoding="utf-8"))
idx = {it["word"]: it for it in bank}

# 1) 例句重写：word -> (例句序号从1开始, 新en, 新cn)
NEW = {
    "thermal": (1,
        "Thermal imaging cameras can detect heat escaping through poorly insulated walls.",
        "热成像摄像机可以探测到从保温不良的墙体散失的热量。"),
    "immune": (1,
        "Adults are not immune to the virus, so vaccination is still strongly recommended.",
        "成年人对此病毒并非免疫，因此仍强烈建议接种疫苗。"),
    "ratify": (1,
        "Parliament is expected to ratify the treaty before the end of the year.",
        "预计议会将在年底前批准该条约。"),
    "amplify": (1,
        "The microphone amplifies the speaker's voice so everyone in the hall can hear.",
        "麦克风会放大讲话者的声音，让大厅里的每个人都能听见。"),
    "apply": (1,
        "You should apply for the scholarship at least three months before the term begins.",
        "你应该在学期开始前至少三个月申请这笔奖学金。"),
    "accompany": (1,
        "Please accompany your grandmother to the hospital because she does not know the way.",
        "请你陪祖母去医院，因为她不认得路。"),
    "occupy": (1,
        "Housing and transport occupy nearly half of a typical household's monthly budget.",
        "住房和交通几乎占了普通家庭月度预算的一半。"),
    "liability": (1,
        "Bad debt is a liability that can destroy a small business within a single year.",
        "坏账是一种可能在一年内拖垮小企业的负债。"),
}

n1 = 0
for w, (i, en, cn) in NEW.items():
    it = idx.get(w)
    if not it:
        print("!! 找不到词:", w); continue
    exs = it.get("examples") or []
    if len(exs) >= i:
        exs[i - 1]["en"] = en
        exs[i - 1]["cn"] = cn
        n1 += 1
print("重写例句 %d 条" % n1)

# 2) 语法错误：parents strict -> parents' strict
n2 = 0
for it in bank:
    for ex in it.get("examples") or []:
        en = ex.get("en") or ""
        if "parents strict" in en:
            ex["en"] = en.replace("parents strict", "parents' strict")
            n2 += 1
print("修语法错误 %d 处" % n2)

# 3) 中文标点 / 拼写
FIX_CN = [
    ("botany", "人和作物如何共同演化，这问题很有趣，迈克尔·保伦就此写了本很有意思的书，《植物的欲望》",
               "人和作物如何共同演化，这问题很有趣，迈克尔·保伦就此写了本很有意思的书《植物的欲望》。"),
    ("hybridisation", "另外一个比较便宜的贮能方式就是hydbridisation.",
                      "另外一种比较便宜的贮能方式就是杂交（hybridisation）。"),
    ("homesick", "然后她说，\"有时候我想家\"", "然后她说：“有时候我想家。”"),
    ("pun", "于是，他想用一句双关语来辟谣，凯撒说\"余非君\"",
            "于是，他想用一句双关语来辟谣，凯撒说：“余非君。”"),
]
n3 = 0
for w, old, new in FIX_CN:
    it = idx.get(w)
    if not it:
        print("!! 找不到词:", w); continue
    done = False
    for ex in it.get("examples") or []:
        if (ex.get("cn") or "").strip() == old:
            ex["cn"] = new
            n3 += 1
            done = True
            break
    if not done:
        print("!! 未匹配到原文:", w, "|", old[:40])
print("修中文标点/拼写 %d 处" % n3)

json.dump(bank, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("✅ 已写回，总词数 %d" % len(bank))
