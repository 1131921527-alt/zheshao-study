# -*- coding: utf-8 -*-
import re, io

# 原始 CLOCK_CSS（深色时钟条，本就适配深色主题）
ORIG_CLOCK_CSS = '''CLOCK_CSS = """
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
"""'''

# 深色黑金 子页 CSS（真实 CSS 常量）
DARK_CSS = """* { margin: 0; padding: 0; box-sizing: border-box }
:root { --bg:#0B0F17; --fg:#E6EAF2; --muted:#9AA6BD; --line:rgba(201,168,106,.16); --primary:#C9A86A; --primary-700:#E4C98C; --primary-050:rgba(201,168,106,.08); --card:#151B2B; }
html { -webkit-text-size-adjust: 100%; }
body { background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; min-height: 100vh; }
a { color: inherit; text-decoration: none; }
.wrap { max-width: 760px; margin: 0 auto; padding: 0 16px 60px; }
.hero { text-align: center; padding: 44px 20px 32px; background: linear-gradient(135deg,#16203a,#0b0f17); border-bottom: 1px solid var(--line); }
.hero .logo { font-size: 48px; line-height: 1; margin-bottom: 10px; }
.hero h1 { font-size: 28px; font-weight: 800; letter-spacing: 1px; color: var(--primary); }
.hero .tag { font-size: 14px; color: var(--primary-700); margin-top: 10px; }
.hero .sub { font-size: 12px; color: var(--muted); margin-top: 6px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 28px 0; }
@media (max-width: 560px) { .grid { grid-template-columns: 1fr; } }
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
DARK_CSS_BLOCK = 'CSS = """' + DARK_CSS + '"""'

TARGETS = [
    r"E:\workbuddyFIle\腾讯龙虾的成品\zheshao-study\build.py",
    r"E:\workbuddyFIle\腾讯龙虾的成品\哲少的学习任务\build.py",
]

for p in TARGETS:
    try:
        with io.open(p, encoding="utf-8") as f:
            s = f.read()
    except FileNotFoundError:
        print("SKIP (not found):", p); continue

    # 1) 还原 CLOCK_CSS（修复之前误把深色页面 CSS 塞进 CLOCK_CSS 的 bug）
    s2, n1 = re.subn(r'CLOCK_CSS = """.*?"""', ORIG_CLOCK_CSS, s, count=1, flags=re.DOTALL)
    if n1 != 1:
        print("WARN CLOCK_CSS not replaced exactly once in:", p, "n=", n1)

    # 2) 真实 CSS 常量（行首 CSS = """）换成深色黑金
    s3, n2 = re.subn(r'(?m)^CSS = """.*?"""', DARK_CSS_BLOCK, s2, count=1, flags=re.DOTALL)
    if n2 != 1:
        print("WARN CSS not replaced exactly once in:", p, "n=", n2)

    if "#0B0F17" not in s3 or "liveClockBar" not in s3:
        print("ERROR guard failed in:", p); continue

    with io.open(p, "w", encoding="utf-8") as f:
        f.write(s3)
    print("REPAIRED:", p)
