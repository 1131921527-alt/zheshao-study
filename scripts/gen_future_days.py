"""
雅思 Future Day 板块重构脚本
1) 解析已下载的 future-dayXX.html，提取每个单词的元数据
2) 按 day01.html 的卡片式 + GB/US 双按钮风格，重写 future-dayXX.html
3) 同时重写 future-index.html

用法：python gen_future_days.py
"""
from __future__ import annotations
import re
import json
import os
import sys
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup

ROOT = Path(r"E:\workbuddyFIle\腾讯龙虾的成品\03-学习网站\zheshao-study")
SRC_DIR = ROOT / "_tmp_fetch"          # 抓回来的旧 HTML
IELTS_DIR = ROOT / "ielts"
AUDIO_DIR = IELTS_DIR / "audio"
OUT_DIR = IELTS_DIR                     # 直接覆盖到正式目录

# ---------- 1. 解析原 HTML 提取单词 ----------
# 把每张卡片整体抠出来，然后单独处理 sentences
CARD_BLOCK_RE = re.compile(
    r'<div class="card">(.*?)<div class="sentences">(.*?)</div>\s*</div>\s*</div>',
    re.DOTALL
)
WHEAD_RE = re.compile(
    r'<div style="display:flex;gap:12px;align-items:center">\s*'
    r'<div style="font-size:34px">([^<]+)</div>\s*'
    r'<div><div style="font-size:20px;font-weight:700;color:#f0f6fc">([^<]+)</div>\s*'
    r'<div style="font-size:13px;color:#8b949e">([^<]+)</div>\s*'
    r'<div style="font-size:14px;color:#7ee787">([^<]+)</div></div></div>',
    re.DOTALL
)
DIFF_RE = re.compile(r'<div style="font-size:12px;color:#8b949e;margin:8px 0">([^<]+)</div>')
MEMORY_RE = re.compile(r'<div style="font-size:13px;color:#d2a8ff;background:#1c2128;padding:8px 10px;border-radius:8px">([^<]+)</div>')
COLL_RE = re.compile(r'<div style="font-size:12px;color:#8b949e;padding:6px 0">([^<]+)</div>')
SENT_ITEM_RE = re.compile(
    r'<div class="sent-item">\s*'
    r'<div class="sent-en">([^<]+)</div>\s*'
    r'<div class="sent-zh">([^<]+)</div>\s*'
    r'<button class="sent-play" data-text="([^"]+)">[^<]+</button>\s*</div>'
)

def parse_day(html_text: str):
    """用 BeautifulSoup 按 DOM 结构稳健解析每张卡片"""
    soup = BeautifulSoup(html_text, "html.parser")
    cards = []
    for card in soup.find_all("div", class_="card"):
        # 单词头
        emoji_div = card.find("div", style=re.compile(r"font-size:34px"))
        word_div = card.find("div", style=re.compile(r"font-size:20px;font-weight:700"))
        ipa_div = card.find("div", style=re.compile(r"font-size:13px;color:#8b949e"))
        pos_div = card.find("div", style=re.compile(r"font-size:14px;color:#7ee787"))
        diff_div = card.find("div", style=re.compile(r"margin:8px 0"))
        memory_div = card.find("div", style=re.compile(r"color:#d2a8ff"))
        coll_div = card.find("div", style=re.compile(r"padding:6px 0"))

        # 例句（BeautifulSoup 一次找全，不会被惰性匹配截断）
        sents = []
        for sent_item in card.find_all("div", class_="sent-item"):
            en_div = sent_item.find("div", class_="sent-en")
            zh_div = sent_item.find("div", class_="sent-zh")
            btn = sent_item.find("button", class_="sent-play")
            if not (en_div and zh_div and btn):
                continue
            en_text = en_div.get_text(strip=True)
            zh_text = zh_div.get_text(strip=True)
            num_match = re.match(r"^(\d+)\.\s*(.+)$", en_text)
            if num_match:
                idx = int(num_match.group(1))
                txt = num_match.group(2).strip()
            else:
                idx = len(sents) + 1
                txt = en_text
            sents.append({"idx": idx, "en": txt, "zh": zh_text})

        if not (word_div and ipa_div and pos_div):
            continue

        word = word_div.get_text(strip=True)
        ipa = ipa_div.get_text(strip=True)
        pos_zh = pos_div.get_text(strip=True)
        emoji = emoji_div.get_text(strip=True) if emoji_div else "🎓"
        difficulty = diff_div.get_text(strip=True) if diff_div else ""
        memory = memory_div.get_text(strip=True) if memory_div else ""
        collocation = coll_div.get_text(strip=True) if coll_div else ""
        collocation = collocation.replace("搭配：", "").strip()

        cards.append({
            "emoji": emoji,
            "word": word,
            "ipa": ipa,
            "pos_zh": pos_zh,
            "difficulty": difficulty,
            "memory": memory,
            "collocation": collocation,
            "sentences": sents,
        })
    return cards

