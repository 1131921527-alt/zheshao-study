# -*- coding: utf-8 -*-
"""
第14轮第四批：把剩余 ~250 个兜底词逐个精准配图。
只做「单词级」精确匹配（\b 边界），不动已有规则。
"""
import io, re, sys, subprocess

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
HTML = ROOT + r"\study.html"
ANCHOR = "    [/武器|兵器|军械|武装/, '\U0001F52B'],\n"

# word -> emoji
M = {
    # 建筑 / 家居 / 工具
    "oversee": "\U0001F441", "stack": "\U0001F4DA", "bundle": "\U0001F4E6",
    "rub": "✋", "bar": "\U0001F37A", "test": "\U0001F4CB", "stationery": "✏️",
    "rod": "\U0001F3A3", "tile": "\U0001F9F1", "hook": "\U0001F9F7", "crane": "\U0001F3D7",
    "weld": "\U0001F527", "saw": "\U0001F6E0", "screw": "\U0001F529", "drill": "\U0001F527",
    "grid": "\U0001F532", "porch": "\U0001F6AA", "storey": "\U0001F3E2", "beam": "\U0001F3D7",
    "arch": "⛪", "cabinet": "\U0001F5C4", "balcony": "\U0001FAF4", "bath": "\U0001F6C1",
    "basin": "\U0001F6B0", "airtight": "\U0001F512", "mason": "\U0001F9F1",
    "villa": "\U0001F3E1", "hostel": "\U0001F3E8", "cabin": "\U0001F3D5", "cradle": "\U0001F476",
    "void": "\U0001F573", "haunt": "\U0001F47B", "ditch": "\U0001F6A7",
    # 食物 / 烹饪
    "sauce": "\U0001F96B", "ketchup": "\U0001F345", "perfume": "\U0001F9F4",
    "bake": "\U0001F35E", "fry": "\U0001F373", "suck": "\U0001F964",
    "soak": "\U0001F4A7", "grind": "☕",
    # 交通 / 旅行
    "visa": "\U0001F6C2", "parachute": "☂️", "carry-on": "\U0001F9F3", "atlas": "\U0001F5FA",
    "avenue": "\U0001F6E3", "signpost": "\U0001F68F", "van": "\U0001F690", "cart": "\U0001F6D2",
    "ferry": "⛴️", "raft": "\U0001F6F6", "canoe": "\U0001F6F6", "oar": "\U0001F6A3",
    "turbine": "⚙️", "underground": "\U0001F687", "tire": "\U0001F62A",
    # 商业 / 法律 / 犯罪
    "discount": "\U0001F3F7", "coupon": "\U0001F39F", "swap": "\U0001F504", "bid": "\U0001F4B0",
    "dump": "\U0001F5D1", "cheque": "\U0001F4B3", "cheap": "\U0001F4B8", "earn": "\U0001F4B0",
    "loss": "\U0001F4C9", "just": "✔️", "complain": "\U0001F624", "rob": "\U0001F9B9",
    "suicide": "\U0001F198", "fraud": "\U0001F3AD", "liar": "\U0001F925", "confess": "\U0001F5E3",
    "copyright": "\U0001F4DC", "expire": "⌛", "stamp": "\U0001F4EE", "bind": "\U0001F517",
    # 军事 / 冲突
    "command": "\U0001F4E2", "bombard": "\U0001F4A3", "cannon": "\U0001F4A3", "pistol": "\U0001F52B",
    "rifle": "\U0001F52B", "blade": "\U0001F52A", "sword": "⚔️", "bow": "\U0001F647",
    "arrow": "\U0001F3F9", "spear": "\U0001F531", "punch": "\U0001F44A",
    "famine": "\U0001F342", "starve": "\U0001F37D", "offend": "\U0001F620", "intrude": "\U0001F6B7",
    "attack": "⚔️", "oppress": "⛓️", "betray": "\U0001F5E1", "treason": "⚖️",
    "blame": "\U0001F449", "reproach": "\U0001F4AC", "turmoil": "\U0001F32A",
    "comfort": "\U0001F6CB", "devil": "\U0001F608", "hang": "\U0001F5BC", "tomb": "⚰️",
    "torture": "\U0001F616", "escape": "\U0001F3C3", "forgo": "\U0001F645", "discard": "\U0001F5D1",
    "tablet": "\U0001F48A", "patrol": "\U0001F693", "burrow": "\U0001F573",
    "veteran": "\U0001F396", "captain": "\U0001F9E2", "crush": "\U0001F5DC",
    # 民族 / 国家 / 文化
    "colony": "\U0001F3DB", "latin": "\U0001F3DB", "roman": "\U0001F3DB", "soviet": "\U0001F3DB",
    "jewish": "✡️", "swiss": "\U0001F1E8\U0001F1ED", "greek": "\U0001F1EC\U0001F1F7",
    "australia": "\U0001F1E6\U0001F1FA", "germany": "\U0001F1E9\U0001F1EA",
    "harmony": "\U0001F3B5", "flourish": "\U0001F331",
    "puppet": "\U0001F38E", "wreath": "\U0001F490", "corpus": "\U0001F4DA",
    # 家庭 / 人物
    "surname": "\U0001F3F7", "couple": "\U0001F46B", "spouse": "\U0001F491", "husband": "\U0001F468",
    "gay": "\U0001F308", "nephew": "\U0001F466", "niece": "\U0001F467",
    "embryo": "\U0001F476", "orphan": "\U0001F9D2", "hostess": "\U0001F469", "landlady": "\U0001F469",
    "host": "\U0001F3E0", "guest": "\U0001F465", "chase": "\U0001F3C3", "marry": "\U0001F48D",
    "honeymoon": "\U0001F3DD", "kiss": "\U0001F48B", "single": "1️⃣", "each": "\U0001F522",
    "hero": "\U0001F9B8", "heroine": "\U0001F478", "haircut": "\U0001F487", "fisherman": "\U0001F3A3",
    "beggar": "\U0001F64F", "coward": "\U0001F631", "mow": "\U0001F33F", "stare": "\U0001F440",
    "vow": "\U0001F48D", "whistle": "\U0001F617", "scold": "\U0001F5EF", "mock": "\U0001F60F",
    "hug": "\U0001F917", "kneel": "\U0001F9CE", "catch": "\U0001F932", "snatch": "✋",
    "grab": "\U0001F44A", "scrape": "\U0001F9FD", "whirl": "\U0001F300", "insert": "\U0001F4E5",
    "obsess": "\U0001F4AB", "marvel": "✨", "expel": "\U0001F6AB", "flee": "\U0001F3C3",
    "revenge": "⚔️", "kidnap": "\U0001F690", "impede": "\U0001F6A7", "bait": "\U0001F41F",
    "detach": "✂️", "aspire": "\U0001F3AF", "itch": "\U0001F99F", "replenish": "\U0001F504",
    "leak": "\U0001F4A7", "impart": "\U0001F4E4", "drop": "\U0001F4A7",
    "welcome": "\U0001F44B", "greet": "\U0001F44B", "farewell": "\U0001F44B",
    "recollect": "\U0001F4AD", "retrospect": "\U0001F519", "sideways": "↔️",
    # 身体
    "forehead": "\U0001F926", "brow": "\U0001F928", "eyelash": "\U0001F441", "mouth": "\U0001F444",
    "throat": "\U0001F5E3", "chin": "\U0001F447", "jaw": "\U0001F62C", "beard": "\U0001F9D4",
    "elbow": "\U0001F4AA", "chest": "\U0001F3BD", "stomach": "\U0001F922", "womb": "\U0001F930",
    "lung": "\U0001F32C", "gland": "\U0001F9EC", "ankle": "\U0001F9B6", "heel": "\U0001F9B6",
    "muscle": "\U0001F4AA", "nerve": "\U0001F9E0", "hormone": "\U0001F489",
    "awake": "⏰", "yawn": "\U0001F971", "dwarf": "\U0001F90F", "pregnancy": "\U0001F930",
    "born": "\U0001F476", "moan": "\U0001F616", "diabetes": "\U0001FA78", "overweight": "⚖️",
    "insomnia": "\U0001F6CC", "arthritis": "\U0001F9B4", "pimple": "\U0001F915",
    "choke": "\U0001F635", "scar": "\U0001FA79", "quarantine": "\U0001F3E5",
    "pill": "\U0001F48A", "morphine": "\U0001F489", "dose": "\U0001F48A",
    # 情绪 / 性格
    "fun": "\U0001F389", "polite": "\U0001F60A", "apology": "\U0001F64F", "admire": "⭐",
    "steadfast": "⛰️", "mundane": "\U0001F611", "bare": "⬜", "agony": "\U0001F616",
    "mourn": "\U0001F56F", "harass": "\U0001F624", "selfish": "\U0001F644", "unkind": "\U0001F612",
    "regret": "\U0001F614", "sigh": "\U0001F4A8", "stupid": "\U0001F92A", "greedy": "\U0001F911",
    # 时间 / 数量
    "century": "\U0001F4C5", "millennium": "\U0001F38A", "million": "\U0001F4B5",
    "billion": "\U0001F4B0", "midday": "\U0001F55B", "regular": "\U0001F501", "overdue": "⏰",
}

