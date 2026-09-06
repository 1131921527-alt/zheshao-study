#!/usr/bin/env python3
"""
第八轮：雅思词库扩容 1151 -> 3900+
词表来源：github Toreinm/ielts-vocab（刘洪波《雅思词汇真经》22章 3402词）
中文释义/音标：有道 fsearch API（dict.youdao.com/fsearch）
双语例句：有道词条页（dict.youdao.com/w/<word>）解析 data-rel + 第二个 <p>
产物：ielts/ielts_bank.json（备份到 ielts_bank.backup_round8.json）
缓存：TEMP/ielts_fetch_cache.jsonl（断点续传，重跑只抓缺的）
"""
import os, sys, json, re, time, html
import urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_PATH = os.path.join(REPO, 'ielts', 'ielts_bank.json')
CACHE_PATH = os.path.join(os.environ.get('TEMP', '.'), 'ielts_fetch_cache.jsonl')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://dict.youdao.com/',
    'Accept-Language': 'en-US,en;q=0.9',
}

def get(url, binary=False, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            r = urllib.request.urlopen(req, timeout=20)
            d = r.read()
            return d if binary else d.decode('utf-8', 'replace')
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(0.8)

def fetch_chapters():
    """拉取22章词表：word -> {ipa, pos_en, def_en}"""
    out = {}
    for i in range(1, 23):
        d = get(f'https://raw.githubusercontent.com/Toreinm/ielts-vocab/master/ch_data/dict/ch{i}.json')
        if not d:
            print(f'ch{i} fetch fail'); continue
        for k, v in json.loads(d):
            out[k] = v
    return out

# ---------- 有道 fsearch：中文释义 + 音标 ----------
TRANS_RE = re.compile(r'<translation><content><!\[CDATA\[(.*?)\]\]></content></translation>', re.S)
PHON_RE = re.compile(r'<phonetic-symbol><!\[CDATA\[(.*?)\]\]></phonetic-symbol>', re.S)

def clean_pos(t):
    """'v. 出价；投标，竞标；努力争取；...' -> 'v. 出价；投标'"""
    t = t.strip()
    if not t:
        return ''
    # 去掉人名/网络释义行
    if t.startswith('【') or t.startswith('[网络]') or t.startswith('['):
        return ''
    parts = [p.strip() for p in t.split('；') if p.strip()]
    keep = parts[:2]
    return '；'.join(keep)

def fetch_fsearch(word):
    x = get('https://dict.youdao.com/fsearch?q=' + urllib.parse.quote(word))
    if not x:
        return None
    phon = (PHON_RE.findall(x) or [''])[0].strip()
    poss = []
    for c in TRANS_RE.findall(x):
        p = clean_pos(c)
        if p and p not in poss:
            poss.append(p)
    return {'phon': phon, 'poss': poss}

# ---------- 有道词条页：双语例句 ----------
def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).replace('\n', ' ').strip()

def parse_examples(h):
    """取前2条双语例句"""
    res = []
    li_re = re.compile(r'<li>\s*<p>(.*?)</p>\s*<p>(.*?)</p>', re.S)
    for m in li_re.finditer(h):
        en_html, cn_html = m.group(1), m.group(2)
        # 英文：优先用 data-rel（干净、无标签）
        dm = re.search(r'data-rel="(.*?)"', en_html)
        if dm:
            en = urllib.parse.unquote_plus(dm.group(1))
        else:
            en = strip_tags(en_html)
        cn = strip_tags(cn_html)
        en, cn = en.strip(), cn.strip()
        if 5 < len(en) < 200 and 2 < len(cn) < 150 and en not in [r[0] for r in res]:
            res.append((en, cn))
        if len(res) >= 2:
            break
    return res

def fetch_page(word):
    h = get('https://dict.youdao.com/w/' + urllib.parse.quote(word))
    if not h:
        return []
    i = h.find('id="bilingual"')
    if i < 0:
        return []
    seg = h[i:i + 30000]
    return parse_examples(seg)

# ---------- 主流程 ----------
def main():
    bank = json.load(open(BANK_PATH, encoding='utf-8'))
    bank_words = set(x['word'].lower() for x in bank)
    chapters = fetch_chapters()
    print('chapters words:', len(chapters))

    # 合法词：字母/空格/连字符，长度<=30
    def valid(w):
        return bool(re.fullmatch(r"[A-Za-z][A-Za-z \-']{0,29}", w))

    new_words = [w for w in chapters if w.lower() not in bank_words and valid(w)]
    print('new words to fetch:', len(new_words))

    # 载入缓存
    cache = {}
    if os.path.exists(CACHE_PATH):
        for line in open(CACHE_PATH, encoding='utf-8'):
            try:
                o = json.loads(line)
                cache[o['word']] = o
            except Exception:
                pass
    todo = [w for w in new_words if w not in cache]
    print('cached already:', len(new_words) - len(todo), 'todo:', len(todo))

    lock_fail = []
    def work(w):
        v = chapters[w]
        # ipa：优先雅思真经自带（OALD），否则 fsearch
        ipa = ''
        raw_ipa = (v.get('ipa') or '').strip()
        if raw_ipa:
            first = raw_ipa.split('·')[0].strip().replace('BrE', '').strip()
            if first.startswith('/'):
                ipa = first
        fs = fetch_fsearch(w)
        poss = fs['poss'] if fs else []
        if not ipa and fs and fs['phon']:
            ipa = '/' + fs['phon'] + '/'
        pos = poss[0] if poss else ((v.get('pos') or '').split(' · ')[0])
        exs = fetch_page(w)
        rec = {'word': w, 'ipa': ipa, 'pos': pos, 'poss': poss,
               'en': exs[0][0] if exs else '', 'cn': exs[0][1] if exs else '',
               'en2': exs[1][0] if len(exs) > 1 else '', 'cn2': exs[1][1] if len(exs) > 1 else ''}
        return rec

    fh = open(CACHE_PATH, 'a', encoding='utf-8')
    done = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(work, w): w for w in todo}
        for fut in as_completed(futs):
            w = futs[fut]
            try:
                rec = fut.result()
                fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
                fh.flush()
                cache[w] = rec
            except Exception as e:
                lock_fail.append((w, str(e)[:60]))
            done += 1
            if done % 100 == 0:
                print(f'  {done}/{len(todo)}')
    fh.close()
    print('fetch done, fail:', len(lock_fail))

    # ---------- 合并生成新 bank ----------
    entries = []
    for w in new_words:
        r = cache.get(w)
        if not r:
            continue
        pos = (r['pos'] or '').strip()
        if not pos:
            continue  # 连释义都拿不到的词丢弃
        e = {
            'word': w,
            'ipa': r['ipa'],
            'pos': pos,
            'story': '', 'tip': '',
            'en': r['en'], 'cn': r['cn'],
        }
        if not e['ipa'] and r['poss'] and len(r['poss']) > 1:
            pass
        entries.append(e)
    print('usable new entries:', len(entries))
    no_ex = sum(1 for e in entries if not e['en'])
    print('entries without example:', no_ex)

    # 备份并写回：旧词条在前（顺序保留），新词按字母序追加
    import shutil
    shutil.copy(BANK_PATH, BANK_PATH.replace('.json', '.backup_round8.json'))
    bank += entries
    json.dump(bank, open(BANK_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('bank total:', len(bank))
    uniq = len(set(x['word'].lower() for x in bank))
    print('unique words:', uniq)

if __name__ == '__main__':
    main()
