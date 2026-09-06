# -*- coding: utf-8 -*-
"""导出第14轮收尾待修明细：例句跑题、标点问题、疑似错别字"""
import io, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
bank = json.load(io.open(ROOT + r"\ielts\ielts_bank.json", encoding="utf-8"))


def infl(w):
    """生成常见屈折形式（粗判用）"""
    out = {w, w.lower()}
    for suf, repl in (("y", "ies"), ("e", "ing"), ("e", "ed"), ("e", "es"),
                      ("e", "ion"), ("e", "ive"), ("e", "able"), ("e", "or"),
                      ("e", "ment"), ("e", "ance"), ("e", "al")):
        if w.endswith(suf):
            out.add(w[:-1] + repl)
    for s in ("s", "es", "ed", "ing", "er", "ers", "ly", "ion", "ions",
              "ive", "able", "al", "ity", "ities", "ance", "ence", "ment",
              "ness", "ism", "ist", "ize", "ise", "ized", "isation",
              "ization", "ation", "ations", "ic", "ical", "ous", "ful"):
        out.add(w + s)
    return out


print("=" * 60)
print("[A] 例句里不含该单词（含屈折粗判）")
print("=" * 60)
bad = []
for it in bank:
    w = (it.get("word") or "").strip()
    if not w:
        continue
    forms = infl(w)
    for i, ex in enumerate(it.get("examples") or []):
        en = (ex.get("en") or "").lower()
        if not en:
            bad.append((w, i, "(空)", ex.get("cn", "")))
            continue
        hit = any(re.search(r"\b" + re.escape(f) + r"\b", en) for f in forms if f)
        if not hit:
            bad.append((w, i, ex.get("en", ""), ex.get("cn", "")))
for w, i, en, cn in bad:
    print("%-18s #%d  %s" % (w, i + 1, en[:90]))
print("合计 %d 条例句 / 涉及 %d 词" % (len(bad), len(set(x[0] for x in bad))))

print()
print("=" * 60)
print("[B] 中文标点问题")
print("=" * 60)
CN_END = "。！？）”」』…—"
cn_pat = re.compile(r"[\u4e00-\u9fff]")
n_end, n_en = 0, 0
for it in bank:
    w = it.get("word", "")
    for ex in it.get("examples") or []:
        cn = (ex.get("cn") or "").strip()
        if not cn or not cn_pat.search(cn):
            continue
        if cn[-1] not in CN_END:
            n_end += 1
            print("[缺句末] %-16s %s" % (w, cn[:80]))
        if re.search(r"[,;:!?]", cn) and not re.search(r"[，；：！？]", cn):
            n_en += 1
            print("[英标点] %-16s %s" % (w, cn[:80]))
print("缺句末 %d 条 / 英文标点 %d 条" % (n_end, n_en))

print()
print("=" * 60)
print("[C] 疑似错别字（上下文）")
print("=" * 60)
WRONG = {"霭": "霭", "叹气": "叹气", "按装": "安装", "报消": "报销",
         "重覆": "重复", "渡假": "度假", "松驰": "松弛", "藉贯": "籍贯",
         "既使": "即使", "好象": "好像", "帐号": "账号", "登陆": "登录",
         "做出": "作出", "做为": "作为", "起原": "起源", "精减": "精简",
         "欢渡": "欢度", "部份": "部分", "_idx": "x"}
for it in bank:
    w = it.get("word", "")
    blob = json.dumps(it, ensure_ascii=False)
    for k in WRONG:
        if isinstance(k, str) and len(k) > 1 and k in blob:
            print("%-16s 命中 %r" % (w, k))
