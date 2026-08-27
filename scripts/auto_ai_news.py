# -*- coding: utf-8 -*-
"""
泽少学习台 · AI 动态每日自动更新（无需任何 API Key，纯标准库）

- 抓取官方博客 + 可信中英科技媒体的 RSS / Atom
- 过滤最近 48 小时、去重、按时间排序
- 生成 assets/ai_cards.json（兼容 study.html 既有字段，并补充 source_url / company / is_new 等）
- 没有任何真实来源链接(source_url)的新闻，绝不进入正式列表（杜绝假新闻）
- 当天新闻不足时，保留前一天重要内容，并记录 updated 日期

运行：python scripts/auto_ai_news.py
"""
import json
import re
import sys
import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'assets' / 'ai_cards.json'

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')

# 订阅源：lang=zh 的提供中文摘要；lang=en 的为官方/英文媒体（标题与链接真实，摘要可能英文）
FEEDS = [
    # —— 中文 AI / 科技媒体（提供中文摘要 + 真实原文链接）——
    {'url': 'https://www.qbitai.com/feed', 'outlet': '量子位', 'lang': 'zh'},
    {'url': 'https://www.jiqizhixin.com/feed', 'outlet': '机器之心', 'lang': 'zh'},
    {'url': 'https://36kr.com/feed', 'outlet': '36氪', 'lang': 'zh'},
    {'url': 'https://www.ifanr.com/feed', 'outlet': '爱范儿', 'lang': 'zh'},
    {'url': 'https://sspai.com/feed', 'outlet': '少数派', 'lang': 'zh'},
    # —— 官方 / 英文媒体（标题与链接真实；摘要英文时仅作补充）——
    # ai_only=True 的官方源只发 AI/技术内容，免去关键词过滤，保证不漏重要发布
    {'url': 'https://huggingface.co/blog/feed.xml', 'outlet': 'Hugging Face', 'lang': 'en', 'company': 'Hugging Face', 'ai_only': True},
    {'url': 'https://github.blog/feed/', 'outlet': 'GitHub', 'lang': 'en', 'company': 'GitHub', 'ai_only': True},
    {'url': 'https://blog.google/technology/ai/rss/', 'outlet': 'Google', 'lang': 'en', 'company': 'Google', 'ai_only': True},
    {'url': 'https://blogs.nvidia.com/feed/', 'outlet': 'NVIDIA', 'lang': 'en', 'company': 'NVIDIA', 'ai_only': True},
    {'url': 'https://openai.com/blog/rss.xml', 'outlet': 'OpenAI', 'lang': 'en', 'company': 'OpenAI', 'ai_only': True},
    {'url': 'https://techcrunch.com/category/artificial-intelligence/feed/', 'outlet': 'TechCrunch', 'lang': 'en'},
    {'url': 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml', 'outlet': 'The Verge', 'lang': 'en'},
    {'url': 'https://arstechnica.com/ai/feed/', 'outlet': 'Ars Technica', 'lang': 'en'},
]

# 公司识别（标题/摘要命中即标记）
COMPANY_MAP = [
    (r'openai|gpt|chatgpt|sora', 'OpenAI'),
    (r'anthropic|claude', 'Anthropic'),
    (r'google|gemini|deepmind|谷歌', 'Google'),
    (r'microsoft|copilot|微软', 'Microsoft'),
    (r'meta|llama|脸书', 'Meta'),
    (r'nvidia|英伟达', 'NVIDIA'),
    (r'hugging ?face', 'Hugging Face'),
    (r'xai|grok|马斯克', 'xAI'),
    (r'deepseek|深度求索', 'DeepSeek'),
    (r'字节|豆包|doubao', '字节跳动'),
    (r'阿里|通义|千问|qwen', '阿里巴巴'),
    (r'百度|文心|ernie', '百度'),
    (r'腾讯|混元|hunyuan', '腾讯'),
    (r'华为|盘古', '华为'),
    (r'智谱|glm|chatglm', '智谱AI'),
    (r'月之暗面|kimi|moonshot', '月之暗面'),
    (r'小米', '小米'),
    (r'苹果|apple', 'Apple'),
    (r'亚马逊|amazon|aws', 'Amazon'),
]

AI_KEYWORDS = re.compile(
    r'ai|人工智能|大模型|模型|gpt|claude|gemini|llm|agent|智能体|芯片|算力|'
    r'神经网络|机器学习|深度学习|机器人|算法|开源模型|推理|训练|多模态|'
    r'chatbot|生成式|向量|rag|微调|提示词|prompt', re.I)

# 统一使用北京时间（UTC+8），保证“更新于 YYYY-MM-DD”与用户感知一致，且不受运行环境时区影响
BJTZ = datetime.timezone(datetime.timedelta(hours=8))
NOW = datetime.datetime.now(BJTZ)
WINDOW = datetime.timedelta(hours=48)


def clean_html(s):
    if not s:
        return ''
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&[a-zA-Z]+;', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def truncate(s, n):
    s = clean_html(s)
    if len(s) > n:
        s = s[:n].rstrip() + '…'
    return s


def detect_company(text):
    t = (text or '').lower()
    for pat, name in COMPANY_MAP:
        if re.search(pat, t):
            return name
    return None


def norm_title(s):
    s = (s or '').lower()
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff]+', '', s)
    return s


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    # RSS pubDate
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(s)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
    except Exception:
        pass
    # ISO (Atom)
    try:
        s2 = s.replace('Z', '+00:00')
        dt = datetime.datetime.fromisoformat(s2)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        pass
    return None


