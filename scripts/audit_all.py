# -*- coding: utf-8 -*-
"""全站体检：词库数据质量 + 图片/音频资源覆盖 + emoji 兜底率"""
import collections
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bank = json.load(io.open(os.path.join(ROOT, 'ielts', 'ielts_bank.json'), encoding='utf-8'))

print('=' * 60)
print('词库总数：%d' % len(bank))
print('=' * 60)

# ---------- 1. 重复词 ----------
words = [x['word'] for x in bank]
dup = [w for w, c in collections.Counter(words).items() if c > 1]
print('\n[1] 重复词：%d' % len(dup), dup[:10])

# ---------- 2. 字段完整性 ----------
miss = collections.Counter()
for x in bank:
    for f in ('word', 'ipa', 'pos', 'cn', 'en'):
        if not (x.get(f) or '').strip():
            miss[f] += 1
    if not (x.get('examples') or []):
        miss['examples'] += 1
print('\n[2] 字段缺失：', dict(miss))

# ---------- 3. 例句里没出现目标词（词形不匹配/例句跑题） ----------
def word_in(word, sent):
    w = word.lower()
    s = sent.lower()
    if re.search(r'\b' + re.escape(w) + r'\b', s):
        return True
    # 允许屈折：travelled/traveling/travels 等
    stem = re.escape(w)
    return bool(re.search(r'\b' + stem + r'(e?s|e?d|ing|ed|es|ly|ment|er|ers)\b', s))

not_match = []
for x in bank:
    exs = (x.get('examples') or [])[:3]
    if not exs:
        continue
    bad = [e['en'] for e in exs if not word_in(x['word'], e['en'] or '')]
    if bad:
        not_match.append((x['word'], bad))
print('\n[3] 例句里不含该单词（可能跑题/词形不匹配）：%d 词' % len(not_match))
for w, b in not_match[:12]:
    print('    %-18s %s' % (w, b[0][:70]))