lines = []
for w, e in M.items():
    wc = w.replace("-", "[ -]")
    lines.append("    [/\\b%s\\b/, '%s']," % (wc, e))

block = ("    /* ===== 第14轮第四批：剩余兜底词逐个精准配图 ===== */\n"
         + "\n".join(lines) + "\n")

src = io.open(HTML, encoding="utf-8").read()
if ANCHOR not in src:
    print("!! 锚点未找到"); sys.exit(1)
if "第14轮第四批" in src:
    print("!! 第四批已存在，跳过"); sys.exit(0)
src = src.replace(ANCHOR, ANCHOR + block, 1)
io.open(HTML, "w", encoding="utf-8").write(src)
print("第四批插入规则 %d 条" % len(lines))

# 语法自检
m = re.search(r"function wordEmoji[\s\S]*?\n  \}\n", src)
if not m:
    m = re.search(r"wordEmoji\s*=\s*function[\s\S]*?\n  \}\n", src)
if m:
    io.open(ROOT + r"\_emoji_fn.js", "w", encoding="utf-8").write(
        "function studyWordEmojiStub(){}\n" + m.group(0))
    r = subprocess.run(["node", "--check", ROOT + r"\_emoji_fn.js"],
                       capture_output=True, text=True)
    print("✅ 语法通过" if r.returncode == 0 else "❌ 语法错误:\n" + r.stderr[:800])
else:
    print("(未定位到 wordEmoji 函数体，跳过语法检查)")
