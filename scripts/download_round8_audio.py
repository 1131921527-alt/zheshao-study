#!/usr/bin/env python3
"""
第八轮配套：为词库里缺本地 mp3 的词下载有道 US 发音（type=2，与线上 url() 一致）
读 ielts/ielts_bank.json，只补 <word>_us.mp3 缺失的词，多线程 + 断点续传
"""
import os, json, time
import urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_PATH = os.path.join(REPO, 'ielts', 'ielts_bank.json')
AUDIO_DIR = os.path.join(REPO, 'ielts', 'audio')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://dict.youdao.com/',
    'Accept': '*/*',
}

def download_one(word, max_retries=3):
    wl = word.lower()  # 空格保留：浏览器 %20 解码后就是文件名里的空格（与线上 url() 一致）
    filepath = os.path.join(AUDIO_DIR, wl + '_us.mp3')
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
        return (word, 'skip')
    url = f'https://dict.youdao.com/dictvoice?audio={urllib.parse.quote(word)}&type=2'
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            resp = urllib.request.urlopen(req, timeout=20)
            data = resp.read()
            if len(data) > 1024:
                with open(filepath, 'wb') as f:
                    f.write(data)
                return (word, 'ok')
            if attempt < max_retries:
                time.sleep(0.5)
            else:
                return (word, f'small:{len(data)}')
        except Exception as e:
            if attempt < max_retries:
                time.sleep(0.6)
            else:
                return (word, f'err:{str(e)[:50]}')
    return (word, 'fail')

def main():
    bank = json.load(open(BANK_PATH, encoding='utf-8'))
    existing = set(os.listdir(AUDIO_DIR))
    need = []
    for x in bank:
        wl = x['word'].lower()  # 空格保留，与浏览器请求的文件名一致
        if wl + '_us.mp3' not in existing:
            need.append(x['word'])
    print('bank words:', len(bank), 'need download:', len(need))
    if not need:
        print('all audio present')
        return

    stats = {'ok': 0, 'skip': 0}
    fails = []
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(download_one, w): w for w in need}
        for fut in as_completed(futs):
            w, st = fut.result()
            if st == 'ok' or st == 'skip':
                stats[st if st in stats else 'ok'] += 1
            else:
                fails.append((w, st))
            done += 1
            if done % 200 == 0:
                print(f'  {done}/{len(need)} ok:{stats["ok"]} fail:{len(fails)} {time.time()-t0:.0f}s')
    print('done:', stats, 'fails:', len(fails))
    for w, s in fails[:20]:
        print('  FAIL', w, s)

if __name__ == '__main__':
    main()
