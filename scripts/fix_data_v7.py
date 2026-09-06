# -*- coding: utf-8 -*-
"""第14轮收尾：修剩余 12 处半角引号/省略号/冒号逗号连用的中文标点问题"""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
P = ROOT + r"\ielts\ielts_bank.json"
bank = json.load(io.open(P, encoding="utf-8"))

# word -> [(旧片段, 新片段), ...]
FIX = {
    "ratify": [('表明：,"是的，我们会遵守公约条款"。',
                '表明：“是的，我们会遵守公约条款。”')],
    "counterbalance": [('"广告商有时会通过补偿或者免责的形式，即对索赔要求的一种限定或条件，来平衡夸大的说辞。',
                        '“广告商有时会通过补偿或者免责的形式，即对索赔要求的一种限定或条件，来平衡夸大的说辞。”')],
    "beast": [('称之为"野兽机器"，', '称之为“野兽机器”，')],
    "pivot": [('叫"省略号"，', '叫“省略号”，')],
    "hallowed": [('愿人都尊你的名为圣..."', '愿人都尊你的名为圣……”')],
    "artefact": [('"在塞加拉的梯形金字塔上，人们发现了一个木制的手工制品，这个手工制品与一种现代滑翔机惊人地相似。',
                  '“在塞加拉的梯形金字塔上，人们发现了一个木制的手工制品，这个手工制品与一种现代滑翔机惊人地相似。”')],
    "soap": [('...他两个耳朵里有肥皂泡沫。', '……他两个耳朵里有肥皂泡沫。')],
    "bribe": [('称他们为"纳贿的巴赛勒斯们"，', '称他们为“纳贿的巴赛勒斯们”，'),
              ('就像荷马史诗中的"王者们"一样。', '就像荷马史诗中的“王者们”一样。')],
    "sibling": [('三个问题：,"你去过伦敦吗？你有弟弟或妹妹吗？”',
                 '三个问题：“你去过伦敦吗？你有弟弟或妹妹吗？”')],
    "dwarf": [('因为小矮人说："我认识你。”', '因为小矮人说：“我认识你。”')],
    "corpus": [('公司"这个词来自于拉丁文corpus，意思是身体，所以法人是种化身。',
                '“公司”这个词来自于拉丁文 corpus，意思是身体，所以法人是种化身。')],
    "wretched": [('这些句子：,“当他们列举出他们贫瘠而浮华的歌颂时”，亦显示出卑鄙无能的低劣之声“。',
                  '这些句子：“当他们列举出他们贫瘠而浮华的歌颂时”，亦显示出卑鄙无能的低劣之声。')],
}

n, touched_first = 0, []
for it in bank:
    w = it.get("word") or ""
    if w not in FIX:
        continue
    for i, ex in enumerate(it.get("examples") or []):
        cn = ex.get("cn") or ""
        orig = cn
        for old, new in FIX[w]:
            cn = cn.replace(old, new)
        if cn != orig:
            ex["cn"] = cn
            n += 1
            if i == 0:
                touched_first.append(w)

print("修中文标点 %d 处" % n)
if touched_first:
    print("改动涉及第 1 条例句（需重生成音频）:", touched_first)

json.dump(bank, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("✅ 已写回，总词数 %d" % len(bank))
