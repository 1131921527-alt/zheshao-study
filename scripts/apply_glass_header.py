"""
全站统一玻璃抬头注入脚本
- 在不破坏原页面结构与功能的前提下，把每个内容页的原有抬头
  重建成「手机玻璃 UI 抬头」：🎓 学士帽 logo + 页面标题 + 副标题 + 圆形实时时钟 + "Time goes by"
- 自动保留原抬头里的额外元素（如「乱序重排」按钮）
- 幂等：已含 id="ghHeader" 的页面跳过

用法：
  python apply_glass_header.py                # 处理全站配置目录
  python apply_glass_header.py 路径/xx.html    # 仅处理单个文件（调试用）
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(r"E:\workbuddyFIle\腾讯龙虾的成品\03-学习网站\zheshao-study")

# 需要处理的目录（index.html 由单独逻辑处理，不在此列）
TARGET_DIRS = ["ielts", "ai-knowledge", "ai-news", "ai-prompt", "knowledge"]
SKIP_FILES = {"tpl_day.html"}

# ---------- 时钟 SVG（圆形 + 刻度 + 三根指针）----------
def build_ticks() -> str:
    import math
    parts = []
    cx = cy = 31
    for i in range(12):
        a = i * 30
        rad = a * 3.141592653589793 / 180
        sin_a, cos_a = math.sin(rad), math.cos(rad)
        r_out = 28
        r_in = 23 if i % 3 == 0 else 25
        x1 = cx + r_out * sin_a
        y1 = cy - r_out * cos_a
        x2 = cx + r_in * sin_a
        y2 = cy - r_in * cos_a
        w = 1.4 if i % 3 == 0 else 0.8
        parts.append(
            f'<line class="gh-tick" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-width="{w}"/>'
        )
    return "\n      ".join(parts)

CLOCK_SVG = f'''<svg class="gh-clock" viewBox="0 0 62 62" aria-hidden="true">
      <defs>
        <linearGradient id="ghGold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#E7C98A"/>
          <stop offset="1" stop-color="#9A7B36"/>
        </linearGradient>
      </defs>
      <circle class="gh-face" cx="31" cy="31" r="28"/>
      <circle class="gh-ring" cx="31" cy="31" r="28"/>
      {build_ticks()}
      <line class="gh-hand-h" id="ghHour" x1="31" y1="31" x2="31" y2="18"/>
      <line class="gh-hand-m" id="ghMin" x1="31" y1="31" x2="31" y2="13"/>
      <line class="gh-hand-s" id="ghSec" x1="31" y1="34" x2="31" y2="11"/>
      <circle class="gh-cap" cx="31" cy="31" r="2.6"/>
    </svg>'''

GLASS_CSS = """
/* ===== 泽少学习助手 · 玻璃圆形时钟抬头（统一组件） ===== */
.gh{position:sticky;top:0;z-index:100;padding:13px 16px 12px;overflow:hidden;border:none;margin:0;text-align:left;background:transparent}
.gh-glass{position:absolute;inset:0;background:linear-gradient(135deg,rgba(20,28,46,.74),rgba(10,14,23,.56));backdrop-filter:blur(16px) saturate(140%);-webkit-backdrop-filter:blur(16px) saturate(140%);border-bottom:1px solid rgba(201,168,106,.22);box-shadow:0 6px 24px rgba(0,0,0,.35)}
.gh-inner{position:relative;display:flex;align-items:center;justify-content:space-between;gap:12px;max-width:720px;margin:0 auto}
.gh-brand{display:flex;align-items:center;gap:11px;min-width:0}
.gh-logo{width:42px;height:42px;border-radius:13px;display:grid;place-items:center;font-size:22px;background:linear-gradient(135deg,#C9A86A,#8A6E33);box-shadow:0 4px 12px rgba(201,168,106,.35),inset 0 1px 0 rgba(255,255,255,.25);flex:0 0 auto}
.gh-titles{min-width:0}
.gh-title{font-size:17px;font-weight:800;color:#E9EDF6;margin:0;line-height:1.25;letter-spacing:.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gh-sub{font-size:11.5px;color:#A7B0C2;margin-top:3px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gh-clock-wrap{display:flex;flex-direction:column;align-items:center;flex:0 0 auto}
.gh-clock{width:50px;height:50px;display:block}
.gh-clock .gh-face{fill:rgba(255,255,255,.04)}
.gh-clock .gh-ring{fill:none;stroke:url(#ghGold);stroke-width:2.4}
.gh-clock .gh-tick{stroke:rgba(201,168,106,.5)}
.gh-clock .gh-hand-h{stroke:#C9A86A;stroke-width:3;stroke-linecap:round}
.gh-clock .gh-hand-m{stroke:#E9EDF6;stroke-width:2;stroke-linecap:round}
.gh-clock .gh-hand-s{stroke:#4F8DFF;stroke-width:1.2;stroke-linecap:round}
.gh-clock .gh-cap{fill:#0B0F17;stroke:#4F8DFF;stroke-width:.6}
.gh-digital{font-size:12px;font-weight:700;color:#E9EDF6;margin-top:3px;font-variant-numeric:tabular-nums;letter-spacing:.5px}
.gh-caption{font-size:9.5px;color:#A7B0C2;letter-spacing:1px;margin-top:1px;font-style:italic;opacity:.85}
.gh-actions{position:relative;display:flex;justify-content:center;padding-top:10px}
""".strip()

CLOCK_JS = r"""
(function(){
  if(window.__ghClockInit) return; window.__ghClockInit = true;
  function p(n){return (n<10?'0':'')+n;}
  var h=document.getElementById('ghHour'),m=document.getElementById('ghMin'),s=document.getElementById('ghSec'),d=document.getElementById('ghDigital');
  if(!h||!m||!s||!d) return;
  function tick(){
    var t=new Date();
    var sec=t.getSeconds()+t.getMilliseconds()/1000;
    var min=t.getMinutes()+sec/60;
    var hr=(t.getHours()%12)+min/60;
    s.setAttribute('transform','rotate('+(sec*6)+' 31 31)');
    m.setAttribute('transform','rotate('+(min*6)+' 31 31)');
    h.setAttribute('transform','rotate('+(hr*30)+' 31 31)');
    d.textContent=p(t.getHours())+':'+p(t.getMinutes())+':'+p(t.getSeconds());
    requestAnimationFrame(tick);
  }
  tick();
})();
""".strip()


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def find_header(html: str):
    """返回 {'tag','start','end','inner_start','inner_end'} 或 None"""
    m = re.search(r'<div\s+class="header"[^>]*>', html, re.I)
    if m:
        open_end = m.end()
        depth = 1
        k = open_end
        while k < len(html):
            lt = html.find("<", k)
            if lt == -1:
                break
            if html.startswith("</div", lt):
                depth -= 1
                k = lt + 6
                if depth == 0:
                    return {"tag": "div", "start": m.start(), "end": lt + 6,
                            "inner_start": open_end, "inner_end": lt}
            elif html.startswith("<div", lt):
                depth += 1
                gt = html.find(">", lt)
                k = gt + 1
            else:
                gt = html.find(">", lt)
                k = (gt + 1) if gt != -1 else len(html)
        return None
    m = re.search(r"<header[^>]*>", html, re.I)
    if m:
        open_end = m.end()
        cm = re.search(r"</header>", html[open_end:], re.I)
        if cm:
            inner_end = open_end + cm.start()
            return {"tag": "header", "start": m.start(), "end": open_end + cm.end(),
                    "inner_start": open_end, "inner_end": inner_end}
    return None


def parse_inner(inner: str):
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", inner, re.DOTALL | re.I)
    title = strip_tags(h1.group(1)) if h1 else ""
    sub_el = None
    for pat in [r'<div class="sub"[^>]*>.*?</div>',
                r'<div class="date"[^>]*>.*?</div>',
                r"<p[^>]*>.*?</p>"]:
        mm = re.search(pat, inner, re.DOTALL | re.I)
        if mm:
            sub_el = mm.group(0)
            break
    sub_html = sub_el if sub_el else ""
    extra = inner
    if h1:
        extra = extra.replace(h1.group(0), "", 1)
    if sub_el:
        extra = extra.replace(sub_el, "", 1)
    extra = re.sub(r"</?header[^>]*>", "", extra, flags=re.I)
    extra = extra.strip()
    return title, sub_html, extra


def build_header(title: str, sub_html: str, extra: str) -> str:
    actions = f'<div class="gh-actions">{extra}</div>' if extra else ""
    return (
        '<header class="gh" id="ghHeader">\n'
        '  <div class="gh-glass"></div>\n'
        '  <div class="gh-inner">\n'
        '    <div class="gh-brand">\n'
        '      <div class="gh-logo">🎓</div>\n'
        '      <div class="gh-titles">\n'
        f'        <h1 class="gh-title">{title}</h1>\n'
        f'        {sub_html}\n'
        '      </div>\n'
        '    </div>\n'
        '    <div class="gh-clock-wrap">\n'
        f'      {CLOCK_SVG}\n'
        '      <div class="gh-digital"><span id="ghDigital">--:--:--</span></div>\n'
        '      <div class="gh-caption">Time goes by</div>\n'
        '    </div>\n'
        '  </div>\n'
        f'  {actions}\n'
        '</header>'
    )


def inject_css(html: str) -> str:
    if "</style>" in html:
        return html.replace("</style>", GLASS_CSS + "\n</style>", 1)
    # 无 style 则插入 head
    head = re.search(r"<head[^>]*>", html, re.I)
    if head:
        return html[:head.end()] + "<style>\n" + GLASS_CSS + "\n</style>\n" + html[head.end():]
    return "<style>\n" + GLASS_CSS + "\n</style>\n" + html


def inject_js(html: str) -> str:
    script = "<script>\n" + CLOCK_JS + "\n</script>\n"
    for tag in ["</body>", "</html>"]:
        if tag in html:
            return html.replace(tag, script + tag, 1)
    return html + script


EMOJI_PALETTE = ["📚", "🎯", "🧠", "✍️", "🔤", "📝", "⚡", "🏛️", "💡", "🌟",
                 "📖", "🔑", "🧩", "📐", "🔭", "🌐", "💬", "📌", "🎓", "🚀"]


def vary_future_emoji(html: str) -> str:
    """future-day 页面：把每个单词卡片千篇一律的 🎓 换成更贴合学习内容的教育类 emoji"""
    i = [0]

    def repl(m):
        em = EMOJI_PALETTE[i[0] % len(EMOJI_PALETTE)]
        i[0] += 1
        return f'<div class="emoji">{em}</div>'

    return re.sub(r'<div class="emoji">🎓</div>', repl, html)


def remove_live_clock_bar(html: str) -> str:
    """删除旧版细长实时时钟条（#liveClockBar）：DOM 元素 + 它专属的 <style> 块（含 body 44px 上边距）。
    保留其 <script>（含 lcZoom/lcCopyWx 等可能有用的函数）。
    保险：仅删除「含 #liveClockBar 且不含主样式标记」的 style 块，避免误删主样式。"""
    # 1) 删除 DOM 元素 <div id="liveClockBar">...</div>
    html = re.sub(r'<div id="liveClockBar"[^>]*>.*?</div>\s*', '', html, flags=re.DOTALL)
    # 2) 删除专属 style 块
    main_markers = ('.card', '.wrap', '.container', ':root', '.header', '.topbar',
                    '.app', '.grid', '.note', '.footer', 'min-width', '@media')

    def _style_cb(m):
        blk = m.group(0)
        if '#liveClockBar' in blk and not any(mk in blk for mk in main_markers):
            return ''
        return blk

    html = re.sub(r'<style[^>]*>.*?</style>', _style_cb, html, flags=re.DOTALL)
    # 3) 兜底清掉可能残留的 44px 上边距规则
    html = re.sub(r'body\{padding-top:44px!important\}', '', html)
    return html


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'id="ghHeader"' in text:
        print(f"SKIP (已处理) {path.name}")
        return False
    text = remove_live_clock_bar(text)
    hdr = find_header(text)
    if not hdr:
        print(f"WARN 未找到抬头，跳过 {path.name}")
        return False
    inner = text[hdr["inner_start"]:hdr["inner_end"]]
    title, sub_html, extra = parse_inner(inner)
    if not title:
        print(f"WARN 抬头无标题，跳过 {path.name}")
        return False

    is_future = "future-day" in path.name
    if is_future:
        text = vary_future_emoji(text)

    new_header = build_header(title, sub_html, extra)
    text = text[:hdr["start"]] + new_header + text[hdr["end"]:]
    text = inject_css(text)
    text = inject_js(text)

    path.write_text(text, encoding="utf-8")
    print(f"OK   {path.name}  title='{title[:24]}'  extra={'Y' if extra else 'N'}")
    return True


def main():
    if len(sys.argv) > 1:
        single = Path(sys.argv[1])
        if not single.is_absolute():
            single = ROOT / single
        process_file(single)
        return
    count = 0
    for d in TARGET_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for f in sorted(base.rglob("*.html")):
            if f.name in SKIP_FILES:
                continue
            if process_file(f):
                count += 1
    print(f"\n完成：共处理 {count} 个文件")


if __name__ == "__main__":
    main()
