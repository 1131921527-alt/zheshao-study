# -*- coding: utf-8 -*-
"""
泽少学习任务 · 站点生成器
扫描 腾讯龙虾的成品 下各自动化产出目录，归一化命名后生成静态站点。
重跑本脚本即可把新内容 + 历史同步进站点，随后 git push 即上线。
"""
import os, shutil, re, glob, datetime

SRC = r"E:\workbuddyFIle\腾讯龙虾的成品"
# OUT 指向线上仓库目录本身。build.py 只更新各板块内容(ai-news/ai-knowledge/ai-prompt/ielts)
# 与其 index.html、assets/style.css、archive.html；**绝不会覆盖手动维护的根 index.html**(App版)。
OUT = r"E:\workbuddyFIle\腾讯龙虾的成品\03-学习网站\zheshao-study"
SITE_TITLE = "泽少学习任务"

WEEK = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# ---------- 联系/收款信息（按需修改） ----------
# 支付宝收款码解码出的真实跳转链接（可直接点击跳转）
ALIPAY_URL = "https://qr.alipay.com/fkx17072tjhicy025mhjk00?0&T=58488-10-14%2017:21:43"
# 微信号（留空则不显示"复制微信号"按钮）；个人微信码是加密码，无法被标准解码器读出链接，
# 只能在微信内长按识别，因此这里提供复制微信号作为兜底。
WECHAT_ID = "Harryalwayslucky"
# 微信 / 支付宝 收款码图片路径（放在 assets/ 下）
WECHAT_QR = "assets/wechat.png"
ALIPAY_QR = "assets/alipay.jpg"

# ---------- 实时时钟（注入到每个页面） ----------
CLOCK_CSS = """
#liveClockBar{position:fixed;top:0;left:0;right:0;z-index:99999;height:44px;display:flex;align-items:center;gap:8px;padding:0 12px;background:linear-gradient(90deg,#0b0f17 0%,#11182a 50%,#0b0f17 100%);border-bottom:1px solid rgba(120,170,255,.4);box-shadow:0 2px 18px rgba(0,0,0,.55),0 1px 0 rgba(88,166,255,.3) inset;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:#c9d1d9;font-size:13px;overflow:hidden}
#liveClockBar .lc-dot{width:8px;height:8px;border-radius:50%;background:#3fb950;box-shadow:0 0 8px #3fb950;animation:lcPulse 1.4s infinite;flex:0 0 auto}
@keyframes lcPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.65)}}
#liveClockBar .lc-date{color:#8b949e;white-space:nowrap}
#liveClockBar .lc-time{font-variant-numeric:tabular-nums;font-weight:700;color:#e6edf3;letter-spacing:.5px;font-size:15px}
#liveClockBar .lc-time #lcH,#liveClockBar .lc-time #lcM{color:#58a6ff}
#liveClockBar .lc-sec{color:#ff7b72}
#liveClockBar .lc-tag{margin-left:auto;color:#d2991d;font-size:11px;white-space:nowrap}
#liveClockBar .lc-bar{position:absolute;left:0;bottom:0;height:2px;background:linear-gradient(90deg,#58a6ff,#ff7b72);width:0%}
#liveClockBar .qr-copy{margin-left:auto;color:#58a6ff;font-size:12px;border:1px solid rgba(88,166,255,.4);border-radius:20px;padding:3px 10px;cursor:pointer;white-space:nowrap}
@media(max-width:430px){#liveClockBar .lc-tag{display:none}#liveClockBar .lc-date{font-size:11px}#liveClockBar .qr-copy{display:none}}
body{padding-top:44px!important}
"""
CLOCK_HTML = """
<div id="liveClockBar">
<span class="lc-dot"></span>
<span class="lc-date" id="lcDate">--</span>
<span class="lc-time"><span id="lcH">--</span>:<span id="lcM">--</span>:<span class="lc-sec" id="lcS">--</span></span>
<span class="lc-tag">time goes by</span>
<i class="lc-bar" id="lcBar"></i>
</div>
"""
CLOCK_JS = """
(function(){
  var w=['周日','周一','周二','周三','周四','周五','周六'];
  function p(n){return (n<10?'0':'')+n;}
  function tick(){
    var d=new Date();
    var dt=document.getElementById('lcDate');
    if(dt) dt.textContent=d.getFullYear()+'年'+p(d.getMonth()+1)+'月'+p(d.getDate())+'日 '+w[d.getDay()];
    var h=document.getElementById('lcH'),m=document.getElementById('lcM'),s=document.getElementById('lcS'),b=document.getElementById('lcBar');
    if(h)h.textContent=p(d.getHours());
    if(m)m.textContent=p(d.getMinutes());
    if(s)s.textContent=p(d.getSeconds());
    if(b)b.style.width=(d.getSeconds()/60*100)+'%';
  }
  tick();setInterval(tick,1000);
  window.lcZoom=function(img){ if(img&&img.src) window.open(img.src,'_blank'); };
  window.lcCopyWx=function(){
    var id=__WECHAT_ID__;
    if(!id) return;
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(id).then(function(){alert('微信号已复制：'+id);}); }
    else { var t=document.createElement('textarea'); t.value=id; document.body.appendChild(t); t.select(); try{document.execCommand('copy');alert('微信号已复制：'+id);}catch(e){} document.body.removeChild(t); }
  };
})();
"""
CLOCK_JS = CLOCK_JS.replace("__WECHAT_ID__", '"%s"' % WECHAT_ID)


