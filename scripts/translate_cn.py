# -*- coding: utf-8 -*-
"""
泽少学习台 · 英文内容中文化模块

引擎链：Google gtx（首选，免费，单次 1500 字符）→ MyMemory 兜底（会话级熔断，480 字符/块）

设计点：
1. 会话级熔断：Google 首次失败后整场降级到 MyMemory（避免 429 重试浪费）
2. 句子边界分块：避免句中断裂
3. 摘要【】前缀保留：剥前缀 → 翻正文 → 拼回，避免「【每日AI动态】」混入译文
4. 失败段存空串：前端按索引回退到英文原文

用法：
    from translate_cn import translate_cards, translate_text
    # translate_text("Hello world") -> '你好世界'
    # translate_cards(cards) -> 修改 cards 列表内每张卡的 title_cn / summary_cn / fulltext_cn
"""

import html
import json
import re
import time
import urllib.parse
import urllib.request


# 会话级状态：Google 失败后整场降级到 MyMemory
_state = {'google_ok': True}

# Google 单次约可吃 1500 utf-16 code units（约 750 汉字 / 500 英文词）
# MyMemory 匿名限制是 500 chars / day / IP；本机会话内节流到 480
_GOOGLE_MAX = 1500
_MY_MEMORY_MAX = 480

# 边界分块：句子级 . / ! / ? 后面空白切分
_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')

# 摘要前缀：【XX】 形式（来自 auto_ai_news.py 的摘要包装）
_PREFIX_RE = re.compile(r'^(【[^】]{0,30}】)([\s\S]*)$')

# MyMemory 长度限制保护，避免 500 chars 触发硬限
# 实际上 google 也吃不下太多，建议句子切分后单个 ≤ 480 字英文 (MyMemory 兜底时)


def _http_get(url, timeout=12):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='replace')


def _google(text):
    """调用 Google gtx，返回译文（HTML 实体已解码）；失败抛 RuntimeError"""
    q = urllib.parse.quote(text, safe='')
    url = ('https://translate.googleapis.com/translate_a/single'
           '?client=gtx&sl=en&tl=zh-CN&dt=t&q=' + q)
    try:
        body = _http_get(url, timeout=15)
    except Exception as e:
        raise RuntimeError('google http: %s' % e)
    try:
        data = json.loads(body)
    except Exception as e:
        raise RuntimeError('google json: %s body=%s' % (e, body[:120]))
    # data[0] = [ [译文, 原文, null, null, 10], ... ]
    if not data or not isinstance(data, list) or not data[0]:
        raise RuntimeError('google shape: %s' % repr(data)[:120])
    parts = []
    for seg in data[0]:
        if seg and seg[0]:
            parts.append(seg[0])
    out = ''.join(parts)
    if not out.strip():
        raise RuntimeError('google empty: %s' % repr(data)[:120])
    return html.unescape(out)


def _mymemory(text):
    """MyMemory 兜底；HTTP 200 但 responseStatus 可能是 200/403/429"""
    q = urllib.parse.quote(text, safe='')
    url = 'https://api.mymemory.translated.net/get?q=' + q + '&langpair=en|zh-CN'
    try:
        body = _http_get(url, timeout=15)
        data = json.loads(body)
    except Exception as e:
        raise RuntimeError('mymemory http: %s' % e)
    rc = str(data.get('responseStatus', ''))
    tr = (data.get('responseData') or {}).get('translatedText', '') or ''
    if rc == '200' and tr and 'QUERY LENGTH' not in tr and 'MYMEMORY WARNING' not in tr.upper():
        return html.unescape(tr)
    raise RuntimeError('mymemory rc=%s body=%s' % (rc, tr[:80]))


def _chunks(text, maxlen):
    """句子级切分；超长单句按空格硬切"""
    text = (text or '').strip()
    if not text:
        return []
    sentences = _SENT_SPLIT.split(text)
    out = []
    buf = ''
    for s in sentences:
        if not s:
            continue
        if len(s) > maxlen:
            # 单句超长，按空格硬切
            if buf:
                out.append(buf)
                buf = ''
            # 切到最后一段超长单句
            words = s.split(' ')
            seg = ''
            for w in words:
                test = (seg + ' ' + w).strip()
                if len(test) > maxlen:
                    if seg:
                        out.append(seg)
                    seg = w
                else:
                    seg = test
            if seg:
                out.append(seg)
            continue
        test = (buf + ' ' + s).strip() if buf else s
        if len(test) > maxlen:
            if buf:
                out.append(buf)
            buf = s
        else:
            buf = test
    if buf:
        out.append(buf)
    return out


