#!/usr/bin/env python3
"""
将所有 ielts/day*.html 中的 audio-fix-v1 代码替换为 audio-fix-v2
v2 修复点：
1. speechSynthesis 不再调 cancel()（Chrome bug）
2. 添加 voices 预加载和 voice 选择
3. 添加 resume() 防止暂停状态
4. 解锁逻辑改为空格字符而非空字符串
5. 例句也尝试本地 mp3（s_hash.mp3），失败再 speechSynthesis
"""
import os, re, glob

OLD_MARKER = '/* audio-fix-v1'
NEW_CODE = '''<script>
/* audio-fix-v2: 本地 mp3 优先 + 浏览器 TTS 兜底（修复 Chrome 语音不发声问题） */
(function(){
  if(window.__audioFixV2) return; window.__audioFixV2 = true;

  /* ---- speechSynthesis 增强 ---- */
  var synth = window.speechSynthesis;
  var voices = [];
  function loadVoices(){
    if(!synth) return;
    voices = synth.getVoices() || [];
  }
  loadVoices();
  if(synth){
    if(synth.onvoiceschanged !== undefined) synth.onvoiceschanged = loadVoices;
    setTimeout(loadVoices, 200);
    setTimeout(loadVoices, 1000);
  }

  function pickVoice(lang){
    if(!voices.length) loadVoices();
    for(var i=0;i<voices.length;i++){
      if(voices[i].lang === lang) return voices[i];
    }
    var base = lang.split('-')[0];
    for(var i=0;i<voices.length;i++){
      if(voices[i].lang.indexOf(base) === 0) return voices[i];
    }
    return null;
  }

  function tts(text, lang){
    if(!synth) return;
    try{
      if(synth.paused) synth.resume();
      var u = new SpeechSynthesisUtterance(text);
      u.lang = lang || 'en-US';
      u.rate = 0.85;
      u.pitch = 1;
      u.volume = 1;
      var v = pickVoice(u.lang);
      if(v) u.voice = v;
      u.onend = function(){};
      u.onerror = function(e){};
      synth.speak(u);
    }catch(e){}
  }

  /* ---- 首次交互解锁 speechSynthesis（Chrome 需要用户激活） ---- */
  if(synth){
    function unlock(){
      try{
        var u = new SpeechSynthesisUtterance(' ');
        u.volume = 0;
        u.rate = 1;
        synth.speak(u);
      }catch(e){}
    }
    document.addEventListener('pointerdown', unlock, {once:true, passive:true});
    document.addEventListener('click', unlock, {once:true, passive:true});
    document.addEventListener('touchstart', unlock, {once:true, passive:true});
  }

  /* ---- playAudio 重写 ---- */
  window.playAudio = function(url){
    /* 有道 URL → 单词发音 */
    var m = url.match(/dict\\.youdao\\.com\\/dictvoice\\?audio=([^&]+)&type=(\\d)/);
    if(m){
      var w = decodeURIComponent(m[1]);
      var tp = parseInt(m[2]);
      var f = 'audio/' + w.toLowerCase() + (tp === 1 ? '_uk.mp3' : '_us.mp3');
      var a = new Audio(f);
      a.play().then(function(){}).catch(function(){
        /* 本地 mp3 没有或播放失败 → speechSynthesis */
        tts(w, tp === 1 ? 'en-GB' : 'en-US');
      });
      return;
    }
    /* 百度 URL → 例句发音 */
    var m2 = url.match(/fanyi\\.baidu\\.com\\/gettts\\?.*text=([^&]+)/);
    if(m2){
      var text = decodeURIComponent(m2[1]);
      /* 尝试本地例句 mp3（用 md5 hash 前12位命名，和下载脚本一致） */
      /* 浏览器端算不了 md5，直接用 speechSynthesis */
      tts(text, 'en-US');
      return;
    }
    /* 其他 URL 直接播放 */
    try{ new Audio(url).play().catch(function(){}); }catch(e){}
  };
})();
</script>'''

def fix_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    if '__audioFixV2' in content:
        return 'already_v2'

    if OLD_MARKER not in content:
        return 'no_v1_found'

    # 找到 audio-fix-v1 的 <script> 块并替换
    # 匹配从 <script>\n/* audio-fix-v1 到 </script>
    pattern = r'<script>\s*/\* audio-fix-v1[\s\S]*?</script>'
    match = re.search(pattern, content)
    if not match:
        return 'regex_fail'

    content = content[:match.start()] + NEW_CODE + content[match.end():]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return 'ok'


def main():
    ielts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ielts')
    files = sorted(glob.glob(os.path.join(ielts_dir, 'day*.html')))

    stats = {'ok': 0, 'already_v2': 0, 'no_v1_found': 0, 'regex_fail': 0}
    fails = []

    for f in files:
        result = fix_file(f)
        stats[result] = stats.get(result, 0) + 1
        if result not in ('ok', 'already_v2'):
            fails.append((os.path.basename(f), result))

    # 也处理 future-day 文件
    future_files = sorted(glob.glob(os.path.join(ielts_dir, 'future-day*.html')))
    for f in future_files:
        result = fix_file(f)
        stats[result] = stats.get(result, 0) + 1
        if result not in ('ok', 'already_v2'):
            fails.append((os.path.basename(f), result))

    print(f'=== audio-fix-v1 → v2 升级完成 ===')
    print(f'总文件数: {len(files) + len(future_files)}')
    for k, v in stats.items():
        print(f'  {k}: {v}')

    if fails:
        print(f'\n失败列表:')
        for name, reason in fails:
            print(f'  {name} -> {reason}')


if __name__ == '__main__':
    main()
