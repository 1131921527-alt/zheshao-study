#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 ai-news/*.html 抽取 AI 卡片，输出 assets/ai_cards.json（百词斩式卡片数据）。
兼容两种版式：新版（<div class="card"> + <h2> + <p>/impact/zh）与旧版（card-heavy + card-title/card-body/card-source）。"""
import os, re, json, glob, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_DIR = os.path.join(ROOT, "ai-news")
OUT = os.path.join(ROOT, "assets", "ai_cards.json")

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = _html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

CARRIER = {"heavy": "重磅", "focus": "重点", "watch": "关注"}

cards = []
for path in glob.glob(os.path.join(NEWS_DIR, "ai-news-*.html")):
    m = re.search(r"ai-news-(\d{4}-\d{2}-\d{2})\.html", os.path.basename(path))
    file_date = m.group(1) if m else ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    # 按卡片拆分（匹配 class="card" 或 class="card xxx"，但不匹配 card-header 等）
    segs = re.split(r'<div class="card(?:["\s])', html)
    for seg in segs[1:]:
        # 卡片类型（旧版 heavy/focus/watch）
        cls_m = re.search(r'^([a-z-]+)"', seg)
        kind = ""
        if cls_m:
            for k, v in CARRIER.items():
                if k in cls_m.group(1):
                    kind = v
        # 标题
        title = ""
        t1 = re.search(r'card-title">(.*?)</div>', seg, re.S)
        if t1:
            title = strip_tags(t1.group(1))
        else:
            h2 = re.search(r'<h2>(.*?)</h2>', seg, re.S)
            if h2:
                title = strip_tags(re.sub(r'<span class="num">.*?</span>', '', h2.group(1)))
        if not title:
            continue
        # 摘要
        summary = ""
        body = re.search(r'card-body">(.*?)</div>', seg, re.S)
        if body:
            summary = strip_tags(body.group(1))
        else:
            ps = re.findall(r'<p>(.*?)</p>', seg, re.S)
            if ps:
                summary = strip_tags(ps[0])
        if not summary:
            continue
        # 影响 / 用法（新版）
        impact = ""
        imp = re.search(r'class="impact">(.*?)</p>', seg, re.S)
        if imp:
            impact = strip_tags(imp.group(1)).replace("对普通人的影响：", "")
        uses = ""
        zh = re.search(r'class="zh">(.*?)</p>', seg, re  .S)
        if zh:
            uses = strip_tags(zh.group(1)).replace("泽少可以怎么用：", "")
        # 标签 / 来源
        tag = "AI"
        tag_m = re.search(r'<span class="tag [^"]*">([^<]+)</span>', seg)
        badge_m = re.search(r'class="badge[^"]*">([^<]+)</span>', seg)
        if tag_m:
            tag = tag_m.group(1).strip()
        elif badge_m:
            tag = badge_m.group(1).strip()
        elif kind:
            tag = kind
        src = ""
        src_m = re.search(r'card-source">(.*?)</div>', seg, re.S)
        if src_m:
            src = strip_tags(src_m.group(1))
        cards.append({
            "tag": tag,
            "title": title,
            "summary": summary,
            "impact": impact,
            "uses": uses,
            "source": src,
            "date": file_date,
        })

seen = set(); uniq = []
for c in cards:
    if c["title"] in seen:
        continue
    seen.add(c["title"]); uniq.append(c)

uniq.sort(key=lambda x: x["date"], reverse=True)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"cards": uniq, "updated": file_date}, f, ensure_ascii=False, indent=2)

print("抽取卡片数:", len(uniq), "| 输出:", OUT)
