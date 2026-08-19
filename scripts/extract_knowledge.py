#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 knowledge/articles/*.html 抽取知识卡片，输出 assets/knowledge_cards.json。
每张卡片：标题 + 分类 + 摘要（前两段）+ 原文链接。"""
import os, re, json, glob, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART_DIR = os.path.join(ROOT, "knowledge", "articles")
OUT = os.path.join(ROOT, "assets", "knowledge_cards.json")

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = _html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

cards = []
for path in sorted(glob.glob(os.path.join(ART_DIR, "*.html"))):
    name = os.path.basename(path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    # 标题
    t = re.search(r'<title>(.*?)</title>', html, re.S)
    title = strip_tags(t.group(1)) if t else name
    # 分类
    cat = ""
    cm = re.search(r'分类：([^｜<]+)', html)
    if cm:
        cat = cm.group(1).strip()
    else:
        pm = re.match(r'([A-Za-z\u4e00-\u9fff]+)-\d', name)
        if pm:
            cat = pm.group(1)
    # 摘要：取正文前若干段（跳过 blockquote 与分隔线）
    # 先去掉 style/script
    body = re.sub(r'<style.*?</style>', '', html, flags=re.S)
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    paras = re.findall(r'<p>(.*?)</p>', body, re.S)
    summary_parts = []
    for p in paras:
        txt = strip_tags(p)
        if not txt or set(txt) <= set('-—·• '):
            continue
        if len(txt) < 15:
            continue
        summary_parts.append(txt)
        if len(summary_parts) >= 2:
            break
    summary = " ".join(summary_parts)
    if not summary:
        summary = title
    cards.append({
        "title": title,
        "cat": cat or "知识",
        "summary": summary,
        "href": "knowledge/articles/" + name,
    })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"cards": cards}, f, ensure_ascii=False, indent=2)

print("知识卡片数:", len(cards), "| 输出:", OUT)
