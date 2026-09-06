# -*- coding: utf-8 -*-
"""第11轮 v6：
1) 修 phenomenon 规则空 emoji（v5 笔误）
2) 在中文语义层最前面插入「优先级规则」——修 无困难→🧗、深蓝绿色→🎨、节奏→🏅、等级→🏢 等被误抢的词
3) excellent 规则 🏅 → 👍；draft 从「formulate/define」规则移出（让 ✍️ 草稿生效）
"""
SRC = 'study.html'
html = open(SRC, encoding='utf-8').read()
n = 0


def rep(old, new):
    global html, n
    if old in html:
        html = html.replace(old, new, 1); n += 1
    else:
        print('WARN not found:', old[:70])


# 1) phenomenon 空 emoji → 💡
rep(r"    [/\b(phenomenon|event|occurrence|situation)\b/, ''],",
    r"    [/\b(phenomenon|event|occurrence|situation)\b/, '\U0001F4A1'],")
# 2) 优先级规则插到中文语义层最前（先于其它中文规则，避免被通用词抢走）
PRIO = [
    (r'光滑|平滑|光洁|光滑的|平滑的', '\u2728'),
    (r'汽油|燃油|柴油|加油站|燃料油', '\u26FD'),
    (r'节奏|韵律|节拍|节奏感|旋律', '\U0001F3B5'),
    (r'等级|级别|阶层|层次|上层|下层', '\U0001FA9C'),
    (r'石头|岩石|石子|石块|石壁|砾石|碎石|巨石', '\U0001FAA8'),
    (r'尊重|尊敬|敬重|尊严|敬佩|崇敬|敬爱', '\U0001F64F'),
    (r'草稿|草案|起草|拟稿|初稿|打草稿', '✍️'),
    (r'专家|行家|能手|专业人员|专家的', '\U0001F393'),
    (r'相信|信任|信赖|诚信|信用|可信', '\U0001F91D'),
    (r'相反|反之|对立|矛盾|悖论', '↔️'),
]
header = "    /* ===== 第11轮：中文语义层（多字词枚举，按语义域分组） ===== */\n"
if header not in html:
    print('FATAL: CN header missing'); sys.exit(1)
prio_lines = "    /* --- 优先级：易被通用词抢走的具体义项 --- */\n" + \
             ''.join("    [/%s/, '%s'],\n" % p for p in PRIO)
html = html.replace(header, header + prio_lines, 1)

# 删掉尾部重复的 6 条（v5 追加的），保持单一来源
for p, _ in PRIO:
    dup = "    [/%s/, '" % p
    idx = html.find(dup, html.find(header) + len(prio_lines) + 100)
    while idx > 0:
        end = html.index('\n', idx) + 1
        html = html[:idx] + html[end:]
        n += 1
        idx = html.find(dup, html.find(header) + len(prio_lines) + 100)

# 3) excellent → 👍；draft 移出 formulate 规则
rep(r"    [/\b(best|better|greatest|top|excellent|outstanding|superior|remarkable|exceptional)\b/, '\U0001F3C5'],",
    r"    [/\b(best|better|greatest|top|excellent|outstanding|superior|remarkable|exceptional)\b/, '\U0001F44D'],")
rep(r"    [/\b(formulate|formulation|define|articulate|frame|conceive|devise|draft)\b/, '\U0001F4DD'],",
    r"    [/\b(formulate|formulation|define|articulate|frame|conceive|devise)\b/, '\U0001F4DD'],")

open(SRC, 'w', encoding='utf-8').write(html)
print('OK. edits:', n)
