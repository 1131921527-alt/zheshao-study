#!/usr/bin/env python3
"""
第九轮配套：给词库每词补足 3 条双语例句
复用有道词条页 dict.youdao.com/w/<word> 的 #bilingual 区块解析
产出：ielts/ielts_bank.json —— 每词新增 examples:[{en,cn},{en,cn},{en,cn}]
保留原 en/cn 做第一条例句兼容（前端旧引用不受影响）
缓存：TEMP/ielts_examples_cache.jsonl（断点续传，只抓缺的）
"""
import os, json, re, time, html
import urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_PATH = os.path.join(REPO, 'ielts', 'ielts_bank.json')
CACHE_PATH = os.path.join(os.environ.get('TEMP', '.'), 'ielts_examples_cache.jsonl')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://dict.youdao.com/',
    'Accept-Language': 'en-US,en;q=0.9',
}

def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            r = urllib.request.urlopen(req, timeout=20)
            return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(0.8)

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).replace('\n', ' ').strip()

def parse_examples(h, want=3):
    """从 #bilingual 区块最多取 want 条双语例句"""
    res = []
    li_re = re.compile(r'<li>\s*<p>(.*?)</p>\s*<p>(.*?)</p>', re.S)
    for m in li_re.finditer(h):
        en_html, cn_html = m.group(1), m.group(2)
        dm = re.search(r'data-rel="(.*?)"', en_html)
        if dm:
            en = urllib.parse.unquote_plus(dm.group(1))
            en = re.sub(r'&[a-z]+=\w+$', '', en).strip()
        else:
            en = strip_tags(en_html)
        cn = re.sub(r'&[a-z]+=\w+$', '', strip_tags(cn_html)).strip()
        # 过滤：非句子(纯音频链接/过长/过短)不要；cn 为空的不要
        if (5 < len(en) < 250 and 2 < len(cn) < 250
            and not en.lower().startswith('http')
            and 'pureaudio' not in en.lower()
            and en not in [x['en'] for x in res]):
            res.append({'en': en, 'cn': cn})
        if len(res) >= want:
            break
    return res

def fetch_page(word):
    h = get('https://dict.youdao.com/w/' + urllib.parse.quote(word))
    if not h:
        return []
    i = h.find('id="bilingual"')
    if i < 0:
        return []
    seg = h[i:i + 60000]
    return parse_examples(seg)

def main():
    bank = json.load(open(BANK_PATH, encoding='utf-8'))
    # 载入缓存
    cache = {}
    if os.path.exists(CACHE_PATH):
        for line in open(CACHE_PATH, encoding='utf-8'):
            try:
                o = json.loads(line); cache[o['word']] = o
            except Exception: pass
    # 需要抓的词：已有 examples(>=3) 或 en 非空的跳过；没抓过的全抓
    todo = []
    for x in bank:
        if x.get('examples') and len(x.get('examples')) >= 3:
            continue
        w = x['word']
        if w not in cache:
            todo.append(w)
    print('bank words:', len(bank), '需抓例句:', len(todo), '已缓存:', sum(1 for x in bank if x['word'] in cache))

    fh = open(CACHE_PATH, 'a', encoding='utf-8')
    done = 0
    def work(w):
        exs = fetch_page(w)
        return {'word': w, 'examples': exs}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(work, w): w for w in todo}
        for fut in as_completed(futs):
            w = futs[fut]
            try:
                rec = fut.result()
                fh.write(json.dumps(rec, ensure_ascii=False) + '\n'); fh.flush()
                cache[w] = rec
            except Exception as e:
                pass
            done += 1
            if done % 100 == 0:
                print(f'  {done}/{len(todo)}')
    fh.close()

    # 合并写回 bank
    updated = 0
    for x in bank:
        w = x['word']
        rec = cache.get(w)
        if not rec:
            continue
        exs = rec['examples']
        if exs:
            x['examples'] = exs
            # 同步第一条例句到 en/cn（保证旧字段一致）
            if not x.get('en') and exs[0]['en']:
                x['en'] = exs[0]['en']; x['cn'] = exs[0]['cn']
            updated += 1
    json.dump(bank, open(BANK_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n3 = sum(1 for x in bank if x.get('examples') and len(x['examples']) >= 3)
    n2 = sum(1 for x in bank if x.get('examples') and len(x['examples']) >= 2)
    n1 = sum(1 for x in bank if x.get('examples') and len(x['examples']) >= 1)
    print(f'写回 {updated} 词 | >=3条例句 {n3} | >=2条 {n2} | >=1条 {n1} | 总 {len(bank)}')

if __name__ == '__main__':
    main()
