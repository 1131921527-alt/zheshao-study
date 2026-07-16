# -*- coding: utf-8 -*-
# 雅思每日单词 · 自动生成器（泽少）
# 逻辑：
#   1) 首次运行从 ielts/full.html（489 词库）抽取全部词条，清洗后缓存到 ielts/ielts_bank.json
#      —— 有「记忆故事+用法提示」的词排前面，无内容的原始词排后面并给兜底文案
#   2) 每次运行：找下一个 dayNN.html 序号 -> 取 15 个「未在任何 day 页面出现过」的词
#   3) 用 tpl_day.html（含 TTS 兜底）生成 dayNN.html，并更新 ielts/index.html 列表与期数
#   4) 幂等：若目标 dayNN.html 已存在则跳过；已用过的词不再重复
# 模型零参与，纯脚本驱动，换号运行结果一致。
import io, re, os, json, glob, html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
IELTS_DIR = os.path.abspath(os.path.join(HERE, "..", "ielts"))
BANK_JSON = os.path.join(IELTS_DIR, "ielts_bank.json")
FULL_HTML = os.path.join(IELTS_DIR, "full.html")
TEMPLATE  = os.path.join(IELTS_DIR, "tpl_day.html")
PER_DAY = 15

EMOJIS = ["📚","🧠","💡","🔤","✍️","🌟","📝","🎯","🧩","⚡","🌈","🔑","📌","🚀","💎"]

def clean(s):
    if not s:
        return ""
    # 先处理实体编码标签（full.html 里常见 &lt;b&gt;word&lt;/b&gt;）
    for ent in ["&lt;b&gt;", "&lt;/b&gt;", "&lt;B&gt;", "&lt;/B&gt;",
                "&lt;strong&gt;", "&lt;/strong&gt;",
                '&lt;span class="highlight"&gt;', "&lt;/span&gt;"]:
        s = s.replace(ent, "")
    s = _html.unescape(s)
    # 递归剥离所有剩余 HTML 标签（<b>, <span ...>, <strong> 等）
    for _ in range(5):
        n = re.sub(r"<[a-zA-Z/][^>]*>", "", s)
        if n == s:
            break
        s = n
    s = s.replace(" ", "").replace("\u200b", "").strip()
    # 只剩标签文字（无真正内容）视为空
    if s in ("", "💡 记忆故事", "📝 用法提示", "记忆故事", "用法提示"):
        return ""
    return s

def build_bank():
    h = io.open(FULL_HTML, encoding="utf-8").read()
    chunks = h.split('<div class="word-card">')
    bank = []
    for ch in chunks[1:]:
        mw = re.search(r'<div class="w-word">([^<]*)</div>', ch)
        mi = re.search(r'<div class="w-ipa">([^<]*)</div>', ch)
        mp = re.search(r'<div class="w-pos">([^<]*)</div>', ch)
        ms = re.search(r'<div class="story-box"><div class="lbl">[^<]*</div>(.*?)</div>', ch, re.S)
        mt = re.search(r'<div class="tip-box"><div class="lbl">[^<]*</div>(.*?)</div>', ch, re.S)
        me = re.search(r'<div class="ex-en">(.*?)</div>', ch, re.S)
        mc = re.search(r'<div class="ex-cn">(.*?)</div>', ch, re.S)
        if not (mw and mi and mp):
            continue
        story = clean(ms.group(1)) if ms else ""
        tip = clean(mt.group(1)) if mt else ""
        bank.append({
            "word": mw.group(1).strip(),
            "ipa": mi.group(1).strip(),
            "pos": mp.group(1).strip(),
            "story": story,
            "tip": tip,
            "en": clean(me.group(1)) if me else "",
            "cn": clean(mc.group(1)) if mc else "",
        })
    return bank

def load_bank():
    if not os.path.exists(BANK_JSON):
        b = build_bank()
        io.open(BANK_JSON, "w", encoding="utf-8").write(
            json.dumps(b, ensure_ascii=False, indent=1))
        print("首次构建词库：%d 词 -> ielts_bank.json" % len(b))
        return b
    return json.load(io.open(BANK_JSON, encoding="utf-8"))

def used_words():
    used = set()
    for f in glob.glob(os.path.join(IELTS_DIR, "day*.html")):
        h = io.open(f, encoding="utf-8").read()
        for m in re.findall(r'\ben:\s*"([^"]*)"', h):
            used.add(m)
    return used

def next_number():
    nums = []
    for f in glob.glob(os.path.join(IELTS_DIR, "day*.html")):
        m = re.search(r'day(\d+)\.html', f)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) if nums else 0) + 1

