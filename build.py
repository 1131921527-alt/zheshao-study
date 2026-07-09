# -*- coding: utf-8 -*-
"""
哲少的学习任务 · 站点生成器
扫描 腾讯龙虾的成品 下各自动化产出目录，归一化命名后生成静态站点。
重跑本脚本即可把新内容 + 历史同步进站点，随后 git push 即上线。
"""
import os, shutil, re, glob, datetime

SRC = r"E:\workbuddyFIle\腾讯龙虾的成品"
OUT = r"E:\workbuddyFIle\腾讯龙虾的成品\哲少的学习任务"
SITE_TITLE = "喆少的学习任务"

WEEK = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def weekday_cn(d):
    return WEEK[d.weekday()]


# ---------- 各板块定义 ----------
SECTIONS = [
    {
        "key": "ai-news",
        "title": "AI动态播报",
        "icon": "📰",
        "color": "#58a6ff",
        "grad": "linear-gradient(135deg,#1f3a5f,#0f3460)",
        "desc": "每天AI圈发生了什么，一页看完",
        "src": os.path.join(SRC, "AI动态播报"),
        "out": "ai-news",
        "kind": "date",
    },
    {
        "key": "ai-knowledge",
        "title": "AI系统性学习",
        "icon": "🧠",
        "color": "#c084fc",
        "grad": "linear-gradient(135deg,#3a1a5c,#533483)",
        "desc": "每天一个AI知识点，30天从小白到上手",
        "src": os.path.join(SRC, "AI学习卡片"),
        "out": "ai-knowledge",
        "kind": "day",
        "prefix": "ai-knowledge-day",
    },
    {
        "key": "ai-prompt",
        "title": "提示词技巧",
        "icon": "🎯",
        "color": "#fbbf24",
        "grad": "linear-gradient(135deg,#5c3a1a,#7a4a1a)",
        "desc": "每天1个提示词技巧，直接复制用",
        "src": os.path.join(SRC, "AI学习卡片"),
        "out": "ai-prompt",
        "kind": "day",
        "prefix": "ai-prompt-day",
    },
    {
        "key": "ielts",
        "title": "雅思单词",
        "icon": "📖",
        "color": "#f87171",
        "grad": "linear-gradient(135deg,#5c1a3a,#7a1a3a)",
        "desc": "每天15个高频词，例句+记忆法",
        "src": os.path.join(SRC, "雅思词汇"),
        "out": "ielts",
        "kind": "ielts",
    },
]


def collect(sec):
    """返回 [(out_name, label, sort_key)]，已按最新在前排序"""
    items = []
    src = sec["src"]
    if not os.path.isdir(src):
        return items
    kind = sec["kind"]

    if kind == "date":
        for f in glob.glob(os.path.join(src, "*.html")):
            base = os.path.basename(f)
            m = re.search(r"(\d{4})-(\d{2})-(\d{2})", base)
            if not m:
                continue
            y, mo, da = map(int, m.groups())
            try:
                d = datetime.date(y, mo, da)
            except ValueError:
                continue
            out = "ai-news-%04d-%02d-%02d.html" % (y, mo, da)
            label = "%02d-%02d %s" % (mo, da, weekday_cn(d))
            items.append((out, label, d))

    elif kind == "day":
        for f in glob.glob(os.path.join(src, "*.html")):
            base = os.path.basename(f)
            if not base.startswith(sec["prefix"]):
                continue
            m = re.search(r"day(\d+)", base)
            if not m:
                continue
            n = int(m.group(1))
            out = "day%02d.html" % n
            label = "Day %d" % n
            items.append((out, label, n))

    elif kind == "ielts":
        for f in glob.glob(os.path.join(src, "*.html")):
            base = os.path.basename(f)
            if base == "ielts-vocab":
                continue
            m = re.search(r"ielts-vocab-day(\d+)", base)
            if m:
                n = int(m.group(1))
                items.append(("day%02d.html" % n, "Day %d" % n, n))
        # 完整版带音频
        full = os.path.join(src, "ielts-vocab", "index.html")
        if os.path.isfile(full):
            items.append(("full.html", "完整版 · 带音频", 9999))

    # 排序：最新在前
    items.sort(key=lambda x: x[2], reverse=True)
    return items