def _run_engine(name, fn, maxlen, text, sleep_s, retries=0):
    for attempt in range(retries + 1):
        try:
            chunks = _chunks(text, maxlen)
            parts = []
            for ck in chunks:
                if not ck.strip():
                    continue
                parts.append(fn(ck))
                if sleep_s > 0 and len(chunks) > 1:
                    time.sleep(sleep_s)
            out = ''.join(parts)
            if out.strip():
                return out
        except Exception:
            if attempt >= retries:
                return None
            time.sleep(0.5)
    return None


def translate_text(text, sleep_s=0.4):
    """单段文本翻译；优先 Google、失败降级 MyMemory"""
    if not text or not text.strip():
        return ''
    if _state['google_ok']:
        out = _run_engine('google', _google, _GOOGLE_MAX, text, sleep_s)
        if out is not None:
            return out
        # Google 失败：熔断
        _state['google_ok'] = False
    out = _run_engine('mm', _mymemory, _MY_MEMORY_MAX, text, sleep_s, retries=2)
    return out if out is not None else ''


def _is_english(s, threshold=0.5):
    """英文判定：英文字符占比 > threshold"""
    if not s:
        return False
    letters = sum(1 for ch in s if ch.isascii() and ch.isalpha())
    return letters / max(1, len(s)) > threshold


def _translate_prefixed(text, sleep_s=0.4):
    """摘要可能含【XX】前缀，剥前缀后翻译，保留原前缀"""
    if not text:
        return ''
    m = _PREFIX_RE.match(text)
    if m:
        prefix, body = m.group(1), m.group(2)
        body_cn = translate_text(body, sleep_s)
        return prefix + body_cn if body_cn else prefix
    return translate_text(text, sleep_s)


def translate_cards(cards, sleep_s=0.4, quiet=False):
    """批量翻译 cards 列表，in-place 写回

    字段规则：
    - title：英文 + 无 title_cn → 翻译填 title_cn
    - summary：英文 + 无 summary_cn → 翻译填 summary_cn（保留【XX】前缀）
    - fulltext：英文 + 无 fulltext_cn → 逐段翻译填 fulltext_cn（list）

    返回 (n_touched, n_holes_remaining)
    """
    if not isinstance(cards, list):
        return 0, 0
    touched = 0
    holes = 0
    for c in cards:
        if not isinstance(c, dict):
            continue
        # ----- 标题 -----
        title = c.get('title') or ''
        if title and _is_english(title) and not (c.get('title_cn') or '').strip():
            t = translate_text(title, sleep_s)
            if t:
                c['title_cn'] = t
                touched += 1
            else:
                holes += 1
        # ----- 摘要 -----
        summary = c.get('summary') or ''
        if summary and _is_english(summary) and not (c.get('summary_cn') or '').strip():
            s = _translate_prefixed(summary, sleep_s)
            if s:
                c['summary_cn'] = s
                touched += 1
            else:
                holes += 1
        # ----- 全文（按段翻译） -----
        ft = c.get('fulltext')
        if isinstance(ft, list) and ft and (c.get('fulltext_lang') == 'en' or _is_english(' '.join(ft[:3]))):
            existing = c.get('fulltext_cn') if isinstance(c.get('fulltext_cn'), list) else []
            # 确保长度对齐
            if len(existing) != len(ft):
                existing = [''] * len(ft)
                c['fulltext_cn'] = existing
            for i, para in enumerate(ft):
                if not isinstance(para, str):
                    continue
                if i < len(existing) and (existing[i] or '').strip():
                    continue  # 已有译文
                if not para.strip():
                    existing[i] = ''
                    continue
                p = translate_text(para, sleep_s)
                if p:
                    existing[i] = p
                    touched += 1
                else:
                    existing[i] = ''  # 失败留空，前端按索引回退
                    holes += 1
    if not quiet:
        import sys
        sys.stderr.write('translate_cards: %d touched, %d holes remain\n' % (touched, holes))
    return touched, holes


def main():
    """CLI: python scripts/translate_cn.py"""
    import sys
    from pathlib import Path

    base = Path(__file__).resolve().parent.parent
    p = base / 'assets' / 'ai_cards.json'
    if not p.exists():
        print('ai_cards.json not found:', p)
        sys.exit(1)
    data = json.loads(p.read_text(encoding='utf-8'))
    cards = data.get('cards') if isinstance(data, dict) else data
    if not isinstance(cards, list):
        print('Bad ai_cards.json shape (expected {cards: [...]})')
        sys.exit(1)
    n, h = translate_cards(cards, sleep_s=0.4, quiet=False)
    if isinstance(data, dict):
        data['cards'] = cards
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        p.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding='utf-8')
    print('done. touched=%d holes=%d' % (n, h))


if __name__ == '__main__':
    main()