# ---------- 4. 标点/格式问题 ----------
CJK = r'[\u4e00-\u9fff]'
issues = collections.Counter()
samples = collections.defaultdict(list)
for x in bank:
    for e in (x.get('examples') or [])[:3]:
        en = e.get('en') or ''
        cn = e.get('cn') or ''
        if re.search(r'[，。？！；：“”‘’（）]', en):
            issues['英文例句混入中文标点'] += 1
            samples['英文例句混入中文标点'].append((x['word'], en[:60]))
        # 数字千分位 / 比分 / 时间 / 小数点 / 版本号 里的半角标点属正常，先剔除再检测
        cn_num = re.sub(r'\d[,.:;!?\']\d', '<N>', cn)
        cn_num = re.sub(r'\d[,.]\d', '<N>', cn_num)
        if re.search(r'[,.;:?!\'\"]', cn_num):
            issues['中文翻译混入英文标点'] += 1
            samples['中文翻译混入英文标点'].append((x['word'], cn[:60]))
        if en and not en.rstrip().endswith(('.', '!', '?', '"')):
            issues['英文例句缺句末标点'] += 1
            samples['英文例句缺句末标点'].append((x['word'], en[:60]))
        # 中文句末也可以是右引号 / 右书名号 / 省略号 / 破折号
        if cn and not cn.rstrip().endswith(('。', '！', '？', '”', '）',
                                            '」', '』', '…', '—', '"')):
            issues['中文翻译缺句末标点'] += 1
            samples['中文翻译缺句末标点'].append((x['word'], cn[:60]))
        if re.search(r'\s{2,}', en):
            issues['英文例句多余空格'] += 1
        if re.search(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', cn):
            issues['中文翻译中间有空格'] += 1
            samples['中文翻译中间有空格'].append((x['word'], cn[:60]))
print('\n[4] 标点/格式问题：')
for k, v in issues.most_common():
    print('    %-22s %d' % (k, v))
    for w, s in samples[k][:4]:
        print('        %-16s %s' % (w, s))

# ---------- 5. 全角/半角、错别字字典 ----------
TYPO = {
    '帐户': '账户', '做为': '作为', '其它': '其他', '按装': '安装', '报消': '报销',
    '部份': '部分', '重迭': '重叠', '渡假': '度假', '防碍': '妨碍', '幅射': '辐射',
    '关健': '关键', '好象': '好像', '既使': '即使', '交待': '交代', '痉孪': '痉挛',
    '具全': '俱全', '棵粒': '颗粒', '了望': '瞭望', '麻疯': '麻风', '迷团': '谜团',
    '偏面': '片面', '凭添': '平添', '趋使': '驱使', '融恰': '融洽', '部份': '部分',
    '甚致': '甚至', '松驰': '松弛', '叹气': '叹气', '趟水': '蹚水', '惟一': '唯一',
    '文诌诌': '文绉绉', '霭': '霭', '按排': '安排', '不落巢臼': '不落窠臼',
    '穿流不息': '川流不息', '惮精竭虑': '殚精竭虑', '飞扬拔扈': '飞扬跋扈',
    '刚腹自用': '刚愎自用', '功亏一蒉': '功亏一篑', '烩炙人口': '脍炙人口',
    '老奸巨滑': '老奸巨猾', '淋漓尽至': '淋漓尽致', '默守成规': '墨守成规',
    '磐竹难书': '罄竹难书', '谈笑风声': '谈笑风生', '委屈求全': '委曲求全',
    '相形见拙': '相形见绌', '一愁莫展': '一筹莫展', '仗义直言': '仗义执言',
}
typo_hits = []
for x in bank:
    text = '%s %s %s %s' % (x.get('pos', ''), x.get('cn', ''), x.get('story', ''), x.get('tip', ''))
    for e in (x.get('examples') or [])[:3]:
        text += ' ' + (e.get('cn') or '')
    for wrong, right in TYPO.items():
        if wrong in text:
            typo_hits.append((x['word'], wrong, right))
print('\n[5] 常见错别字：%d 处' % len(typo_hits))
for t in typo_hits[:15]:
    print('    %-18s %s → %s' % t)

# ---------- 6. 图片覆盖 ----------
IMG = os.path.join(ROOT, 'ielts', 'images')
imgs = set(os.listdir(IMG)) if os.path.isdir(IMG) else set()
no_img, bad_img = [], []
for x in bank:
    p = x.get('image')
    if not p:
        no_img.append(x['word'])
    elif os.path.basename(p) not in imgs:
        bad_img.append((x['word'], p))
print('\n[6] 图片：目录内 %d 张' % len(imgs))
print('    无 image 字段：%d 词（走 emoji 兜底）' % len(no_img))
print('    字段指向但文件不存在：%d' % len(bad_img), bad_img[:5])

# ---------- 7. 音频覆盖 ----------
AUD = os.path.join(ROOT, 'ielts', 'audio')
EX1 = os.path.join(AUD, 'ex1')
auds = set(os.listdir(AUD)) if os.path.isdir(AUD) else set()
ex1s = set(os.listdir(EX1)) if os.path.isdir(EX1) else set()
no_us, no_uk, no_ex1 = [], [], []
for x in bank:
    w = x['word'].strip().lower()
    if (w + '_us.mp3') not in auds:
        no_us.append(x['word'])
    if (w + '_uk.mp3') not in auds:
        no_uk.append(x['word'])
    slug = re.sub(r'[^a-z0-9]+', '_', w).strip('_')
    if (slug + '.mp3') not in ex1s:
        no_ex1.append(x['word'])
print('\n[7] 音频：单词 mp3 %d 个，例句 mp3 %d 个' % (len(auds), len(ex1s)))
print('    缺单词美音(_us)：%d 词' % len(no_us), no_us[:8])
print('    缺单词英音(_uk)：%d 词' % len(no_uk))
print('    缺例句音频(ex1)：%d 词' % len(no_ex1), no_ex1[:8])

# ---------- 8. emoji 兜底率 ----------
print('\n[8] emoji：无配图 %d 词（占 %.1f%%），需靠 wordEmoji 兜底'
      % (len(no_img), 100.0 * len(no_img) / len(bank)))
print('\n' + '=' * 60)