CSS = """* { margin: 0; padding: 0; box-sizing: border-box }
:root { --bg:#0d1117; --fg:#c9d1d9; --muted:#8b949e; --line:#30363d; --card:#161b22; }
html { -webkit-text-size-adjust: 100%; }
body { background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; min-height: 100vh; }
a { color: inherit; text-decoration: none; }
.wrap { max-width: 760px; margin: 0 auto; padding: 0 16px 60px; }
.hero { text-align: center; padding: 48px 20px 36px; background: radial-gradient(120% 120% at 50% 0%, #1b2740 0%, #0d1117 70%); border-bottom: 1px solid var(--line); }
.hero .logo { font-size: 52px; line-height: 1; margin-bottom: 12px; }
.hero h1 { font-size: 28px; color: #fff; font-weight: 800; letter-spacing: 1px; }
.hero .tag { font-size: 14px; color: #58a6ff; margin-top: 10px; }
.hero .sub { font-size: 12px; color: var(--muted); margin-top: 6px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 28px 0; }
@media (max-width: 560px) { .grid { grid-template-columns: 1fr; } }
.card { border-radius: 16px; padding: 22px 20px; position: relative; overflow: hidden; border: 1px solid var(--line); transition: transform .15s, border-color .15s; display: block; }
.card:active { transform: scale(.98); }
.card .icon { font-size: 30px; }
.card .title { font-size: 17px; font-weight: 700; color: #fff; margin: 8px 0 4px; }
.card .latest { display: inline-block; font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 20px; background: rgba(255,255,255,.14); color: #fff; margin-bottom: 8px; }
.card .desc { font-size: 12.5px; color: rgba(255,255,255,.72); line-height: 1.55; }
.card .count { font-size: 12px; color: rgba(255,255,255,.55); margin-top: 10px; }
.support { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 26px 22px; text-align: center; margin-top: 8px; }
.support h2 { font-size: 18px; color: #fff; margin-bottom: 8px; }
.support p { font-size: 13px; color: var(--muted); margin-bottom: 18px; }
.qr-row { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
.qr-card { width: 140px; }
.qr-card img { width: 140px; height: 140px; object-fit: cover; border-radius: 12px; background: #fff; border: 1px solid var(--line); }
.qr-card .qr-fallback { width: 140px; height: 140px; border-radius: 12px; background: repeating-linear-gradient(45deg,#1f6feb22,#1f6feb22 8px,#0d1117 8px,#0d1117 16px); border: 1px dashed var(--muted); display: none; align-items: center; justify-content: center; color: var(--muted); font-size: 12px; text-align: center; padding: 8px; }
.qr-card .label { display: block; margin-top: 8px; font-size: 13px; color: var(--fg); font-weight: 600; }
.support .hint { font-size: 11px; color: var(--muted); margin-top: 16px; }
.footer { text-align: center; color: #555; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--line); line-height: 1.8; }
.back { display: inline-flex; align-items: center; gap: 6px; color: #58a6ff; font-size: 14px; font-weight: 600; margin: 22px 0 6px; }
.sec-head { text-align: center; padding: 36px 0 8px; }
.sec-head .icon { font-size: 40px; }
.sec-head h1 { font-size: 24px; color: #fff; margin: 8px 0 4px; }
.sec-head .desc { font-size: 13px; color: var(--muted); }
.list { display: flex; flex-direction: column; gap: 2px; margin-top: 18px; }
.list a { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; background: var(--card); border: 1px solid var(--line); border-radius: 10px; font-size: 14px; transition: border-color .15s, background .15s; }
.list a:active { background: #1f2937; }
.list a .label { font-weight: 600; color: #e6edf3; }
.list a .arrow { color: #555; font-size: 16px; }
.list a:active .arrow { color: #58a6ff; }
"""


def write_css():
    d = os.path.join(OUT, "assets")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)


