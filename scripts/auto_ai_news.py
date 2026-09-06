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
# 中文译文缓存：按 source_url 索引，跨天保留。
# 每日列表只留最新 10 条，卡片一旦被挤出列表，人工翻译的中文就会丢失；
# 这份缓存让已翻译过的条目即使暂时掉出列表，再次出现时中文也能自动找回。
CN_CACHE = BASE / 'assets' / 'ai_cards_cn_cache.json'

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
    # —— 官方 / 权威科技源（标题与链接真实可靠）——
    # AI 官方：免关键词过滤，保证不漏重要 AI 发布
    {'url': 'https://huggingface.co/blog/feed.xml', 'outlet': 'Hugging Face', 'lang': 'en', 'company': 'Hugging Face', 'ai_only': True},
    {'url': 'https://github.blog/feed/', 'outlet': 'GitHub', 'lang': 'en', 'company': 'GitHub', 'ai_only': True},
    {'url': 'https://blog.google/technology/ai/rss/', 'outlet': 'Google', 'lang': 'en', 'company': 'Google', 'ai_only': True},
    {'url': 'https://blogs.nvidia.com/feed/', 'outlet': 'NVIDIA', 'lang': 'en', 'company': 'NVIDIA', 'ai_only': True},
    {'url': 'https://openai.com/blog/rss.xml', 'outlet': 'OpenAI', 'lang': 'en', 'company': 'OpenAI', 'ai_only': True},
    {'url': 'https://news.microsoft.com/source/topics/ai/rss/', 'outlet': 'Microsoft', 'lang': 'en', 'company': 'Microsoft', 'ai_only': True},
    # 综合科技媒体（不强制 AI，用于补 Apple/Tesla/手机/芯片等）
    {'url': 'https://techcrunch.com/category/artificial-intelligence/feed/', 'outlet': 'TechCrunch', 'lang': 'en'},
    {'url': 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml', 'outlet': 'The Verge', 'lang': 'en'},
    {'url': 'https://arstechnica.com/ai/feed/', 'outlet': 'Ars Technica', 'lang': 'en'},
    # Apple 官方
    {'url': 'https://www.apple.com/newsroom/rss-feed.rss', 'outlet': 'Apple Newsroom', 'lang': 'en', 'company': 'Apple', 'category': 'Apple'},
    {'url': 'https://developer.apple.com/news/rss/news.rss', 'outlet': 'Apple Developer', 'lang': 'en', 'company': 'Apple', 'category': 'Apple'},
    # Tesla / 电动车
    {'url': 'https://www.teslarati.com/feed/', 'outlet': 'Teslarati', 'lang': 'en', 'company': 'Tesla', 'category': 'Tesla'},
    # Samsung
    {'url': 'https://news.samsung.com/global/feed/', 'outlet': 'Samsung', 'lang': 'en', 'company': 'Samsung', 'category': '手机'},
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

# 分类标签（按语义命中优先顺序，谁先命中就是谁）
# 优先级：Tesla > Apple > 手机 > 芯片 > 自动驾驶 > 机器人 > AI
CATEGORY_KEYWORDS = [
    ('Tesla',      re.compile(r'tesla\b|(?<![a-z])fsd\b(?!\w+)|robotaxi|cybercab|\boptimus\b|cybertruck|powerwall|(?<![a-z])model\s+[3ysx]\b|(?<![a-z])model[ -][3ysx]\b', re.I)),
    ('Apple',      re.compile(r'apple|苹果|iphone|ipad|macbook|mac ?os|ios|vision\s*pro|apple ?intelligence|airpods|apple ?watch|homepod', re.I)),
    ('手机',       re.compile(r'华为|huawei|mate\s*\d+|harmonyos|harmony\s*os|小米|xiaomi|hyperos|荣耀|honor|vivo|oppo|三星|samsung|galaxy|google ?pixel|一加|oneplus', re.I)),
    ('芯片',       re.compile(r'芯片|chip|半导体|semiconductor|gpu|tpu|高通|qualcomm|骁龙|snapdragon|联发科|mediatek|麒麟|apple ?silicon|m[1-9]\s*(pro|max|ultra)|tsmc|台积电|3nm|2nm', re.I)),
    ('自动驾驶',   re.compile(r'自动驾驶|autonomous ?driving|autonomous ?vehicle|fsd|robotaxi|waymo|apollo|自驾|端到端|城区|领航辅助', re.I)),
    ('机器人',     re.compile(r'机器人|robot|humanoid|optimus|figure|unitree|宇树|1x|boston dynamics', re.I)),
    ('AI',         re.compile(r'(openai|anthropic|claude|gpt|gemini|llama|llm|deep ?seek|qwen|kimi|hunyuan|智能体|agent|ai |artificial intelligence|machine learning|深度学习|多模态|multimodal|foundation model|chatbot|rag|大模型|推理模型|open ?source model)', re.I)),
]

# 重要性评分关键词（high=重大，med=一般，low=小修小补）
HIGH_IMPACT = re.compile(
    r'(release|launch|introduce|unveil|announce|unveils|announces|debut|正式发布|正式推出|震撼|首发|首测|'
    r'new model|new phone|new chip|new ?gpu|next.gen|next-generation|'
    r'GPT-?\s*\d+|Claude-?\s*\d+|Gemini-?\s*\d+|Sora-?\s*\d+|Llama-?\s*\d+|Qwen-?\s*\d+|DeepSeek-?\s*\d+|'
    r'iPhone-?\s*\d+|iPhone-?\s*Pro|iPhone-?\s*Air|MacBook|iPad|Vision-?\s*Pro|Apple-?\s*Watch|Apple-?\s*Intelligence|'
    r'Tesla|Mate-?\s*\d+|Xiaomi-?\s*\d+|Pixel-?\s*\d+|Galaxy-?\s*S\d+|'
    r'收购|acquire|acquisition|merger|'
    r'invest|round of funding|融资|估值|billion|million|'
    r'rescue|breakthrough|break ?through|开创|首创|首次|first|epoch|milestone|里程碑|'
    r'IPO|上市|'
    r'Regulator|regulation|ban|sue|lawsuit|监管|调查|罚款|禁令|'
    r'Roundtable|Cannes|GTC|IFA|OFC|首映|开幕式|start-up|发布|launches|'
    r'全球|重磅|震撼|最大规模|最贵|最强|最强)',
    re.I)

MED_IMPACT = re.compile(
    r'(update|upgrade|feature|新功能|性能|bench|benchmarks|tools|api|beta|preview|ra preview|figma|'
    r'now available|generally available|downloadable|available today|开始推送|开放|预览|'
    r'整合|integration|partner|合作|compatible|可用|上线|推出|fast|fast ?charge|improvement|'
    r'price|release ?date|date ?set|pre-order|reservation)',
    re.I)

# 不让它进 list 的关键词（纯粹的营销话术/页面推广/友情链接广告）
LOW_BLOCK = re.compile(
    r'(赞助内容|promoted|paid ?partner|广告|sponsored|advertis|newsletter ?signup|订阅 ?newsletter|'
    r'disclaimer|免责声明)',
    re.I)


def classify_category(text, default='AI'):
    """返回分类标签：AI / Apple / Tesla / 手机 / 芯片 / 机器人 / 自动驾驶"""
    for name, pat in CATEGORY_KEYWORDS:
        if pat.search(text):
            return name
    return default


def score_importance(title, summary, official=False):
    """
    重要性: 'high' / 'med' / 'low'
    - official 源的默认不会是 low（官方发布一定不是营销）
    - 命中明确『发布/收购/重大/重大产品/版本大更新/重大更新/监管/里程碑』→ high
    - 命中『feature/update/tools/beta/preview』『合作/上线/推送』→ med
    - 命中仅为『newsletter/赞助/广告』→ low (会被过滤)
    """
    text = (title or '') + ' ' + (summary or '')
    if LOW_BLOCK.search(text) and not HIGH_IMPACT.search(text):
        return 'low'
    if HIGH_IMPACT.search(text):
        return 'high'
    if MED_IMPACT.search(text):
        return 'med'
    # 官方源默认中（中性的更新）；非官方源默认中
    return 'med' if official else 'med'


_IMPORTANCE_RANK = {'high': 0, 'med': 1, 'low': 2}

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


def load_cn_cache():
    """读取中文译文缓存；任何异常都退化为空 dict，绝不影响每日更新。"""
    try:
        if CN_CACHE.exists():
            d = json.loads(CN_CACHE.read_text(encoding='utf-8'))
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return {}


def save_cn_cache(cache):
    try:
        CN_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2),
                            encoding='utf-8')
    except Exception:
        pass