def split_pos(pos):
    pos = pos.strip()
    m = re.match(r'^(adj|n|v|adv|pron|prep|conj|num|int|art)\.?\s*(.*)$', pos, re.I)
    if m and m.group(2):
        return m.group(1).rstrip('.') + '.', m.group(2).strip()
    return pos, ""

def jd(s):
    return json.dumps(s, ensure_ascii=False)

def extract_sentmap():
    """从 full.html 提取完整的 _sentMap（例句→音频文件映射），保证 day 页面和 full.html 同步"""
    h = io.open(FULL_HTML, encoding="utf-8").read()
    m = re.search(r'var _sentMap\s*=\s*(\{[^}]+\});', h)
    if m:
        return m.group(1)
    return "{}"

def gen_day(nn, words):
    tpl = io.open(TEMPLATE, encoding="utf-8").read()
    # 从 full.html 提取最新 _sentMap 并注入模板（保证 day 页面有完整音频映射）
    sentmap = extract_sentmap()
    tpl = re.sub(r'var _sentMap\s*=\s*\{[^}]*\};',
                 'var _sentMap=' + sentmap + ';', tpl, count=1)
    blocks = []
    for i, w in enumerate(words, 1):
        p, zh = split_pos(w["pos"])
        grad = "gradient-%d" % ((i % 15) + 1)
        emoji = EMOJIS[i % len(EMOJIS)]
        story = w["story"] or ("💡 记忆线索：看例句「%s」，体会 %s 的用法。" % (w["en"], w["word"]))
        tip = w["tip"] or ("📝 %s %s——多在语境里理解。" % (w["pos"], w["zh"]))
        s = []
        if w["en"]:
            s.append("      { en: %s, zh: %s }" % (jd(w["en"]), jd(w["cn"])))
        entry = (
            "  {\n"
            "    id: %d,\n"
            "    en: %s, ipa: %s, pos: %s, zh: %s,\n"
            "    emoji: %s, grad: %s,\n"
            "    story: %s,\n"
            "    tip: %s,\n"
            "    sentences: [\n%s\n"
            "    ]\n  }"
        ) % (
            i,
            jd(w["word"]), jd(w["ipa"]),
            jd(p), jd(zh),
            jd(emoji), jd(grad),
            jd(story), jd(tip),
            ",\n".join(s),
        )
        blocks.append(entry)
    block = "const WORDS = [\n" + ",\n".join(blocks) + "\n];"
    tpl = re.sub(r'const WORDS = \[.*?\n\];', block, tpl, count=1, flags=re.S)
    tpl = re.sub(r'<title>.*?</title>',
                 '<title>雅思核心词汇 Day %d — 每日15词自动更新</title>' % nn, tpl, count=1)
    out = os.path.join(IELTS_DIR, "day%02d.html" % nn)
    io.open(out, "w", encoding="utf-8").write(tpl)
    return out

def update_index(nn):
    idx = os.path.join(IELTS_DIR, "index.html")
    h = io.open(idx, encoding="utf-8").read()
    links = ['<a href="full.html"><span class="label">完整版 · 带音频</span><span class="arrow">→</span></a>']
    for n in range(nn, 0, -1):
        label = nn - n + 1
        links.append('<a href="day%02d.html"><span class="label">Day %d</span><span class="arrow">→</span></a>' % (n, label))
    listblock = '<div class="list">\n' + "\n".join(links) + '\n</div>'
    h = re.sub(r'<div class="list">.*?</div>', listblock, h, count=1, flags=re.S)
    h = re.sub(r'共 \d+ 期', '共 %d 期' % (nn + 1), h, count=1)
    io.open(idx, "w", encoding="utf-8").write(h)

def main():
    bank = load_bank()
    # 有内容的词优先，保证每日质量
    quality = [w for w in bank if w["story"] and w["tip"]]
    rest = [w for w in bank if not (w["story"] and w["tip"])]
    bank = quality + rest
    nn = next_number()
    out = os.path.join(IELTS_DIR, "day%02d.html" % nn)
    if os.path.exists(out):
        print("day%02d.html 已存在，跳过（幂等）" % nn)
        return
    used = used_words()
    avail = [w for w in bank if w["word"] not in used]
    if len(avail) < PER_DAY:
        extra = [w for w in bank if w["word"] not in [x["word"] for x in avail]]
        avail = (avail + extra)[:PER_DAY]
    pick = avail[:PER_DAY]
    gen_day(nn, pick)
    update_index(nn)
    print("已生成 day%02d.html（%d 词，其中带记忆故事 %d 个），列表与期数已更新"
          % (nn, len(pick), sum(1 for w in pick if w["story"] and w["tip"])))

if __name__ == "__main__":
    main()
