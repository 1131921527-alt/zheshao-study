# -*- coding: utf-8 -*-
"""
Manual pre-translation cache for English articles.
The 18th round logic is in study.html + scripts/translate_cn.py, but on
this Windows machine both Google gtx and MyMemory return 429. GitHub Actions
runs the workflow from US IP where Google gtx works fine, so future runs
will progressively fill the translations. To make the bracket-format UI
useful immediately, we pre-bake title_cn / summary_cn by hand here.

This file is NOT a long-lived translation source; it's only used once when
ai_cards.json has empty title_cn/summary_cn for the known English cards
included in 2026-09-06's fetch.

Running: python scripts/manual_translate_18th.py
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
P = BASE / 'assets' / 'ai_cards.json'


# Manual translations keyed by source_url (most stable identifier).
MANUAL = {
    # Card #4 - TechCrunch - 2026-09-06
    'https://techcrunch.com/2026/09/06/authors-push-back-as-publishers-and-agents-seek-share-of-anthropic-settlement/': {
        'title_cn': '作者集体反击：出版社和代理方在 Anthropic 和解金上狮子大开口',
        'summary_cn': '【Anthropic】作者们表示，出版社在 Anthropic 的和解金分配上似乎拿走了远超其应得的份额。',
    },
    # Card #7 - Android Authority
    'https://www.androidauthority.com/motorola-google-foldables-beat-samsung-3704932/': {
        'title_cn': '摩托罗拉和谷歌的折叠屏，正在悄悄在关键阵地上击败三星',
        'summary_cn': '【Google】如果预算不是问题、要挑最强配置的折叠屏，三星 Galaxy Z Fold 8 Ultra 仍然稳坐王位——领先幅度还不小。它的轻薄机身、5000mAh 大电池等亮点确实亮眼。但从销量和性价比上看，…',
    },
    # Card #8 - Android Authority
    'https://www.androidauthority.com/samsung-record-sales-keep-us-from-better-phones-3704357/': {
        'title_cn': '我也想要更好的三星手机，但这些最新销量数据告诉你为什么我们等不到',
        'summary_cn': '【Android Authority】几年前，三星旗舰是公认的最强安卓标杆，但随着其他市场的竞争对手不断追赶，这种印象越来越像一种怀旧情怀。三星高端机销量依旧稳健，…',
    },
    # Card #9 - OpenAI
    'https://openai.com/index/an-alien-mind': {
        'title_cn': '外星人的思维',
        'summary_cn': '【OpenAI】Jakub Pachocki 反思日益强大的 AI 以及让其保持对齐的挑战。他呼吁更严的安全护栏和跨国协同监管。',
    },
}


def main():
    data = json.loads(P.read_text(encoding='utf-8'))
    cards = data.get('cards') if isinstance(data, dict) else data
    if not isinstance(cards, list):
        print('Bad shape'); return

    touched = 0
    for c in cards:
        url = c.get('source_url') or ''
        m = MANUAL.get(url)
        if not m:
            continue
        if m.get('title_cn') and not c.get('title_cn'):
            c['title_cn'] = m['title_cn']
            touched += 1
        if m.get('summary_cn') and not c.get('summary_cn'):
            c['summary_cn'] = m['summary_cn']
            touched += 1

    if isinstance(data, dict):
        data['cards'] = cards
        P.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        P.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding='utf-8')
    print('manual pre-translate touched:', touched)


if __name__ == '__main__':
    main()
