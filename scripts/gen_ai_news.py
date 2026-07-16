# -*- coding: utf-8 -*-
# AI动态播报 生成器（泽少）
# 读取 gen_ai_news 同目录下的 ai-news-today.json（由自动化 WebSearch 后写入），
# 生成 ai-news-YYYY-MM-DD.html，同步到：
#   - E:\workbuddyFIle\腾讯龙虾的成品\AI动态播报\            （产物源目录）
#   - E:\workbuddyFIle\腾讯龙虾的成品\zheshao-study\ai-news\ （部署目录）
# 并更新 zheshao-study/ai-news/index.html 的列表与期数。
# 幂等：若今日文件已存在则跳过生成（仍确保 index 同步）。
import io, os, re, sys, json, datetime

DEST_AI = r"E:\workbuddyFIle\腾讯龙虾的成品\zheshao-study\ai-news"
SRC_AI  = r"E:\workbuddyFIle\腾讯龙虾的成品\AI动态播报"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

WEEK = ["周一","周二","周三","周四","周五","周六","周日"]

# 允许的 badge 样式类（与模板一致）
BADGE_CLASSES = {"b-openai","b-anthropic","b-google","b-deepseek","b-china","b-xai","b-reg","b-tencent"}

CSS = """  :root{
    --bg:#0b0f1a;
    --card:#141b2d;
    --card2:#1b2236;
    --accent:#3b82f6;
    --accent2:#22d3ee;
    --text:#e8edf7;
    --muted:#93a0b8;
    --line:#26304a;
    --tag:#1e293b;
  }
  *{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;}
  body{
    font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
    background:linear-gradient(180deg,#0b0f1a 0%,#0e1424 100%);
    color:var(--text);
    line-height:1.6;
    padding:16px 14px 40px;
    max-width:680px;
    margin:0 auto;
  }
  .hero{
    text-align:center;
    padding:26px 16px 20px;
    background:radial-gradient(120% 120% at 50% 0%,rgba(59,130,246,.22),transparent 60%);
    border:1px solid var(--line);
    border-radius:18px;
    margin-bottom:18px;
  }
  .hero .kicker{
    font-size:13px;letter-spacing:3px;color:var(--accent2);
    text-transform:uppercase;font-weight:600;
  }
  .hero h1{font-size:26px;font-weight:800;margin:8px 0 4px;letter-spacing:.5px;}
  .hero .date{font-size:14px;color:var(--muted);}
  .hero .sub{font-size:12px;color:var(--muted);margin-top:6px;}
  .count{
    display:inline-block;background:var(--tag);color:var(--accent2);
    font-size:12px;padding:3px 10px;border-radius:20px;margin-top:10px;
    border:1px solid var(--line);
  }
  .news{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:16px 16px 14px;
    margin-bottom:14px;
    position:relative;
    overflow:hidden;
  }
  .news::before{
    content:"";position:absolute;left:0;top:0;bottom:0;width:4px;
    background:linear-gradient(180deg,var(--accent),var(--accent2));
  }
  .news .head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;}
  .badge{
    font-size:11px;font-weight:700;padding:3px 9px;border-radius:8px;
    color:#fff;white-space:nowrap;
  }
  .b-openai{background:#10a37f;}
  .b-anthropic{background:#d97757;}
  .b-google{background:#4285f4;}
  .b-deepseek{background:#4d6bfe;}
  .b-china{background:#e23b3b;}
  .b-xai{background:#7c3aed;}
  .b-reg{background:#f59e0b;}
  .b-tencent{background:#12b7f5;}
  .news h2{font-size:17px;font-weight:700;line-height:1.4;margin:2px 0 8px;}
  .news p{font-size:14.5px;color:#cfd8ea;margin-bottom:8px;}
  .news .meta{font-size:12px;color:var(--muted);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;}
  .news .meta a{color:var(--accent2);text-decoration:none;font-weight:600;}
  .news .meta a:active{opacity:.7;}
  .num{
    position:absolute;right:14px;top:10px;font-size:34px;font-weight:900;
    color:rgba(59,130,246,.13);line-height:1;
  }
  footer{
    text-align:center;color:var(--muted);font-size:12px;margin-top:24px;
    border-top:1px solid var(--line);padding-top:16px;
  }
  footer .dot{color:var(--accent2);}"""

