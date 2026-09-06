# -*- coding: utf-8 -*-
"""第11轮 v5：修英文规则冲突（travel→🛤️/➡️、nation→🗾、phenomenon→🌠）+ 补 6 条常用语义"""
SRC = 'study.html'
html = open(SRC, encoding='utf-8').read()
n = 0

ROAD   = '\U0001F6E4️'   # 🛤️
JPNMAP = '\U0001F5FE'    # 🗾
WFLAG  = '\U0001F3F3️'   # 🏳️
SHOOT  = '\U0001F320'    # 🌠
BATT   = '\U0001F50B'    # 🔋
ROCK   = '\U0001FAA8'    # 🪨
PRAY   = '\U0001F64F'    # 🙏
GRAD   = '\U0001F393'    # 🎓
HAND   = '\U0001F91D'    # 🤝


def rep(old, new):
    global html, n
    if old in html:
        html = html.replace(old, new, 1); n += 1
    else:
        print('WARN not found:', old[:70])


# 1) travel 系列从「道路」「移动」规则移出，让后面的 🧭 旅行规则接管
rep(r"    [/\b(road|street|path|highway|route|journey|trip|travel|tour|tourism)\b/, '%s']," % ROAD,
    r"    [/\b(road|street|path|highway|route)\b/, '%s']," % ROAD)
rep(r"    [/\b(go|move|move|motion|movement|travel|travel)\b/, '➡️'],",
    r"    [/\b(go|move|motion|movement)\b/, '➡️'],")
# 2) country/nation 不再用日本地图 🗾；state（状态）移出该规则
rep(r"    [/\b(country|nation|national|state|region|rural)\b/, '%s']," % JPNMAP,
    r"    [/\b(country|nation|national|region|rural)\b/, '%s']," % WFLAG)
# 3) phenomenon 不再用流星 🌠
rep(r"    [/\b(phenomenon|event|occurrence|situation|trend|development)\b/, '%s']," % SHOOT,
    r"    [/\b(phenomenon|event|occurrence|situation)\b/, '']")

# 4) 补常用语义
MISC = [
    (r'石头|岩石|石子|石块|石壁|砾石|碎石|巨石', ROCK),
    (r'尊重|尊敬|敬重|尊严|敬佩|崇敬|敬爱', PRAY),
    (r'草稿|草案|起草|拟稿|初稿', '✍️'),
    (r'专家|行家|能手|专业人员|专家的', GRAD),
    (r'光滑|平滑|光洁|光滑的|平滑的', '✨'),
    (r'相信|信任|信赖|诚信|信用|可信', HAND),
]
anchor = "    [/能源|能量|动力|燃料|石油|煤炭|天然气|太阳能|核能|电能/, '%s'],\n" % BATT
if anchor not in html:
    print('FATAL: anchor missing'); sys.exit(1)
add = ''.join("    [/%s/, '%s'],\n" % (p, e) for p, e in MISC)
html = html.replace(anchor, anchor + add, 1)
open(SRC, 'w', encoding='utf-8').write(html)
print('OK. replacements:', n, '+ misc:', len(MISC))