# ---------- 统一手机壳（桌面端把独立内容页也收成手机宽度） ----------
FRAME_CSS = """
/*zsframe*/
@media (min-width: 600px) {
  html, body { background: #06090F !important; }
  .wrap, .lesson {
    max-width: 540px !important; margin: 16px auto !important;
    background: #0B0F17 !important; border-radius: 16px !important;
    box-shadow: 0 8px 60px rgba(0,0,0,.5) !important;
    border-left: 1px solid rgba(201,168,106,.10) !important;
    border-right: 1px solid rgba(201,168,106,.10) !important;
    overflow: hidden !important;
  }
  /* 内容页（body 本身就是列，无 .app/.wrap/.lesson 外层）直接把 body 收成手机壳 */
  body:not(:has(.app)):not(:has(.wrap)):not(:has(.lesson)) {
    max-width: 540px !important; margin: 16px auto !important;
    background: #0B0F17 !important; border-radius: 16px !important;
    box-shadow: 0 8px 60px rgba(0,0,0,.5) !important;
    border-left: 1px solid rgba(201,168,106,.10) !important;
    border-right: 1px solid rgba(201,168,106,.10) !important;
    min-height: calc(100vh - 32px) !important;
  }
  .grid { grid-template-columns: 1fr !important; }
  .qr-row { flex-direction: column; align-items: center; }
}
"""


def inject_clock(html):
    """在每个页面注入实时时钟（自包含，不依赖外部资源）。"""
    if "liveClockBar" in html:
        return html
    block = "<style>" + CLOCK_CSS + "</style>" + CLOCK_HTML + "<script>" + CLOCK_JS + "</script>"
    if "</body>" in html:
        return html.replace("</body>", block + "</body>", 1)
    if "</html>" in html:
        return html.replace("</html>", block + "</html>", 1)
    return html + block


def inject_frame(html):
    """在每个独立内容页注入统一手机壳样式（仅桌面端生效，依赖 :has()）。"""
    if "zsframe" in html:
        return html
    block = "<style>" + FRAME_CSS + "</style>"
    if "</body>" in html:
        return html.replace("</body>", block + "</body>", 1)
    if "</html>" in html:
        return html.replace("</html>", block + "</html>", 1)
    return html + block


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

    # 对 day/ielts 板块重新按顺序编号（最新=1），避免跳号影响观感
    if kind == "day":
        items = [(out, "Day %d" % (i + 1), sk) for i, (out, label, sk) in enumerate(items)]
    elif kind == "ielts":
        new_items = []
        day_i = 0
        for out, label, sk in items:
            if sk == 9999:
                new_items.append((out, label, sk))
            else:
                day_i += 1
                new_items.append((out, "Day %d" % day_i, sk))
        items = new_items

    return items


