# -*- coding: utf-8 -*-
"""
第14轮数据修复 v1：
  1) 中文翻译标点规范化（英文逗号/问号/叹号转全角、补句末句号、删中文间多余空格）
  2) 英文例句标点净化（中文标点→英文标点、补句末句号、合并多余空格、首字母大写）
  3) 常见错别字（惟一→唯一、部份→部分、其它→其他）
  4) 重复词去重（合并释义与例句）
  5) 修完后同步 en/cn 字段 = examples[0]
"""
import io
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'ielts', 'ielts_bank.json')

CJK = r'\u4e00-\u9fff'
CN_END = '。！？”’》）】…'
EN_END = ('.', '!', '?', '"', "'")

# ---------- 错别字表 ----------
TYPO = {'惟一': '唯一', '部份': '部分', '其它': '其他', '做为': '作为',
        '帐户': '账户', '按装': '安装', '重迭': '重叠', '防碍': '妨碍',
        '关健': '关键', '好象': '好像', '既使': '即使', '松驰': '松弛'}


def fix_cn(s):
    """中文翻译标点规范化"""
    if not s:
        return s
    s = s.strip()
    # 1) 中文之间的多余空格（"互联网人 想要" → 去掉）
    s = re.sub(r'(?<=[%s])\s+(?=[%s])' % (CJK, CJK), '', s)
    # 2) 英文标点 → 中文标点（只在紧邻中文时转，避免误伤夹在翻译里的英文原句）
    for a, b in [(',', '，'), ('?', '？'), ('!', '！'), (';', '；'), (':', '：')]:
        s = re.sub(r'(?<=[%s])\s*%s\s*' % (CJK, re.escape(a)), b, s)
        s = re.sub(r'%s\s*(?=[%s])' % (re.escape(a), CJK), b, s)
    # 3) 中文右引号后紧跟中文逗号等，去多余空格
    s = re.sub(r'\s+([，。？！；：])', r'\1', s)
    # 4) 补句末句号
    s = s.rstrip()
    if s and s[-1] not in CN_END and s[-1] not in EN_END:
        s += '。'
    return s


def fix_en(s):
    """英文例句标点净化"""
    if not s:
        return s
    s = s.strip()
    # 1) 中文标点 → 英文标点
    table = {'，': ', ', '。': '.', '？': '?', '！': '!', '；': ';', '：': ':',
             '“': '"', '”': '"', '‘': "'", '’': "'", '（': '(', '）': ')', '…': '...'}
    for a, b in table.items():
        s = s.replace(a, b)
    # 2) 合并多余空格
    s = re.sub(r'\s{2,}', ' ', s)
    # 3) 逗号后缺空格的补上（英文语境）
    s = re.sub(r'(?<=[a-zA-Z]),(?=[a-zA-Z])', ', ', s)
    # 4) 句末标点：去掉尾部多余逗号/空格后补一句号
    s = s.rstrip()
    s = re.sub(r'[,;:]+\s*$', '', s).rstrip()
    if s and not s.endswith(EN_END) and not s.endswith('...'):
        s += '.'
    # 5) 首字母大写
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    return s


def main():
    bank = json.load(io.open(BANK, encoding='utf-8'))
    shutil.copy(BANK, BANK + '.bak')
    stat = {'cn': 0, 'en': 0, 'typo': 0, 'dup': 0}

    # ---- 3) 错别字（先做，后面标点修复基于正确文本）----
    for x in bank:
        for f in ('pos', 'cn', 'story', 'tip'):
            v = x.get(f) or ''
            nv = v
            for wrong, right in TYPO.items():
                if wrong in nv:
                    nv = nv.replace(wrong, right)
            if nv != v:
                x[f] = nv
                stat['typo'] += 1

    # ---- 1)2) 标点修复 ----
    for x in bank:
        exs = x.get('examples') or []
        for e in exs:
            oc, oe = e.get('cn') or '', e.get('en') or ''
            nc, ne = fix_cn(oc), fix_en(oe)
            if nc != oc:
                e['cn'] = nc
                stat['cn'] += 1
            if ne != oe:
                e['en'] = ne
                stat['en'] += 1
        # 顶层 en/cn 字段（同步回 examples[0] 由后面统一处理）
        if x.get('cn'):
            x['cn'] = fix_cn(x['cn'])
        if x.get('en'):
            x['en'] = fix_en(x['en'])

    # ---- 4) 重复词去重 ----
    seen = {}
    deduped = []
    for x in bank:
        w = x['word']
        if w in seen:
            first = seen[w]
            stat['dup'] += 1
            # 释义取更长的（信息更全）
            if len(x.get('pos') or '') > len(first.get('pos') or ''):
                first['pos'] = x['pos']
            # 例句合并去重
            have = {(e.get('en') or '').strip() for e in (first.get('examples') or [])}
            for e in (x.get('examples') or []):
                if (e.get('en') or '').strip() and (e.get('en') or '').strip() not in have:
                    have.add((e.get('en') or '').strip())
                    first.setdefault('examples', []).append(e)
            # 音标取更长的
            if len(x.get('ipa') or '') > len(first.get('ipa') or ''):
                first['ipa'] = x['ipa']
            continue
        seen[w] = x
        deduped.append(x)
    bank = deduped

    # ---- 5) en/cn 同步 = examples[0]，并裁剪到 3 条 ----
    for x in bank:
        exs = [e for e in (x.get('examples') or []) if (e.get('en') or '').strip()]
        x['examples'] = exs[:3]
        if exs:
            x['en'] = exs[0]['en']
            x['cn'] = exs[0].get('cn') or ''

    with io.open(BANK, 'w', encoding='utf-8') as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)
    print('修复统计：中文标点 %d 处 | 英文例句 %d 处 | 错别字 %d 处 | 去重 %d 词'
          % (stat['cn'], stat['en'], stat['typo'], stat['dup']))
    print('词库 %d → %d' % (len(json.load(io.open(BANK + '.bak', encoding='utf-8'))), len(bank)))


if __name__ == '__main__':
    main()
