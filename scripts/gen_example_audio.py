# -*- coding: utf-8 -*-
"""
用 Edge 神经网络语音 (en-US-AriaNeural) 离线批量生成「每词第 1 条例句」的 mp3。
产出： ielts/audio/ex1/<slug>.mp3   （slug = 单词小写、空格/连字符转下划线）

前端按 word 直接拼路径播放，播不到自动回退系统语音 / 有道在线发音。
脚本可重复执行：已存在且非 0 字节的文件会跳过。
"""
import asyncio
import io
import json
import os
import re
import sys
import time

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'ielts', 'ielts_bank.json')
OUT = os.path.join(ROOT, 'ielts', 'audio', 'ex1')
VOICE = 'en-US-AriaNeural'
CONCURRENCY = 10
RETRY = 3


def slug(word):
    s = (word or '').strip().lower()
    s = re.sub(r"[^a-z0-9]+", '_', s).strip('_')
    return s or 'x'


def load_tasks():
    with io.open(BANK, encoding='utf-8') as f:
        bank = json.load(f)
    tasks, seen = [], set()
    for it in bank:
        w = it.get('word') or ''
        exs = it.get('examples') or []
        if not exs:
            continue
        text = (exs[0].get('en') or '').strip()
        if not text:
            continue
        s = slug(w)
        # 保证唯一
        if s in seen:
            s = s + '_2'
        seen.add(s)
        tasks.append((s, text))
    return tasks


async def one(sem, name, text, stats):
    path = os.path.join(OUT, name + '.mp3')
    if os.path.exists(path) and os.path.getsize(path) > 1024:
        stats['skip'] += 1
        return
    async with sem:
        for attempt in range(RETRY):
            try:
                await edge_tts.Communicate(text, VOICE).save(path)
                if os.path.getsize(path) > 1024:
                    stats['ok'] += 1
                    return
                raise RuntimeError('file too small')
            except Exception as e:
                if attempt == RETRY - 1:
                    stats['fail'] += 1
                    stats['errors'].append('%s: %s' % (name, str(e)[:120]))
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                    except OSError:
                        pass
                    return
                await asyncio.sleep(1.5 * (attempt + 1))


async def main():
    os.makedirs(OUT, exist_ok=True)
    tasks = load_tasks()
    print('待生成: %d 条 -> %s' % (len(tasks), OUT), flush=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    stats = {'ok': 0, 'skip': 0, 'fail': 0, 'errors': []}
    t0 = time.time()
    BATCH = 200
    for i in range(0, len(tasks), BATCH):
        chunk = tasks[i:i + BATCH]
        await asyncio.gather(*[one(sem, n, t, stats) for n, t in chunk])
        done = min(i + BATCH, len(tasks))
        el = time.time() - t0
        print('进度 %d/%d  新增%d 跳过%d 失败%d  用时%.0fs  预计剩余%.0fs'
              % (done, len(tasks), stats['ok'], stats['skip'], stats['fail'],
                 el, el / done * (len(tasks) - done)), flush=True)
    print('完成: 新增%d 跳过%d 失败%d 总用时%.0fs'
          % (stats['ok'], stats['skip'], stats['fail'], time.time() - t0))
    if stats['errors']:
        print('失败样例前20:')
        for e in stats['errors'][:20]:
            print('  ', e)


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
