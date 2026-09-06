# -*- coding: utf-8 -*-
"""
抓取 AI 卡片每篇文章的全文，存入 assets/ai_cards.json 的 fulltext 字段。
- 最大文本块算法定位正文容器（对量子位/爱范儿/少数派/TechCrunch/The Verge 通用）
- 段落清洗：去广告、推荐、版权尾巴
- 幂等：已有 fulltext(>=800字) 跳过；可用 --force 强制重抓
- 前端在 renderNews 里优先读 fulltext，没有就回退 summary
用法：python fetch_fulltext.py [--force]
"""
import io, json, re, sys, time, urllib.request
from lxml import html as LH

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
P = ROOT + r"\assets\ai_cards.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# 尾巴/噪音黑名单（段首或整段匹配）
NOISE = re.compile(
    r"^(关注|扫码|添加微信|加群|加我|入群|戳这里|点击.{0,4}(阅读|查看|下载)|原文链接|相关阅读|推荐阅读|"
    r"延伸阅读|精选专题|更多内容|热门.{0,6}(文章|推荐)|往期.{0,6}(推荐|回顾)|精选.{0,4}推荐|"
    r"欢迎|点赞|在看|分享|转发|收藏|订阅|打赏|广告|赞助|投稿|合作|版权|©|本站|免责声明|"
    r"参考链接|References?|Advertisement|Share this|Related|Sign up|Subscribe|Read more|"
    r"Follow|Credit|Image Credits?|Photo|All rights reserved)",
)
# 署名/导航行：'XX 发自 XX'、'量子位 | 公众号'、'See All ...'、'Posts from ...'
NOISE2 = re.compile(
    r"^(\S{1,12}\s*发自\s*\S{1,12}$|.*公众号\s*QbitAI|量子位\s*\|\s*公众号|"
    r"See All(\s|by)|Posts from (this topic|this author)|^\d+\s*(分钟|字)读完)"
)
MIN_PARA = 10          # 短于这个字数且无句号的段落丢弃
MAX_CHARS = 20000      # 单篇全文软上限（防超长页误抓）


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    raw = urllib.request.urlopen(req, timeout=20).read()
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def clean_paras(div):
    """从正文容器提取并清洗段落"""
    seen, out = set(), []
    for p in div.xpath(".//p"):
        t = "".join(p.itertext())
        t = re.sub(r"\s+", " ", t).strip()
        if not t:
            continue
        if len(t) < MIN_PARA and not re.search(r"[。！？.!?]", t):
            continue                       # 疑似署名/标签
        if NOISE.match(t) or NOISE2.match(t):
            continue                       # 广告/推荐/署名/导航噪音
        if t in seen:
            continue                       # 重复段
        seen.add(t)
        out.append(t)
    # 去重后若首段就是标题的重复，也无所谓；控制总长
    total = sum(len(t) for t in out)
    if total > MAX_CHARS:
        keep, n = [], 0
        for t in out:
            keep.append(t)
            n += len(t)
            if n >= MAX_CHARS:
                keep.append("……（超长已截断，完整内容见文末原文链接）")
                break
        out = keep
    return out


def find_best_div(doc):
    """最大文本块：所有 div 里 .//p 总字数最多且 >=500 的"""
    best, bl = None, 0
    for div in doc.xpath("//div"):
        ps = div.xpath(".//p")
        if len(ps) < 3:
            continue
        n = sum(len("".join(p.itertext())) for p in ps)
        if n > bl:
            bl, best = n, div
    return best, bl


def lang_of(paras):
    txt = "".join(paras)
    if not txt:
        return "zh"
    cjk = len(re.findall(r"[\u4e00-\u9fff]", txt))
    return "zh" if cjk / max(len(txt), 1) > 0.25 else "en"


def main():
    force = "--force" in sys.argv
    d = json.load(io.open(P, encoding="utf-8"))
    cards = d["cards"]
    ok_n = fail_n = skip_n = 0
    for i, it in enumerate(cards):
        w = (it.get("title_cn") or it.get("title") or "")[:24]
        ft = it.get("fulltext")
        if ft and len("".join(ft)) >= 800 and not force:
            print("[%d/%d] %-26s 已有全文，跳过" % (i + 1, len(cards), w))
            skip_n += 1
            continue
        url = it.get("source_url") or ""
        if not url:
            print("[%d/%d] %-26s 无 source_url" % (i + 1, len(cards), w))
            fail_n += 1
            continue
        try:
            html = fetch(url)
            doc = LH.fromstring(html)
            best, bl = find_best_div(doc)
            paras = clean_paras(best) if best is not None else []
            n = sum(len(t) for t in paras)
            if n < 500:
                print("[%d/%d] %-26s 正文仅 %d 字，放弃" % (i + 1, len(cards), w, n))
                fail_n += 1
                continue
            it["fulltext"] = paras
            it["fulltext_lang"] = lang_of(paras)
            it["fulltext_chars"] = n
            print("[%d/%d] %-26s %5d 字 / %2d 段 / %s  OK" %
                  (i + 1, len(cards), w, n, len(paras), it["fulltext_lang"]))
            ok_n += 1
        except Exception as e:
            print("[%d/%d] %-26s FAIL: %s" % (i + 1, len(cards), w, str(e)[:60]))
            fail_n += 1
        time.sleep(1.0)                   # 礼貌间隔
    json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n抓取成功 %d / 失败 %d / 跳过 %d" % (ok_n, fail_n, skip_n))


if __name__ == "__main__":
    main()
