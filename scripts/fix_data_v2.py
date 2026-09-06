# -*- coding: utf-8 -*-
"""
第14轮数据修复 v2（在 v1 之后跑）：
  1) 错别字补修：v1 只扫了 pos/cn/story/tip，漏掉 examples[].cn，这里补上
  2) 中文引号配对：连续两个 “ 时，第二个应为 ”
  3) 补齐 5 个没有例句的词（skin / bible / communism / union / massacre）
  4) 找出「例句里真的没有该单词任何形式」的词，导出待人工复核
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'ielts', 'ielts_bank.json')
CJK = r'\u4e00-\u9fff'

TYPO = {'惟一': '唯一', '部份': '部分', '其它': '其他', '做为': '作为',
        '帐户': '账户', '按装': '安装', '重迭': '重叠', '防碍': '妨碍',
        '关健': '关键', '好象': '好像', '既使': '即使', '松驰': '松弛'}


def fix_quotes(s):
    """中文引号交替配对：第1个 “ 保持，第2个改 ”，以此类推"""
    if not s or '“' not in s:
        return s
    out, n = [], 0
    for ch in s:
        if ch == '“':
            n += 1
            out.append('“' if n % 2 == 1 else '”')
        elif ch == '”':
            n += 1
            out.append('”' if n % 2 == 0 else '“')
        else:
            out.append(ch)
    return ''.join(out)


def word_in(word, sent):
    """单词的任意屈折/派生形式是否出现在句子里"""
    w = (word or '').lower().strip()
    s = (sent or '').lower()
    if not w or not s:
        return False
    if re.search(r'\b' + re.escape(w) + r'\b', s):
        return True
    # 去尾 e / y→i
    if w.endswith('y'):
        alt = w[:-1]
    elif w.endswith('e'):
        alt = w[:-1]
    else:
        alt = w
    stems = {w, alt}
    if not w.endswith('e'):
        stems.add(w)
    forms = set()
    for st in stems:
        for suf in ('s', 'es', 'ed', 'ing', 'er', 'ers', 'ly', 'ness', 'ment', 'tion',
                    'ity', 'ies', 'ied', 'ally', 'ance', 'ive', 'al', 'ous', 'ism', 'ist'):
            forms.add(st + suf)
        # 双写末辅音 + ing/ed
        if len(st) > 2 and st[-1] not in 'aeiou' and st[-2] in 'bcdfghjklmnpqrstvwxz':
            forms.add(st + st[-1] + 'ing')
            forms.add(st + st[-1] + 'ed')
    for f in forms:
        if re.search(r'\b' + re.escape(f) + r'\b', s):
            return True
    for pre in ('geo', 'im', 'un', 'de', 'non', 're', 'pre', 'over', 'under', 'anti'):
        if re.search(r'\b' + pre + re.escape(w) + r'\w{0,5}\b', s):
            return True
    return False


FILL = {
    'skin': [
        ('The rough surface of the rock scratched the skin on my hands.', '岩石粗糙的表面划伤了我手上的皮肤。'),
        ('Regular moisturising keeps your skin healthy and smooth.', '经常保湿能让皮肤保持健康光滑。'),
        ('The tribe used animal skins to make warm clothing.', '这个部落用兽皮制作保暖的衣物。'),
    ],
    'bible': [
        ('This handbook is regarded as the bible of modern architecture.', '这本手册被视为现代建筑的宝典。'),
        ('She read a short passage from the Bible before going to bed.', '她睡前读了《圣经》里的一小段。'),
        ('His latest book has become the investor bible.', '他的新书成了投资者的必备宝典。'),
    ],
    'communism': [
        ('The rise and fall of communism in Eastern Europe reshaped the region.', '东欧共产主义的兴衰重塑了整个地区。'),
        ('Many scholars still debate the economic legacy of communism.', '许多学者仍在争论共产主义的经济遗产。'),
        ('The party was founded to promote the ideals of communism.', '该党成立是为了推行共产主义的理想。'),
    ],
    'union': [
        ('The trade union negotiated a better pay deal for its members.', '工会为会员争取到了更好的薪酬协议。'),
        ('The European Union sets common standards for its member states.', '欧盟为其成员国制定共同标准。'),
        ('Workers voted to join the union after months of dispute.', '经过数月纠纷，工人们投票加入了工会。'),
    ],
    'massacre': [
        ('The massacre shocked the world and prompted international intervention.', '那场屠杀震惊世界，并引发了国际干预。'),
        ('Historians still debate the true death toll of the massacre.', '历史学家仍在争论这场屠杀的真实死亡人数。'),
        ('The novel describes the massacre through the eyes of a survivor.', '这部小说以一位幸存者的视角描述了那场屠杀。'),
    ],
}


def main():
    bank = json.load(io.open(BANK, encoding='utf-8'))
    stat = {'typo': 0, 'quote': 0, 'fill': 0}

    for x in bank:
        # 1) 错别字 + 2) 引号：覆盖 pos/cn/story/tip 与 examples[].cn
        for f in ('pos', 'cn', 'story', 'tip'):
            v = x.get(f) or ''
            if not v:
                continue
            nv = v
            for wrong, right in TYPO.items():
                nv = nv.replace(wrong, right)
            nv = fix_quotes(nv)
            if nv != v:
                if any(k in v for k in TYPO):
                    stat['typo'] += 1
                else:
                    stat['quote'] += 1
                x[f] = nv
        for e in (x.get('examples') or []):
            v = e.get('cn') or ''
            if not v:
                continue
            nv = v
            for wrong, right in TYPO.items():
                nv = nv.replace(wrong, right)
            nv = fix_quotes(nv)
            if nv != v:
                if any(k in v for k in TYPO):
                    stat['typo'] += 1
                else:
                    stat['quote'] += 1
                e['cn'] = nv

        # 3) 补缺例句的词
        w = x['word']
        if not (x.get('examples') or []) and w in FILL:
            x['examples'] = [{'en': a, 'cn': b} for a, b in FILL[w]]
            stat['fill'] += 1

        # 同步 en/cn
        exs = [e for e in (x.get('examples') or []) if (e.get('en') or '').strip()]
        x['examples'] = exs[:3]
        if exs:
            x['en'] = exs[0]['en']
            x['cn'] = exs[0].get('cn') or ''

    with io.open(BANK, 'w', encoding='utf-8') as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)
    print('错别字 %d 处 | 引号配对 %d 处 | 补例句 %d 词' % (stat['typo'], stat['quote'], stat['fill']))

    # 4) 真跑题检查
    bad = []
    for x in bank:
        exs = (x.get('examples') or [])[:3]
        if not exs:
            continue
        off = [e['en'] for e in exs if not word_in(x['word'], e['en'])]
        if off:
            bad.append((x['word'], off))
    print('\n例句里找不到该词任何形式的词：%d' % len(bad))
    for w, o in bad:
        print('  %-18s %s' % (w, o[0][:75]))


if __name__ == '__main__':
    main()