def fetch(url):
    req = Request(url, headers={'User-Agent': UA, 'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*'})
    with urlopen(req, timeout=20) as r:
        raw = r.read()
    return raw


def parse_feed(raw):
    """返回 list of {title, link, summary, published}"""
    items = []
    try:
        root = ET.fromstring(raw)
    except Exception:
        return items
    # RSS
    for it in root.iter('item'):
        title = (it.findtext('title') or '').strip()
        link = (it.findtext('link') or '').strip()
        desc = it.findtext('description') or ''
        # 优先 content:encoded
        for c in it.iter():
            if c.tag.endswith('encoded') and c.text:
                desc = c.text
                break
        pub = it.findtext('pubDate') or ''
        items.append({'title': title, 'link': link, 'summary': desc, 'published': parse_date(pub)})
    # Atom
    if not items:
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        for en in root.iter('{http://www.w3.org/2005/Atom}entry'):
            title = (en.findtext('{http://www.w3.org/2005/Atom}title') or '').strip()
            link = ''
            for l in en.findall('{http://www.w3.org/2005/Atom}link'):
                if l.get('rel') in (None, 'alternate'):
                    link = l.get('href') or ''
                    break
            summary = en.findtext('{http://www.w3.org/2005/Atom}summary') or en.findtext('{http://www.w3.org/2005/Atom}content') or ''
            pub = en.findtext('{http://www.w3.org/2005/Atom}updated') or en.findtext('{http://www.w3.org/2005/Atom}published') or ''
            items.append({'title': title, 'link': link, 'summary': summary, 'published': parse_date(pub)})
    return items


def load_prev():
    if OUT.exists():
        try:
            d = json.loads(OUT.read_text(encoding='utf-8'))
            if isinstance(d, dict):
                return d.get('cards', []), d.get('updated', '')
        except Exception:
            pass
    return [], ''


