# -*- coding: utf-8 -*-
"""第14轮最后一处标点：句末「，」补句号 + ratify/hallowed 引号与省略号"""
import io, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
P = ROOT + r"\ielts\ielts_bank.json"
bank = json.load(io.open(P, encoding="utf-8"))

# 1) 句末是逗号/顿号/分号/冒号 -> 改句号
n1 = 0
for it in bank:
    for e in it.get("examples") or []:
        cn = (e.get("cn") or "").strip()
        if cn and cn[-1] in "，、；：,;:":
            e["cn"] = cn[:-1] + "。"
            n1 += 1
print("句末补句号 %d 处" % n1)

# 2) 特定条目引号 / 省略号
FIX = {
    "ratify": [('表明：,“是的，我们会遵守公约条款”。',
                '表明：“是的，我们会遵守公约条款”。')],
    "hallowed": [('愿人都尊你的名为圣...”', '愿人都尊你的名为圣……”')],
}
idx = {it["word"]: it for it in bank}
n2 = 0
for w, pairs in FIX.items():
    it = idx.get(w)
    if not it:
        print("!! 找不到词:", w); continue
    for e in it.get("examples") or []:
        cn = e.get("cn") or ""
        for old, new in pairs:
            if old in cn:
                e["cn"] = cn.replace(old, new)
                n2 += 1
print("修引号/省略号 %d 处" % n2)

json.dump(bank, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("✅ 已写回，总词数 %d" % len(bank))
