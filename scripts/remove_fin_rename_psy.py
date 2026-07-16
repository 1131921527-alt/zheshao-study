"""
删除财经板块 + 心理·情商→心理学 重命名
幂等：重复运行不报错，已删的内容跳过。
"""

import re

SRC = "E:/workbuddyFIle/腾讯龙虾的成品/zheshao-study/index.html"

with open(SRC, encoding="utf-8") as f:
    lines = f.readlines()

# ============================================================
# 1) 删除 9 篇 fin-* 文章 section
#    每篇从 <!-- 长文：fin-xxx --> 到下一个同级别 </section> 之前
# ============================================================
FIN_SLUGS = [
    "fin-inflation", "fin-compound", "fin-stockfund",
    "fin-exchange", "fin-insurance", "fin-asset",
    "fin-interest", "fin-tax", "fin-crypto",
]

deleted_sections = 0
i = 0
new_lines = []
while i < len(lines):
    line = lines[i]
    # detect start of a fin article section
    match = re.match(r'\s*<!--\s*长文：(fin-\S+)\s*-->', line)
    if match and match.group(1) in FIN_SLUGS:
        slug = match.group(1)
        # skip until we find the closing </section>
        depth = 0
        started = False
        while i < len(lines):
            l = lines[i]
            if '<section' in l and 'id="art-' in l:
                started = True
                depth += 1
            if '</section>' in l and started:
                depth -= 1
                if depth == 0:
                    i += 1  # skip past the </section>
                    deleted_sections += 1
                    break
            i += 1
        continue
    new_lines.append(line)
    i += 1

lines = new_lines
print(f"[1/6] 删除 {deleted_sections} 篇财经文章 section")

# ============================================================
# 2) 删除 const FIN=[...] 数组
# ============================================================
new_lines = []
skip_fin_array = False
for i, line in enumerate(lines):
    if re.match(r'\s*const FIN=\[', line):
        skip_fin_array = True
        print(f"[2/6] 删除 const FIN 数组 (行 ~{i+1})")
        continue
    if skip_fin_array:
        # end of array: standalone ]; or inline ];
        if re.match(r'\s*\];', line) or (' ];' in line.strip() and not line.strip().startswith('//')):
            skip_fin_array = False
            continue
        continue
    new_lines.append(line)

lines = new_lines

# ============================================================
# 3) SLUG 中移除 fin:[...], renderK/openArticle 移除 fin:FIN
# ============================================================
new_lines = []
for i, line in enumerate(lines):
    # remove fin:"..." from SLUG
    if re.search(r'fin:\[.*?\]', line):
        line = re.sub(r',?\s*fin:\[.*?\]', '', line)
        print(f"[3a] 从 SLUG 移除 fin 条目")
    # remove fin:FIN from maps
    if 'fin:FIN,' in line or ',fin:FIN}' in line:
        line = line.replace('fin:FN,', '').replace(',fin:FIN}', '}').replace('fin:FIN,', '')
        print(f"[3b] 从 renderK maps 移除 fin:FIN")
    # remove fin:FIN from openArticle literal
    if ',fin:FIN,' in line or 'fin:FN,' in line:
        line = re.sub(r',?fin:FN', '', line)
        print(f"[3c] 从 openArticle 字面量移除 fin:FIN")
    new_lines.append(line)
lines = new_lines

# ============================================================
# 4) 删除 klist-fin 折叠块 + 首页财经卡
# ============================================================
new_lines = []
skip_klist_fin = False
skip_qcard_fin = False
for i, line in enumerate(lines):
    # klist-fin toggle title
    if re.match(r".*onclick=\"toggleK\\('fin'\\)\">.*财经.*</div>", line):
        skip_klist_fin = True
        print(f"[4a] 删除 k-toggle 财经标题行 (行~{i+1})")
        continue
    if skip_klist_fin:
        if 'klist-fin' in line:
            print(f"[4b] 删除 klist-fin 容器 (行~{i+1})")
            skip_klist_fin = False
            continue
        continue
    # home qcard for finance
    if re.match(r'.*<div class="qcard" onclick="goKnow\\(\'fin\'\\)">.*', line):
        skip_qcard_fin = True
        print(f"[4c] 删除首页财经卡片 (行~{i+1})")
        continue
    if skip_qcard_fin:
        if '</div>' in line and 'qcard' not in line:
            # check if it's the closing div of the qcard
            skip_qcard_fin = False
            continue
        if '</div>' in line:
            skip_qcard_fin = False
            continue
        continue
    new_lines.append(line)
lines = new_lines

# ============================================================
# 5) 更新顶栏 sub、meta description、hero 统计数字
# ============================================================
new_lines = []
total_articles_after = 55 - 9  # 46
for line in lines:
    # meta description: remove 财经 reference, update count
    if 'meta name="description"' in line:
        line = line.replace(
            '（历史 / 文化·文学 / 地理 / 财经 / 心理·情商）',
            '（历史 / 文化·文学 / 地理 / 心理学）'
        ).replace(
            '共 55 篇长文',
            f'共 {total_articles_after} 篇长文'
        )
        print("[5a] 更新 meta description")
    # topbar sub: remove 财经
    if '历史 · 文化·文学 · 地理 · 财经 · 心理·情商' in line:
        line = line.replace('历史 · 文化·文学 · 地理 · 财经 · 心理·情商',
                           '历史 · 文化·文学 · 地理 · 心理学')
        print("[5b] 更新顶栏 sub（移除财经）")
    # home hero stats: 6 knowledge categories → 5
    if '<div class="n">6</div>' in line and '知识类目' in str(lines[min(i+1, len(lines)-1)] if i < len(lines)-1 else ''):
        line = line.replace('<div class="n">6</div>', '<div class="n">5</div>')
        print("[5c] 首页知识类目数 6→5")

    # ====== Task #27: Rename 心理·情商 → 心理学 ======
    # Home card
    if '心理·情商' in line and 'qcard' in line:
        line = line.replace('>心理·情商<', '>心理学<')
        if '心理学 · 职场关系' in line:
            line = line.replace('心理学 · 职场关系', '认知偏差 · 情商沟通')
        print("[6a] 首页卡「心理·情商」→「心理学」")
    # Section title
    if '心理·情商（职场）' in line:
        line = line.replace('心理·情商（职场）', '心理学')
        print("[6b] s-know 标题「心理·情商（职场）」→「心理学」")
    new_lines.append(line)

lines = new_lines

# Write back
with open(SRC, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"\n✅ 完成！已写入 {SRC}")
print(f"   删除 {deleted_sections} 篇财经文章")
print(f"   剩余文章预计: {total_articles_after} 篇")