# ---------- 2. 新模板渲染 ----------
TPL_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.7;min-height:100vh;padding-bottom:24px}
.wrap{max-width:1100px;margin:0 auto;padding:0 12px}
.header{background:linear-gradient(135deg,#1a2332,#0d1117);padding:28px 16px 20px;text-align:center;border-bottom:1px solid #21262d;position:sticky;top:0;z-index:100}
.header h1{font-size:22px;font-weight:700;color:#58a6ff}
.header .sub{font-size:13px;color:#8b949e;margin-top:4px}
.grid{display:grid;grid-template-columns:1fr;gap:14px;margin:16px 0}
@media(min-width:720px){.grid{grid-template-columns:1fr 1fr}}
.card{background:#161b22;border:1px solid #21262d;border-radius:14px;padding:16px;transition:all .3s}
.card h3{color:#f0f6fc;font-size:17px;margin-bottom:6px}
.card p{color:#8b949e;font-size:13px}
.whead{display:flex;gap:12px;align-items:center}
.emoji{font-size:34px;line-height:1;flex-shrink:0}
.winfo{flex:1;min-width:0}
.winfo .word{font-size:20px;font-weight:700;color:#f0f6fc;letter-spacing:.5px}
.winfo .ipa{font-size:13px;color:#8b949e;margin-top:2px}
.winfo .pos{font-size:14px;color:#7ee787;margin-top:2px}
.audio-btns{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.audio-btn{background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:6px;padding:5px 12px;font-size:12px;cursor:pointer;display:inline-flex;align-items:center;gap:4px;transition:all .15s;font-family:inherit}
.audio-btn:hover{border-color:#58a6ff;color:#58a6ff}
.audio-btn:active{background:#1f6feb;color:#fff;border-color:#1f6feb}
.audio-btn.playing{background:#1f6feb !important;color:#fff !important;border-color:#1f6feb !important}
.audio-btn .flag{font-size:13px}
.audio-btn .lbl{font-weight:600}
.diff{font-size:12px;color:#8b949e;margin:8px 0}
.memory{font-size:13px;color:#d2a8ff;background:#1c2128;padding:8px 10px;border-radius:8px;line-height:1.6}
.coll{font-size:12px;color:#8b949e;padding:6px 0;line-height:1.6}
.sentences{margin-top:10px;border-top:1px solid #21262d;padding-top:10px}
.sent-title{font-size:12px;color:#58a6ff;font-weight:600;margin-bottom:8px}
.sent-item{background:#0d1117;border-radius:8px;padding:10px 12px;margin-bottom:8px}
.sent-item:last-child{margin-bottom:0}
.sent-en{font-size:14px;color:#e6edf3;margin-bottom:3px;line-height:1.55}
.sent-en .highlight{color:#ffa657;font-weight:600}
.sent-zh{font-size:12px;color:#8b949e;margin-bottom:5px;line-height:1.55}
.sent-play{background:transparent;border:1px solid #30363d;border-radius:5px;padding:3px 10px;font-size:11px;color:#8b949e;cursor:pointer;display:inline-flex;align-items:center;gap:3px;transition:all .15s;font-family:inherit}
.sent-play:hover{border-color:#58a6ff;color:#58a6ff}
.sent-play:active{background:#1f6feb;color:#fff;border-color:#1f6feb}
.sent-play.playing{background:#1f6feb !important;color:#fff !important;border-color:#1f6feb !important}
.note{background:#1c2128;border:1px solid #30363d;border-radius:10px;padding:12px 14px;font-size:13px;color:#8b949e;margin:16px 0;line-height:1.7}
.back{display:inline-block;margin:14px 0;color:#58a6ff;text-decoration:none;font-size:14px}
footer{text-align:center;color:#6e7681;font-size:12px;padding:24px 12px}
""".strip()

TPL_JS = r"""
(function(){
  var PLAYER = document.getElementById('player');
  var cur = null;
  function tts(text, lang){
    try{
      if(!window.speechSynthesis) return;
      var u = new SpeechSynthesisUtterance(text);
      u.lang = lang || 'en-US';
      u.rate = 0.95;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    }catch(e){}
  }
  function playWord(word, accent, btn){
    if(cur && cur.classList) cur.classList.remove('playing');
    var file = 'audio/' + word.toLowerCase() + (accent === 1 ? '_uk.mp3' : '_us.mp3');
    var audio = new Audio(file);
    audio.onended = function(){ btn && btn.classList.remove('playing'); cur = null; };
    audio.onerror = function(){
      btn && btn.classList.remove('playing');
      tts(word, accent === 1 ? 'en-GB' : 'en-US');
    };
    btn && btn.classList.add('playing');
    cur = btn;
    audio.play().catch(function(){
      btn && btn.classList.remove('playing');
      tts(word, accent === 1 ? 'en-GB' : 'en-US');
    });
  }
  function playSentence(text, btn){
    if(cur && cur.classList) cur.classList.remove('playing');
    tts(text, 'en-US');
    btn.classList.add('playing');
    cur = btn;
    setTimeout(function(){ btn.classList.remove('playing'); cur = null; }, 1800);
  }
  window.playWord = playWord;
  window.playSentence = playSentence;
  document.querySelectorAll('.audio-btn[data-word]').forEach(function(b){
    b.addEventListener('click', function(e){
      e.preventDefault();
      var w = b.getAttribute('data-word');
      var a = parseInt(b.getAttribute('data-accent'), 10);
      playWord(w, a, b);
    });
  });
  document.querySelectorAll('.sent-play').forEach(function(b){
    b.addEventListener('click', function(e){
      e.preventDefault();
      playSentence(b.getAttribute('data-text'), b);
    });
  });
})();
""".strip()


def has_audio(word: str, accent: int) -> bool:
    """检查 audio 目录里是否有该单词对应口音的 mp3"""
    suffix = "_uk.mp3" if accent == 1 else "_us.mp3"
    return (AUDIO_DIR / f"{word.lower()}{suffix}").exists()


def render_card(c: dict) -> str:
    """渲染一个单词卡片（含 GB/US 双按钮 + 例句播放）"""
    has_uk = has_audio(c["word"], 1)
    has_us = has_audio(c["word"], 2)
    uk_tip = "" if has_uk else ' title="暂无音频，将用浏览器朗读兜底"'
    us_tip = "" if has_us else ' title="暂无音频，将用浏览器朗读兜底"'
    uk_style = "" if has_uk else ' style="opacity:.7"'
    us_style = "" if has_us else ' style="opacity:.7"'

    # 例句 HTML
    sent_html = ""
    for s in c["sentences"]:
        text_en = s["en"]
        # 高亮单词本身
        highlight = re.sub(
            r'\b(' + re.escape(c["word"]) + r')\b',
            r'<span class="highlight">\1</span>',
            text_en,
            flags=re.IGNORECASE,
            count=1,
        )
        sent_html += (
            '<div class="sent-item">'
            f'<div class="sent-en">{s["idx"]}. {highlight}</div>'
            f'<div class="sent-zh">{escape(s["zh"])}</div>'
            f'<button class="sent-play" data-text="{escape(text_en, quote=True)}">🔊 播放</button>'
            '</div>'
        )

    return (
        '<div class="card">'
        '<div class="whead">'
        f'<div class="emoji">{escape(c["emoji"])}</div>'
        '<div class="winfo">'
        f'<div class="word">{escape(c["word"])}</div>'
        f'<div class="ipa">{escape(c["ipa"])}</div>'
        f'<div class="pos">{escape(c["pos_zh"])}</div>'
        '<div class="audio-btns">'
        f'<button class="audio-btn"{uk_tip}{uk_style} data-word="{escape(c["word"])}" data-accent="1">'
        '<span class="flag">🇬🇧</span><span class="lbl">GB</span>'
        '</button>'
        f'<button class="audio-btn"{us_tip}{us_style} data-word="{escape(c["word"])}" data-accent="2">'
        '<span class="flag">🇺🇸</span><span class="lbl">US</span>'
        '</button>'
        '</div>'
        '</div>'
        '</div>'
        f'<div class="diff">{escape(c["difficulty"])}</div>'
        f'<div class="memory">{escape(c["memory"])}</div>'
        f'<div class="coll">搭配：{escape(c["collocation"])}</div>'
        '<div class="sentences">'
        '<div class="sent-title">📝 例句</div>'
        f'{sent_html}'
        '</div>'
        '</div>'
    )


def render_day(day_num: int, cards: list) -> str:
    """渲染完整 future-dayXX.html"""
    body_html = "\n".join(render_card(c) for c in cards)
    title = f"雅思 Future Day {day_num} · 泽少学习助手"
    note = (
        f"📌 Future Day {day_num} · 共 {len(cards)} 词。"
        f"单词发音优先调用本地 mp3（英式 _uk.mp3 / 美式 _us.mp3），"
        f"若文件缺失则自动用浏览器语音合成兜底；音标未经人工核验（未验证），以权威词典为准。"
    )
    return (
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN"><head><meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>{escape(title)}</title><style>\n'
        f'{TPL_CSS}\n'
        '</style></head>\n'
        '<body><div class="wrap">\n'
        f'<div class="header"><h1>雅思 Future Day {day_num}</h1>'
        '<div class="sub">🎓 教育话题 · 20 词 · 双口音发音</div></div>\n'
        f'<a class="back" href="future-index.html">← 返回 Future Day 预览</a>\n'
        f'<div class="note">{escape(note)}</div>\n'
        f'<div class="grid">{body_html}</div>\n'
        '<audio id="player"></audio>\n'
        f'<script>{TPL_JS}</script>\n'
        '<footer>泽少学习助手 · 每天进步一点点</footer>\n'
        '</div></body></html>'
    )


def render_index(days: list) -> str:
    """渲染 future-index.html"""
    title = "雅思 Future Day 单词计划 · 泽少学习助手"
    toc_links = "\n".join(
        f'<a class="toc-link" href="future-day{n:02d}.html">Future Day {n}（{cnt}词）</a>'
        for n, cnt in days
    )
    note = "📌 Future Day 单词计划：30 天 × 每天 20 词，共 600 词。每个单词下方有 🇬🇧 GB（英式）/ 🇺🇸 US（美式）两个独立发音按钮，例句支持朗读播放。"
    return (
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN"><head><meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>{escape(title)}</title><style>\n'
        f'{TPL_CSS}\n'
        '</style></head>\n'
        '<body><div class="wrap">\n'
        '<div class="header"><h1>雅思 Future Day 单词计划</h1>'
        '<div class="sub">教育话题精选 · 双口音发音 · 30 天 × 20 词</div></div>\n'
        f'<div class="note">{escape(note)}</div>\n'
        f'<div style="margin:12px 0">{toc_links}</div>\n'
        '<a class="back" href="../ielts/index.html">← 返回现有雅思目录</a>\n'
        '<footer>泽少学习助手 · 每天进步一点点</footer>\n'
        '</div></body></html>'
    )


def main():
    if not SRC_DIR.exists():
        print(f"ERR: 源目录不存在 {SRC_DIR}")
        sys.exit(1)

    days_data = []
    for n in range(1, 31):
        src = SRC_DIR / f"future-day{n:02d}.html"
        if not src.exists():
            print(f"WARN: {src.name} 缺失，跳过")
            continue
        html_text = src.read_text(encoding="utf-8")
        cards = parse_day(html_text)
        if not cards:
            print(f"WARN: {src.name} 解析失败（找不到任何 card）")
            continue
        out_html = render_day(n, cards)
        out_path = OUT_DIR / f"future-day{n:02d}.html"
        out_path.write_text(out_html, encoding="utf-8")
        days_data.append((n, len(cards)))
        print(f"OK  future-day{n:02d}.html  词数={len(cards)}  size={len(out_html)}")

    # index
    idx_html = render_index(days_data)
    (OUT_DIR / "future-index.html").write_text(idx_html, encoding="utf-8")
    print(f"OK  future-index.html  size={len(idx_html)}")


if __name__ == "__main__":
    main()