def _cache_put(cache, c):
    """把一张卡片的中文译文写入缓存（必须同时有链接和中文标题才算有效译文）。"""
    u, t = c.get('source_url', ''), c.get('title_cn', '')
    if u and t:
        cache[u] = {'title_cn': t,
                    'summary': c.get('summary', ''),
                    'impact': c.get('impact', ''),
                    'uses': c.get('uses', '')}


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
                # 非 AI 专属 / 非分类专用源（中文媒体 / 综合英文媒体）必须命中 AI 关键词，避免无关垃圾内容混入
                # 已知分类（如 Apple/Tesla）的官方源，跳过 AI 关键词检查（它们本身就在自家领域内）
                if not feed.get('ai_only') and not feed.get('category') and not AI_KEYWORDS.search(text):
                    continue
                company = feed.get('company') or detect_company(title) or detect_company(feed['outlet']) or feed['outlet']
                pub_bj = pub.astimezone(BJTZ) if pub else NOW
                date_str = pub_bj.strftime('%Y-%m-%d')
                cap = 320 if feed['lang'] == 'zh' else 200
                summary = truncate(it['summary'], cap)
                if feed['lang'] == 'en':
                    head = ('【%s 官方动态】' % company) if not summary else ('【%s】' % company)
                    summary = head + (summary if summary else title)
                # 先用 feed 直接声明的 category（如 Apple/Tesla/Samsung），再用关键词推断
                cat_default = feed.get('category') or ('AI' if feed.get('ai_only') else 'AI')
                importance = score_importance(title, summary, official=bool(feed.get('ai_only') or feed.get('category')))
                cat = feed.get('category') or classify_category(title + ' ' + (summary or ''), default=cat_default)
                card = {
                    'tag': company,
                    'company': company,
                    'category': cat,
                    'importance': importance,
                    'source': feed['outlet'],
                    'title': title,
                    'title_cn': '',
                    'date': date_str,
                    'published_at': pub_bj.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
                    'summary': summary,
                    'impact': '',
                    'uses': '',
                    'source_url': link,
                    'official': bool(feed.get('ai_only') or feed.get('category')),
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
    # 给历史的旧卡补 importance / category（兼容升级前的数据）
    for c in prev_cards:
        if not c.get('category'):
            c['category'] = classify_category((c.get('title') or '') + ' ' + (c.get('summary') or ''), default='AI')
        if not c.get('importance'):
            c['importance'] = score_importance(c.get('title', ''), c.get('summary', ''), official=c.get('official', False))

    prev_titles = {c.get('title') for c in prev_cards}
    prev_map = {c.get('title'): c for c in prev_cards}

    # 载入中文缓存，并先把历史里已有的中文译文沉淀进缓存
    cn_cache = load_cn_cache()
    try:
        for c in prev_cards:
            _cache_put(cn_cache, c)
    except Exception:
        pass

    fresh = collect()
    # 过滤掉纯营销/低质内容（importance=low）
    fresh = [c for c in fresh if c.get('importance') != 'low']
    # 排序：高重要性优先，同重要性内按时间新→旧
    def _sort_key(c):
        return (_IMPORTANCE_RANK.get(c.get('importance', 'med'), 1),
                c.get('published_at', ''))
    fresh.sort(key=_sort_key, reverse=True)
    fresh = fresh[:10]

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
        # 标题没命中历史时，再按 source_url 找回缓存里的中文
        # （防止标题被微调、或卡片曾掉出最新 10 条导致译文丢失）
        if not c.get('title_cn'):
            cu = cn_cache.get(c.get('source_url', ''))
            if cu:
                if cu.get('title_cn'):
                    c['title_cn'] = cu['title_cn']
                if cu.get('summary') and len(cu.get('summary', '')) > len(c.get('summary', '')):
                    c['summary'] = cu['summary']
                if not c.get('impact') and cu.get('impact'):
                    c['impact'] = cu['impact']
                if not c.get('uses') and cu.get('uses'):
                    c['uses'] = cu['uses']
        c['is_new'] = t not in prev_titles
        seen_t.add(t)
        final.append(c)
    # 当日新不足 5 条时，用前一天高重要性内容补齐，但总量仍不超过 10
    # 按 importance 优先、时间次排序的回忆卡
    if len(final) < 5:
        backup_pool = [c for c in prev_cards if c.get('importance') != 'low']
        backup_pool.sort(key=lambda c: (_IMPORTANCE_RANK.get(c.get('importance', 'med'), 1), c.get('published_at', '')), reverse=True)
        for c in backup_pool:
            t = c.get('title')
            if t in seen_t:
                continue
            if len(final) >= 5:
                break
            c['is_new'] = False
            c['_carryover'] = True  # 标记为跨天延续，前端可显示"昨日重点"
            seen_t.add(t)
            final.append(c)

    # 把本次最终列表里的中文译文沉淀进缓存，供后续复用
    try:
        for c in final:
            _cache_put(cn_cache, c)
        save_cn_cache(cn_cache)
    except Exception:
        pass

    today = NOW.strftime('%Y-%m-%d')
    out = {'updated': today, 'cards': [dict(c) for c in final]}  # 先 copy 避免后续修改 prev_cards 影响输出
    # 清理内部标记字段，仅保留前端实际需要的
    for c in out['cards']:
        c.pop('_carryover', None)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    new_count = sum(1 for c in final if c.get('is_new'))
    sys.stderr.write('generated %d cards (new today: %d)\n' % (len(final), new_count))


if __name__ == '__main__':
    main()
