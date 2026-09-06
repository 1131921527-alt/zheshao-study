# -*- coding: utf-8 -*-
"""提取 study.html 内联 JS 做 node --check 语法校验"""
import io, re, subprocess, sys

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
src = io.open(ROOT + r"\study.html", encoding="utf-8").read()
blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", src)
js = "\n;\n".join(blocks)
out = ROOT + r"\_inline.js"
io.open(out, "w", encoding="utf-8").write(js)
r = subprocess.run(["node", "--check", out], capture_output=True, text=True)
if r.returncode == 0:
    print("✅ 内联 JS 语法通过（%d 个 script 块，%d 字符）" % (len(blocks), len(js)))
else:
    print("❌ 语法错误:")
    print(r.stderr[:2000])
sys.exit(r.returncode)