def esc(s):
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def render_item(it, idx):
    bc = it.get("badge_class","b-openai")
    if bc not in BADGE_CLASSES:
        bc = "b-openai"
    bt = esc(it.get("badge_text",""))
    title = esc(it.get("title",""))
    summary = esc(it.get("summary",""))
    source = esc(it.get("source",""))
    url = esc(it.get("url",""))
    link = '<a href="%s">查看原文 ↗</a>' % url if url else ""
    return (
'<div class="news">\n'
'    <span class="num">%d</span>\n'
'    <div class="head"><span class="badge %s">%s</span></div>\n'
'    <h2>%s</h2>\n'
'    <p>%s</p>\n'
'    <div class="meta"><span>来源：%s</span>%s</div>\n'
'  </div>' % (idx, bc, bt, title, summary, source, link)
    )

def render_page(date_str, items):
    d = datetime.date.fromisoformat(date_str)
    week = WEEK[d.weekday()]
    date_cn = "%d 年 %d 月 %d 日 · %s" % (d.year, d.month, d.day, week)
    count = len(items)
    items_html = "\n".join(render_item(it, i+1) for i, it in enumerate(items))
    return (
'<!DOCTYPE html>\n'
'<html lang="zh-CN">\n'
'<head>\n'
'<meta charset="UTF-8">\n'
'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
'<title>AI动态播报 · %s</title>\n'
'<style>\n%s\n</style>\n'
'</head>\n'
'<body>\n'
'  <div class="hero">\n'
'    <div class="kicker">AI Daily Brief</div>\n'
'    <h1>AI 动态播报</h1>\n'
'    <div class="date">%s</div>\n'
'    <div class="sub">主流厂商最新发布 · 重大更新 · 行业要闻</div>\n'
'    <span class="count">今日精选 %d 条</span>\n'
'  </div>\n\n'
'%s\n\n'
'  <footer>\n'
'    AI 动态播报 · 每日自动生成 <span class="dot">●</span> 数据来源公开网络，仅供参考<br>\n'
'    生成时间：%s · 由 AI 助手自动整理\n'
'  </footer>\n'
'</body>\n'
'</html>\n'
    ) % (date_str, CSS, date_cn, count, items_html, date_str)

def update_index(index_path, date_str):
    html = io.open(index_path, encoding="utf-8").read()
    if ('ai-news-%s.html' % date_str) in html:
        return False  # 已在列表
    d = datetime.date.fromisoformat(date_str)
    week = WEEK[d.weekday()]
    mmdd = "%02d-%02d" % (d.month, d.day)
    new_link = ('<a href="ai-news-%s.html"><span class="label">%s %s</span><span class="arrow">→</span></a>\n'
                % (date_str, mmdd, week))
    html = html.replace('<div class="list">\n', '<div class="list">\n' + new_link, 1)
    # 期数：统计列表中的 ai-news- 链接数
    n = len(re.findall(r'<a href="ai-news-\d{4}-\d{2}-\d{2}\.html">', html))
    html = re.sub(r'共 \d+ 期', "共 %d 期" % n, html, count=1)
    io.open(index_path, "w", encoding="utf-8").write(html)
    return True

def main():
    # JSON 路径：命令行第一个参数，或脚本同目录 ai-news-today.json
    json_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, "ai-news-today.json")
    override_dst = sys.argv[2] if len(sys.argv) > 2 else None  # 测试用
    override_src = sys.argv[3] if len(sys.argv) > 3 else None

    data = json.load(io.open(json_path, encoding="utf-8"))
    date_str = data.get("date") or datetime.date.today().isoformat()
    items = data.get("items", [])
    if not items:
        print("没有新闻条目，跳过"); return

    dst = override_dst or DEST_AI
    src = override_src or SRC_AI
    os.makedirs(dst, exist_ok=True)
    os.makedirs(src, exist_ok=True)

    fname = "ai-news-%s.html" % date_str
    if os.path.exists(os.path.join(dst, fname)):
        print("%s 已存在，跳过生成（幂等）" % fname)
    else:
        page = render_page(date_str, items)
        io.open(os.path.join(src, fname), "w", encoding="utf-8").write(page)
        io.open(os.path.join(dst, fname), "w", encoding="utf-8").write(page)
        print("已生成 %s（%d 条）" % (fname, len(items)))

    idx_changed = update_index(os.path.join(dst, "index.html"), date_str)
    print("已更新 index.html 列表" if idx_changed else "index.html 已含今日条目")

if __name__ == "__main__":
    main()
