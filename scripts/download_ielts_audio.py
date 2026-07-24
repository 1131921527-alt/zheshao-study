#!/usr/bin/env python3
"""
批量下载雅思单词发音mp3
从所有 day*.html 提取单词列表，用有道API下载UK+US发音
多线程加速，支持断点续传（已有文件跳过）
"""
import os, re, glob, time, hashlib
import urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ielts', 'audio')
IELTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ielts')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://dict.youdao.com/',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}

def extract_words():
    """从所有day*.html提取单词和例句"""
    words = set()
    # (word_lower, sentence_text) pairs for sentence audio
    word_sentences = []  # [(word_lower, sent_text, sent_idx), ...]

    for f in sorted(glob.glob(os.path.join(IELTS_DIR, 'day*.html'))):
        with open(f, encoding='utf-8') as fh:
            content = fh.read()
        # 提取单词（en: "word", ipa:）
        for m in re.finditer(r'en:\s*"([^"]+)"\s*,\s*ipa:', content):
            w = m.group(1).strip()
            if w and len(w) < 50:
                words.add(w)

        # 提取例句（从sentences数组中）
        # 格式: { en: "sentence", cn: "translation" }
        for m in re.finditer(r'\{\s*en:\s*"([^"]+)"\s*,\s*cn:', content):
            s = m.group(1).strip()
            if s and len(s) < 200:
                # 用hash作为文件名
                h = hashlib.md5(s.encode()).hexdigest()[:12]
                word_sentences.append((s, h))

    return words, word_sentences


def download_one(word, voice_type, max_retries=2):
    """下载单个单词的发音"""
    wl = word.lower()
    suffix = '_uk.mp3' if voice_type == 1 else '_us.mp3'
    filepath = os.path.join(AUDIO_DIR, wl + suffix)

    # 已存在且大于1KB则跳过
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
        return (word, voice_type, 'skip')

    url = f'https://dict.youdao.com/dictvoice?audio={urllib.parse.quote(word)}&type={voice_type}'
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            resp = urllib.request.urlopen(req, timeout=15)
            data = resp.read()
            if len(data) > 1024:
                with open(filepath, 'wb') as f:
                    f.write(data)
                return (word, voice_type, 'ok')
            else:
                if attempt < max_retries:
                    time.sleep(0.5)
                else:
                    return (word, voice_type, f'small:{len(data)}')
        except Exception as e:
            if attempt < max_retries:
                time.sleep(0.5)
            else:
                return (word, voice_type, f'err:{str(e)[:50]}')

    return (word, voice_type, 'fail')


def download_sentence(sent_text, sent_hash, max_retries=2):
    """下载例句发音"""
    filepath = os.path.join(AUDIO_DIR, f's_{sent_hash}.mp3')
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
        return (sent_text[:30], 'skip')

    # 用有道API读句子
    url = f'https://dict.youdao.com/dictvoice?audio={urllib.parse.quote(sent_text)}&type=1'
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            resp = urllib.request.urlopen(req, timeout=15)
            data = resp.read()
            if len(data) > 1024:
                with open(filepath, 'wb') as f:
                    f.write(data)
                return (sent_text[:30], 'ok')
            else:
                if attempt < max_retries:
                    time.sleep(0.5)
                else:
                    return (sent_text[:30], f'small:{len(data)}')
        except Exception as e:
            if attempt < max_retries:
                time.sleep(0.5)
            else:
                return (sent_text[:30], f'err:{str(e)[:50]}')

    return (sent_text[:30], 'fail')


def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)

    print('=== 提取单词和例句 ===')
    words, sentences = extract_words()
    print(f'唯一单词: {len(words)}')
    print(f'唯一例句: {len(sentences)}')

    # 检查已有文件
    existing = set(os.listdir(AUDIO_DIR))
    need_uk = [(w, 1) for w in sorted(words) if f'{w.lower()}_uk.mp3' not in existing]
    need_us = [(w, 2) for w in sorted(words) if f'{w.lower()}_us.mp3' not in existing]
    # 去重例句
    seen_sents = set()
    need_sents = []
    for text, h in sentences:
        if h not in seen_sents and f's_{h}.mp3' not in existing:
            seen_sents.add(h)
            need_sents.append((text, h))

    total = len(need_uk) + len(need_us) + len(need_sents)
    print(f'需下载单词UK: {len(need_uk)}')
    print(f'需下载单词US: {len(need_us)}')
    print(f'需下载例句: {len(need_sents)}')
    print(f'总下载量: {total}')
    print()

    if total == 0:
        print('所有文件已存在，无需下载')
        return

    # 多线程下载
    results = {'ok': 0, 'skip': 0, 'fail': 0}
    fails = []
    done = 0
    start = time.time()

    all_tasks = []
    for w, vt in need_uk:
        all_tasks.append(('word', w, vt, None))
    for w, vt in need_us:
        all_tasks.append(('word', w, vt, None))
    for text, h in need_sents:
        all_tasks.append(('sent', text, None, h))

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {}
        for task_type, a, b, c in all_tasks:
            if task_type == 'word':
                fut = pool.submit(download_one, a, b)
            else:
                fut = pool.submit(download_sentence, a, c)
            futures[fut] = (task_type, a)

        for fut in as_completed(futures):
            task_type, label = futures[fut]
            try:
                result = fut.result()
                status = result[-1] if isinstance(result, tuple) else str(result)
                if status == 'ok' or status == 'skip':
                    results['ok' if status == 'ok' else 'skip'] += 1
                else:
                    results['fail'] += 1
                    fails.append((task_type, label, status))
            except Exception as e:
                results['fail'] += 1
                fails.append((task_type, label, str(e)[:80]))

            done += 1
            if done % 100 == 0 or done == total:
                elapsed = time.time() - start
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                print(f'  进度: {done}/{total} ({done*100//total}%) | 成功:{results["ok"]} 跳过:{results["skip"]} 失败:{results["fail"]} | {rate:.1f}/s | ETA:{eta:.0f}s')

    print()
    print(f'=== 下载完成 ===')
    print(f'成功: {results["ok"]}')
    print(f'跳过: {results["skip"]}')
    print(f'失败: {results["fail"]}')
    elapsed = time.time() - start
    print(f'耗时: {elapsed:.1f}s')

    if fails:
        print(f'\n失败列表（前20个）:')
        for t, l, s in fails[:20]:
            print(f'  [{t}] {l[:40]} -> {s}')

    # 最终统计
    final_count = len([f for f in os.listdir(AUDIO_DIR) if f.endswith('.mp3')])
    print(f'\naudio目录总mp3文件数: {final_count}')


if __name__ == '__main__':
    main()
