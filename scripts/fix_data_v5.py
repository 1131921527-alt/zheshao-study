# -*- coding: utf-8 -*-
"""第14轮 v5：把 7 个「词性是英文 noun/adjective 且没有中文释义」的词补全"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'ielts', 'ielts_bank.json')

POS_FIX = {
    'mainland': 'n. 大陆；本土',
    'rock': 'n. 岩石；礁石；摇滚乐',
    'portuguese': 'adj. 葡萄牙的；葡萄牙人的；n. 葡萄牙语',
    'spanish': 'adj. 西班牙的；西班牙语的；n. 西班牙语',
    'italian': 'adj. 意大利的；意大利人的；n. 意大利语',
    'hell': 'n. 地狱；极痛苦的境地',
    'beard': 'n. 胡须，络腮胡子',
}


def main():
    bank = json.load(io.open(BANK, encoding='utf-8'))
    n = 0
    for x in bank:
        if x['word'] in POS_FIX and not __import__('re').search(r'[\u4e00-\u9fff]', x.get('pos') or ''):
            x['pos'] = POS_FIX[x['word']]
            n += 1
    with io.open(BANK, 'w', encoding='utf-8') as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)
    print('补全词性释义 %d 词' % n)


if __name__ == '__main__':
    main()