def collect():
    seen = {}
    for feed in FEEDS:
        try:
            raw = fetch(feed['url'])
            for it in parse_feed(raw):
                title = it['title']
                link = it['link']
                if not title or not link:
                    continue
                # 必须要有真实来源链接
                if not re.match(r'^https?://', link):
                    continue
                pub = it['published']
                # 无日期或超窗口（英文官方源可能无近期内容）则降权但不丢弃英文源近期项；
                # 中文源严格要求近 48h，避免陈旧
                if pub is None:
                    age_ok = feed['lang'] != 'zh'
                else:
                    age = NOW - pub
                    age_ok = (datetime.timedelta(0) <= age <= WINDOW)
                    if feed['lang'] == 'zh' and not age_ok:
                        continue
                    if feed['lang'] == 'en' and age > WINDOW * 3:
                        continue
                text = title + ' ' + it['summary']
                # 非 AI 专属源（中文媒体 / 综合英文媒体）必须命中 AI 关键词，避免无关科技新闻混入
                if not feed.get('ai_only') and not AI_KEYWORDS.search(text):
                    continue
                company = feed.get('company') or detect_company(title) or detect_company(feed['outlet']) or feed['outlet']
                pub_bj = pub.astimezone(BJTZ) if pub else NOW
                date_str = pub_bj.strftime('%Y-%m-%d')
                # 中文源取完整内容（content:encoded），英文源也尽量保留更长摘录；
                # 人工翻译的中文正文/标题会在 main() 中按标题回填，不被此处自动片段覆盖
                cap = 320 if feed['lang'] == 'zh' else 200
                summary = truncate(it['summary'], cap)
                if feed['lang'] == 'en':
                    # 英文源：用官方口吻包装，绝不编造细节（中文翻译由人工补充并回填）
                    head = ('【%s 官方动态】' % company) if not summary else ('【%s】' % company)
                    summary = head + (summary if summary else title)
                card = {
                    'tag': company,
                    'company': company,
                    'source': feed['outlet'],
                    'title': title,
                    'title_cn': '',
                    'date': date_str,
                    'published_at': pub_bj.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
                    'summary': summary,
                    'impact': '',
                    'uses': '',
                    'source_url': link,
                    'official': bool(feed.get('ai_only')),
                }
                # 去重：优先按归一化标题（跨源同事件只留一条），其次按链接
                key = norm_title(title) or link
                if key not in seen:
                    seen[key] = card
                else:
                    # 同一事件已存在，保留更完整的摘要
                    if len(summary) > len(seen[key]['summary']):
                        seen[key] = card
        except (URLError, HTTPError, Exception) as e:
            sys.stderr.write('feed failed %s: %s\n' % (feed['url'], e))
            continue
    return list(seen.values())


def main():
    prev_cards, prev_updated = load_prev()
    prev_titles = {c.get('title') for c in prev_cards}
    prev_map = {c.get('title'): c for c in prev_cards}
    fresh = collect()
    # 官方来源优先，各自按时间新 -> 旧；每日精选上限 10 条
    official = sorted([c for c in fresh if c.get('official')],
                      key=lambda c: c.get('published_at', ''), reverse=True)
    other = sorted([c for c in fresh if not c.get('official')],
                   key=lambda c: c.get('published_at', ''), reverse=True)
    fresh = (official + other)[:10]

    # 合并：今日新抓在前（is_new = 不在历史里），总量控制在 5~10 条，宁缺毋滥
    final = []
    seen_t = set()
    for c in fresh:
        t = c.get('title')
        if t in seen_t:
            continue
        # 回填历史中已有中文解读，避免被新抓的空值覆盖
        pc = prev_map.get(t)
        if pc:
            # 若历史中有更长的中文正文（人工翻译），优先保留，避免被 80 字片段覆盖
            if pc.get('summary') and len(pc.get('summary', '')) > len(c.get('summary', '')):
                c['summary'] = pc['summary']
            if not c.get('title_cn') and pc.get('title_cn'):
                c['title_cn'] = pc['title_cn']
            if not c.get('impact') and pc.get('impact'):
                c['impact'] = pc['impact']
            if not c.get('uses') and pc.get('uses'):
                c['uses'] = pc['uses']
        c['is_new'] = t not in prev_titles
        seen_t.add(t)
        final.append(c)
    # 当日新不足 5 条时，用前一天重要内容补齐，但总量仍不超过 10
    if len(final) < 5:
        for c in prev_cards:
            t = c.get('title')
            if t in seen_t:
                continue
            if len(final) >= 5:
                break
            c['is_new'] = False
            seen_t.add(t)
            final.append(c)

    today = NOW.strftime('%Y-%m-%d')
    out = {'updated': today, 'cards': final}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    new_count = sum(1 for c in final if c.get('is_new'))
    sys.stderr.write('generated %d cards (new today: %d)\n' % (len(final), new_count))


if __name__ == '__main__':
    main()