def section_index_html(sec, items):
    cards = ""
    for out, label, _ in items:
        cards += ('<a href="%s"><span class="label">%s</span><span class="arrow">→</span></a>\n' % (out, label))
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s · %s</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="wrap">
<a class="back" href="../">← 返回首页</a>
<div class="sec-head">
<div class="icon">%s</div>
<h1>%s</h1>
<div class="desc">%s · 共 %d 期</div>
</div>
<div class="list">
%s</div>
<div class="footer">腾讯龙虾的成品 · %s<br>内容每日自动更新</div>
</div>
</body>
</html>""" % (SITE_TITLE, sec["title"], sec["icon"], sec["title"], sec["desc"], len(items), cards, sec["title"])


def main_index_html(sections_data):
    cards = ""
    total = 0
    for sec, items in sections_data:
        total += len(items)
        latest = items[0][1] if items else "—"
        cards += (
            '<a class="card" style="background:%s" href="%s/index.html">'
            '<span class="icon">%s</span>'
            '<span class="latest">最新 %s</span>'
            '<div class="title">%s</div>'
            '<div class="desc">%s</div>'
            '<div class="count">已积累 %d 期 →</div>'
            '</a>\n'
        ) % (sec["grad"], sec["out"], sec["icon"], latest, sec["title"], sec["desc"], len(items))

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="喆少的学习任务：每天自动更新的 AI 动态播报、AI 系统性学习、提示词技巧、雅思单词，免费公开，手机随时看。">
<title>%s</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="hero">
<div class="logo">🦞</div>
<h1>%s</h1>
<div class="tag">每天自动更新 · AI / 雅思 / 提示词 一站式学习</div>
<div class="sub">已积累 %d 期内容 · 手机点开就能看</div>
</header>
<main class="wrap">
<section class="grid">
%s</section>

<section class="support">
<h2>☕ 请喆少喝杯咖啡</h2>
<p>内容全部免费公开。如果对你有帮助，扫下面的码支持 1 元，就是最大的鼓励。</p>
<div class="qr-row">
<div class="qr-card">
<img src="assets/wechat.png" alt="微信收款码" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
<div class="qr-fallback">微信收款码<br>放入 assets/wechat.png</div>
<span class="label">微信</span>
</div>
<div class="qr-card">
<img src="assets/alipay.jpg" alt="支付宝收款码" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
            <div class="qr-fallback">支付宝收款码<br>放入 assets/alipay.jpg</div>
<span class="label">支付宝</span>
</div>
</div>
<div class="hint">收款码位置：喆少的学习任务/assets/wechat.png、alipay.jpg，放进去就自动显示。</div>
</section>
</main>
<footer>腾讯龙虾的成品 · %s<br>内容每日自动更新 · 由 GitHub Pages 托管</footer>
</body>
</html>""" % (SITE_TITLE, SITE_TITLE, total, cards, SITE_TITLE)


def main():
    os.makedirs(OUT, exist_ok=True)
    write_css()
    sections_data = []
    for sec in SECTIONS:
        items = collect(sec)
        out_dir = os.path.join(OUT, sec["out"])
        os.makedirs(out_dir, exist_ok=True)
        # 复制内容文件
        src = sec["src"]
        for out_name, _, _ in items:
            # 找源文件
            src_file = None
            if sec["kind"] == "date":
                m = re.search(r"(\d{4}-\d{2}-\d{2})", out_name)
                if m:
                    d = m.group(1)
                    cand1 = os.path.join(src, "ai-news-%s.html" % d)
                    cand2 = os.path.join(src, "AI动态播报-%s.html" % d)
                    src_file = cand1 if os.path.isfile(cand1) else (cand2 if os.path.isfile(cand2) else None)
            elif sec["kind"] == "day":
                m = re.search(r"day(\d+)", out_name)
                if m:
                    src_file = os.path.join(src, "%s%s.html" % (sec["prefix"], m.group(1)))
            elif sec["kind"] == "ielts":
                if out_name == "full.html":
                    src_file = os.path.join(src, "ielts-vocab", "index.html")
                else:
                    m = re.search(r"day(\d+)", out_name)
                    if m:
                        src_file = os.path.join(src, "ielts-vocab-day%s.html" % m.group(1))
            if src_file and os.path.isfile(src_file):
                shutil.copy2(src_file, os.path.join(out_dir, out_name))
        # ielts 板块：复制本地音频目录（单词发音+例句发音）
        if sec["kind"] == "ielts":
            audio_src = os.path.join(src, "audio")
            if os.path.isdir(audio_src):
                audio_dst = os.path.join(out_dir, "audio")
                os.makedirs(audio_dst, exist_ok=True)
                cnt = 0
                for af in os.listdir(audio_src):
                    if af.endswith(".mp3"):
                        shutil.copy2(os.path.join(audio_src, af), os.path.join(audio_dst, af))
                        cnt += 1
                print("  [%s] 复制音频 %d 个" % (sec["title"], cnt))
        # 写板块列表页
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(section_index_html(sec, items))
        sections_data.append((sec, items))
        print("  [%s] %d 期" % (sec["title"], len(items)))
    # 写首页
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(main_index_html(sections_data))
    print("首页已生成。站点目录：%s" % OUT)


if __name__ == "__main__":
    main()
