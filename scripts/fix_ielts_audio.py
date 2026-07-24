# -*- coding: utf-8 -*-
"""
雅思发音修复脚本
问题：day01-day77 老版页面用有道 dictvoice（防盗链返回空音频）+ 百度 gettts（连接失败），发音全挂。
方案：在每个 dayXX.html 的 </body> 前注入修复脚本，覆盖 window.playAudio：
  - 有道 URL → 提取单词，先试本地 audio/<word>_uk.mp3/_us.mp3，失败后用 speechSynthesis 兜底
  - 百度 URL → 提取文本，直接用 speechSynthesis 朗读
  - 其他 URL → 原样播放
同时注入 iOS/微信 speechSynthesis 解锁逻辑。
"""
import os, re, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IELTS = os.path.join(BASE, "ielts")

FIX_TAG = "audio-fix-v1"

FIX_SCRIPT = """<script>
/* """ + FIX_TAG + """: 有道/百度 TTS API 已失效，改用本地 mp3 + 浏览器 TTS 兜底 */
(function(){
  function tts(t,l){try{if(!window.speechSynthesis)return;var u=new SpeechSynthesisUtterance(t);u.lang=l||'en-US';u.rate=0.9;window.speechSynthesis.cancel();window.speechSynthesis.speak(u);}catch(e){}}
  if(window.speechSynthesis){function ul(){try{speechSynthesis.speak(new SpeechSynthesisUtterance(''));}catch(e){}}document.addEventListener('click',ul,{once:true});document.addEventListener('touchstart',ul,{once:true});}
  window.playAudio=function(url){
    var m=url.match(/dict\\.youdao\\.com\\/dictvoice\\?audio=([^&]+)&type=(\\d)/);
    if(m){var w=decodeURIComponent(m[1]),tp=parseInt(m[2]),f='audio/'+w.toLowerCase()+(tp===1?'_uk.mp3':'_us.mp3'),a=new Audio(f);a.play().catch(function(){tts(w,tp===1?'en-GB':'en-US');});return;}
    var m2=url.match(/fanyi\\.baidu\\.com\\/gettts\\?.*text=([^&]+)/);
    if(m2){tts(decodeURIComponent(m2[1]),'en-US');return;}
    new Audio(url).play().catch(function(){});
  };
})();
</script>"""


def fix_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    if FIX_TAG in html:
        return False  # 已注入过

    if "</body>" in html:
        html = html.replace("</body>", FIX_SCRIPT + "\n</body>", 1)
    elif "</html>" in html:
        html = html.replace("</html>", FIX_SCRIPT + "\n</html>", 1)
    else:
        html += FIX_SCRIPT

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True


def main():
    # 处理 day01-day78（排除 future-dayXX）
    files = sorted(glob.glob(os.path.join(IELTS, "day*.html")))
    # 排除 future-day*.html
    files = [f for f in files if not os.path.basename(f).startswith("future-")]

    fixed = 0
    skipped = 0
    for f in files:
        if fix_file(f):
            fixed += 1
        else:
            skipped += 1

    print(f"修复完成：注入 {fixed} 个文件，跳过 {skipped} 个（已注入过）")
    print(f"总计 {len(files)} 个 day 文件")

    # 也处理 future-dayXX（增强 TTS 解锁）
    future_files = sorted(glob.glob(os.path.join(IELTS, "future-day*.html")))
    ff_fixed = 0
    ff_skipped = 0
    for f in future_files:
        if fix_file(f):
            ff_fixed += 1
        else:
            ff_skipped += 1
    print(f"future 系列：注入 {ff_fixed} 个，跳过 {ff_skipped} 个")


if __name__ == "__main__":
    main()