CSS = """* { margin: 0; padding: 0; box-sizing: border-box }
:root { --bg:#0B0F17; --fg:#E6EAF2; --muted:#9AA6BD; --line:rgba(201,168,106,.16); --primary:#C9A86A; --primary-700:#E4C98C; --primary-050:rgba(201,168,106,.08); --card:#151B2B; }
html { -webkit-text-size-adjust: 100%; }
body { background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; min-height: 100vh; }
a { color: inherit; text-decoration: none; }
.wrap { max-width: 540px; margin: 0 auto; padding: 0 16px 60px; }
.hero { text-align: center; padding: 44px 20px 32px; background: linear-gradient(135deg,#16203a,#0b0f17); border-bottom: 1px solid var(--line); }
.hero .logo { font-size: 48px; line-height: 1; margin-bottom: 10px; }
.hero h1 { font-size: 28px; font-weight: 800; letter-spacing: 1px; color: var(--primary); }
.hero .tag { font-size: 14px; color: var(--primary-700); margin-top: 10px; }
.hero .sub { font-size: 12px; color: var(--muted); margin-top: 6px; }
.grid { display: grid; grid-template-columns: 1fr; gap: 14px; margin: 28px 0; }

/* 桌面端统一手机壳：列表/归档页收成手机宽度并居中，与首页 .app 一致 */
@media (min-width: 600px) {
  html, body { background: #06090F !important; }
  .wrap { max-width: 540px !important; margin: 16px auto !important; background: #0B0F17 !important; border-radius: 16px !important; box-shadow: 0 8px 60px rgba(0,0,0,.5) !important; border-left: 1px solid rgba(201,168,106,.10) !important; border-right: 1px solid rgba(201,168,106,.10) !important; overflow: hidden !important; }
}
.card { border-radius: 16px; padding: 22px 20px; position: relative; overflow: hidden; border: 1px solid var(--line); background: linear-gradient(135deg,#1b2742,#121a2e); box-shadow: 0 1px 2px rgba(0,0,0,.3); transition: transform .2s, box-shadow .2s; display: block; }
.card:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,.45); }
.card:active { transform: scale(.98); }
.card .icon { font-size: 30px; }
.card .title { font-size: 17px; font-weight: 700; color: #fff; margin: 8px 0 4px; }
.card .latest { display: inline-block; font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 20px; background: rgba(201,168,106,.18); color: var(--primary-700); margin-bottom: 8px; }
.card .desc { font-size: 12.5px; color: rgba(230,234,242,.78); line-height: 1.55; }
.card .count { font-size: 12px; color: rgba(230,234,242,.6); margin-top: 10px; }
.support { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 26px 22px; text-align: center; margin-top: 8px; box-shadow: 0 1px 2px rgba(0,0,0,.3); }
.support h2 { font-size: 18px; color: var(--fg); margin-bottom: 8px; }
.support p { font-size: 13px; color: var(--muted); margin-bottom: 18px; }
.qr-row { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
.qr-card { width: 140px; }
.qr-card img { width: 140px; height: 140px; object-fit: contain; border-radius: 12px; background: #fff; border: 1px solid var(--line); }
.qr-card .qr-fallback { width: 140px; height: 140px; border-radius: 12px; background: repeating-linear-gradient(45deg,rgba(201,168,106,.08),rgba(201,168,106,.08) 8px,#0b0f17 8px,#0b0f17 16px); border: 1px dashed var(--muted); display: none; align-items: center; justify-content: center; color: var(--muted); font-size: 12px; text-align: center; padding: 8px; }
.qr-card .label { display: block; margin-top: 8px; font-size: 13px; color: var(--fg); font-weight: 600; }
.qr-img { cursor: zoom-in; }
.qr-link { display: block; text-decoration: none; }
.wx-copy { display: inline-block; margin-top: 14px; color: #0b0f17; font-size: 13px; border: none; border-radius: 20px; padding: 9px 20px; cursor: pointer; font-weight: 700; background: var(--primary); }
.wx-copy:hover { transform: translateY(-2px); }
.wx-copy:active { transform: translateY(0); }
.support .hint { font-size: 11px; color: var(--muted); margin-top: 16px; }
.footer { text-align: center; color: var(--muted); font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--line); line-height: 1.8; }
.back { display: inline-flex; align-items: center; gap: 6px; color: var(--primary); font-size: 14px; font-weight: 600; margin: 22px 0 6px; }
.sec-head { text-align: center; padding: 36px 0 8px; }
.sec-head .icon { font-size: 40px; }
.sec-head h1 { font-size: 24px; margin: 8px 0 4px; color: var(--primary); }
.sec-head .desc { font-size: 13px; color: var(--muted); }
.list { display: flex; flex-direction: column; gap: 2px; margin-top: 18px; }
.list a { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; background: var(--card); border: 1px solid var(--line); border-radius: 10px; font-size: 14px; transition: border-color .15s, background .15s, transform .15s; }
.list a:hover { border-color: var(--primary); background: var(--primary-050); transform: translateX(4px); }
.list a:active { background: var(--primary-050); }
.list a .label { font-weight: 600; color: var(--fg); }
.list a .arrow { color: var(--muted); font-size: 16px; }
.list a:active .arrow { color: var(--primary); }
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

    copy_btn = ""
    if WECHAT_ID:
        copy_btn = '<div class="hint" style="margin-top:2px">想一起交流？加我微信：<span class="wx-copy" onclick="lcCopyWx()">复制微信号 %s</span></div>\n' % WECHAT_ID
    support_html = (
        '<section class="support">\n'
        '<h2>☕ 觉得有用，欢迎打赏</h2>\n'
        '<p>这些内容会一直免费更新。如果觉得我做得还可以，欢迎扫码打赏，随意就好 —— 也欢迎加我微信一起交流。</p>\n'
        '<div class="qr-row">\n'
        '  <div class="qr-card">\n'
        '    <img class="qr-img" src="%s" alt="微信赞赏码" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">\n'
        '    <div class="qr-fallback">微信赞赏码<br>放入 assets/wechat.png</div>\n'
        '    <span class="label">微信赞赏码</span>\n'
        '  </div>\n'
        '</div>\n'
        '<div class="hint">在微信里打开本页，长按上方二维码即可打赏。</div>\n'
        '%s'
        '</section>\n'
    ) % (WECHAT_QR, copy_btn)

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="泽少学习任务：每天自动更新的 AI 动态播报、AI 系统性学习、提示词技巧、雅思单词，免费公开，手机随时看。">
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

%s
</main>
<footer>腾讯龙虾的成品 · %s<br>内容每日自动更新 · 由 GitHub Pages 托管</footer>
</body>
</html>""" % (SITE_TITLE, SITE_TITLE, total, cards, support_html, SITE_TITLE)


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
                dst = os.path.join(out_dir, out_name)
                shutil.copy2(src_file, dst)
                # 注入实时时钟（自包含，不依赖页面路径）
                try:
                    with open(dst, "r", encoding="utf-8") as fh:
                        html = fh.read()
                    with open(dst, "w", encoding="utf-8") as fh:
                        fh.write(inject_frame(inject_clock(html)))
                except Exception as e:
                    print("  [warn] 注入时钟失败 %s: %s" % (out_name, e))
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
            f.write(inject_frame(inject_clock(section_index_html(sec, items))))
        sections_data.append((sec, items))
        print("  [%s] %d 期" % (sec["title"], len(items)))
    # 写首页：旧版设计保留为 archive.html，新的金融蓝 App 首页由独立的 index.html 提供（不被覆盖）
    with open(os.path.join(OUT, "archive.html"), "w", encoding="utf-8") as f:
        f.write(inject_frame(inject_clock(main_index_html(sections_data))))
    print("旧版首页已存为 archive.html（线上首页为新的金融蓝 App 版 index.html，不会被覆盖）")
    print("首页目录：%s" % OUT)


if __name__ == "__main__":
    main()
