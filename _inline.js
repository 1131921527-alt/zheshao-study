
/* ============ 图标工具 ============ */
function svg(p){return '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+p+'</svg>';}
var ICONS={word:'📖',ai:'🤖',know:'🧠',speak:'🔊',back:'←'};

/* ============ 牌组配置（沿用，不改动数据源） ============ */
var DECKS=[
  {key:'en', name:'英语 · 雅思词汇', desc:'3934 词 · 乱序学习 · 发音+四选一+拼写', type:'word', src:'ielts/ielts_bank.json', color:'linear-gradient(135deg,#1f6feb,#a371f7)', icon:'📖', batch:20},
  {key:'ai', name:'AI · 科技精选', desc:'每天自动更新的 AI / 科技精选', type:'news', src:'assets/ai_cards.json', color:'linear-gradient(135deg,#ff8a5c,#ff5d8f)', icon:'🤖', batch:10},
  {key:'kn_all', name:'知识文章', desc:'35 篇 · 一次刷完所有类目', type:'know', src:'assets/knowledge_cards.json', color:'linear-gradient(135deg,#9aa7ff,#6b78ff)', icon:'📚', batch:5}
];

/* ============ 存储（与 index.html 共享前缀 wb_zs_） ============ */
var ZS_PREFIX='wb_zs_';
var STUDY_KEY='study', XP_KEY='xp', TASKS_KEY='tasks', FAV_KEY='fav', NEWSREAD_KEY='newsread';
var SET_SOUND='sound', SET_AUTO='auto', SET_SPELL='spell', LAST_KEY='last';
function zg(k,def){try{var v=localStorage.getItem(ZS_PREFIX+k);return v===null?def:JSON.parse(v);}catch(e){return def;}}
function zs(k,v){try{localStorage.setItem(ZS_PREFIX+k,JSON.stringify(v));}catch(e){toast('存储失败，空间可能已满');}}

var G={
  xp:zg(XP_KEY,0),
  study:zg(STUDY_KEY,{words:[],news:[],articles:[],spellToday:0,wordToday:0,newsToday:0,artToday:0,lastDate:''}),
  tasks:zg(TASKS_KEY,{}),
  fav:zg(FAV_KEY,[]),
  newsRead:zg(NEWSREAD_KEY,[]),
  sound:zg(SET_SOUND,true),
  auto:zg(SET_AUTO,true),
  spell:zg(SET_SPELL,true),
  last:zg(LAST_KEY,null)
};
function saveStudy(){zs(STUDY_KEY,G.study);}
function saveTasks(){zs(TASKS_KEY,G.tasks);}
function todayStr(){var d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function resetDailyIfNeeded(){var t=todayStr(); if(G.study.lastDate!==t){G.study.lastDate=t;G.study.spellToday=0;G.study.wordToday=0;G.study.newsToday=0;G.study.artToday=0;saveStudy();}}

/* ============ 设置 ============ */
function toggleSetting(which){
  if(which==='sound'){ G.sound=!G.sound; zs(SET_SOUND,G.sound); Sound.setOn(G.sound); document.getElementById('tgSound').classList.toggle('on',G.sound); if(G.sound) Sound.play('click'); }
  else if(which==='auto'){ G.auto=!G.auto; zs(SET_AUTO,G.auto); document.getElementById('tgAuto').classList.toggle('on',G.auto); if(G.auto) toast('自动发音已开'); }
  else if(which==='spell'){ G.spell=!G.spell; zs(SET_SPELL,G.spell); document.getElementById('tgSpell').classList.toggle('on',G.spell); }
}
function openSettings(){ document.getElementById('tgSound').classList.toggle('on',G.sound); document.getElementById('tgAuto').classList.toggle('on',G.auto); document.getElementById('tgSpell').classList.toggle('on',G.spell); refreshVoiceDesc(); document.getElementById('setOv').classList.add('on'); }
// 第12轮：显示当前例句用的是哪把嗓子，方便判断是否够自然
function refreshVoiceDesc(){
  var d=document.getElementById('voiceDesc'); if(!d) return;
  var n=NeuralVoice.name(), q=NeuralVoice.quality();
  if(!n){ d.textContent='系统无英文语音，例句自动用离线音频 / 有道发音'; return; }
  d.textContent='当前音色：'+n+(q>=60?'（神经网络音色，自然）':'（偏机械，建议用 Edge/Chrome 桌面版）');
}
function testVoice(){ Pron.speakSentence('This is a sample sentence for testing the voice.', null, -1); }
function closeSettings(){ document.getElementById('setOv').classList.remove('on'); }

/* ============ 统一音效系统（WebAudio 合成，无外部文件）增强版 ============ */
var Sound=(function(){
  var ctx=null, master=null, on=true, last={}, comboCount=0, lastPlayAt=0;
  function ensure(){
    if(!ctx){
      try{
        var AC=window.AudioContext||window.webkitAudioContext;
        if(!AC) return;
        ctx=new AC(); master=ctx.createGain(); master.gain.value=0.16; master.connect(ctx.destination);
      }catch(e){ ctx=null; return; }
    }
    // iOS/安卓：AudioContext 初始为 suspended，必须在用户手势里 resume 才出声
    if(ctx&&ctx.state==='suspended'){ try{ var p=ctx.resume(); if(p&&p.catch) p.catch(function(){}); }catch(e){} }
  }
  function tone(freq,start,dur,type,vol,glide){
    if(!ctx) return;
    var t0=ctx.currentTime+start;
    var o=ctx.createOscillator(), g=ctx.createGain();
    o.type=type||'sine'; o.frequency.setValueAtTime(freq,t0);
    if(glide) o.frequency.exponentialRampToValueAtTime(glide,t0+dur);
    g.gain.setValueAtTime(0.0001,t0);
    g.gain.exponentialRampToValueAtTime(vol||0.5,t0+0.012);
    g.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
    o.connect(g); g.connect(master); o.start(t0); o.stop(t0+dur+0.02);
  }
  function play(name){
    if(!on) return;
    ensure(); if(!ctx) return;
    var now=Date.now();
    if(last[name]&&now-last[name]<35) return;
    last[name]=now; lastPlayAt=now;
    switch(name){
      case 'click': tone(620,0,0.05,'square',0.35); break;
      case 'next': tone(480,0,0.06,'triangle',0.4,720); break;
      case 'back': tone(420,0,0.06,'triangle',0.35,300); break;
      case 'correct': tone(660,0,0.10,'sine',0.5); tone(880,0.08,0.12,'sine',0.5); break;
      case 'wrong':
        // 噔噔：两声连续下坠的错误音（比单低音更"游戏错误"感）
        tone(330,0,0.11,'square',0.32,220);
        tone(220,0.14,0.17,'square',0.30,138);
        break;
      // 拼写正确：比普通答对更亮、更清脆的 ding+sparkle
      case 'spellCorrect':
        tone(880,0,0.08,'sine',0.5);
        tone(1320,0.06,0.10,'sine',0.4);
        tone(1760,0.12,0.14,'sine',0.3);
        break;
      // 3连击 combo：轻快上升感
      case 'combo3':
        tone(523,0,0.06,'sine',0.4);
        tone(659,0.05,0.06,'sine',0.4);
        tone(784,0.10,0.08,'sine',0.45);
        break;
      // 5连击 combo：更饱满的胜利感
      case 'combo5':
        tone(523,0,0.05,'sine',0.35);
        tone(659,0.04,0.05,'sine',0.35);
        tone(784,0.08,0.05,'sine',0.4);
        tone(1047,0.12,0.06,'sine',0.42);
        tone(1318,0.16,0.10,'sine',0.45);
        break;
      // 过关完成：短促胜利号角
      case 'complete':
        tone(523,0,0.08,'sine',0.45);
        tone(659,0.07,0.08,'sine',0.45);
        tone(784,0.14,0.08,'sine',0.45);
        tone(1047,0.22,0.12,'sine',0.42);
        break;
      case 'ding': tone(880,0,0.10,'sine',0.5); tone(1320,0.07,0.14,'sine',0.4); break;
      case 'xp': tone(988,0,0.08,'triangle',0.4); tone(1318,0.07,0.12,'triangle',0.4); break;
      case 'fav': tone(1200,0,0.08,'sine',0.3); break;
    }
  }
  function addCombo(){ comboCount++; if(comboCount===3){ play('combo3'); showComboToast('🔥 3连击!'); } else if(comboCount>=5 && comboCount%5===0){ play('combo5'); showComboToast('⚡ '+comboCount+'连击!'); } }
  function resetCombo(){ comboCount=0; }
  function showComboToast(txt){ var el=document.getElementById('comboToast'); el.textContent=txt; el.classList.remove('on'); void el.offsetWidth; el.classList.add('on'); setTimeout(function(){el.classList.remove('on');},1200); }
  return {play:play, setOn:function(v){on=v;}, isOn:function(){return on;}, unlock:ensure, addCombo:addCombo, resetCombo:resetCombo, recentlyPlayed:function(){return (Date.now()-lastPlayAt)<80;}};
})();

/* ============ 第12轮：例句发音统一化 —— 系统神经语音 / 离线Aria / 有道 三层兜底 ============
   背景：微软 Edge TTS 的 WSS 端点强制校验 Origin=chrome-extension:// 与 UA/Cookie，
        浏览器 WebSocket 无法自定义这些头（forbidden header），网页端直连必然握手失败，
        因此改为「系统自带的神经语音为主 + 离线预生成 Aria mp3 兜底 + 有道兜底」。
   优先级：① 系统神经语音（全站同一把嗓子，离线可用，最自然）
           ② 离线 mp3：ielts/audio/ex1/<slug>.mp3（en-US-AriaNeural 离线合成，仅第1条例句）
           ③ 有道 dictvoice type=0（美音）在线兜底
*/
var NeuralVoice=(function(){
  var synth=(typeof window!=='undefined'&&window.speechSynthesis)?window.speechSynthesis:null;
  var picked=null, pickedScore=0;
  // 音色打分：越高越自然。刻意压低英音(en-GB)，保证全站统一美音
  var PREFS=[[/aria/i,100],[/jenny/i,96],[/natural/i,92],[/neural/i,88],[/microsoft[^|]*online/i,84],
             [/google (us )?english/i,76],[/samantha/i,72],[/karen/i,62],[/daniel/i,60],[/moira/i,55],
             [/tessa/i,55],[/zira/i,42],[/david/i,42],[/hazel/i,42],[/mark/i,42],[/english/i,20]];
  function score(v){
    if(!v) return 0;
    var lang=v.lang||'';
    if(!/^en[-_]/i.test(lang)) return 0;
    var nm=(v.name||'')+' '+(v.voiceURI||''), best=0;
    for(var i=0;i<PREFS.length;i++){ if(PREFS[i][0].test(nm)) best=Math.max(best,PREFS[i][1]); }
    if(/en[-_]GB|United Kingdom|British|Irish|Scottish|en[-_]AU|en[-_]IN/i.test(lang+' '+nm)) best-=30;
    if(v.localService) best+=3;
    return best;
  }
  function pick(){
    if(!synth) return null;
    var list=[]; try{ list=synth.getVoices()||[]; }catch(e){ return null; }
    var best=null,bs=9;   // 低于 10 分认为音色不可接受（多半是机械合成器）
    for(var i=0;i<list.length;i++){ var s=score(list[i]); if(s>bs){bs=s;best=list[i];} }
    pickedScore=best?bs:0;
    return best;
  }
  function ready(){ if(!synth) return null; if(!picked) picked=pick(); return picked; }
  function quality(){ if(!synth) return 0; if(!picked) picked=pick(); return pickedScore; }
  if(synth&&typeof synth.addEventListener==='function'){
    try{ synth.addEventListener('voiceschanged',function(){ picked=pick(); }); }catch(e){}
  }
  var keepAlive=null;
  // Chrome 长句 15s 后会自动停，定时 pause/resume 续命
  function watch(text){
    if(keepAlive) clearInterval(keepAlive);
    var t0=Date.now();
    keepAlive=setInterval(function(){
      try{
        if(!synth.speaking||Date.now()-t0>25000){ clearInterval(keepAlive); keepAlive=null; return; }
        synth.pause(); synth.resume();
      }catch(e){ clearInterval(keepAlive); keepAlive=null; }
    },8000);
  }
  // speak(text,onFail)：成功返回 true；失败/无音色调用 onFail 交给下一层
  function speak(text,onFail){
    if(!text){ if(onFail) onFail(); return false; }
    var v=ready();
    if(!v){ if(onFail) onFail(); return false; }
    try{
      synth.cancel();
      var u=new SpeechSynthesisUtterance(text);
      u.voice=v; u.lang=v.lang||'en-US'; u.rate=0.95; u.pitch=1; u.volume=1;
      u.onerror=function(ev){
        var err=(ev&&ev.error)||'';
        if(err==='interrupted'||err==='canceled') return;   // 自己 cancel 掉的不算失败
        if(onFail) onFail();
      };
      synth.speak(u);
      watch(text);
      return true;
    }catch(e){ if(onFail) onFail(); return false; }
  }
  function name(){ var v=ready(); return v?String(v.name||v.voiceURI||''):''; }
  return {speak:speak, quality:quality, name:name, ok:function(){ return !!ready(); }};
})();

/* ============ 自动发音 + 预加载（复用现有 mp3） ============ */
var Pron=(function(){
  var el=document.getElementById('audio');
  // 本地 mp3 加载失败（404）时，自动回退到有道在线发音，保证任何词都能出声
  try{
    el.addEventListener('error', function(){
      var src=el.src||'';
      // 离线例句 mp3（/ex1/）缺失：改用系统神经语音，再退有道
      if(src.indexOf('/ex1/')>=0){
        if(lastSent){ NeuralVoice.speak(lastSent, function(){ youdao(lastSent); }); }
        return;
      }
      if(src.indexOf('ielts/audio/')>=0){
        try{
          var m=decodeURIComponent(src).match(/audio\/(.+)_us\.mp3/);
          if(m){
            // 第12轮：本地 mp3 缺失时改用系统神经语音（和例句同一把嗓子），再回退有道
            NeuralVoice.speak(m[1], function(){
              el.src='https://dict.youdao.com/dictvoice?audio='+encodeURIComponent(m[1])+'&type=2';
              var p=el.play(); if(p&&p.catch) p.catch(function(){});
            });
          }
        }catch(e){}
      }
    });
  }catch(e){}
  // 极小静音 wav，仅用于首次手势里解锁移动端 <audio>（iOS/安卓不解锁则点喇叭没声音）
  var SILENT='data:audio/wav;base64,UklGRmQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YUAAAACAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA';
  var unlocked=false;
  var lastSent='';   // 最近一次朗读的例句，供离线 mp3 404 时回退使用
  // 音频文件名统一小写（下载脚本用的是 word.lower()），这里必须转小写才能命中，
  // 否则 Edition 这类首字母大写的词会拼成不存在的 Edition_us.mp3 而哑掉
  function url(w){ return 'ielts/audio/'+encodeURIComponent(String(w||'').trim().toLowerCase())+'_us.mp3'; }
  function speak(w){   // 立即发音：不理“自动发音”开关，手动点喇叭必须出声
    if(!w) return;
    try{
      el.src=url(w);
      try{ el.currentTime=0; }catch(e){}
      var p=el.play(); if(p&&p.catch) p.catch(function(){});
    }catch(e){}
  }
  // 例句整句发音（第12轮）：系统神经语音 → 离线 Aria mp3 → 有道美音，三层兜底且音色尽量统一
  function exMp3(word, idx){
    if(idx!==0||!word) return '';   // 离线 mp3 只合成了每词的第 1 条例句
    var s=String(word).trim().toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'');
    return s?('ielts/audio/ex1/'+encodeURIComponent(s)+'.mp3'):'';
  }
  function youdao(sent){
    try{
      el.src='https://dict.youdao.com/dictvoice?audio='+encodeURIComponent(sent)+'&type=0';
      try{ el.currentTime=0; }catch(e){}
      var p=el.play(); if(p&&p.catch) p.catch(function(){});
    }catch(e){}
  }
  function speakSentence(sent, word, idx){
    if(!sent) return;
    lastSent=sent;
    var q=NeuralVoice.quality();          // 0=没有可用英文语音
    var mp3=exMp3(word, idx);
    // ① 音色够好（神经网络/自然音色）→ 系统语音，全站同一把嗓子
    if(q>=60){ NeuralVoice.speak(sent, function(){ if(mp3) playMp3(mp3, youdao.bind(null,sent)); else youdao(sent); }); return; }
    // ② 音色一般但有离线 Aria mp3（第1条例句）→ 优先离线，更自然也更统一
    if(mp3){ playMp3(mp3, function(){ if(q>0) NeuralVoice.speak(sent, youdao.bind(null,sent)); else youdao(sent); }); return; }
    // ③ 退而求其次：有系统语音就用，否则有道
    if(q>0){ NeuralVoice.speak(sent, youdao.bind(null,sent)); return; }
    youdao(sent);
  }
  function playMp3(src, onFail){
    try{
      el.src=src; try{ el.currentTime=0; }catch(e){}
      var p=el.play();
      if(p&&p.catch) p.catch(function(){ if(onFail) onFail(); });
      else if(!p && el.error && onFail) onFail();
    }catch(e){ if(onFail) onFail(); }
  }
  function play(w){ if(!G.auto) return; speak(w); }   // 自动发音：受开关控制
  function unlock(){   // 必须在真实用户手势里调用，才能解锁移动端音频
    if(unlocked) return;
    // 无论成功失败都必须把音量恢复为 1，否则后续发音全被静音
    var done=function(){ try{ el.pause(); }catch(e){} try{ el.volume=1; }catch(e){} };
    try{
      el.volume=0; el.src=SILENT;
      var p=el.play();
      if(p&&p.then){ p.then(function(){ unlocked=true; }, function(){}).then(done, done); }
      else { unlocked=true; done(); }
    }catch(e){ done(); }
  }
  function stop(){ try{ el.pause(); el.currentTime=0; }catch(e){} }
  function preload(w){ if(!w) return; var a=new Audio(); a.preload='auto'; a.src=url(w); }
  return {play:play, speak:speak, speakSentence:speakSentence, stop:stop, preload:preload, unlock:unlock};
})();

/* ============ 图片预加载（文字优先，绝不卡图片） ============ */
var imgCache={};
function preloadImg(it){ if(!it||!it.image||imgCache[it.image]) return; var im=new Image(); im.src=it.image; imgCache[it.image]=im; }

/* ============ 触觉反馈 ============ */
function vibe(ms){ try{ if(navigator.vibrate) navigator.vibrate(ms); }catch(e){} }

/* ============ XP（复用同一钱包 wb_zs_xp，不另建系统） ============ */
function addXp(n){
  G.xp+=n; zs(XP_KEY,G.xp);
  document.getElementById('xpChip').textContent='XP '+G.xp;
  var p=document.getElementById('xppop'); p.textContent='+'+n+' XP'; p.classList.remove('on'); void p.offsetWidth; p.classList.add('on');
  Sound.play('xp');
}
function claimGoal(key,xp){
  var day=todayStr();
  if(!G.tasks[day]) G.tasks[day]={};
  if(G.tasks[day][key+'_claimed']) return;
  G.tasks[day][key]=1; G.tasks[day][key+'_claimed']=1; saveTasks();
  addXp(xp);
}

/* ============ 数据缓存 ============ */
var cache={};
var rawCache={};
var artCache={};
function loadDeck(deck,cb){
  if(cache[deck.key]){cb(cache[deck.key]);return;}
  if(rawCache[deck.src]){ finishDeck(deck, rawCache[deck.src], cb); return; }
  var opts = deck.type==='news' ? {cache:'no-cache'} : {};
  fetch(deck.src, opts).then(function(r){return r.json();}).then(function(data){
    rawCache[deck.src]=data; finishDeck(deck, data, cb);
  }).catch(function(){ toast('内容加载失败，请刷新重试'); });
}
function finishDeck(deck,data,cb){
  var all=(deck.type==='word')?data:(data.cards||[]);
  var items=deck.cat? all.filter(function(it){return it.cat===deck.cat;}) : all;
  cache[deck.key]=items; cb(items);
}

/* ============ emoji 配图 ============ */
function wordEmoji(word, cn){
  var s=(word+' '+cn).toLowerCase();
  var map=[    [/\b(bird|eagle|owl|pigeon|swallow)\b/, '🐦'],
    [/\b(cat|kitten)\b/, '🐱'],
    [/\b(dog|puppy|canine)\b/, '🐶'],
    [/\b(fish|salmon|tuna)\b/, '🐟'],
    [/\b(horse|equine)\b/, '🐴'],
    [/\b(cow|cattle|bull|ox)\b/, '🐮'],
    [/\b(pig|swine|hog)\b/, '🐷'],
    [/\b(sheep|lamb|wool)\b/, '🐑'],
    [/\b(monkey|ape|primate)\b/, '🐒'],
    [/\b(lion|tiger|leopard|panther)\b/, '🐯'],
    [/\b(bear|polar)\b/, '🐻'],
    [/\b(elephant)\b/, '🐘'],
    [/\b(rabbit|hare|bunny)\b/, '🐰'],
    [/\b(snake|serpent|cobra)\b/, '🐍'],
    [/\b(frog|toad)\b/, '🐸'],
    [/\b(whale|dolphin)\b/, '🐬'],
    [/\b(butterfly)\b/, '🦋'],
    [/\b(bee|honey)\b/, '🐝'],
    [/\b(ant)\b/, '🐜'],
    [/\b(spider)\b/, '🕷️'],
    [/\b(crab|lobster|shrimp)\b/, '🦀'],
    [/\b(snail|slug)\b/, '🐌'],
    [/\b(turtle|tortoise)\b/, '🐢'],
    [/\b(crocodile|alligator)\b/, '🐊'],
    [/\b(penguin)\b/, '🐧'],
    [/\b(kangaroo)\b/, '🦘'],
    [/\b(koala)\b/, '🐨'],
    [/\b(mouse|rat|rodent)\b/, '🐭'],
    [/\b(tree|forest|woodland|oak|pine)\b/, '🌳'],
    [/\b(flower|bloom|blossom|petal|rose|tulip)\b/, '🌸'],
    [/\b(grass|lawn|meadow)\b/, '🌿'],
    [/\b(leaf|foliage)\b/, '🍃'],
    [/\b(fruit|fruit)\b/, '🍎'],
    [/\b(apple)\b/, '🍎'],
    [/\b(banana)\b/, '🍌'],
    [/\b(orange|citrus)\b/, '🍊'],
    [/\b(grape)\b/, '🍇'],
    [/\b(strawberry)\b/, '🍓'],
    [/\b(peach|lemon|mango|pineapple|watermelon|cherry)\b/, '🍉'],
    [/\b(vegetable|carrot|potato|tomato|onion|cabbage|broccoli|cucumber)\b/, '🥦'],
    [/\b(corn|maize|wheat|grain|rice|cereal)\b/, '🌾'],
    [/\b(nut|peanut|walnut|almond)\b/, '🥜'],
    [/\b(mushroom|fungus)\b/, '🍄'],
    [/\b(rain|rainy|rainfall|drizzle|downpour)\b/, '🌧️'],
    [/\b(snow|snowy|blizzard|snowfall)\b/, '❄️'],
    [/\b(wind|windy|breeze|gust|gale)\b/, '🌬️'],
    [/\b(cloud|cloudy|overcast)\b/, '☁️'],
    [/\b(storm|thunder|lightning|thunderstorm)\b/, '⛈️'],
    [/\b(rainbow)\b/, '🌈'],
    [/\b(sun|sunny|sunlight|sunshine)\b/, '☀️'],
    [/\b(moon|lunar)\b/, '🌙'],
    [/\b(star|starry|astronomy)\b/, '⭐'],
    [/\b(fog|smog|mist|haze|foggy)\b/, '🌫️'],
    [/\b(flood|flooding)\b/, '🌊'],
    [/\b(drought)\b/, '🏜️'],
    [/\b(earthquake|quake|seismic)\b/, '🌍'],
    [/\b(volcano|volcanic|eruption|lava)\b/, '🌋'],
    [/\b(tsunami)\b/, '🌊'],
    [/\b(ice|glacier|frozen|frost)\b/, '🧊'],
    [/\b(fire|flame|burning|combust)\b/, '🔥'],
    [/\b(water|ocean|sea|river|lake|pond|stream)\b/, '💧'],
    [/\b(wave)\b/, '🌊'],
    [/\b(desert|arid)\b/, '🏜️'],
    [/\b(island)\b/, '🏝️'],
    [/\b(mountain|mount|peak|summit|ridge)\b/, '⛰️'],
    [/\b(hill)\b/, '⛰️'],
    [/\b(beach|shore|coast|seaside)\b/, '🏖️'],
    [/\b(bread|toast)\b/, '🍞'],
    [/\b(cake|cookie|biscuit|pastry)\b/, '🍰'],
    [/\b(milk|dairy|cheese|yogurt|butter)\b/, '🥛'],
    [/\b(egg)\b/, '🥚'],
    [/\b(meat|beef|pork|lamb|chicken|sausage)\b/, '🍖'],
    [/\b(pizza)\b/, '🍕'],
    [/\b(noodle|pasta|spaghetti)\b/, '🍝'],
    [/\b(rice)\b/, '🍚'],
    [/\b(soup|stew)\b/, '🍲'],
    [/\b(salad)\b/, '🥗'],
    [/\b(sandwich|burger|hamburger|hotdog)\b/, '🍔'],
    [/\b(sushi)\b/, '🍣'],
    [/\b(curry|spice|spicy)\b/, '🍛'],
    [/\b(sweet|sugar|candy|dessert|chocolate)\b/, '🍬'],
    [/\b(coffee)\b/, '☕'],
    [/\b(tea|green tea)\b/, '🍵'],
    [/\b(juice)\b/, '🧃'],
    [/\b(wine|alcohol|beer|whisky|liquor|drunk|intoxicat)\b/, '🍷'],
    [/\b(water)\b/, '🥤'],
    [/\b(sleep|asleep|nap|sleepy)\b/, '😴'],
    [/\b(eat|eating|consume|diet|nutrition)\b/, '🍽️'],
    [/\b(drink)\b/, '🥤'],
    [/\b(run|running|jog|sprint)\b/, '🏃'],
    [/\b(walk|walking|stroll|pedestrian)\b/, '🚶'],
    [/\b(jump|leap|hop|bounce)\b/, '🦘'],
    [/\b(swim|swimming)\b/, '🏊'],
    [/\b(fly|flying|flight)\b/, '✈️'],
    [/\b(climb|climbing)\b/, '🧗'],
    [/\b(dance|dancing)\b/, '💃'],
    [/\b(sing|singing|song|vocal)\b/, '🎤'],
    [/\b(cry|weep|sob|tear)\b/, '😢'],
    [/\b(laugh|smile|funny|humor|amuse|joy|cheer)\b/, '😄'],
    [/\b(angry|anger|rage|furious|annoy|frustrat)\b/, '😠'],
    [/\b(afraid|fear|scared|terrify|frighten|panic)\b/, '😨'],
    [/\b(surprise|surprised|amaze|astonish|shock)\b/, '😲'],
    [/\b(sad|sadness|sorrow|grief|depress|gloom|melanchol)\b/, '😞'],
    [/\b(happy|happiness|delight|pleasure|satisfaction)\b/, '😊'],
    [/\b(love|like|affection|romantic|passion|fond|adore)\b/, '❤️'],
    [/\b(hate|hatred|dislike|loathe|hostil)\b/, '💔'],
    [/\b(worry|anxious|anxiety|nervous|stress|tension)\b/, '😟'],
    [/\b(excit|thrill|enthusiast|eager|passionat)\b/, '🤩'],
    [/\b(tired|fatigue|exhaust|weary|drowsy)\b/, '🥱'],
    [/\b(proud|pride)\b/, '😌'],
    [/\b(shy|shame|embarrass|timid)\b/, '😳'],
    [/\b(jealous|envy|envious|envious)\b/, '😒'],
    [/\b(calm|peace|relax|tranquil|serene|quiet|gentle)\b/, '😌'],
    [/\b(confuse|confused|puzzle|bewilder)\b/, '😕'],
    [/\b(disappoint|let join|letdown|frustrate)\b/, '😔'],
    [/\b(boring|bored|tedious|dull|monoton)\b/, '🥱'],
    [/\b(teacher|educator|instructor|professor|tutor|mentor)\b/, '👨‍🏫'],
    [/\b(student|pupil|learner|undergraduate)\b/, '🎓'],
    [/\b(doctor|physician|surgeon|medical)\b/, '👨‍⚕️'],
    [/\b(nurse)\b/, '👩‍⚕️'],
    [/\b(lawyer|attorney|counsel|legal)\b/, '⚖️'],
    [/\b(judge)\b/, '⚖️'],
    [/\b(police|officer|cop)\b/, '👮'],
    [/\b(soldier|army|military|warrior|troop|battle|war)\b/, '🎖️'],
    [/\b(farmer|agriculture|agricultural)\b/, '👨‍🌾'],
    [/\b(cook|chef|cooking|kitchen)\b/, '👨‍🍳'],
    [/\b(driver|driving)\b/, '🚗'],
    [/\b(artist|painter|drawing|sketch|artistic)\b/, '🎨'],
    [/\b(musician|music|instrument|piano|guitar|violin|melody|symphony)\b/, '🎵'],
    [/\b(singer)\b/, '🎤'],
    [/\b(actor|actress|film|movie|cinema|drama|theatre|stage)\b/, '🎬'],
    [/\b(writer|author|author|literature|novel|poem|poetry|essay)\b/, '✍️'],
    [/\b(journalist|reporter|news|media|press)\b/, '📰'],
    [/\b(scientist|research|laboratory|experiment|experimental)\b/, '🔬'],
    [/\b(engineer|engineering|technical|mechanical)\b/, '⚙️'],
    [/\b(business|entrepreneur|commerce|commercial|trade|merchant|enterprise)\b/, '💼'],
    [/\b(banker|finance|financial|investment|stock)\b/, '💰'],
    [/\b(athlete|sport|sports|exercise|training|gym|fitness)\b/, '🏋️'],
    [/\b(player|game|playing|soccer|football|basketball|tennis|match|team|competition)\b/, '⚽'],
    [/\b(king|queen|prince|princess|royal|emperor|empire|noble|monarch|dynasty)\b/, '👑'],
    [/\b(house|home|building|apartment|residence|dwelling)\b/, '🏠'],
    [/\b(school|classroom|college|university|campus|education)\b/, '🏫'],
    [/\b(hospital|clinic|care)\b/, '🏥'],
    [/\b(bank)\b(?!note)/, '🏦'],
    [/\b(shop|store|mall|market|shopping|retail|supermarket)\b/, '🛒'],
    [/\b(restaurant|cafe|café|dining|meal|dinner|lunch|breakfast)\b/, '🍽️'],
    [/\b(car|vehicle|auto|automobile|truck|bus|taxi)\b/, '🚗'],
    [/\b(train|railway|rail|subway|metro|locomotive)\b/, '🚆'],
    [/\b(plane|airplane|aircraft|aviation|flight)\b/, '✈️'],
    [/\b(ship|boat|vessel|sail|port|harbor)\b/, '🚢'],
    [/\b(bicycle|bike|cycle)\b/, '🚲'],
    [/\b(motorcycle|motorbike)\b/, '🏍️'],
    [/\b(phone|telephone|cellphone|smartphone|mobile)\b/, '📱'],
    [/\b(computer|laptop|computer|desktop|software|program|programming|coding)\b/, '💻'],
    [/\b(internet|online|web|network|website|digital)\b/, '🌐'],
    [/\b(email|mail|letter|post)\b/, '✉️'],
    [/\b(book|textbook|magazine|library|reading|read)\b/, '📚'],
    [/\b(newspaper)\b/, '📰'],
    [/\b(television|tv|broadcast)\b/, '📺'],
    [/\b(radio)\b/, '📻'],
    [/\b(camera|photograph|photo|photography|picture)\b/, '📷'],
    [/\b(clock|watch|time|temporal)\b/, '⏰'],
    [/\b(calendar|date)\b/, '📅'],
    [/\b(pen|pencil|notebook|paper|stationery)\b/, '✏️'],
    [/\b(key)\b(?!note)/, '🔑'],
    [/\b(lock|locked|security)\b/, '🔒'],
    [/\b(message|note|note)\b/, '💬'],
    [/\b(light|lamp|electric|electricity|power|energy)\b/, '💡'],
    [/\b(battery)\b/, '🔋'],
    [/\b(bag|backpack|suitcase|luggage|pocket)\b/, '🎒'],
    [/\b(umbrella|raincoat)\b/, '☂️'],
    [/\b(shoe|sneaker|boot|footwear|slipper)\b/, '👟'],
    [/\b(clothes|clothing|dress|shirt|coat|jacket|jeans|skirt|fashion|wear)\b/, '👕'],
    [/\b(hat|cap)\b/, '🎩'],
    [/\b(glasses|spectacles)\b/, '👓'],
    [/\b(ring|jewelry|jewel|diamond|necklace)\b/, '💍'],
    [/\b(gift|present|prize|award|bonus|reward)\b/, '🎁'],
    [/\b(ticket)\b/, '🎫'],
    [/\b(map)\b/, '🗺️'],
    [/\b(cup|glass|mug|bottle|container)\b/, '🥛'],
    [/\b(plate|bowl|dish)\b/, '🍽️'],
    [/\b(knife|fork|spoon|cutlery)\b/, '🍴'],
    [/\b(bed|bedroom|sleeping)\b/, '🛏️'],
    [/\b(chair|desk|table|furniture|sofa|bench)\b/, '🪑'],
    [/\b(door|entrance|gate|exit)\b/, '🚪'],
    [/\b(window)\b/, '🪟'],
    [/\b(road|street|path|highway|route)\b/, '🛤️'],
    [/\b(bridge)\b/, '🌉'],
    [/\b(park|garden|yard|playground)\b/, '🏞️'],
    [/\b(city|urban|town|village|capital)\b/, '🏙️'],
    [/\b(country|nation|national|region|rural)\b/, '🏳️'],
    [/\b(border|boundary|frontier|edge)\b/, '↔️'],
    [/\b(flag)\b/, '🚩'],
    [/\b(fire|flame|burn)\b/, '🔥'],
    [/\b(water|ocean|sea|river)\b/, '💧'],
    [/\b(glass|glassy)\b/, '🥃'],
    [/\b(stone|rock|mineral)\b/, '🪨'],
    [/\b(sand|sandy)\b/, '🏖️'],
    [/\b(metal|iron|steel|gold|silver|copper)\b/, '⚙️'],
    [/\b(wood|wooden|timber)\b/, '🪵'],
    [/\b(plastic)\b/, '🧴'],
    [/\b(paper)\b/, '📄'],
    [/\b(cloth|fabric|cotton|silk|wool)\b/, '🧵'],
    [/\b(paint|color|colour|dye|pigment)\b/, '🎨'],
    [/\b(think|thought|consider|contemplate|ponder|mind|idea|concept)\b/, '🤔'],
    [/\b(learn|learning|study|study)\b/, '📖'],
    [/\b(teach|teaching|educate|instruct)\b/, '👨‍🏫'],
    [/\b(know|knowing|knowledge|understand|understanding)\b/, '🧠'],
    [/\b(remember|recall|memorize|memory)\b/, '🧠'],
    [/\b(forget|forget)\b/, '😵'],
    [/\b(speak|speech|talk|say|tell|conversation|communicate|communication|language|discuss)/, '🗣️'],
    [/\b(listen|hearing|listen)\b/, '👂'],
    [/\b(see|seeing|view|look|watch|observe|vision|visual)\b/, '👀'],
    [/\b(write|writing|word|vocabulary|spelling|text|typing|type)\b/, '✍️'],
    [/\b(read|reading|literacy)\b/, '📖'],
    [/\b(buy|purchase|shop|pay|cost|spend|expense|price|worth)\b/, '💳'],
    [/\b(sell|sale|market|merchandise|profit)\b/, '💰'],
    [/\b(money|cash|currency|salary|wage|income)\b/, '💵'],
    [/\b(budget|save|saving|finance|economy|economic|wealth|rich|fortune)\b/, '💲'],
    [/\b(borrow|lend|loan|debt|owe)\b/, '🏦'],
    [/\b(work|working|job|labor|employment|profession|career|task|duty)\b/, '💼'],
    [/\b(rest|break|relax|leisure|holiday|vacation|weekend)\b/, '🏖️'],
    [/\b(go|move|motion|movement)\b/, '➡️'],
    [/\b(come|arrive|return|reach)\b/, '↩️'],
    [/\b(give|offer|provide|supply|provide)\b/, '🤲'],
    [/\b(get|obtain|gain|acquire|receive|attain|achieve)\b/, '🎯'],
    [/\b(make|create|produce|build|construct|manufacture|generate|fabricate)\b/, '🛠️'],
    [/\b(change|change|alter|modify|transform|shift|vary|convert|adjust|adapt)\b/, '🔄'],
    [/\b(improve|improvement|enhance|develop|development|progress|advance|boost|upgrade)\b/, '📈'],
    [/\b(reduce|decrease|decline|lower|diminish|cut|shrink|less|minimize)\b/, '📉'],
    [/\b(increase|rise|grow|growth|expand|extend|add|boost|augment|raise)\b/, '📈'],
    [/\b(start|begin|commence|origin|initial|launch|establish|found|initiate)\b/, '🚀'],
    [/\b(stop|end|finish|cease|complete|conclude|halt|terminate|abandon)\b/, '⏹️'],
    [/\b(help|help|aid|assist|support|facilitate|relief)\b/, '🤝'],
    [/\b(prevent|avoid|stop|hinder|block|obstruct|prohibit|ban|forbid)\b/, '🚫'],
    [/\b(allow|permit|enable|let)\b/, '✅'],
    [/\b(open|opening)\b/, '🔓'],
    [/\b(close|closed|shut)\b/, '🔒'],
    [/\b(success|succeed|successful|achievement|accomplish|victory|win|triumph)\b/, '🏆'],
    [/\b(fail|failure|fail|defeat|lose|setback)\b/, '❌'],
    [/\b(problem|issue|challenge|difficulty|trouble|crisis|obstacle|hardship)\b/, '⚠️'],
    [/\b(solve|solution|resolve|fix|repair|settle)\b/, '🔧'],
    [/\b(choose|choice|select|select|elect|decide|decision|option|prefer|preference)\b/, '☑️'],
    [/\b(compare|comparison|contrast|similar|same|equal|identical)\b/, '⚖️'],
    [/\b(differ|difference|different|distinguish|unique|distinct|vary|categorize|classify|classify)\b/, '🔀'],
    [/\b(important|importance|significant|significant|crucial|vital|essential|key|major|critical)\b/, '⭐'],
    [/\b(benefit|benefit|advantage|useful|helpful|valuable|worthwhile|profitable)\b/, '👍'],
    [/\b(danger|dangerous|risk|risky|hazard|threat|threaten|peril|lurking)\b/, '⚠️'],
    [/\b(safety|safe|secure|security|safeguard|protection|protect|defend)\b/, '🛡️'],
    [/\b(health|healthy|fitness|wellness|medical|treat|treatment|recover|heal|cure)\b/, '💊'],
    [/\b(ill|sick|disease|illness|symptom|infection|virus|bacteria|germ)\b/, '🤒'],
    [/\b(pain|hurt|injury|injure|wound|ache|suffer)\b/, '🤕'],
    [/\b(save|rescue|safety|save)\b/, '🛟'],
    [/\b(strong|strength|powerful|power|force|energy|vigor|sturdy|robust)\b/, '💪'],
    [/\b(weak|weakness|fragile|feeble|vulnerable)\b/, '🪫'],
    [/\b(fast|speed|rapid|quick|swift|hurry|hasten|accelerate|accelerate)\b/, '⚡'],
    [/\b(slow|slowly|delay|lag|postpone|put off|delayed)\b/, '🐢'],
    [/\b(new|novel|fresh|recent|modern|latest)\b/, '🆕'],
    [/\b(old|ancient|age|aged|elderly|senior|antique|outdated)\b/, '👴'],
    [/\b(big|large|huge|giant|massive|enormous|vast|immense|grand|substantial)\b/, '🐘'],
    [/\b(small|little|tiny|minor|slight|miniature|modest|slender)\b/, '🐜'],
    [/\b(long|length|cross|span)\b/, '📏'],
    [/\b(short|brief|brief|concise|height)\b/, '📐'],
    [/\b(high|height|tall|elevated|altitude)\b/, '⛰️'],
    [/\b(deep|depth|profound)\b/, '🌊'],
    [/\b(wide|broad|width|extensive)\b/, '↔️'],
    [/\b(narrow|tight)\b/, '↔️'],
    [/\b(heavy|weight|load|mass)\b/, '🏋️'],
    [/\b(light|lighter|lightweight|weightless)\b/, '🪶'],
    [/\b(hot|heat|warm|temperature|thermal|scorching)\b/, '🌡️'],
    [/\b(cold|cool|chilly|freeze|chill)\b/, '🥶'],
    [/\b(wet|moist|damp|humidity|humid|drizzle)\b/, '💦'],
    [/\b(dry|dry|arid|drought)\b/, '🏜️'],
    [/\b(clean|clean|wash|purify|hygiene)\b/, '🧼'],
    [/\b(dirty|mess|polluted|pollution|contaminate)\b/, '💩'],
    [/\b(beautiful|beauty|pretty|gorgeous|elegant|attractive|charm|lovely|handsome)\b/, '🌸'],
    [/\b(ugly|hideous)\b/, '👹'],
    [/\b(rich|wealthy|wealth)\b/, '💰'],
    [/\b(poor|poverty|impoverish)\b/, '🪙'],
    [/\b(free|liberty|freedom|independent|independence)\b/, '🕊️'],
    [/\b(fair|justice|equal|equality|fairness|impartial)\b/, '⚖️'],
    [/\b(correct|right|proper|accurate|accurate|precise|exact)\b/, '✔️'],
    [/\b(wrong|false|error|mistake|bug|incorrect|inaccurate)\b/, '❌'],
    [/\b(true|truth|genuine|authentic|real|fact|honest|sincere)\b/, '💎'],
    [/\b(fake|false|fraud|forgery|counterfeit|deceive|deceit|lie|loyal)/, '🃏'],
    [/\b(beauty|beautiful)\b/, '🌸'],
    [/\b(hard|difficult|tough|challenging|arduous|rigorous)\b/, '🧗'],
    [/\b(easy|simple|easy|effortless|straightforward|facile)\b/, '🟢'],
    [/\b(possible|possibility|possible|feasible)\b/, '🤷'],
    [/\b(impossible|impossibility|impossible)\b/, '🚫'],
    [/\b(sure|certain|definite|confident|convincing|determine)\b/, '🎯'],
    [/\b(uncertain|doubt|doubtful|ambiguous|vague|unclear|hesitant|hesitate)\b/, '🤔'],
    [/\b(together|joint|collaborate|cooperate|cooperation|collective|unite|unity|union|unified)\b/, '🤝'],
    [/\b(separate|apart|divide|div[ie]de|split|distinguish|isolate|segregate)\b/, '✂️'],
    [/\b(best|better|greatest|top|excellent|outstanding|superior|remarkable|exceptional)\b/, '👍'],
    [/\b(worst|terrible|awful|horrible|bad|dreadful)\b/, '💀'],
    [/\b(good|well|fine|great|nice|positive|favorable)\b/, '😊'],
    [/\b(bad|harm|harmful|damage|damage|negative|adverse|detrimental)\b/, '👎'],
    [/\b(agree|agreement|consent|approve|approval|accept)\b/, '👍'],
    [/\b(disagree|disagreement|object|oppose|opposition|reject|refuse|deny)\b/, '👎'],
    [/\b(explain|explain|describe|description|illustrate|define|definition|demonstrate)\b/, '💬'],
    [/\b(discuss|discussion|debate|argue|argument|controversial|dispute|negotiate)\b/, '⚖️'],
    [/\b(believe|belief|faith|opinion|view|perspective|conviction|assume)\b/, '💭'],
    [/\b(doubt)\b/, '❓'],
    [/\b(question|ask|inquiry|query|enquiry)\b/, '❓'],
    [/\b(answer|reply|response|respond|reply)\b/, '🗨️'],
    [/\b(hope|wish|desire|expect|expectation|dream|aspiration|ambition)\b/, '🌠'],
    [/\b(plan|planning|strategy|scheme|arrange|arrangement|schedule|organize|organize)\b/, '📋'],
    [/\b(prepare|preparation|ready|get ready)\b/, '🧳'],
    [/\b(evaluate|evaluation|assessment|assess|appraisal)\b/, '📊'],
  [/\b(test|exam|quiz|score|mark)\b/, '📋'],
    [/\b(school)\b/, '🏫'],
    [/\b(travel|travel|journey|trip|tour|visit|explore|exploration|adventure)\b/, '🧭'],
    [/\b(discover|discovery|find|invent|invention|explore)\b/, '🔍'],
    [/\b(search|look for|seek|hunt)\b/, '🔎'],
    [/\b(show|display|exhibit|present|reveal|demonstrate)\b/, '📽️'],
    [/\b(hide|conceal|cover|secret|disguise)\b/, '🙈'],
    [/\b(wait|await|delay|postpone)\b/, '⏳'],
    [/\b(arrive|arrival|reach|land|depart|departure|leave|set off)\b/, '🛬'],
    [/\b(enter|entry|enter)\b/, '🚪'],
    [/\b(exit|leave|depart|departure)\b/, '🚪'],
    [/\b(return|go back|come back)\b/, '↩️'],
    [/\b(use|usage|utilize|employ|apply|application|adopt)\b/, '🛠️'],
    [/\b(need|require|requirement|demand|necessary|essential)\b/, '🆘'],
    [/\b(want|would like|desire)\b/, '🙏'],
    [/\b(can|could|able|ability|capability)\b/, '💪'],
    [/\b(must|should|ought|oblig|duty|responsible|responsibility)\b/, '📌'],
    [/\b(may|might|perhaps|maybe|probably|likely|possibility)\b/, '🤷'],
    [/\b(always|often|usually|frequently|sometimes|rarely|seldom|never|customary|habit)\b/, '🔁'],
    [/\b(now|today|present|current|recent|modern)\b/, '🕐'],
    [/\b(past|previous|former|last)\b/, '⏪'],
    [/\b(future|upcoming|coming|next|tomorrow)\b/, '🔮'],
    [/\b(early|late|on time|punctual|timely)\b/, '⏰'],
    [/\b(day|daily|daytime)\b/, '🌞'],
    [/\b(night|nighttime|midnight|evening)\b/, '🌙'],
    [/\b(week|month|year|annual|yearly|weekly|monthly|daily)\b/, '📆'],
    [/\b(season|seasonal)\b/, '🍂'],
    [/\b(spring|summer|autumn|winter|fall)\b/, '🍂'],
    [/\b(negative)\b/, '➖'],
    [/\b(positive)\b/, '➕'],
    [/\b(rhetoric|allegory|metaphor|symbolize|symbolic|imagery)\b/, '🎭'],
    [/\b(subtle|nuance|delicate|intricate|elaborate|refined)\b/, '🧵'],
    [/\b(manipulate|manipulation|control|influence|sway|exploit)\b/, '🎮'],
    [/\b(epidemic|pandemic|outbreak|plague|contagious|infectious)\b/, '🦠'],
    [/\b(acknowledge|acknowledgment|admit|concede|recognize|recognize)\b/, '🙋'],
    [/\b(apparent|obvious|evident|evident|manifest|clear)\b/, '👁️'],
    [/\b(bias|prejudice|biased|partial|favoritism)\b/, '🎭'],
    [/\b(concurrent|simultaneous|parallel|coincide|synchronize)\b/, '⏱️'],
    [/\b(consolidate|consolidation|strengthen|reinforce|combine|merge|unify)\b/, '🧱'],
    [/\b(derive|derivation|originate|stem from|obtain from)\b/, '🌱'],
    [/\b(distribute|distribution|allocate|allot|dispense|spread|disseminate)\b/, '📤'],
    [/\b(exclude|exclusion|exclude|omit|eliminate|rule out)\b/, '🚫'],
    [/\b(extract|extraction|remove|withdraw|pull out|elicit)\b/, '🧪'],
    [/\b(formulate|formulation)\b/, '📋'],
  [/\b(define|definition)\b/, '📖'],
  [/\barticulate\b/, '🗣️'],
  [/\bframe\b/, '🖼️'],
  [/\bconceive\b/, '💭'],
  [/\bdevise\b/, '⚙️'],
    [/\b(hierarchy|hierarchical|rank|layered|pyramid)\b/, '🏢'],
    [/\b(incentive|motivation|motivate|stimulus|reward|encourage|encourage)\b/, '🎯'],
    [/\b(incorporate|integrate|include|merge|embody|absorb|blend)\b/, '🧩'],
    [/\b(indicate|indication|suggest|imply|signal|denote|signify|represent)\b/, '💡'],
    [/\b(interpret|interpretation|translate|explain|construe|decode|decipher)\b/, '📖'],
    [/\b(legitimate|legitimacy|valid|justified|lawful|proper|authentic)\b/, '✅'],
    [/\b(mediate|mediation|intervene|arbitrate|negotiate|broker)\b/, '🤝'],
    [/\b(perceive|perception|sense|detect|discern|realize|recognize)\b/, '👁️'],
    [/\b(radical|extreme|drastic|profound|revolutionary|fundamental)\b/, '🔥'],
    [/\b(random|randomly|arbitrary|haphazard|unsystematic)\b/, '🎲'],
    [/\b(react|reaction|respond|reply|feedback|response)\b/, '💥'],
    [/\b(seminar|workshop|conference|symposium|lecture|lecture|tutorial)\b/, '🎓'],
    [/\b(census|survey|poll|statistics|data|statistical|questionnaire)\b/, '📊'],
    [/\b(legislature|legislative|parliament|congress|senate|council|law|statute|policy|regulation)\b/, '🏛️'],
    [/\b(ecosystem|habitat|biodiversity|environment|ecological|sustainable)/, '🌍'],
    [/\b(landfill|waste|garbage|recycle|recycling|disposal|pollutant|emission)\b/, '♻️'],
    [/\b(ozone|atmosphere|greenhouse|carbon|climate|glacier|emission)\b/, '🌫️'],
    [/\b(algorithm|computation|computational|logic|logical|formula|syntax|code)\b/, '🧮'],
    [/\b(database|storage|data|record|archive|memory)\b/, '🗃️'],
    [/\b(virtual|simulate|simulation|digital|artificial|synthetic|simulate|simulation)\b/, '🖥️'],
    [/\b(prototype|model|sample|version|demo|blueprint|framework)\b/, '🧩'],
    [/\b(constitute|constitution|establish|form|compose|comprise|represent)\b/, '🧱'],
    [/\b(constrain|constraint|restrict|restriction|limit|limitation|confine|bound|restrain)\b/, '⛓️'],
    [/\b(culminate|culmination|climax|peak|apex|finalize)\b/, '🏔️'],
    [/\b(degrade|degradation|deteriorate|decline|worsen|deterioration)\b/, '📉'],
    [/\b(deem|consider|regard|treat as|view as)\b/, '🤔'],
    [/\b(deficit|deficiency|shortage|scarcity|lack|insufficient|inadequate)\b/, '📉'],
    [/\b(demolish|demolition|destroy|tear down|raze|dismantle)\b/, '💥'],
    [/\b(depict|depiction|portray|illustrate|picture|characterize)\b/, '🖼️'],
    [/\b(designate|designation|appoint|assign|name|label|categorize)\b/, '🏷️'],
    [/\b(detriment|detrimental|harmful|adverse|damaging|prejudicial)\b/, '👎'],
    [/\b(deviate|deviation|diverge|depart|vary)\b/, '↪️'],
    [/\b(dimension|aspect|factor|element|component|perspective|facets)\b/, '🧊'],
    [/\b(discrepancy|inconsistency|contradiction|mismatch|gap|difference)\b/, '↔️'],
    [/\b(discriminate|discrimination|distinguish|differentiate|segregate)\b/, '⚖️'],
    [/\b(displace|displacement|replace|relocate|substitute|shift)\b/, '🔄'],
    [/\b(disseminate|distribution|spread|propagate|circulate|broadcast)\b/, '📡'],
    [/\b(elicit|evoke|provoke|trigger|generate|prompt|draw out)\b/, '⚡'],
    [/\b(emerge|emergence|appear|arise|surface|come about)\b/, '🌅'],
    [/\b(encompass|include|cover|comprise|embrace|contain|span)\b/, '🌐'],
    [/\b(endorse|endorsement|approve|support|sanction|back|advocate)\b/, '👍'],
    [/\b(enhance|enhancement|improve|boost|amplify|heighten|strengthen)\b/, '⬆️'],
    [/\b(equate|equation|equivalent|equal|compare|correspond)\b/, '⚖️'],
    [/\b(erode|erosion|wear away|corrode|undermine|weaken)\b/, '🌊'],
    [/\b(evaluate|evaluation|assess|appraise|judge|estimate|measure)\b/, '📊'],
    [/\b(evident|evidence|proof|testimony|witness|demonstrate)\b/, '📜'],
    [/\b(exceed|exceed|surpass|outdo|outstrip|go beyond|transcend)\b/, '📈'],
    [/\b(exert|apply|exercise|wield|employ)\b/, '💪'],
    [/\b(expenditure|expense|spending|cost|outlay|consumption)\b/, '💸'],
    [/\b(exploit|exploitation|utilize|leverage|take advantage)\b/, '🛠️'],
    [/\b(extensive|comprehensive|widespread|broad|far-reaching|exhaustive)\b/, '📚'],
    [/\b(facilitate|facilitation|enable|promote|ease|accelerate)\b/, '⚡'],
    [/\b(feature|characteristic|trait|attribute|aspect|quality)\b/, '🏷️'],
    [/\b(fluctuate|fluctuation|wave|vary|vacillate|swing|oscillate)\b/, '📈'],
    [/\b(framework|structure|system|infrastructure|scaffold|setup)\b/, '🏗️'],
    [/\b(fundamental|essential|basic|core|underlying|primary)\b/, '🧱'],
    [/\b(generate|generation|produce|create|yield|bring about)\b/, '⚙️'],
    [/\b(hypothesis|theory|assumption|premise|supposition|postulate)\b/, '💡'],
    [/\b(implement|implementation|execute|carry out|enforce|realize|realize)\b/, '🛠️'],
    [/\b(imply|implication|suggest|insinuate|entail|involve)\b/, '💭'],
    [/\b(incentivize|encourage|motivate|promote|spur|drive)\b/, '🚀'],
    [/\b(inclination|tendency|tend|disposition|propensity|lean|prefer)\b/, '🧭'],
    [/\b(inevitable|unavoidable|certain|inescapable|bound to)\b/, '⏳'],
    [/\b(inherent|intrinsic|innate|natural|innate|inborn)\b/, '🧬'],
    [/\b(inhibit|inhibition|hinder|restrain|suppress|stifle|discourage)\b/, '⛔'],
    [/\b(initiate|initiative|launch|begin|start|kick off|originate)\b/, '🚀'],
    [/\b(innovate|innovation|creative|original|novel|breakthrough)\b/, '💡'],
    [/\b(integral|essential|necessary|essential|vital|indispensable)\b/, '🔗'],
    [/\b(interpret|interpretation|read|understand|make sense|construe)\b/, '📖'],
    [/\b(intricate|complicated|complex|elaborate|detailed|sophisticated)\b/, '🕸️'],
    [/\b(intuition|intuitive|instinct|gut feeling|subconscious)\b/, '🔮'],
    [/\b(investigate|investigation|examine|probe|inquire|inspect|scrutinize)\b/, '🔍'],
    [/\b(justify|justification|warrant|rationale|defend|explain)\b/, '⚖️'],
    [/\b(legislate|legislation|make law|enact|pass|decree)\b/, '📜'],
    [/\b(leverage|utilize|exploit|use|capitalize|benefit)\b/, '⚖️'],
    [/\b(manifest|manifestation|evident|show|demonstrate|reveal|display)\b/, '👁️'],
    [/\b(mechanism|process|method|system|procedure|apparatus)\b/, '⚙️'],
    [/\b(mitigate|mitigation|alleviate|lessen|reduce|ease|relieve)\b/, '💊'],
    [/\b(norm|standard|criterion|benchmark|convention|rule)\b/, '📐'],
    [/\b(notion|concept|idea|thought|belief|perception)\b/, '💭'],
    [/\b(obstacle|barrier|hurdle|impediment|blockage|hindrance)\b/, '🚧'],
    [/\b(optimum|optimal|ideal|best|perfect|most favorable)\b/, '⭐'],
    [/\b(paradigm|model|pattern|framework|example|prototype)\b/, '📐'],
    [/\b(parameter|variable|factor|metric|limit|boundary)\b/, '🎚️'],
    [/\b(phenomenon|event|occurrence|situation)\b/, '💡'],
    [/\b(plausible|credible|believable|reasonable|feasible|sound)\b/, '🤷'],
    [/\b(precede|preceding|prior|previous|former|earlier)\b/, '⏪'],
    [/\b(predominant|dominant|main|primary|principal|prevailing)\b/, '👑'],
    [/\b(preliminary|initial|early|first|introductory|prior)\b/, '1️⃣'],
    [/\b(premise|assumption|proposition|basis|foundation)\b/, '🏗️'],
    [/\b(prescribe|prescription|recommend|direct|order|stipulate)\b/, '💊'],
    [/\b(prevalent|widespread|common|widespread|current|pervasive)\b/, '🌊'],
    [/\b(profound|deep|intense|far-reaching|significant|meaningful)\b/, '🌌'],
    [/\b(prohibit|prohibition|ban|forbid|outlaw|restrict)\b/, '⛔'],
    [/\b(prominent|famous|well-known|notable|distinguished|leading)\b/, '🌟'],
    [/\b(prompt|prompt|trigger|elicit|initiate|induce|cause)\b/, '⚡'],
    [/\b(proportion|ratio|percentage|share|portion|extent)\b/, '📊'],
    [/\b(prospect|outlook|likelihood|expectation|future|chance)\b/, '🔭'],
    [/\b(prudent|wise|sensible|judicious|cautious|careful)\b/, '🧠'],
    [/\b(regulate|regulation|control|govern|manage|supervise|administer)\b/, '🎛️'],
    [/\b(reinforce|strengthen|bolster|support|fortify|consolidate)\b/, '🧱'],
    [/\b(relevant|relevance|pertinent|applicable|related|appropriate)\b/, '🔗'],
    [/\b(reluctant|hesitant|unwilling|averse|resistant)\b/, '🙃'],
    [/\b(remarkable|notable|extraordinary|striking|exceptional|impressive)\b/, '🌟'],
    [/\b(resilient|resilience|tough|adaptable|robust|flexible)\b/, '🌊'],
    [/\b(retrieve|recover|fetch|regain|reclaim|restore)\b/, '📤'],
    [/\b(scrutinize|scrutiny|examine|inspect|audit|review)\b/, '🔎'],
    [/\b(sequence|order|series|succession|chain|arrangement)\b/, '🔢'],
    [/\b(simultaneous|concurrent|at the same time|coincident)\b/, '⏱️'],
    [/\b(sophisticated|advanced|complex|refined|high-tech|intricate)\b/, '🛰️'],
    [/\b(spectrum|range|gamut|variety|continuum)\b/, '🌈'],
    [/\b(spontaneous|impromptu|voluntary|natural|automatic)\b/, '🌀'],
    [/\b(stimulate|stimulus|encourage|prompt|motivate|spur|provoke)\b/, '⚡'],
    [/\b(strategy|strategic|plan|approach|tactic|policy)\b/, '♟️'],
    [/\b(substitute|replacement|alternative|replace|surrogate)\b/, '🔄'],
    [/\b(subtle|understated|delicate|fine|slight)\b/, '🪶'],
    [/\b(sufficient|enough|adequate|ample|satisfactory)\b/, '✅'],
    [/\b(supplement|complement|addition|extra|adjunct)\b/, '➕'],
    [/\b(surpass|exceed|outdo|outshine|transcend|outstrip)\b/, '🏆'],
    [/\b(susceptible|vulnerable|prone|sensitive|exposed)\b/, '🥀'],
    [/\b(sustain|sustainable|maintain|support|uphold|persist)\b/, '♻️'],
    [/\b(tangible|concrete|physical|real|substantial)\b/, '✋'],
    [/\b(transparent|clear|open|obvious|blatant)\b/, '🔎'],
    [/\b(undermine|weaken|sabotage|erode|impair|compromise)\b/, '🕳️'],
    [/\b(undertake|take on|embark|assume|pursue|commit)\b/, '🎒'],
    [/\b(utilize|use|employ|apply|exploit)\b/, '🛠️'],
    [/\b(validate|validation|verify|confirm|substantiate|authenticate)\b/, '✅'],
    [/\b(versatile|adaptable|flexible|all-round|multifaceted)\b/, '🎭'],
    [/\b(vivid|graphic|lively|striking|clear|picturesque)\b/, '🎨'],
    [/\b(whereas|while|although|conversely|however)\b/, '↔️'],
    [/\b(carbon)\b/, '💨'],
    [/\b(nitrogen|oxygen|hydrogen)\b/, '🧪'],
    [/\b(atom|molecule|particle|particle|electron|proton|nucleus)\b/, '⚛️'],
    [/\b(gravity|gravitational|magnetic|magnetism|electric|magnetic field)\b/, '🧲'],
    [/\b(equator|latitude|longitude|hemisphere|tropic|tropic)\b/, '🌐'],
    [/\b(orbit|revolve|rotate|revolution|rotation|spin)\b/, '🪐'],
    [/\b(galaxy|universe|cosmos|cosmic|astronaut|spacecraft|space|planet)\b/, '🌌'],
    [/\b(geology|geological|mineral|rock formation|fossil|dinosaur)\b/, '🪨'],
    [/\b(biology|biological|botany|zoology|species|organism|cell)\b/, '🧬'],
    [/\b(chemistry|chemical|compound|substance|reaction|element)\b/, '⚗️'],
    [/\b(physics|physical|mechanics|velocity|acceleration|momentum|force)\b/, '⚛️'],
    [/\b(mathematics|mathematical|geometry|equation|algebra|calculus|triangle)\b/, '📐'],
    [/\b(statistics|statistical|probability|distribution|correlation|average|mean|median)\b/, '📊'],

    /* ===== 第11轮：中文语义层（多字词枚举，按语义域分组） ===== */
    /* --- 优先级：易被通用词抢走的具体义项 --- */
    [/光滑|平滑|光洁|光滑的|平滑的/, '✨'],
    [/汽油|燃油|柴油|加油站|燃料油/, '⛽'],
    [/节奏|韵律|节拍|节奏感|旋律/, '🎵'],
    [/等级|级别|阶层|层次|上层|下层/, '🪜'],
    [/石头|岩石|石子|石块|石壁|砾石|碎石|巨石/, '🪨'],
    [/尊重|尊敬|敬重|尊严|敬佩|崇敬|敬爱/, '🙏'],
    [/草稿|草案|起草|拟稿|初稿|打草稿/, '✍️'],
    [/专家|行家|能手|专业人员|专家的/, '🎓'],
    [/相信|信任|信赖|诚信|信用|可信/, '🤝'],
    [/相反|反之|对立|矛盾|悖论/, '↔️'],
    [/动物|兽类|哺乳动物|野生动物|宠物|牲畜|家禽|昆虫|鸟类的|兽/, '🐾'],
    [/植物|草木|植被|灌木|作物|草木的|植物学/, '🌿'],
    [/树木|乔木|树干|树枝|树林|森林|木材|林地|植树/, '🌳'],
    [/花朵|鲜花|花卉|花瓣|开花|花丛|花束|花粉|花蜜/, '🌸'],
    [/海洋|大海|海水|海域|海滨|海浪|海底|海岸|海上|海面|海潮|深海|航海/, '🌊'],
    [/河流|河水|江水|溪流|湖泊|湖水|池塘|水池|水流|水域|水源|淡水|咸水|水位|水质|洪水|水灾|泪水|汗水|雨水|供水|排水|污水/, '💧'],
    [/山峰|山脉|山地|山区|山谷|山坡|山顶|山洞|山林|火山|雪山/, '⛰️'],
    [/天气|气候|气象|气温|晴天|阴天|多云/, '🌤️'],
    [/下雨|降雨|暴雨|雷雨|阵雨|雨季|雨量|雨衣|雨点|大雨|小雨|酸雨/, '🌧️'],
    [/下雪|积雪|雪花|冰雪|暴雪|雪崩|雪地|雪堆/, '❄️'],
    [/刮风|微风|大风|狂风|台风|风暴|风力|风向|顺风|逆风|风速|阵风/, '🌬️'],
    [/云层|乌云|云彩|云雾|云朵|云海/, '☁️'],
    [/太阳|阳光|日照|日光|日出|日落|阳光照射/, '☀️'],
    [/月亮|月光|月球|月食|满月/, '🌙'],
    [/星星|星球|恒星|星空|星际|银河|星座|星系|天体/, '⭐'],
    [/火焰|火灾|大火|燃烧|着火|点火|灭火|消防|烈火|野火/, '🔥'],
    [/冰川|结冰|冰冻|冰块|浮冰|冰山|冰雪|冰层|冰河/, '🧊'],
    [/地震|地壳|断层|余震|震级/, '🌋'],
    [/环境|生态|环保|生态学|大自然|自然环境/, '🌱'],
    [/地球|世界|全球|行星|全世界|国际|跨国/, '🌍'],
    [/太空|宇宙|航天|宇宙飞船|卫星|宇航员|外太空/, '🚀'],
    [/人类|个人|某人|人们|人物|人士|人口|人群|某人/, '👤'],
    [/社会|社区|社群|社会的|公共的|公众/, '👥'],
    [/家庭|家人|亲属|亲戚|父母|婚姻|家务|家园/, '👨‍👩‍👧'],
    [/儿童|孩子|小孩|少年|青少年|婴儿|幼儿|未成年/, '🧒'],
    [/老人|老年|年长|长者|长辈|老龄化/, '👴'],
    [/男性|男子|雄性|男人/, '👨'],
    [/女性|女子|雌性|女人/, '👩'],
    [/国家|民族|国民|国度|祖国的/, '🏳️'],
    [/政府|政治|政党|国会|议会|选举|投票|民主|部长|首相|总统|官员|官方|行政/, '🏛️'],
    [/法律|法规|合法|非法|律师|法庭|法官|判决|司法|诉讼|立法|宪法|条例|犯罪|罪行|违法|合规/, '⚖️'],
    [/战争|军事|军队|陆军|海军|部队|士兵|武器|子弹|导弹|爆炸|战斗|作战|侵略|占领|国防/, '⚔️'],
    [/警察|警方|治安|逮捕|监狱|囚犯|惩罚|处罚|罚款|判刑|治安的/, '🚓'],
    [/宗教|上帝|教堂|寺庙|礼拜|祈祷|信仰|神圣|佛教|基督教|伊斯兰|神明|神灵|神学/, '🛐'],
    [/文化|传统|习俗|惯例|遗产|民俗|仪式|典礼|节日/, '🎎'],
    [/工作|职业|就业|失业|雇员|雇主|员工|劳动|劳动力|岗位|职位|职场|职业的/, '💼'],
    [/公司|企业|厂商|商号|集团|公司/, '🏢'],
    [/商业|贸易|生意|商人|市场|营销|销售|零售|批发|品牌|广告|顾客|客户|消费者|经商/, '🛒'],
    [/金钱|货币|现金|资金|资本|金融|财政|收入|工资|薪水|薪酬|报酬|利润|预算|成本|费用|价格|收费|账单|债务|税收|税|经济|财务/, '💰'],
    [/银行|借贷|贷款|抵押|存款|储蓄|账户|信贷/, '🏦'],
    [/保险|投保|承保|保费|保单/, '🛡️'],
    [/工业|工厂|制造业|生产线|产业|加工|工业化的/, '🏭'],
    [/农业|农场|耕种|耕作|农作物|庄稼|播种|收割|施肥|灌溉|田园/, '🌾'],
    [/技术|科技|数字化|设备|机器|机械|工程|工程师|自动化|软件|硬件|编程|人工智能|机器人/, '⚙️'],
    [/医学|医疗|医院|医生|护士|疾病|病人|治疗|疗法|药物|药品|手术|康复|健康|卫生|症状|诊断|药业/, '🏥'],
    [/教育|教学|教师|学生|学校|大学|学院|课程|学位|学术|学习|培训|校园|学费|入学|毕业|教育学/, '🏫'],
    [/语言|言语|语法|词汇|口音|翻译|方言|演讲|语文|语言的/, '💬'],
    [/文学|小说|诗歌|戏剧|散文|作家|诗人|叙事|文学作品/, '📖'],
    [/艺术|美术|绘画|雕塑|音乐|乐器|舞蹈|表演|音乐会|展览|博物馆|画廊|设计|创意|绘画的/, '🎨'],
    [/媒体|新闻|记者|报纸|杂志|报道|广播|电视|电台|频道|节目|出版|传媒/, '📰'],
    [/体育|运动|锻炼|健身|运动员|比赛|竞赛|赛事|球队|球类|田径|游泳|跑步|竞技/, '🏅'],
    [/旅行|旅游|旅程|游客|观光|远足|跋涉|旅途/, '🧭'],
    [/研究|实验|调查|分析|考察|探索|发现|证据|证明|数据|统计|科研|实验室|研究方法/, '🔬'],
    [/重要|关键|重大|核心|主要|首要|至关重要|显著|重要性/, '⭐'],
    [/巨大|庞大|宏大|大型|大规模|庞大/, '🐘'],
    [/微小|细小|细微|极小|微量|微小的/, '🔍'],
    [/大量|众多|许多|大量地|大量的|数量|数额|数目|总量|总数|数字|统计数据/, '🔢'],
    [/增加|增长|上升|提高|提升|扩大|扩张|加剧|增强|涨幅|激增/, '📈'],
    [/减少|下降|降低|缩减|缩小|减退|削减|减轻|减弱|滑坡|萎缩/, '📉'],
    [/快速|迅速|急速|加速|飞快|高速|快捷|快速(?!餐)/, '⚡'],
    [/缓慢|迟缓|减速|慢速|逐渐|缓慢的/, '🐢'],
    [/强大|强烈|剧烈|激烈|有力|坚强|加强|强化|强劲|强(?!迫|制|调|烈|大|奸|盗)/, '💪'],
    [/虚弱|微弱|脆弱|软弱|削弱|脆弱的/, '🥀'],
    [/困难|艰难|棘手|艰苦|困境|艰险/, '🧗'],
    [/简单|容易|简易|轻松|简单的|容易地/, '🟢'],
    [/良好|优秀|有益|有利|积极|优质|优良的|出色的|极佳/, '👍'],
    [/糟糕|有害|不利|负面|消极|恶劣|不良|有害的/, '👎'],
    [/新的|新鲜|创新|新颖|更新|崭新|新近|全新|新式的/, '🆕'],
    [/旧的|古老|古代|过时|老化|古董|古典|陈旧/, '🏺'],
    [/开始|起始|启动|发起|起源|开端|起初|开头|初始化/, '🚀'],
    [/结束|终止|终结|完结|落幕|最终|终止符|完毕/, '🏁'],
    [/变化|改变|转变|变革|演变|转换|改造|改革|变迁/, '🔄'],
    [/原因|起因|根源|引起|归因|由于|诱因/, '🔗'],
    [/结果|后果|结局|成果|成效|产出/, '🏁'],
    [/影响|作用|效果|冲击|效应/, '💫'],
    [/问题|难题|疑问|质疑|困惑|麻烦|缺陷|缺点|弊端|隐患/, '❓'],
    [/解决|应对|措施|方案|办法|答案|解答|修复|补救|对策/, '🔧'],
    [/目标|目的|指标|意图|瞄准|追求|宗旨|目的性/, '🎯'],
    [/计划|规划|安排|部署|策略|战略|策划|日程|计划性/, '📋'],
    [/时间|时期|阶段|时代|期间|期限|持续|短暂|漫长|时刻|瞬间|年代/, '⏳'],
    [/部分|组成|成分|要素|元素|组件|局部|组成部分/, '🧩'],
    [/系统|体系|结构|框架|机制|制度|体制|系统性/, '⚙️'],
    [/方法|方式|途径|手段|技巧|手法|做法|方法论/, '🛠️'],
    [/能力|才能|技能|本领|潜力|能够|有能力/, '💪'],
    [/思想|想法|概念|观念|观点|思考|思维|看法|见解|信念|理论|哲学|逻辑|理性|意识|认知|理念/, '💭'],
    [/知识|学问|学识|理解|了解|明白|知道|知晓/, '🧠'],
    [/情感|感情|情绪|感觉|心情|感受|喜爱|热爱|喜欢|爱|亲密/, '❤️'],
    [/生气|愤怒|恼怒|气愤|激怒|发火|怒火|愤慨/, '😠'],
    [/悲伤|难过|痛苦|悲哀|忧伤|哭泣|流泪|沮丧|失望|悲痛/, '😢'],
    [/害怕|恐惧|惊恐|恐慌|畏惧|担心|担忧|焦虑|紧张|压力/, '😰'],
    [/高兴|快乐|愉快|开心|喜悦|兴奋|乐观|满意|满足|欢乐/, '😄'],
    [/惊讶|吃惊|震惊|惊奇|意外|出乎意料|不可思议/, '😲'],
    [/讨厌|厌恶|憎恨|反感|憎恶|不满|怨恨|仇恨/, '😖'],
    [/美丽|漂亮|优美|美观|魅力|迷人|壮丽|优雅|美观的/, '🌺'],
    [/丑陋|难看|丑恶|丑的/, '🙈'],
    [/干净|清洁|洁净|整洁|卫生|清洗|打扫/, '🧼'],
    [/肮脏|污秽|污染|弄脏|垃圾|废物|废弃|污垢|雾霾/, '🗑️'],
    [/真实|确实|真正的|真实性|真实的|真诚的/, '✅'],
    [/虚假|伪造|假装|欺骗|谎言|假冒|假的|虚伪/, '🚫'],
    [/危险|风险|冒险|威胁|危害|危机|风险性/, '⚠️'],
    [/安全|保护|防护|保安|平安|救援|拯救|保存|守护|保障/, '🛡️'],
    [/破坏|损害|摧毁|毁坏|伤害|损坏|摧毁|毁灭|破坏性/, '💥'],
    [/帮助|援助|协助|支持|支援|救济|帮忙|有助于/, '🤝'],
    [/合作|协作|配合|协同|共同|联合|联手|团队合作/, '🤝'],
    [/竞争|对抗|争夺|对手|竞争者|竞赛的/, '🥇'],
    [/成功|成就|胜利|获胜|达成|实现|完成|圆满/, '🏆'],
    [/失败|失利|落败|挫折|失败者|落空/, '❌'],
    [/努力|勤奋|刻苦|尽力|奋斗|勤勉|用功/, '💪'],
    [/交流|沟通|对话|讨论|谈判|商议|交谈|表达|说明|解释|描述|宣布|声明|评论|回应|回答|提问|讲话|说话/, '💬'],
    [/同意|赞成|认可|批准|接受|赞同|拥护/, '👍'],
    [/反对|拒绝|抵制|驳斥|否认|异议|反抗|抵抗/, '👎'],
    [/控制|支配|管理|统治|掌控|抑制|限制|约束|管制|调控/, '🕹️'],
    [/自由|解放|独立|自主|释放|独立自主/, '🕊️'],
    [/规则|规范|标准|准则|原则|规定|常规|惯例|规章|规矩|规格/, '📏'],
    [/相同|同样|一致|相等|平等|相似|类似|类同|近似|相仿|类似的/, '🔗'],
    [/不同|差异|区别|相反|对立|矛盾|冲突|对比|差异性/, '↔️'],
    [/正确|准确|精确|无误|正确的|对的/, '✅'],
    [/错误|失误|不正确|谬误|差错|错误地/, '❌'],
    [/可能|可能性|也许|或许|大概|或许|概率/, '🎲'],
    [/必然|肯定|确定|一定|不可避免|必定/, '💯'],
    [/特殊|特别|尤其|独特|特有|专门|独特的|特殊性/, '✨'],
    [/普遍|广泛|普及|全球性|国际的/, '🌐'],
    [/普通|一般|常见|通常|平常|寻常|一般的/, '🔘'],
    [/明显|显著|显然|清楚|清晰|明确|显而易见/, '🔎'],
    [/模糊|含糊|隐晦|朦胧|不清楚|模糊的/, '🌫️'],
    [/秘密|隐秘|隐藏|保密|私下|暗中|偷偷/, '🤫'],
    [/公开|公布|透明|披露|公开化|公示/, '📢'],
    [/权力|权威|势力|统治权|王权/, '👑'],
    [/富裕|富有|财富|财富的|富裕的|奢华|奢侈/, '💎'],
    [/贫穷|贫困|赤贫|贫困的|贫民/, '🏚️'],
    [/城市|都市|城镇|市区|城市的|城市化/, '🏙️'],
    [/农村|乡村|乡下|农村的|农田|村民/, '🚜'],
    [/地区|区域|地方|地域|地带|场所|地点|位置|场地|区域/, '🗺️'],
    [/建筑|建筑物|大楼|楼房|建造|施工|修建|盖房|竣工|建筑工程/, '🏗️'],
    [/房子|房屋|住宅|住房|住所|居所|家居|住户/, '🏠'],
    [/道路|公路|街道|路径|路线|通道|街道|人行道|小路/, '🛣️'],
    [/桥梁|天桥|桥(?!牌|梁)/, '🌉'],
    [/汽车|车辆|轿车|卡车|巴士|公交|出租车|自行车|摩托车|交通|驾驶|开车|停车/, '🚗'],
    [/火车|铁路|轨道|地铁|列车|轨道交通/, '🚆'],
    [/轮船|船只|船舶|航海|港口|码头|船舶|航海的|舰队/, '🚢'],
    [/飞机|航空|飞行|机场|航班|飞行员|航线|飞机场|乘坐飞机/, '✈️'],
    [/食物|食品|饮食|营养|膳食|美味|餐食|进食|饲养|喂养/, '🍽️'],
    [/衣服|服装|衣着|穿戴|衣物|服饰|时尚|布料|纺织/, '👕'],
    [/颜色|色彩|红色|蓝色|绿色|黄色|黑色|白色|彩色|颜色的/, '🎨'],
    [/身体|躯体|肉体|身体的|生理|身体的/, '🧍'],
    [/头部|脑袋|额头|头顶|头部/, '🧠'],
    [/眼睛|视觉|视力|目光|注视|观看|观察|看见|眼球/, '👁️'],
    [/耳朵|听力|听觉|聆听|听见|耳朵的/, '👂'],
    [/手指|手掌|手臂|用手|手动|手工|手势|手写的/, '✋'],
    [/脚步|腿部|脚部|脚趾|赤脚|步行|走路|行走|腿部/, '🦶'],
    [/心脏|心理|内心|心态|心脏病|心理的/, '❤️'],
    [/血液|流血|出血|血液的/, '🩸'],
    [/大脑|头脑|智力|智能|智慧|聪明|智商|脑力/, '🧠'],
    [/声音|声响|噪音|响声|发声|音量|吵闹|喧闹|喧哗/, '🔊'],
    [/安静|寂静|沉默|无声|静音|宁静/, '🔇'],
    [/光线|照明|发光|明亮|光亮|灯光|强光|微光|光泽|照明的/, '💡'],
    [/黑暗|阴暗|昏暗|漆黑|阴影|暗处|暗的/, '🌑'],
    [/电力|电流|电压|电池|电路|电子|电器|电动|发电|用电/, '⚡'],
    [/能源|能量|动力|燃料|石油|煤炭|天然气|太阳能|核能|电能/, '🔋'],
    [/草稿|草案|起草|拟稿|初稿/, '✍️'],
    [/传播|传递|传送|散播|播送|传输/, '📡'],
    [/排放|排出|废气|尾气|散发|释放气体/, '💨'],
    [/地形|地貌|地势|地形/, '🗺️'],
    [/疫苗|接种|免疫|防疫/, '💉'],
    [/自治|自治的|自治权/, '🕊️'],
    [/断言|宣称|声称|主张|宣称/, '🗣️'],
    [/吞并|兼并|并吞|合并领土/, '➕'],
    [/类别|类型|种类|分类|范畴|门类|流派|体裁/, '🗂️'],
    [/背景|语境|上下文|环境背景|背景的/, '🖼️'],
    [/强调|着重|重视|突出|凸显/, '📣'],
    [/亮点|精彩部分|高潮|最精彩/, '✨'],
    [/执照|许可证|许可|授权|执照/, '📜'],
    [/克服|战胜|克制|克服的/, '🧗'],
    [/平台|站台|讲台|月台/, '🖥️'],
    [/重复|反复|重做|重申|复述|重复地/, '🔁'],
    [/规模|范围|尺度|比例|刻度/, '📏'],
    [/严格|严厉|严谨|严苛|严密的|严谨的/, '🧐'],
    [/对称|对称性|对称的/, '🪞'],
    [/运输|运送|输送|货运|运输业|托运/, '🚚'],
    [/美德|品德|道德|伦理|道义|道德规范/, '😇'],
    [/事故|车祸|交通事故|碰车/, '🚧'],
    [/灾难|灾害|灾祸|灾情|灾难性|厄运|不幸/, '🌪️'],
    [/难民|流民|避难|避难所/, '🧳'],
    [/小溪|小河|溪水|山涧/, '🏞️'],
    [/淤泥|泥沙|泥浆|泥沙层/, '🪨'],
    [/采摘|摘取|摘下|采集|采集的/, '✋'],
    [/弯曲|卷曲|盘绕|弯曲的|弯折/, '🌀'],
    [/乌鸦|公鸡|啼叫|鸟叫/, '🐦'],
    [/牧羊人|羊倌|牧民|放牧|牧(?!师|草)/, '👨‍🌾'],
    [/触须|触角|天线/, '📡'],
    [/百科全书|百科|全书/, '📚'],
    [/幻想|想象|想象产物|空想|幻象/, '💭'],
    [/怀旧|念旧|怀念|乡愁/, '🕰️'],
    [/短语|词组|惯用语|习语|成语|措辞/, '💬'],
    [/双关语|俏皮话|文字游戏/, '😜'],
    [/乐队|乐团|一伙|一群人|一群/, '🎵'],
    [/东西|物品|物件|实物|用品/, '📦'],
    [/被子|被褥|羽绒被|毯子|毛毯/, '🛏️'],
    [/墨水|油墨|墨汁/, '🖋️'],
    [/真空|真空的|真空吸尘器/, '🕳️'],
    [/纽扣|扣子|按钮|按键|键/, '🔘'],
    [/丝带|绸带|绶带|勋带|缎带/, '🎀'],
    [/菜单|菜肴|饭菜|食谱/, '🍽️'],
    [/萝卜|芜菁|胡萝卜|块根/, '🥕'],
    [/馅饼|果馅饼|肉馅饼|派的/, '🥧'],
    [/牙龈|牙床|牙齿|牙|拔牙/, '🦷'],
    [/楼梯|阶梯|梯级|台阶|梯子/, '🪜'],
    [/房间|室|客房|屋子|卧室/, '🚪'],
    [/表面|外表|外观|外貌|表面的/, '🎭'],
    [/撞车|坠毁|猛撞|碰撞|撞击|撞/, '💥'],
    [/包裹|包装|包装盒|包装袋|小包/, '📦'],
    [/亚洲|欧洲|美洲|大洋洲|非洲|拉丁美洲/, '🌍'],
    [/租约|租契|租赁|租用|出租|租金/, '📄'],
    [/偿还|付还|还款|清偿/, '💰'],
    [/贼|小偷|偷窃|盗窃|窃贼|扒手/, '🦹'],
    [/转向|偏斜|偏转|使转向/, '↩️'],
    [/暂停|停顿|中止|暂停键/, '⏸️'],
    [/继承人|子嗣|接班人|继承|遗产继承/, '🧬'],
    [/女仆|女佣|佣人|仆人|侍女/, '🧹'],
    [/委员会|理事会|委员会的/, '🏛️'],
    [/咒骂|诅咒|发誓|起誓|宣誓/, '🤬'],
    [/挠|抓破|划破|搔|抓伤/, '🖐️'],
    [/定罪|宣判|有罪|罪名/, '⚖️'],
    [/借口|托词|辩解|正当理由/, '💬'],
    [/脸颊|面颊|脸|面颊的/, '😊'],
    [/肋骨|排骨|骨骼|骨头|骨架/, '🦴'],
    [/小睡|打盹|打瞌睡|瞌睡|午睡/, '😴'],
    [/检查|核对|查看|查询|审查|核查|检验/, '🔍'],
    [/感激|感谢|感恩|感激之情/, '🙏'],
    [/笨拙|不灵活|笨拙的|手脚笨拙/, '🤷'],
    [/活动|行动|行为|举动|活动/, '🎬'],
    [/表示|表明|意味着|意味着|意指|表示的/, '💡'],
    [/使用|利用|运用|应用|采用|使用的/, '🛠️'],
    [/移动|搬动|迁移|搬迁|挪动/, '🚶'],
    [/严重|严峻|严重的|重症/, '🚨'],
    [/液体|流体|液态|液态的|液体的/, '💧'],
    [/装饰|装饰品|点缀|装饰的|装饰物/, '🎀'],
    [/突然|忽然|骤然|猛然|突然的/, '⚡'],
    [/事件|事情|事变|事件/, '📌'],
    [/材料|原料|物质|材质|材料的/, '🧱'],
    [/模型|模式|模范|模型的|建模/, '📐'],
    [/中心|中央|中部|中心的|中央的/, '🎯'],
    [/上级|下级|等级|级别|阶层|层次/, '🪜'],
    [/倾向|趋势|趋向|潮流|趋势的/, '📈'],
    [/深度|深度的|深的|深层/, '🕳️'],
    [/边缘|边界|边界的|边缘的|边际/, '📐'],
    [/邻居|邻近|附近的|邻近的|邻接/, '🏘️'],
    [/运气|幸运|侥幸|运气好|好运/, '🍀'],
    [/名声|声誉|名望|声望|名誉|威望/, '🌟'],
    [/习惯|习性|习惯于|习惯性/, '🔁'],
    [/责任|义务|职责|负责|责任心/, '📌'],
    [/证据|证明|证词|佐证|凭证/, '🔏'],
    [/会议|大会|集会|会场|峰会/, '🪑'],
    [/报告|报道|简报|汇报/, '📄'],
    [/信件|信函|书信|函件|来函/, '✉️'],
    [/礼物|礼品|赠送|赠品|馈赠/, '🎁'],
    [/武器|兵器|军械|武装/, '🔫'],
    /* ===== 第14轮第四批：剩余兜底词逐个精准配图 ===== */
    [/\bcasino\b/, '🎰'],
    [/\bclerk\b/, '💼'],
    [/\binterview\b/, '🎤'],
    [/\bdismiss\b/, '🚪'],
    [/\bsack\b/, '🛍️'],
    [/\boversee\b/, '👁'],
    [/\bstack\b/, '📚'],
    [/\bbundle\b/, '📦'],
    [/\brub\b/, '✋'],
    [/\bbar\b/, '🍺'],
    [/\btest\b/, '📋'],
    [/\bstationery\b/, '✏️'],
    [/\brod\b/, '🎣'],
    [/\btile\b/, '🧱'],
    [/\bhook\b/, '🧷'],
    [/\bcrane\b/, '🏗'],
    [/\bweld\b/, '🔧'],
    [/\bsaw\b/, '🛠'],
    [/\bscrew\b/, '🔩'],
    [/\bdrill\b/, '🔧'],
    [/\bgrid\b/, '🔲'],
    [/\bporch\b/, '🚪'],
    [/\bstorey\b/, '🏢'],
    [/\bbeam\b/, '🏗'],
    [/\barch\b/, '⛪'],
    [/\bcabinet\b/, '🗄'],
    [/\bbalcony\b/, '🫴'],
    [/\bbath\b/, '🛁'],
    [/\bbasin\b/, '🚰'],
    [/\bairtight\b/, '🔒'],
    [/\bmason\b/, '🧱'],
    [/\bvilla\b/, '🏡'],
    [/\bhostel\b/, '🏨'],
    [/\bcabin\b/, '🏕'],
    [/\bcradle\b/, '👶'],
    [/\bvoid\b/, '🕳'],
    [/\bhaunt\b/, '👻'],
    [/\bditch\b/, '🚧'],
    [/\bsauce\b/, '🥫'],
    [/\bketchup\b/, '🍅'],
    [/\bperfume\b/, '🧴'],
    [/\bbake\b/, '🍞'],
    [/\bfry\b/, '🍳'],
    [/\bsuck\b/, '🥤'],
    [/\bsoak\b/, '💧'],
    [/\bgrind\b/, '☕'],
    [/\bvisa\b/, '🛂'],
    [/\bparachute\b/, '☂️'],
    [/\bcarry[ -]on\b/, '🧳'],
    [/\batlas\b/, '🗺'],
    [/\bavenue\b/, '🛣'],
    [/\bsignpost\b/, '🚏'],
    [/\bvan\b/, '🚐'],
    [/\bcart\b/, '🛒'],
    [/\bferry\b/, '⛴️'],
    [/\braft\b/, '🛶'],
    [/\bcanoe\b/, '🛶'],
    [/\boar\b/, '🚣'],
    [/\bturbine\b/, '⚙️'],
    [/\bunderground\b/, '🚇'],
    [/\btire\b/, '😪'],
    [/\bdiscount\b/, '🏷'],
    [/\bcoupon\b/, '🎟'],
    [/\bswap\b/, '🔄'],
    [/\bbid\b/, '💰'],
    [/\bdump\b/, '🗑'],
    [/\bcheque\b/, '💳'],
    [/\bcheap\b/, '💸'],
    [/\bearn\b/, '💰'],
    [/\bloss\b/, '📉'],
    [/\bjust\b/, '✔️'],
    [/\bcomplain\b/, '😤'],
    [/\brob\b/, '🦹'],
    [/\bsuicide\b/, '🆘'],
    [/\bfraud\b/, '🎭'],
    [/\bliar\b/, '🤥'],
    [/\bconfess\b/, '🗣'],
    [/\bcopyright\b/, '📜'],
    [/\bexpire\b/, '⌛'],
    [/\bstamp\b/, '📮'],
    [/\bbind\b/, '🔗'],
    [/\bcommand\b/, '📢'],
    [/\bbombard\b/, '💣'],
    [/\bcannon\b/, '💣'],
    [/\bpistol\b/, '🔫'],
    [/\brifle\b/, '🔫'],
    [/\bblade\b/, '🔪'],
    [/\bsword\b/, '⚔️'],
    [/\bbow\b/, '🙇'],
    [/\barrow\b/, '🏹'],
    [/\bspear\b/, '🔱'],
    [/\bpunch\b/, '👊'],
    [/\bfamine\b/, '🍂'],
    [/\bstarve\b/, '🍽'],
    [/\boffend\b/, '😠'],
    [/\bintrude\b/, '🚷'],
    [/\battack\b/, '⚔️'],
    [/\boppress\b/, '⛓️'],
    [/\bbetray\b/, '🗡'],
    [/\btreason\b/, '⚖️'],
    [/\bblame\b/, '👉'],
    [/\breproach\b/, '💬'],
    [/\bturmoil\b/, '🌪'],
    [/\bcomfort\b/, '🛋'],
    [/\bdevil\b/, '😈'],
    [/\bhang\b/, '🖼'],
    [/\btomb\b/, '⚰️'],
    [/\btorture\b/, '😖'],
    [/\bescape\b/, '🏃'],
    [/\bforgo\b/, '🙅'],
    [/\bdiscard\b/, '🗑'],
    [/\btablet\b/, '💊'],
    [/\bpatrol\b/, '🚓'],
    [/\bburrow\b/, '🕳'],
    [/\bveteran\b/, '🎖'],
    [/\bcaptain\b/, '🧢'],
    [/\bcrush\b/, '🗜'],
    [/\bcolony\b/, '🏛'],
    [/\blatin\b/, '🏛'],
    [/\broman\b/, '🏛'],
    [/\bsoviet\b/, '🏛'],
    [/\bjewish\b/, '✡️'],
    [/\bswiss\b/, '🇨🇭'],
    [/\bgreek\b/, '🇬🇷'],
    [/\baustralia\b/, '🇦🇺'],
    [/\bgermany\b/, '🇩🇪'],
    [/\bharmony\b/, '🎵'],
    [/\bflourish\b/, '🌱'],
    [/\bpuppet\b/, '🎎'],
    [/\bwreath\b/, '💐'],
    [/\bcorpus\b/, '📚'],
    [/\bsurname\b/, '🏷'],
    [/\bcouple\b/, '👫'],
    [/\bspouse\b/, '💑'],
    [/\bhusband\b/, '👨'],
    [/\bgay\b/, '🌈'],
    [/\bnephew\b/, '👦'],
    [/\bniece\b/, '👧'],
    [/\bembryo\b/, '👶'],
    [/\borphan\b/, '🧒'],
    [/\bhostess\b/, '👩'],
    [/\blandlady\b/, '👩'],
    [/\bhost\b/, '🏠'],
    [/\bguest\b/, '👥'],
    [/\bchase\b/, '🏃'],
    [/\bmarry\b/, '💍'],
    [/\bhoneymoon\b/, '🏝'],
    [/\bkiss\b/, '💋'],
    [/\bsingle\b/, '1️⃣'],
    [/\beach\b/, '🔢'],
    [/\bhero\b/, '🦸'],
    [/\bheroine\b/, '👸'],
    [/\bhaircut\b/, '💇'],
    [/\bfisherman\b/, '🎣'],
    [/\bbeggar\b/, '🙏'],
    [/\bcoward\b/, '😱'],
    [/\bmow\b/, '🌿'],
    [/\bstare\b/, '👀'],
    [/\bvow\b/, '💍'],
    [/\bwhistle\b/, '😗'],
    [/\bscold\b/, '🗯'],
    [/\bmock\b/, '😏'],
    [/\bhug\b/, '🤗'],
    [/\bkneel\b/, '🧎'],
    [/\bcatch\b/, '🤲'],
    [/\bsnatch\b/, '✋'],
    [/\bgrab\b/, '👊'],
    [/\bscrape\b/, '🧽'],
    [/\bwhirl\b/, '🌀'],
    [/\binsert\b/, '📥'],
    [/\bobsess\b/, '💫'],
    [/\bmarvel\b/, '✨'],
    [/\bexpel\b/, '🚫'],
    [/\bflee\b/, '🏃'],
    [/\brevenge\b/, '⚔️'],
    [/\bkidnap\b/, '🚐'],
    [/\bimpede\b/, '🚧'],
    [/\bbait\b/, '🐟'],
    [/\bdetach\b/, '✂️'],
    [/\baspire\b/, '🎯'],
    [/\bitch\b/, '🦟'],
    [/\breplenish\b/, '🔄'],
    [/\bleak\b/, '💧'],
    [/\bimpart\b/, '📤'],
    [/\bdrop\b/, '💧'],
    [/\bwelcome\b/, '👋'],
    [/\bgreet\b/, '👋'],
    [/\bfarewell\b/, '👋'],
    [/\brecollect\b/, '💭'],
    [/\bretrospect\b/, '🔙'],
    [/\bsideways\b/, '↔️'],
    [/\bforehead\b/, '🤦'],
    [/\bbrow\b/, '🤨'],
    [/\beyelash\b/, '👁'],
    [/\bmouth\b/, '👄'],
    [/\bthroat\b/, '🗣'],
    [/\bchin\b/, '👇'],
    [/\bjaw\b/, '😬'],
    [/\bbeard\b/, '🧔'],
    [/\belbow\b/, '💪'],
    [/\bchest\b/, '🎽'],
    [/\bstomach\b/, '🤢'],
    [/\bwomb\b/, '🤰'],
    [/\blung\b/, '🌬'],
    [/\bgland\b/, '🧬'],
    [/\bankle\b/, '🦶'],
    [/\bheel\b/, '🦶'],
    [/\bmuscle\b/, '💪'],
    [/\bnerve\b/, '🧠'],
    [/\bhormone\b/, '💉'],
    [/\bawake\b/, '⏰'],
    [/\byawn\b/, '🥱'],
    [/\bdwarf\b/, '🤏'],
    [/\bpregnancy\b/, '🤰'],
    [/\bborn\b/, '👶'],
    [/\bmoan\b/, '😖'],
    [/\bdiabetes\b/, '🩸'],
    [/\boverweight\b/, '⚖️'],
    [/\binsomnia\b/, '🛌'],
    [/\barthritis\b/, '🦴'],
    [/\bpimple\b/, '🤕'],
    [/\bchoke\b/, '😵'],
    [/\bscar\b/, '🩹'],
    [/\bquarantine\b/, '🏥'],
    [/\bpill\b/, '💊'],
    [/\bmorphine\b/, '💉'],
    [/\bdose\b/, '💊'],
    [/\bfun\b/, '🎉'],
    [/\bpolite\b/, '😊'],
    [/\bapology\b/, '🙏'],
    [/\badmire\b/, '⭐'],
    [/\bsteadfast\b/, '⛰️'],
    [/\bmundane\b/, '😑'],
    [/\bbare\b/, '⬜'],
    [/\bagony\b/, '😖'],
    [/\bmourn\b/, '🕯'],
    [/\bharass\b/, '😤'],
    [/\bselfish\b/, '🙄'],
    [/\bunkind\b/, '😒'],
    [/\bregret\b/, '😔'],
    [/\bsigh\b/, '💨'],
    [/\bstupid\b/, '🤪'],
    [/\bgreedy\b/, '🤑'],
    [/\bcentury\b/, '📅'],
    [/\bmillennium\b/, '🎊'],
    [/\bmillion\b/, '💵'],
    [/\bbillion\b/, '💰'],
    [/\bmidday\b/, '🕛'],
    [/\bregular\b/, '🔁'],
    [/\boverdue\b/, '⏰'],
    /* ===== 第14轮第三批：具体名词逐个精准配图 ===== */
    [/\bbeak\b/, '🐦'],
    [/\bmosquito\b/, '🦟'],
    [/\bcamel\b/, '🐫'],
    [/\bpanda\b/, '🐼'],
    [/\bhorn\b/, '📯'],
    [/\bwolf\b/, '🐺'],
    [/\bdragon\b/, '🐉'],
    [/\bfox\b/, '🦊'],
    [/\bcalf\b/, '🐄'],
    [/\bpup\b/, '🐶'],
    [/\bbuffalo\b/, '🐃'],
    [/\bzebra\b/, '🦓'],
    [/\bdonkey\b/, '🐴'],
    [/\bfalcon\b/, '🦅'],
    [/\bhawk\b/, '🦅'],
    [/\bgoose\b/, '🦆'],
    [/\bsquirrel\b/, '🐿'],
    [/\bbite\b/, '🦷'],
    [/\bbark\b/, '🐕'],
    [/\btame\b/, '🐕'],
    [/\balga\b/, '🌿'],
    [/\bbud\b/, '🌱'],
    [/\bhay\b/, '🌾'],
    [/\bstraw\b/, '🥤'],
    [/\bviolet\b/, '🟣'],
    [/\bmint\b/, '🌿'],
    [/\bpea\b/, '🫛'],
    [/\bpear\b/, '🍐'],
    [/\bkiwi\b/, '🥝'],
    [/\bberry\b/, '🍓'],
    [/\bpapaya\b/, '🥭'],
    [/\bflour\b/, '🌾'],
    [/\bporridge\b/, '🥣'],
    [/\bpaste\b/, '🧴'],
    [/\bturkey\b/, '🦃'],
    [/\bmutton\b/, '🍖'],
    [/\bcream\b/, '🥛'],
    [/\bjam\b/, '🍯'],
    [/\bvanilla\b/, '🍨'],
    [/\bscallion\b/, '🧅'],
    [/\bvinegar\b/, '🍶'],
    [/\bflavour\b/, '🍽'],
    [/\bsour\b/, '🍋'],
    [/\bthirsty\b/, '🥤'],
    [/\blime\b/, '🍋'],
    [/\bacid\b/, '🍋'],
    [/\bprotein\b/, '🍗'],
    [/\bvitamin\b/, '💊'],
    [/\bdevour\b/, '🍽'],
    [/\bcafeteria\b/, '🍽'],
    [/\bbuffet\b/, '🍽'],
    [/\bbarbecue\b/, '🍖'],
    [/\bbanquet\b/, '🍽'],
    [/\bsnack\b/, '🍿'],
    [/\bgourmet\b/, '👨'],
    [/\bporcelain\b/, '🍽'],
    [/\bkettle\b/, '🫖'],
    [/\bpan\b/, '🍳'],
    [/\bstove\b/, '🔥'],
    [/\bfurnace\b/, '🔥'],
    [/\blid\b/, '🫙'],
    [/\bsoda\b/, '🥤'],
    [/\bbrandy\b/, '🥃'],
    [/\btobacco\b/, '🚬'],
    [/\bcigarette\b/, '🚬'],
    [/\bpeel\b/, '🍊'],
    [/\bhull\b/, '🚢'],
    [/\bspade\b/, '⛏'],
    [/\brake\b/, '🌾'],
    [/\bplough\b/, '🚜'],
    [/\bpluck\b/, '✂'],
    [/\bharvest\b/, '🌾'],
    [/\bhorticulture\b/, '🌻'],
    [/\breproduce\b/, '🧬'],
    [/\brespire\b/, '🫁'],
    [/\bdense\b/, '🌫'],
    [/\bgush\b/, '💦'],
    [/\bpuff\b/, '💨'],
    [/\bblow\b/, '🌬'],
    [/\bdrip\b/, '💧'],
    [/\bpour\b/, '🫗'],
    [/\bdew\b/, '💧'],
    [/\bfountain\b/, '⛲'],
    [/\bvapour\b/, '💨'],
    [/\bdusk\b/, '🌆'],
    [/\bdebris\b/, '💥'],
    [/\bfringe\b/, '💇'],
    [/\bcomet\b/, '☄'],
    [/\bmeteorite\b/, '☄'],
    [/\bash\b/, '🌫'],
    [/\benzyme\b/, '🧪'],
    [/\buptake\b/, '🥫'],
    [/\bmature\b/, '🍇'],
    [/\bbarrel\b/, '🛢'],
    [/\bbucket\b/, '🪣'],
    [/\bpail\b/, '🪣'],
    [/\bbell\b/, '🔔'],
    [/\bfridge\b/, '🧊'],
    [/\bswitch\b/, '🎛'],
    [/\bshelf\b/, '🗄'],
    [/\bstool\b/, '🪑'],
    [/\bjar\b/, '🫙'],
    [/\bknob\b/, '🔘'],
    [/\bbolt\b/, '⚡'],
    [/\bpump\b/, '🚰'],
    [/\bplug\b/, '🔌'],
    [/\bpipe\b/, '🚰'],
    [/\bmop\b/, '🧹'],
    [/\bbroom\b/, '🧹'],
    [/\bmat\b/, '🟫'],
    [/\bcushion\b/, '🛋'],
    [/\bsheet\b/, '🛏'],
    [/\bpillow\b/, '🛏'],
    [/\bsponge\b/, '🧽'],
    [/\bnail\b/, '🔩'],
    [/\bshave\b/, '🪒'],
    [/\bcord\b/, '🔌'],
    [/\bstrand\b/, '🧵'],
    [/\bwax\b/, '🕯'],
    [/\bglue\b/, '🧴'],
    [/\btag\b/, '🏷'],
    [/\benvelope\b/, '✉'],
    [/\bcurve\b/, '📈'],
    [/\bion\b/, '⚛'],
    [/\bquantum\b/, '⚛'],
    [/\bsquash\b/, '🔨'],
    [/\butensil\b/, '🍴'],
    [/\bshampoo\b/, '🧴'],
    [/\bsoap\b/, '🧼'],
    [/\bdespair\b/, '😔'],
    [/\bnovice\b/, '🌱'],
    [/\billiteracy\b/, '🔤'],
    [/\bindulge\b/, '🍰'],
    [/\bidiot\b/, '🤪'],
    [/\bdegree\b/, '🌡'],
    [/\bdorm\b/, '🛏'],
    [/\bbibliography\b/, '📚'],
    [/\breel\b/, '🎡'],
    [/\bgauge\b/, '📏'],
    [/\bmicroscope\b/, '🔬'],
    [/\blens\b/, '🔍'],
    [/\bmicrophone\b/, '🎤'],
    [/\bcassette\b/, '📼'],
    [/\btape\b/, '📼'],
    [/\brefine\b/, '⚗'],
    [/\bdistil\b/, '⚗'],
    [/\btribe\b/, '🏕'],
    [/\barchaeology\b/, '🏺'],
    [/\bengrave\b/, '✍'],
    [/\bsoul\b/, '🕋'],
    [/\bchoir\b/, '🎵'],
    [/\bmonk\b/, '🧘'],
    [/\bpagoda\b/, '🛕'],
    [/\bhomesick\b/, '🏠'],
    [/\bempress\b/, '👑'],
    [/\bduchess\b/, '👑'],
    [/\bearl\b/, '🎩'],
    [/\bbaron\b/, '🎩'],
    [/\bpeep\b/, '👀'],
    [/\bforesee\b/, '🔮'],
    [/\blandmark\b/, '🗽'],
    [/\bknot\b/, '🪟'],
    [/\bphoneme\b/, '🔤'],
    [/\bvowel\b/, '🔤'],
    [/\blogogram\b/, '✍'],
    [/\bsuffix\b/, '➕'],
    [/\bsynonym\b/, '🔁'],
    [/\bantonym\b/, '🔀'],
    [/\bnoun\b/, '🔤'],
    [/\bpronoun\b/, '🔤'],
    [/\bverb\b/, '🔤'],
    [/\badverb\b/, '🔤'],
    [/\bparaphrase\b/, '🔄'],
    [/\bjargon\b/, '🗣'],
    [/\bslang\b/, '🗣'],
    [/\brumour\b/, '📢'],
    [/\bmanuscript\b/, '📜'],
    [/\bleaflet\b/, '📄'],
    [/\bballet\b/, '🩰'],
    [/\bopt\b/, '☑'],
    [/\bcarve\b/, '🔪'],
    [/\btone\b/, '🎵'],
    [/\btune\b/, '🎵'],
    [/\bdisc\b/, '💿'],
    [/\bcello\b/, '🎻'],
    [/\btrumpet\b/, '🎺'],
    [/\bdrum\b/, '🥁'],
    [/\bflute\b/, '🎵'],
    [/\bsprawl\b/, '🤸'],
    [/\bbadminton\b/, '🏸'],
    [/\bbilliards\b/, '🎱'],
    [/\bhockey\b/, '🏒'],
    [/\bbat\b/, '🦇'],
    [/\bsouvenir\b/, '🎁'],
    [/\bjewellery\b/, '💍'],
    [/\bjade\b/, '🟢'],
    [/\bmasquerade\b/, '🎭'],
    [/\bveil\b/, '👰'],
    [/\brobe\b/, '🛶'],
    [/\btrousers\b/, '👖'],
    [/\bbrim\b/, '🎩'],
    [/\bscarf\b/, '🧣'],
    [/\bhandkerchief\b/, '🧻'],
    [/\bpurse\b/, '👛'],
    [/\bvest\b/, '👕'],
    [/\bcollar\b/, '👔'],
    [/\bsleeve\b/, '👕'],
    [/\bsock\b/, '🧦'],
    [/\blace\b/, '👞'],
    [/\bsew\b/, '🪡'],
    [/\bstitch\b/, '🪡'],
    [/\bneedle\b/, '🪡'],
    [/\bthread\b/, '🧵'],
    [/\bstrap\b/, '🎒'],
    [/\bbracelet\b/, '💍'],
    [/\bvelvet\b/, '🧶'],
    [/\brag\b/, '🧹'],
    [/\bgrey\b/, '🖤'],
    [/\bstain\b/, '🎨'],
    [/\bknit\b/, '🧶'],
    [/\bweave\b/, '🧶'],
    [/\bcanvas\b/, '🎨'],
    [/\bnylon\b/, '🧦'],
    [/\bvogue\b/, '✨'],
    [/\boverturn\b/, '🔄'],
    [/\boverseas\b/, '✈'],
    [/\boverlap\b/, '🔀'],
    [/\boverall\b/, '📊'],
    [/\boutline\b/, '📋'],
    [/\binvest\b/, '💹'],
    [/\baccuse\b/, '🫵'],
    [/\badvice\b/, '💡'],
    [/\banalog\b/, '📡'],
    [/\banecdote\b/, '💬'],
    [/\bcondemn\b/, '👎'],
    [/\bdocument\b/, '📄'],
    [/\bextinguish\b/, '🧯'],
    [/\blay\b/, '🛠'],
    [/\bsubgroup\b/, '🔢'],
    [/\bdredge\b/, '🚜'],
    [/\balloy\b/, '⚙'],
    [/\bbronze\b/, '🥉'],
    [/\bmine\b/, '⛏'],
    [/\bpaperback\b/, '📕'],
    [/\bpamphlet\b/, '📄'],
    [/\bstationery\b/, '🖋'],
    /* ===== 第14轮第三批：中文语义 ===== */
    [/彗星|陨石|陨星/, '☄'],
    [/蚊子|蚊/, '🦟'],
    [/骆驼|驼/, '🐫'],
    [/熊猫|猫熊/, '🐼'],
    [/狐狸|狐/, '🦊'],
    [/斑马/, '🦓'],
    [/松鼠/, '🐿'],
    [/蚊子|老鹰|猎鹰|隼/, '🦅'],
    [/大提琴|小提琴|提琴/, '🎻'],
    [/小号|喇叭|号角/, '🎺'],
    [/长笛|笛子/, '🎵'],
    [/鼓|大鼓/, '🥁'],
    [/羽毛球/, '🏸'],
    [/台球|桌球|弹子/, '🎱'],
    [/曲棍球|冰球/, '🏒'],
    [/芭蕾|芭蕾舞/, '🩰'],
    [/自助餐|自助/, '🍽'],
    [/烧烤|烤肉/, '🍖'],
    [/宴会|盛宴|筵席/, '🍽'],
    [/零食|小吃|点心/, '🍿'],
    [/洗发|香波/, '🧴'],
    [/肥皂|香皂/, '🧼'],
    [/冰箱|冰柜/, '🧊'],
    [/炉子|火炉|厨灶/, '🔥'],
    [/水壶|锅/, '🫖'],
    [/平底锅/, '🍳'],
    [/桶|水桶|提桶/, '🪣'],
    [/罐子|广口瓶|瓶子/, '🫙'],
    [/开关|电闸|骤变/, '🎛'],
    [/搁板|架子|陆架/, '🗄'],
    [/凳子| stool/, '🪑'],
    [/拖把|扫帚/, '🧹'],
    [/垫子|坐垫|地垫|缓冲垫/, '🛋'],
    [/床单|被单|盖布/, '🛏'],
    [/枕头/, '🛏'],
    [/海绵/, '🧽'],
    [/钉子|指甲|趾甲/, '🔩'],
    [/剃|刮胡子|刮去/, '🪒'],
    [/电线|细绳|粗线/, '🔌'],
    [/蜡|蜂蜡/, '🕯'],
    [/胶水|浆糊|面糊/, '🧴'],
    [/标签|标牌|标牌/, '🏷'],
    [/信封|封皮/, '✉'],
    [/曲线|弧线|弯道/, '📈'],
    [/离子|量子/, '⚛'],
    [/压扁|压碎|挤进/, '🔨'],
    [/绝望/, '😔'],
    [/初学者|新手|见习/, '🌱'],
    [/文盲|无知/, '🔤'],
    [/沉溺|纵容|迁就/, '🍰'],
    [/白痴|笨蛋|低能/, '🤪'],
    [/度数|度，度数|度数/, '🌡'],
    [/宿舍/, '🛏'],
    [/参考书目|文献目录|目录学/, '📚'],
    [/卷轴|线轴|卷线轮/, '🎡'],
    [/测量仪器|厚度|宽度/, '📏'],
    [/显微镜/, '🔬'],
    [/透镜|镜片|镜头/, '🔍'],
    [/麦克风|扩音器|话筒/, '🎤'],
    [/磁带|盒式|胶片盒/, '📼'],
    [/精炼|提纯|蒸馏|提炼/, '⚗'],
    [/部落|宗族/, '🏕'],
    [/考古学|考古/, '🏺'],
    [/雕刻|铭刻|雕，刻/, '✍'],
    [/灵魂|心灵/, '🕋'],
    [/唱诗班|合唱团/, '🎵'],
    [/僧侣|修道士|和尚/, '🧘'],
    [/佛塔|宝塔/, '🛕'],
    [/想家|思乡/, '🏠'],
    [/皇后|女皇|伯爵|男爵|公爵/, '👑'],
    [/窥视|偷看|隐现/, '👀'],
    [/预见|预知|预料/, '🔮'],
    [/地标|陆标|里程碑/, '🗽'],
    [/针脚|缝线|一针/, '🪡'],
    [/音位|音素|元音|母音/, '🔤'],
    [/后缀|词尾|尾标/, '➕'],
    [/同义词|代名词/, '🔁'],
    [/反义词/, '🔀'],
    [/名词|代词|动词|副词/, '🔤'],
    [/改述|释义|转述/, '🔄'],
    [/行话|黑话|俚语|切口/, '🗣'],
    [/谣言|传闻|流言/, '📢'],
    [/手稿|原稿|手抄本/, '📜'],
    [/传单|小册子|活页/, '📄'],
    [/平装书|简装书/, '📕'],
    [/选择|抉择|作出抉择/, '☑'],
    [/语气|腔调|口吻|基调/, '🎵'],
    [/曲调|曲子|乐段|歌曲/, '🎵'],
    [/圆盘|唱片|光盘|碟片/, '💿'],
    [/蔓延|伸开四肢/, '🤸'],
    [/球棒|球拍|蝙蝠/, '🦇'],
    [/纪念品|纪念物/, '🎁'],
    [/珠宝|首饰|手镯|臂镯/, '💍'],
    [/翡翠|玉|玉制品/, '🟢'],
    [/化装舞会|假面舞会|伪装|掩饰/, '🎭'],
    [/面纱|面罩|头巾|围巾|披巾/, '🧣'],
    [/袍服|礼袍|睡袍|浴衣|长袍/, '🛶'],
    [/裤子|长裤/, '👖'],
    [/帽檐|帽边|边沿/, '🎩'],
    [/手帕/, '🧻'],
    [/钱包|皮夹子|手提包|手袋/, '👛'],
    [/背心|汗衫|马甲/, '👕'],
    [/衣领|领口|颈圈/, '👔'],
    [/袖子|袖套/, '👕'],
    [/短袜|袜子/, '🧦'],
    [/蕾丝|鞋带|系带/, '👞'],
    [/缝纫|缝补|缝，/, '🪡'],
    [/线|细线|线状物|股|缕/, '🧵'],
    [/带子|皮带|金属带/, '🎒'],
    [/天鹅绒|丝绒|编织|针织/, '🧶'],
    [/抹布|破布|破衣/, '🧹'],
    [/灰色|灰白|花白/, '🖤'],
    [/玷污|污渍|染色|着色/, '🎨'],
    [/帆布|画布|油画/, '🎨'],
    [/尼龙|锦纶/, '🧦'],
    [/流行|时髦|风尚/, '✨'],
    [/合金|青铜/, '⚙'],
    [/疏浚|清淤|挖掘|打捞/, '🚜'],
    [/熄灭|消灭|破灭/, '🧯'],
    [/安放|放置|铺设|铺放/, '🛠'],
    [/子群|小群|小组织/, '🔢'],
    [/摄取|吸收|吸收量/, '🥫'],
    [/成熟的|成年|发育完全/, '🍇'],
    [/ overflow|溢出/, '💦'],
    /* ===== 第14轮第二批：单词级 ===== */
    [/\bpace\b/, '🚶'],
    [/\bpastime\b/, '🎲'],
    [/\bpatch\b/, '🩹'],
    [/\bpersonnel\b/, '👥'],
    [/\bplateau\b/, '⛰'],
    [/\bplead\b/, '🙏'],
    [/\bpolish\b/, '✨'],
    [/\bpose\b/, '📸'],
    [/\bposit\b/, '📍'],
    [/\brebel\b/, '🚩'],
    [/\brecruit\b/, '🪖'],
    [/\bremain\b/, '➡'],
    [/\bremind\b/, '🔔'],
    [/\bremote\b/, '📡'],
    [/\brequest\b/, '🙏'],
    [/\breserve\b/, '🗄'],
    [/\breside\b/, '🏠'],
    [/\bresource\b/, '⛏'],
    [/\bretain\b/, '🗄'],
    [/\bretreat\b/, '🔙'],
    [/\breverse\b/, '↔'],
    [/\bsacrifice\b/, '🙏'],
    [/\bscenario\b/, '🎬'],
    [/\bslump\b/, '📉'],
    [/\bsoar\b/, '🚀'],
    [/\bsole\b/, '🔟'],
    [/\bsolid\b/, '🧱'],
    [/\bspare\b/, '🔋'],
    [/\bstatus\b/, '📊'],
    [/\bsteady\b/, '📏'],
    [/\bstretch\b/, '🤸'],
    [/\bsubject\b/, '📚'],
    [/\bsubmerge\b/, '🌊'],
    [/\bsubmit\b/, '📤'],
    [/\bsuppose\b/, '🤔'],
    [/\bsupreme\b/, '🏔'],
    [/\bsurplus\b/, '📦'],
    [/\bsurround\b/, '⭕'],
    [/\bsuspect\b/, '🕵'],
    [/\bswamp\b/, '🐸'],
    [/\bsymbol\b/, '🔣'],
    [/\btempt\b/, '😈'],
    [/\bthorough\b/, '🔍'],
    [/\bthreshold\b/, '🚪'],
    [/\bthroughout\b/, '🌐'],
    [/\btrace\b/, '🔍'],
    [/\btrail\b/, '🥾'],
    [/\btrajectory\b/, '🛰'],
    [/\btreasure\b/, '💎'],
    [/\bunderlie\b/, '🧱'],
    [/\buniform\b/, '👕'],
    [/\bunjust\b/, '⚖'],
    [/\bupright\b/, '↕'],
    [/\bupstream\b/, '⬆'],
    [/\butmost\b/, '🔝'],
    [/\bvanish\b/, '💨'],
    [/\bvia\b/, '🔀'],
    [/\bvictim\b/, '🆘'],
    [/\bwhereby\b/, '🔗'],
    [/\bfurthermore\b/, '➕'],
    [/\bsomewhat\b/, '🔅'],
    [/\bthereby\b/, '➡'],
    [/\btherefore\b/, '➡'],
    [/\bunlike\b/, '↔'],
    [/\bwhilst\b/, '⏳'],
    [/\boxide\b/, '🧪'],
    [/\bmantle\b/, '🧥'],
    [/\bhorizon\b/, '🌅'],
    [/\bore\b/, '⛏'],
    [/\bmarble\b/, '🗿'],
    [/\bquartz\b/, '💎'],
    [/\bhurricane\b/, '🌪'],
    [/\bmagma\b/, '🌋'],
    [/\bcliff\b/, '⛰'],
    [/\bdelta\b/, '🏞'],
    [/\bpole\b/, '🧭'],
    [/\bgulf\b/, '🌊'],
    [/\btide\b/, '🌊'],
    [/\bflat\b/, '📐'],
    [/\bmainland\b/, '🗺'],
    [/\bpeninsula\b/, '🏝'],
    [/\bhail\b/, '👏'],
    [/\bfrigid\b/, '❄'],
    [/\bcelsius\b/, '🌡'],
    [/\bsouthern\b/, '🔽'],
    [/\beastern\b/, '➡'],
    [/\bmuddy\b/, '🟫'],
    [/\bclay\b/, '🧱'],
    [/\bdirt\b/, '🧹'],
    [/\bsuburb\b/, '🏘'],
    /* ===== 第14轮第二批：中文语义 ===== */
    [/步伐|踱步|步调/, '🚶'],
    [/消遣|娱乐|休闲/, '🎲'],
    [/补丁|修补|补片/, '🩹'],
    [/人员|员工|全体职员/, '👥'],
    [/高原|高地|停滞期/, '⛰'],
    [/恳求|请求|乞求/, '🙏'],
    [/磨光|润色|擦亮|抛光/, '✨'],
    [/造成|引|摆姿势|姿势/, '📸'],
    [/假定|假设|推测/, '🤔'],
    [/反叛|叛乱|造反/, '🚩'],
    [/招募|征募|新兵/, '🪖'],
    [/保持|剩余|仍然是/, '➡'],
    [/提醒|使想起|提示/, '🔔'],
    [/遥远的|远程|偏远/, '📡'],
    [/保留|储备|预订/, '🗄'],
    [/居住|驻留|存在于/, '🏠'],
    [/资源|物力|财力/, '⛏'],
    [/撤退|后退|静修/, '🔙'],
    [/反转|逆转|倒退/, '↔'],
    [/牺牲|献身|舍弃/, '🙏'],
    [/情景|剧本|场景/, '🎬'],
    [/暴跌|萧条|下滑/, '📉'],
    [/飙升|猛增|高涨/, '🚀'],
    [/唯一的|独有|仅有/, '🔟'],
    [/固体的|固体|可靠的/, '🧱'],
    [/备用的|备用|备件/, '🔋'],
    [/地位|状态|身份/, '📊'],
    [/稳定的|稳固|平稳/, '📏'],
    [/伸展|舒展|拉伸/, '🤸'],
    [/主题|学科|科目/, '📚'],
    [/淹没|潜入|浸没/, '🌊'],
    [/提交|呈交|屈服/, '📤'],
    [/最高的|至高|最高/, '🏔'],
    [/过剩|多余|盈余/, '📦'],
    [/包围|环绕|围住/, '⭕'],
    [/怀疑|嫌疑犯|可疑/, '🕵'],
    [/沼泽|湿地/, '🐸'],
    [/象征|符号|标志/, '🔣'],
    [/引诱|诱惑|吸引/, '😈'],
    [/彻底的|彻底|详尽/, '🔍'],
    [/门槛|临界|阈值|门口/, '🚪'],
    [/遍及|遍布|贯穿/, '🌐'],
    [/痕迹|追踪|追溯/, '🔍'],
    [/小径|小路|跟踪/, '🥾'],
    [/轨迹|弹道|路线/, '🛰'],
    [/宝藏|珍宝|珍视/, '💎'],
    [/构成.{0,3}基础|是.{0,3}的基础/, '🧱'],
    [/统一的|统一|制服/, '👕'],
    [/不公平|不公正|非正义/, '⚖'],
    [/直立的|直立|竖直/, '↕'],
    [/上游|逆流/, '⬆'],
    [/极度的|极限|极度/, '🔝'],
    [/消失|消逝|不见/, '💨'],
    [/经由|通过|借助于/, '🔀'],
    [/受害者|遇难者|受害人/, '🆘'],
    [/此外|而且|再者/, '➕'],
    [/有点|稍微|略微/, '🔅'],
    [/从而|因此|由此/, '➡'],
    [/不像|不同于|与.{0,3}不同/, '↔'],
    [/氧化物|氧化/, '🧪'],
    [/地幔|披风|斗篷/, '🧥'],
    [/地平线|眼界|视野/, '🌅'],
    [/矿石|矿砂|矿/, '⛏'],
    [/大理石/, '🗿'],
    [/石英/, '💎'],
    [/飓风|台风|暴风/, '🌪'],
    [/岩浆|熔岩/, '🌋'],
    [/悬崖|峭壁|绝壁/, '⛰'],
    [/三角洲|希腊字母/, '🏞'],
    [/地极|杆子|柱/, '🧭'],
    [/海湾|鸿沟|分歧/, '🌊'],
    [/潮汐|潮水|涨潮/, '🌊'],
    [/平坦|平坦的|平的/, '📐'],
    [/大陆|本土|内陆/, '🗺'],
    [/半岛/, '🏝'],
    [/冰雹|欢呼|赞扬/, '👏'],
    [/寒冷|严寒|寒冷的/, '❄'],
    [/摄氏|摄氏度/, '🌡'],
    [/南方|南部|南方的/, '🔽'],
    [/东方|东部|东方的/, '➡'],
    [/泥泞|泥泞的|浑浊/, '🟫'],
    [/黏土|陶土|泥土/, '🧱'],
    [/污物|尘土|灰尘/, '🧹'],
    [/城郊|近郊|郊区/, '🏘'],
    /* ===== 第14轮追加：单词级精确规则（避免同义中文互抢） ===== */
    [/\b(export|exporting|exported)\b/, '📤'],
    [/\b(import|importing|imported)\b/, '📥'],
    [/\boutlet\b/, '🏬'],
    [/\bportfolio\b/, '💼'],
    [/\bprotocol\b/, '📋'],
    [/\binterface\b/, '🖥'],
    [/\bnode\b/, '🔗'],
    [/\bbond\b/, '🧾'],
    [/\borgan\b/, '🫀'],
    [/\bmedium\b/, '📻'],
    [/\bformat\b/, '📐'],
    [/\bgrade\b/, '📊'],
    [/\bindex\b/, '📁'],
    [/\b(alarm|alert)\b/, '🚨'],
    [/\barray\b/, '🔢'],
    [/\battach\b/, '📎'],
    [/\battract\b/, '🧲'],
    [/\bfocus\b/, '🎯'],
    [/\blink\b/, '🔗'],
    [/\bitem\b/, '📌'],
    [/\binput\b/, '⌨'],
    [/\bdebug\b/, '🐛'],
    [/\bcache\b/, '💾'],
    [/\bfirmware\b/, '💾'],
    [/\b(gene|genetic)\b/, '🧬'],
    [/\bparasite\b/, '🪱'],
    [/\bmodule\b/, '🧱'],
    [/\bthesis\b/, '📜'],
    [/\b(faculty|alumnus|dean)\b/, '🎓'],
    [/\bdropout\b/, '🎒'],
    [/\bdiscipline\b/, '📚'],
    [/\bcohort\b/, '👥'],
    [/\bconsole\b/, '🫂'],
    [/\bcorrupt\b/, '💸'],
    [/\bembargo\b/, '🚫'],
    [/\bamnesia\b/, '🧠'],
    [/\bbenign\b/, '🟢'],
    [/\boverdose\b/, '💊'],
    [/\bwelfare\b/, '🫱'],
    [/\bdiplomat\b/, '🤝'],
    [/\bsovereignty\b/, '👑'],
    [/\btreaty\b/, '📜'],
    [/\bverdict\b/, '⚖'],
    [/\bpropaganda\b/, '📢'],
    [/\bsatire\b/, '🎭'],
    [/\bstereotype\b/, '🗿'],
    [/\bempathy\b/, '🤗'],
    [/\bproficiency\b/, '🎯'],
    [/\babolish\b/, '🚫'],
    [/\bcivil\b/, '🏛'],
    [/\bbandwidth\b/, '📶'],
    [/\bencrypt\b/, '🔐'],
    [/\bgadget\b/, '📱'],
    [/\bcompute\b/, '🧮'],
    [/\blatency\b/, '🐢'],
    [/\bsynthesis\b/, '🔀'],
    [/\bsubsidy\b/, '💸'],
    [/\bbankruptcy\b/, '📉'],
    [/\bassets\b/, '🏦'],
    [/\bdividend\b/, '💵'],
    [/\bequilibrium\b/, '⚖'],
    [/\bforecast\b/, '🔮'],
    [/\binventory\b/, '📦'],
    [/\binvoice\b/, '🧾'],
    [/\bbureaucracy\b/, '🏢'],
    [/\bbureau\b/, '🏢'],
    [/\bimpulse\b/, '💥'],
    [/\battitude\b/, '🧭'],
    [/\bconsensus\b/, '🤝'],
    [/\bcontroversy\b/, '🗯'],
    /* ===== 第14轮追加：中文语义规则（多字词，避免单字子串误命中） ===== */
    [/宣传|鼓动|煽动|宣扬/, '📢'],
    [/讽刺|嘲讽|讥讽|挖苦/, '🎭'],
    [/刻板印象|成见/, '🗿'],
    [/共情|同理心|感同身受/, '🤗'],
    [/熟练|精通|娴熟/, '🎯'],
    [/废除|废止|取缔/, '🚫'],
    [/裁决|判决|裁定|定罪/, '⚖'],
    [/条约|公约|协定|协议/, '📜'],
    [/主权|统治权/, '👑'],
    [/外交官|外交的|外交/, '🤝'],
    [/福利|救济|抚恤/, '🫱'],
    [/官僚|行政机关/, '🏢'],
    [/腐败|贪污|受贿|腐化/, '💸'],
    [/禁运|封锁|制裁/, '🚫'],
    [/补贴|津贴|补助/, '💸'],
    [/破产|倒闭|清算/, '📉'],
    [/资产|财产|财富/, '🏦'],
    [/债券|公债|国债/, '🧾'],
    [/股息|红利|分红/, '💵'],
    [/均衡|平衡|均势/, '⚖'],
    [/预测|预报|预估|预料/, '🔮'],
    [/库存|存货|仓储/, '📦'],
    [/发票|票据|账单|收据/, '🧾'],
    [/带宽|网速|频宽/, '📶'],
    [/加密|密码|密文/, '🔐'],
    [/界面|接口|介面/, '🖥'],
    [/小装置|小工具|小玩意/, '📱'],
    [/缓存|快取/, '💾'],
    [/计算|运算|算出/, '🧮'],
    [/调试|除错/, '🐛'],
    [/延迟|时延|滞后/, '🐢'],
    [/节点|结点|网点/, '🔗'],
    [/综合|合成|整合/, '🔀'],
    [/论文|论点|学位论文/, '📜'],
    [/院系|教职|全体教员/, '🎓'],
    [/辍学|退学|肄业/, '🎒'],
    [/校友|毕业生|校友会/, '🎓'],
    [/院长|系主任|教务长/, '🎓'],
    [/学科|科目|专业/, '📚'],
    [/模块|单元|模组/, '🧱'],
    [/评分|打分|评级|年级/, '📊'],
    [/指数|索引|指标/, '📁'],
    [/汇编|编纂|编撰/, '📚'],
    [/抽象的|抽象/, '🌀'],
    [/制定|拟定|起草/, '📋'],
    [/评价|评估|评定|估价/, '📊'],
    [/良性的|良性/, '🟢'],
    [/基因|遗传/, '🧬'],
    [/过量|服药过量/, '💊'],
    [/寄生虫|寄生/, '🪱'],
    [/器官|脏器/, '🫀'],
    [/失忆|健忘|遗忘/, '🧠'],
    [/冲动|一时兴起/, '💥'],
    [/态度|心态/, '🧭'],
    [/洞察力|洞察|见识/, '💡'],
    [/激励|启发|鼓舞|鼓励/, '✨'],
    [/使信服|说服|信服/, '🤝'],
    [/忽视|忽略|疏于|漠视/, '🙈'],
    [/推测|猜测|揣测/, '🤔'],
    [/构想|设想|构思|想象/, '💭'],
    [/反映|映照|反射/, '🪞'],
    [/贡献|捐献|出力/, '🫱'],
    [/分散|散开|疏散|散布/, '💨'],
    [/多样性|多样化|多样的/, '🌈'],
    [/援引|引用|援用/, '📣'],
    [/占据|占领|占用|占据着/, '🚩'],
    [/提议|提出|提案/, '💡'],
    [/经历|经受|遭受/, '🔄'],
    [/陪伴|陪同|伴随|伴奏/, '👫'],
    [/负担得起|支付得起|负担/, '💰'],
    [/警报|警钟|告警/, '🚨'],
    [/警觉|警惕|警醒/, '🚨'],
    [/修正|修订|修改|修正案/, '✏'],
    [/阵列|排列|一系列/, '🔢'],
    [/组装|装配|集合|聚集/, '🔧'],
    [/保证|担保|确保|保障/, '🛡'],
    [/附加|附上|附属|附件/, '📎'],
    [/尝试|试图|企图|试图/, '🎯'],
    [/吸引|招引|吸引力/, '🧲'],
    [/尴尬|难堪|窘迫/, '😅'],
    [/使熟悉|熟悉|了解/, '👋'],
    [/议程|议事日程|日程/, '📋'],
    [/荒谬|荒唐|荒诞/, '🤪'],
    [/滥用|虐待|辱骂/, '⛔'],
    [/鼓掌|拍手|称赞|赞赏/, '👏'],
    [/代表|利益| behalf/, '🙋'],
    [/举止|行为|表现/, '🎭'],
    [/办事处|分局|局、/, '🏢'],
    [/绕过|避开|旁路/, '↩'],
    [/线索|端倪|提示/, '🔍'],
    [/倒塌|崩溃|瓦解|垮塌/, '💥'],
    [/同事|同僚|同仁/, '👥'],
    [/强迫|迫使|强制|逼迫/, '⛓'],
    [/压缩|浓缩|精简|凝结/, '🗜'],
    [/实施|进行|开展|引导/, '🎬'],
    [/遵守|符合|顺从|遵从/, '✅'],
    [/连接|连结|联系|链接/, '🔗'],
    [/咨询|请教|商议/, '💬'],
    [/接触|联络/, '📞'],
    [/合同|契约|合约/, '📄'],
    [/应付|应对|妥善处理/, '🛡'],
    [/十年|十年期|十年间/, '📅'],
    [/衰退|腐烂|腐朽|衰败/, '🍂'],
    [/文件|文档|记录/, '📄'],
    [/领域|域名|范畴/, '🌐'],
    [/赋予权利|使有权利|题名/, '🎟'],
    [/装备|配备|使具备/, '🎒'],
    [/擦除|抹去|删除|消除/, '🧽'],
    [/暴露|揭露|使接触/, '🔦'],
    [/有限的|有限/, '⏳'],
    [/含蓄|隐含|暗含|暗示/, '🌫'],
    [/输入端|输入/, '⌨'],
    [/安装|任命|设置/, '🛠'],
    [/机构|学会|协会|研究所/, '🏛'],
    [/互动|交互|相互作用/, '🔄'],
    [/干涉|干扰|干预/, '🚧'],
    [/项目|条款|条目|项/, '📌'],
    [/风景|景观|景色/, '🏞'],
    [/松散|松动|松垮/, '🧵'],
    [/媒介|媒体|传媒/, '📻'],
    [/中等的|中间|适中/, '📻'],
    [/仅仅|只不过|只是/, '➖'],
    [/最小|最少|最低限/, '🔽'],
    [/发生|出现|产生/, '⚡'],
    [/奇怪|古怪|奇异|奇数/, '❓'],
    [/抵消|弥补|补偿/, '↔'],
    [/应得|值得|配得上/, '🏅'],
];
  for(var i=0;i<map.length;i++){ if(map[i][0].test(s)) return map[i][1]; }
  // 词缀兜底：-tion/-ment/-ness 名词类、-er/-or 人、-ful/-able 形容词等
  var affixMap=[
    [/(tion|sion|ment|ness|ity|ance|ence|ship|hood|age|ism)$/, '🧩'],
    [/(er|or|ist|ian|eer|ant|ent)$/, '👤'],
    [/ing$/, '🟢'],
    [/ed$/, '🔙'],
    [/ly$/, '✨'],
    [/(ful|less|ous|able|ible|ive|al|ic|ary)$/, '🏷️'],
    [/(ize|ise|ify|ate|en)$/, '🔧'],
  ];
  for(var i=0;i<affixMap.length;i++){ if(affixMap[i][0].test(word)) return affixMap[i][1]; }
  // 最末兜底：按词性给合理默认表情（不再一律📚）
  if(/[aiou].*(ability|tion|sion|ment|ness|ity|ism|ship|hood|ance|ence)$/.test(word)) return '🧩';
  if(/ly$/.test(word)) return '\u2728';
  return '📝';
}

/* ============ 首页 ============ */
var curView='home';
function goHome(){ Sound.play('back'); renderHome(); }
function renderHome(){
  curView='home';
  resetDailyIfNeeded();
  document.getElementById('view-home').style.display='';
  document.getElementById('view-word').style.display='none';
  document.getElementById('view-news').style.display='none';
  document.getElementById('view-article').style.display='none';
  document.getElementById('thumb').classList.remove('on');
  document.getElementById('xpChip').textContent='XP '+G.xp;

  // 继续学习 banner
  var cb=document.getElementById('contiBox');
  if(G.last && G.last.deck){
    var dk=DECKS.filter(function(d){return d.key===G.last.deck;})[0];
    if(dk){
      var seen=getSeen(dk.key).length;
      cb.innerHTML='<div class="conti" onclick="resumeLast()"><div class="ci">▶️</div>'
        +'<div class="cb"><div class="ct">继续学习 · '+dk.name+'</div>'
        +'<div class="cd">已学 '+seen+' 个 · 点这里接着学</div></div>'
        +'<div class="cgo">继续 →</div></div>';
    } else cb.innerHTML='';
  } else cb.innerHTML='';

  // 今日目标
  var goals=[
    {key:'word',label:'英语 20 词',need:20,prog:G.study.wordToday,deck:'en',xp:10},
    {key:'ai',label:'AI 新闻 3 篇',need:3,prog:G.study.newsToday,deck:'ai',xp:10},
    {key:'art',label:'知识卡 1 篇',need:1,prog:G.study.artToday,deck:'kn_all',xp:20}
  ];
  var gl=document.getElementById('goalList'); var gh='';
  goals.forEach(function(g){
    var pct=Math.min(100,Math.round(g.prog/g.need*100));
    var done=g.prog>=g.need;
    gh+='<div class="goal"><div class="gname">'+g.label+'</div>'
      +'<div class="gbar"><i style="width:'+pct+'%"></i></div>';
    if(done){
      if(!G.tasks[todayStr()]||!G.tasks[todayStr()][g.key+'_claimed']){ claimGoal(g.key,g.xp); }
      gh+='<div class="gok">✓ 完成</div>';
    } else {
      gh+='<div class="gtodo">'+Math.min(g.prog,g.need)+'/'+g.need+'</div>';
    }
    gh+='</div>';
  });
  gl.innerHTML=gh;
  // 目标可点击跳转（未完成时）
  Array.prototype.forEach.call(gl.querySelectorAll('.goal'),function(el,idx){
    if(goals[idx].prog<goals[idx].need){
      el.style.cursor='pointer';
      el.onclick=function(){ startDeck(goals[idx].deck); };
    }
  });

  // 板块列表
  var box=document.getElementById('deckList'); var h='';
  DECKS.forEach(function(d){
    h+='<div class="deck" data-key="'+d.key+'" style="background:linear-gradient(160deg,'+d.color.replace('135deg','150deg')+',rgba(255,255,255,.02))">'
      + (d.key==='ai' ? '<span class="badge-new" id="deckNew_ai" style="display:none"></span>' : '')
      +'<div class="row">'
      +'<div class="emoji-box" style="background:'+d.color+'">'+d.icon+'</div>'
      +'<div class="info"><div class="dn">'+d.name+'</div><div class="dd">'+d.desc+'</div></div>'
      +'</div>'
      +'<div class="prog"><i id="deckProg_'+d.key+'"></i></div>'
      +'<div class="meta"><span id="deckMeta_'+d.key+'">加载中…</span><span class="go">开始学习 →</span></div>'
      +'</div>';
  });
  box.innerHTML=h;  // 先插 DOM，loadDeck 异步回调时元数据元素已存在
  DECKS.forEach(function(d){
    loadDeck(d,function(items){
      var p=deckProgress(d, items);
      var prog=document.getElementById('deckProg_'+d.key);
      if(prog){ prog.style.width=p.pct+'%'; }
      var meta=document.getElementById('deckMeta_'+d.key);
      if(meta){ meta.textContent=p.text; }
      if(d.key==='ai'){
        var raw=rawCache[d.src];
        if(raw && raw.cards){
          var updated=raw.updated||'';
          var total=raw.cards.length;
          var newCnt=raw.cards.filter(function(c){return c.is_new || c.date===updated;}).length;
          var readCnt=raw.cards.filter(function(c){return G.newsRead.indexOf(newsIdKey(c))>=0;}).length;
          if(meta){ meta.innerHTML='今日更新 '+updated+' · 新增 '+newCnt+' / '+total+' 条 · 已读 '+readCnt+'/'+total+' <span class="go">开始阅读 →</span>'; }
          var badge=document.getElementById('deckNew_ai');
          if(badge && newCnt>0){ badge.style.display=''; badge.textContent='NEW '+newCnt; }
        }
      }
    });
  });
  box.querySelectorAll('.deck').forEach(function(el){
    el.addEventListener('click',function(){ Sound.play('click'); startDeck(el.getAttribute('data-key')); });
  });
}
function deckProgress(d, items){
  var seen=(d.type==='word')?G.study.words:(d.type==='news')?G.study.news:G.study.articles;
  var known=0;
  items.forEach(function(it){ if(seen.indexOf(idOf(d,it))>=0) known++; });
  var total=items.length;
  var pct=total?Math.round(known/total*100):0;
  return {known:known,total:total,pct:pct,text:known+' / '+total+' 已学 ('+pct+'%)'};
}

/* 洗牌：每次进入英语牌组都随机乱序，不再是词库正序（abundant 开头） */
function shuffleArr(a){
  var arr=a.slice();
  for(var i=arr.length-1;i>0;i--){
    var j=Math.floor(Math.random()*(i+1));
    var t=arr[i]; arr[i]=arr[j]; arr[j]=t;
  }
  return arr;
}
/* ============ 学习会话 ============ */
var cur=null;
// 学习阶段常量
var STAGE={CARD:'card', QUIZ:'quiz', EXPLAIN:'explain', SPELL:'spell', DONE:'done'};
function startDeck(key){
  var deck=DECKS.filter(function(d){return d.key===key;})[0];
  loadDeck(deck,function(items){
    var seen=getSeen(key);
    var unseen=items.filter(function(it){return seen.indexOf(idOf(deck,it))<0;});
    var seenItems=items.filter(function(it){return seen.indexOf(idOf(deck,it))>=0;});
    // 单词牌组：未学的洗牌在前，已学的洗牌在后 —— 每次进入都是随机顺序
    var pool=(deck.type==='word')? shuffleArr(unseen).concat(shuffleArr(seenItems)) : unseen.concat(seenItems);
    var n=Math.min(deck.batch, pool.length);
    if(n===0){ toast('该板块已学完，去复习吧～'); return; }
    cur={
      deck:deck, items:pool.slice(0,n), idx:0, type:deck.type,
      stage:STAGE.CARD,
      ws:{}, // wordState per current word
      combo:0, correctStreak:0
    };
    enterWordView();
  });
}
function resumeLast(){
  if(!G.last||!G.last.deck) return;
  var deck=DECKS.filter(function(d){return d.key===G.last.deck;})[0];
  if(!deck) return;
  loadDeck(deck,function(items){
    var seen=getSeen(deck.key);
    var unseen=items.filter(function(it){return seen.indexOf(idOf(deck,it))<0;});
    var seenItems=items.filter(function(it){return seen.indexOf(idOf(deck,it))>=0;});
    // 单词牌组：继续学习同样走乱序（泽少要求每次进入都是随机顺序）
    var pool=(deck.type==='word')? shuffleArr(unseen).concat(shuffleArr(seenItems)) : unseen.concat(seenItems);
    var n=Math.min(deck.batch, pool.length);
    if(n===0){ startDeck(deck.key); return; }
    var idx=Math.min(G.last.idx||0, n-1);
    cur={
      deck:deck, items:pool.slice(0,n), idx:idx, type:deck.type,
      stage:STAGE.CARD,
      ws:{}, combo:0, correctStreak:0
    };
    enterWordView();
  });
}
function enterWordView(){
  curView='word';
  Sound.resetCombo();
  cur.combo=0; cur.correctStreak=0;
  updateComboDisplay();
  document.getElementById('view-home').style.display='none';
  document.getElementById('view-word').style.display='';
  if(cur.deck.key==='en'){
    enterLearnStage();
  } else if(cur.deck.key==='ai'){
    document.getElementById('view-word').style.display='none';
    document.getElementById('view-news').style.display=''; renderNewsList();
  } else {
    document.getElementById('view-word').style.display='none';
    document.getElementById('view-article').style.display=''; renderArticle();
  }
}
function getSeen(key){
  if(key==='en') return G.study.words||[];
  if(key==='ai') return G.study.news||[];
  return G.study.articles||[];
}
function addSeen(key,id){
  if(key==='en'){ if(G.study.words.indexOf(id)<0){ G.study.words.push(id); G.study.wordToday++; } }
  else if(key==='ai'){ if(G.study.news.indexOf(id)<0){ G.study.news.push(id); G.study.newsToday++; } }
  else { if(G.study.articles.indexOf(id)<0){ G.study.articles.push(id); G.study.artToday++; } }
  saveStudy();
}
function idOf(deck,it){ return deck.type==='word'? it.word : (it.title||''); }
function updateProgress(id, idx, total){
  var pct=Math.round((idx+1)/total*100);
  document.getElementById(id).style.width=pct+'%';
  document.getElementById(id.replace('prog','cnt')).textContent=(idx+1)+' / '+total;
}
function saveLast(){
  if(cur) G.last={deck:cur.deck.key, idx:cur.idx}; else G.last=null;
  zs(LAST_KEY,G.last);
}
function updateComboDisplay(){
  var el=document.getElementById('comboDisplay');
  if(cur && cur.combo>=3) el.textContent='🔥 '+cur.combo+'连击'; else el.textContent='';
}

/* ========== 新版英语单词学习流程（分阶段） ========== */

/**
 * 进入当前单词的学习流程
 * 流程：CARD → QUIZ → EXPLAIN → [SPELL] → DONE(next)
 */
function enterLearnStage(){
  initWordState();
  showStageCard();
}

/**
 * 初始化当前单词的状态追踪
 */
function initWordState(){
  var it=cur.items[cur.idx];
  var seenWords=G.study.words||[];
  var isNew=seenWords.indexOf(it.word)<0;
  cur.ws={
    isNew:isNew,
    quizResult:null,
    wrongCount:0,
    spellRequired:false,
    spellAttempts:0,
    spellRepeat:0, // 第10轮：拼错后需连拼对的剩余遍数（错一次置3，连对3遍才放行）
    spellHintLevel:0, // 0=无提示 1=首字母 2=更多提示
    mastery:'unknown',
    revealed:false, // 拼写时是否点开了"显示单词"
    quizAnswered:false
  };
}

// ---- 阶段1：显示单词卡片（图+词+音标+例句）----
// 取例句数组：优先 examples（含3条），兼容旧 en/cn 单条
function getExamples(it){
  var arr = (it.examples && it.examples.length) ? it.examples : [];
  if(!arr.length && it.en){ arr = [{en:it.en, cn:it.cn||''}]; }
  return arr;
}
// 渲染一条例句（英文高亮单词 + 播放按钮 + 中文），返回 HTML
// 播放按钮用 data-en-idx 索引，由点击时从当前词句 examples 里取整句交给有道，避免内联整句的转义问题
function exHtml(it, ex, idx){
  var sent=ex.en||'';
  var hl=sent.replace(new RegExp('\\b'+escapeRegExp(it.word)+'\\b','gi'),'<span class="hl">'+esc(it.word)+'</span>');
  return '<div class="example" id="ex_'+idx+'" style="margin-bottom:8px">'
    +'<div class="ex-row"><span style="flex:1">'+hl+'</span>'
    +'<span class="speaker" onclick="playEx('+idx+')" style="cursor:pointer">🔊</span></div>'
    +(ex.cn?'<div style="font-size:13px;color:var(--mut);margin-top:4px">'+esc(ex.cn)+'</div>':'')
    +'</div>';
}
// 点击例句播放按钮：从当前词取第 idx 条例句整句，交给有道在线发音
function playEx(idx){
  if(!cur||!cur.items) return;
  var it=cur.items[cur.idx];
  var exs=getExamples(it);
  var ex=exs[idx];
  if(ex&&ex.en) Pron.speakSentence(ex.en, it.word, idx);
}
function showStageCard(){
  cur.stage=STAGE.CARD;
  var it=cur.items[cur.idx];
  var sc=document.getElementById('wordCard');
  sc.classList.remove('swap');

  var mediaHtml='';
  if(it.image){
    mediaHtml='<div class="media" id="wordMedia"><img id="wm" src="'+esc(it.image)+'" alt="'+esc(it.word)+'" style="opacity:0;transition:opacity .16s"></div>';
  } else {
    mediaHtml='<div class="media" id="wordMedia"><div style="font-size:80px">'+wordEmoji(it.word,it.pos||it.cn||'')+'</div></div>';
  }

  // 例句（显示最多 3 条，每条带发音按钮）
  var exampleHtml='';
  var exs=getExamples(it);
  if(exs.length){
    var shown=exs.slice(0,3);
    exampleHtml='<div id="wordExamples">';
    for(var ei=0;ei<shown.length;ei++){ exampleHtml+=exHtml(it, shown[ei], ei); }
    exampleHtml+='</div>';
  }

  document.getElementById('stageContent').innerHTML=
    '<div class="ft">英语 · 雅思词汇</div>'
    +mediaHtml
    +'<div class="big" id="wordText">'+esc(it.word)+'</div>'
    +'<div class="ipa" id="wordIpa"><span>'+esc(it.ipa||'')+'</span><span class="speaker" id="wordSpeak">🔊</span></div>'
    +(it.pos?'<div class="pos" id="wordPos">'+esc(it.pos)+'</div>':'')
    +exampleHtml;

  document.getElementById('wprog').textContent=(cur.idx+1)+' / '+cur.items.length;
  var fav=document.getElementById('wFav'); fav.classList.toggle('on', G.fav.indexOf(it.word)>=0);

  // 图片淡入
  if(it.image){
    var im=document.getElementById('wm');
    if(im){
      im.onload=function(){ this.style.opacity=1; };
      im.onerror=function(){ document.getElementById('wordMedia').innerHTML='<div style="font-size:80px">'+wordEmoji(it.word,it.pos||it.cn||'')+'</div>'; };
    }
  }

  // 绑定发音
  var sp=document.getElementById('wordSpeak');
  if(sp) sp.onclick=function(){ replayWord(); };

  // 自动发音
  Pron.play(it.word);

  // 预加载
  preloadAround();

  // 底部栏：隐藏（四选一会直接渲染在卡片下方）
  hideThumb();

  // 延迟一点后自动进入四选一（让用户先看到单词）
  setTimeout(function(){ showStageQuiz(); }, 600);
}

// ---- 阶段2：四选一（主学习方式）----
function showStageQuiz(){
  cur.stage=STAGE.QUIZ;
  var it=cur.items[cur.idx];
  var sc=document.getElementById('wordCard');

  // 第11轮：四选一时隐藏会泄题的元素（释义+例句就在选项答案旁边），点“看提示”才显示
  var wpEl=document.getElementById('wordPos'); if(wpEl) wpEl.style.display='none';
  var wexEl=document.getElementById('wordExamples'); if(wexEl) wexEl.style.display='none';

  // 取词条释义：pos 是单词短释义；cn 是例句整句翻译，不能用作四选一选项
  function defText(o){ return (o.pos||o.cn||o.word); }
  var myDef=defText(it);

  // 构建干扰项：取3个释义与当前词不同的其他词（去重）
  var others=[], seen={};
  var candidates=shuffle(cur.items.filter(function(o){return o!==it;}));
  for(var i=0;i<candidates.length && others.length<3;i++){
    var d=defText(candidates[i]);
    if(d!==myDef && !seen[d]){ seen[d]=1; others.push(candidates[i]); }
  }
  var options=[it].concat(others);
  options=shuffle(options);

  // 渲染四选一区域（追加在卡片内容后面）——前面带“看提示”按钮（默认答案隐藏）
  var gridHtml='<div class="quiz-hint-row" id="quizHintRow"><button class="spell-reveal" id="quizHintBtn" onclick="toggleQuizHint()">👁 看提示</button></div>'
    +'<div class="quiz-area"><div class="qgrid" id="qgrid">';
  options.forEach(function(opt){
    gridHtml+='<div class="qopt" data-word="'+esc(opt.word)+'">'+esc(defText(opt))+'</div>';
  });
  gridHtml+='</div></div>';

  // 如果 stageContent 当前只有卡片内容，追加四选一区域
  var content=document.getElementById('stageContent');
  var existingQuiz=document.querySelector('.quiz-area');
  if(!existingQuiz){
    content.insertAdjacentHTML('beforeend', gridHtml);
  }

  // 绑定选项点击
  setTimeout(function(){
    var opts=document.querySelectorAll('#qgrid .qopt');
    opts.forEach(function(opt){
      opt.onclick=function(){ handleQuizAnswer(this, opt.getAttribute('data-word')===it.word, opt.getAttribute('data-word')); };
    });
  }, 50);

  hideThumb(); // 四选一时不需要固定底栏
}

/** 第11轮：四选一"看提示"——默认释义/例句隐藏，点一下显示（想抄答案也得自己动手） */
function toggleQuizHint(){
  var wp=document.getElementById('wordPos');
  var wex=document.getElementById('wordExamples');
  var btn=document.getElementById('quizHintBtn');
  var showing = wp ? wp.style.display!=='none' : (wex && wex.style.display!=='none');
  if(wp) wp.style.display = showing?'none':'';
  if(wex) wex.style.display = showing?'none':'';
  if(btn) btn.textContent = showing?'👁 看提示':'🙈 收起提示';
  Sound.play('click');
}

/**
 * 处理四选一答案
 */
function handleQuizAnswer(btn, isCorrect, chosenWord){
  if(cur.ws.quizAnswered && cur.stage===STAGE.QUIZ) return; // 防重复点
  var it=cur.items[cur.idx];

  if(isCorrect){
    // 答对了！
    cur.ws.quizAnswered=true;
    cur.ws.quizResult='correct';
    btn.dataset.done='1';
    btn.classList.add('right','pop2');
    Sound.play('correct'); vibe(20);
    addXp(5);

    // 连击计数
    cur.combo++;
    cur.correctStreak++;
    Sound.addCombo();
    updateComboDisplay();

    // 锁定其他选项
    lockAllOptions();

    // 延迟进入解释阶段（完成时才记入学过）
    setTimeout(function(){ showStageExplain(); }, 500);
  } else {
    // 答错了
    cur.ws.wrongCount++;
    cur.ws.quizResult='wrong';
    cur.combo=0;
    cur.correctStreak=0;
    Sound.resetCombo();
    updateComboDisplay();

    btn.dataset.done='1';
    btn.classList.add('wrong','shake');
    flashWrong();
    Sound.play('wrong'); vibe(40);

    // 不立刻显示正确答案，让用户可以继续尝试
    setTimeout(function(){
      btn.classList.remove('wrong','shake');
      btn.dataset.done='';
      // 显示正确答案高亮
      var allOpts=document.querySelectorAll('#qgrid .qopt');
      for(var i=0;i<allOpts.length;i++){
        if(allOpts[i].getAttribute('data-word')===it.word){
          allOpts[i].classList.add('right');
          allOpts[i].dataset.done='1';
          break;
        }
      }
      // 答错也进入解释阶段（完成时才记入学过）
      cur.ws.quizAnswered=true;
      setTimeout(function(){ showStageExplain(); }, 800);
    }, 600);
  }
}

function lockAllOptions(){
  var opts=document.querySelectorAll('#qgrid .qopt');
  opts.forEach(function(opt){ opt.style.pointerEvents='none'; });
}

// ---- 阶段3：解释面板 ----
function showStageExplain(){
  cur.stage=STAGE.EXPLAIN;
  var it=cur.items[cur.idx];
  var sc=document.getElementById('wordCard');

  // 决定是否需要拼写
  determineSpellingNeed();

  // 构建解释面板HTML
  // 第13轮：卡片上方已经渲染了 3 条例句（wordExamples）和词性（wordPos），
  // 这里不再重复推「例句」「词性」标签，只保留「助记」（story/tip，卡片上没有的内容）
  var tabs=[];
  var exs=getExamples(it);
  if((it.story||it.tip)) tabs.push(['助记', '<div>'+(esc(it.story)||'')+'</div><div style="margin-top:6px;color:var(--mut)">'+(esc(it.tip)||'')+'</div>']);

  var explainHtml='<div class="detail" style="display:block">';
  if(tabs.length>0){
    explainHtml+='<div class="dtabs" id="dtabs">';
    tabs.forEach(function(t,i){
      explainHtml+='<div class="dt'+(i===0?' on':'')+'" data-i="'+i+'">'+t[0]+'</div>';
    });
    explainHtml+='</div>';
    explainHtml+='<div class="dpanel on" id="dpanel">'+tabs[0][1]+'</div>';
  }
  // 第13轮：整句翻译 cn 与例句1的中文翻译是同一句，只在卡片上没有任何例句时才补显示
  var coreHtml=(!exs.length && it.cn && !document.getElementById('wordCore')) ? '<div class="core" style="margin-bottom:10px">'+esc(it.cn)+'</div>' : '';
  explainHtml+='</div>';

  // 替换或追加解释内容到卡片
  if(tabs.length>0 || coreHtml){
    var existingDetail=document.querySelector('.detail');
    if(!existingDetail){
      var content=document.getElementById('stageContent');
      // 移除四选一区域
      var quizArea=document.querySelector('.quiz-area');
      if(quizArea) quizArea.remove();
      // 第11轮：恢复四选一时隐藏的释义/例句，移除"看提示"按钮
      var wpEl2=document.getElementById('wordPos'); if(wpEl2) wpEl2.style.display='';
      var wexEl2=document.getElementById('wordExamples'); if(wexEl2) wexEl2.style.display='';
      var hintRow=document.getElementById('quizHintRow'); if(hintRow) hintRow.remove();
      content.insertAdjacentHTML('beforeend', coreHtml+explainHtml);
    }
    if(tabs.length>0) bindDetailTabs(tabs);
  }

  // 绑定详情标签
  bindDetailTabs(tabs);

  // 显示底部操作栏（解释阶段）
  showThumbExplain();
}

function bindDetailTabs(tabs){
  if(!tabs || !tabs.length) return;
  var box=document.getElementById('dtabs'); var panel=document.getElementById('dpanel');
  if(!box) return;
  function show(i){ panel.innerHTML=tabs[i][1]; panel.classList.add('on'); Array.prototype.forEach.call(box.querySelectorAll('.dt'),function(d,di){ d.classList.toggle('on',di===i); }); }
  box.querySelectorAll('.dt').forEach(function(d){ d.onclick=function(){ Sound.play('click'); show(parseInt(d.getAttribute('data-i'),10)); }; });
}

// 解释阶段统一出口：需要拼写就拼，否则进入下一词（"继续"按钮也走这里）
function explainContinue(){
  if(cur.ws.spellRequired && G.spell){ showStageSpell(); }
  else { proceedNext(); }
}

// ---- 阶段4：强制拼写 ----
function determineSpellingNeed(){
  // 新词一定拼
  if(cur.ws.isNew){ cur.ws.spellRequired=true; return; }
  // 答错一定拼
  if(cur.ws.quizResult==='wrong'){ cur.ws.spellRequired=true; return; }
  // 默认不拼（等用户选掌握度再决定）
  cur.ws.spellRequired=false;
}

function showStageSpell(){
  cur.stage=STAGE.SPELL;
  var it=cur.items[cur.idx];
  cur.ws.revealed=false;

  // 隐藏会透露单词的元素：单词本体/音标/英文例句(高亮露词)/卡片释义，只留拼写框里的中文释义作线索
  var wt=document.getElementById('wordText'); if(wt) wt.style.display='none';
  var wi=document.getElementById('wordIpa'); if(wi) wi.style.display='none';
  var wp=document.getElementById('wordPos'); if(wp) wp.style.display='none';
  var ex=document.getElementById('wordExamples'); if(ex) ex.style.display='none'; // 第11轮：隐藏整个例句容器（旧写法只隐藏第1条，2/3条仍露词）

  // 构建拼写填空题
  var hintCn=it.pos||it.cn||it.word;   // 用短释义作线索，不用整句翻译
  var blankHtml='_ '.repeat(it.word.length);
  var exSentence='';
  if(it.en){
    // 把句子中的单词替换为空格
    exSentence=it.en.replace(new RegExp('\\b'+escapeRegExp(it.word)+'\\b','i'), '<span class="blank">'+blankHtml+'</span>');
  }

  var spellHtml='<div class="spell-box" id="spellBox">'
    +'<div class="lab">✏️ 拼写练习</div>'
    +'<div class="hint-cn">'+esc(hintCn)+'</div>'
    +(exSentence?'<div class="hint-ex">'+exSentence+'</div>':'')
    +'<div class="spell-actions"><button class="spell-reveal" id="spellRevealBtn" onclick="toggleSpellReveal()">👁 显示单词</button></div>'
    +'<input type="text" id="spellInput" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" placeholder="输入英文单词">'
    +'<div class="res" id="spellRes"></div>'
    +'<div class="hint-text" id="spellHint"></div>'
    +'<button class="spell-btn" id="spellSubmitBtn" onclick="checkSpell()">确认</button>'
    +'</div>';

  // 替换内容
  var content=document.getElementById('stageContent');
  var existingSpell=document.getElementById('spellBox');
  if(existingSpell) existingSpell.remove();
  var existingDetail=document.querySelector('.detail');
  if(existingDetail) existingDetail.remove();
  var existingQuiz=document.querySelector('.quiz-area');
  if(existingQuiz) existingQuiz.remove();

  content.insertAdjacentHTML('beforeend', spellHtml);

  // 聚焦输入框并滚到可视区中央（避免手机键盘遮挡）
  setTimeout(function(){
    var inp=document.getElementById('spellInput');
    if(inp){ inp.focus(); if(inp.scrollIntoView){ try{ inp.scrollIntoView({block:'center'}); }catch(e){} } }
  }, 200);

  // 显示拼写专用底栏
  showThumbSpell();
}

// 点击"显示单词"：默认隐藏，点一下才显示并朗读；再点收起
function toggleSpellReveal(){
  var wt=document.getElementById('wordText');
  var wi=document.getElementById('wordIpa');
  var btn=document.getElementById('spellRevealBtn');
  var revealing = wt && wt.style.display==='none';
  if(wt) wt.style.display = revealing ? '' : 'none';
  if(wi) wi.style.display = revealing ? '' : 'none';
  if(btn) btn.textContent = revealing ? '🙈 已显示' : '👁 显示单词';
  if(revealing){ Pron.speak(cur.items[cur.idx].word); }
  Sound.play('click');
}

function checkSpell(){
  var it=cur.items[cur.idx];
  var inp=document.getElementById('spellInput');
  var res=document.getElementById('spellRes');
  var hint=document.getElementById('spellHint');
  if(!inp) return;

  var answer=inp.value.trim().toLowerCase();
  var correct=it.word.toLowerCase();

  if(answer===correct){
    if(cur.ws.spellRepeat>1){
      // "再拼3遍"模式中：这一遍拼对了，还剩 spellRepeat-1 遍
      cur.ws.spellRepeat--;
      var doneTimes=3-cur.ws.spellRepeat;
      res.className='res ok';
      res.textContent='✓ 第 '+doneTimes+'/3 遍正确，再拼 '+cur.ws.spellRepeat+' 遍';
      hint.textContent='';
      inp.className='correct';
      Sound.play('correct'); vibe(15);
      // 短暂展示✓后清空输入框，继续拼下一遍
      setTimeout(function(){
        if(cur.stage!==STAGE.SPELL) return;
        inp.value=''; inp.className='';
        try{ inp.focus(); }catch(e){}
      },420);
    } else {
      // 最终拼对：再拼3遍的第3遍完成，或一次不错的直接过
      var finishedRepeat=(cur.ws.spellRepeat===1);
      cur.ws.spellRepeat=0;
      inp.className='correct';
      inp.disabled=true;
      res.className='res ok';
      res.textContent=finishedRepeat?'🎉 3/3 遍全部拼对！':'✓ 正确！';
      Sound.play('spellCorrect');
      vibe(20);
      addXp(8);
      G.study.spellToday++;
      saveStudy();

      // 隐藏提交按钮
      var btn=document.getElementById('spellSubmitBtn');
      if(btn) btn.style.display='none';

      // 更新底栏为"继续"
      showThumbExplainDone();

      cur.ws.spellAttempts=0;
    }
  } else {
    // 拼写错误：❌弹出 + 噔噔音效 + 抖动；开启"再拼3遍"
    cur.ws.spellAttempts++;
    cur.ws.spellRepeat=3; // 拼错了，需连拼对3遍才能过（中途再错重置回3）
    flashWrong();
    Sound.play('wrong'); vibe(40);
    inp.className='wrong-shake';
    setTimeout(function(){
      if(cur.stage!==STAGE.SPELL) return;
      inp.className='';
      try{ inp.select(); }catch(e){} // 选中错误内容，直接重敲无需先删
    },450);
    res.className='res err';
    // 分级提示
    if(cur.ws.spellAttempts>=3){
      // 连错3次：亮出完整答案（仍需照着拼对3遍，强化记忆）
      res.textContent='❌ 拼错了，再拼 3 遍 · 答案：'+it.word;
      hint.textContent='照着答案输入，把它记住';
    } else if(cur.ws.spellAttempts===2){
      // 第2次拼错：显示首字母提示
      var hintStr=buildSpellHint(correct,2);
      res.textContent='❌ 拼错了，再拼 3 遍 · 提示：'+hintStr;
      hint.textContent='';
    } else {
      // 第1次拼错：轻微提示
      res.textContent='❌ 拼错了，需再拼 3 遍';
      hint.textContent='提示：共 '+it.word.length+' 个字母';
    }
  }
}

function buildSpellHint(word, level){
  if(level>=2) return '首字母是 '+word[0].toUpperCase()+'.';
  return '以 '+word[0].toUpperCase()+' 开头，'+word.length+' 个字母';
}

// ---- 阶段5：进入下一词 ----
function proceedNext(){
  cur.stage=STAGE.DONE;
  addSeen('en', idOf(cur.deck, cur.items[cur.idx]));
  saveLast();

  if(cur.idx>=cur.items.length-1){
    finishWord();
  } else {
    cur.idx++;
    Sound.play('next');
    enterLearnStage();
  }
}

function finishWord(){
  Sound.play('complete');
  addXp(10);
  G.last=null; zs(LAST_KEY,null);
  toast('本轮完成！+10 XP');
  hideThumb();
  setTimeout(renderHome, 600);
}

/* ============ 底部栏管理（按阶段切换） ============ */
function hideThumb(){ document.getElementById('thumb').classList.remove('on'); document.getElementById('thumbInner').innerHTML=''; }

/** 解释阶段底栏：发音 + 上一个 + 继续（继续会先判断是否需要拼写） */
function showThumbExplain(){
  var thumb=document.getElementById('thumb'); var inner=document.getElementById('thumbInner');
  thumb.classList.add('on');
  inner.innerHTML='<div class="thumb-explain">'
    +'<button class="tbtn tbtn-spk speaker" onclick="replayWord()">🔊</button>'
    +'<button class="tbtn tbtn-nav" onclick="prevWord()" '+(cur.idx<=0?'style="visibility:hidden"':'')+'>←</button>'
    +'<button class="tbtn tbtn-next" onclick="explainContinue()">继续 →</button>'
    +'</div>';
}

/** 拼写完成后底栏 */
function showThumbExplainDone(){
  var thumb=document.getElementById('thumb'); var inner=document.getElementById('thumbInner');
  thumb.classList.add('on');
  inner.innerHTML='<div class="thumb-explain">'
    +'<button class="tbtn tbtn-spk speaker" onclick="replayWord()">🔊</button>'
    +'<button class="tbtn tbtn-nav" onclick="prevWord()" '+(cur.idx<=0?'style="visibility:hidden"':'')+'>←</button>'
    +'<button class="tbtn tbtn-next" style="background:linear-gradient(135deg,var(--green),#2fd6c0)" onclick="proceedNext()">继续 ✓</button>'
    +'</div>';
}

/** 拼写阶段底栏 */
function showThumbSpell(){
  var thumb=document.getElementById('thumb'); var inner=document.getElementById('thumbInner');
  thumb.classList.add('on');
  var forced = (cur.ws.isNew||cur.ws.quizResult==='wrong'); // 强制拼写时不可跳过
  inner.innerHTML='<div class="thumb-spell">'
    +(forced?'':'<button class="tbtn tbtn-skip" onclick="skipSpell()">跳过拼写</button>')
    +'<button class="tbtn tbtn-submit" onclick="checkSpell()">提交拼写</button>'
    +'</div>';
  // 绑定回车键提交
  var inp=document.getElementById('spellInput');
  if(inp){
    inp.onkeydown=function(e){ if(e.key==='Enter'){ e.preventDefault(); checkSpell(); } };
  }
}

function skipSpell(){
  // 仅非强制拼写时可跳过，且跳过时不奖励拼写 XP
  cur.ws.spellRequired=false;
  proceedNext();
}

function prevWord(){
  if(cur.idx>0){ cur.idx--; Sound.play('back'); enterLearnStage(); }
}

function replayWord(){ Sound.play('click'); Pron.stop(); Pron.speak(cur.items[cur.idx].word); }
function favoriteCurrent(){
  if(!cur||cur.deck.key!=='en') return;
  var w=cur.items[cur.idx].word;
  var i=G.fav.indexOf(w);
  if(i>=0){ G.fav.splice(i,1); } else { G.fav.push(w); Sound.play('fav'); }
  zs(FAV_KEY,G.fav);
  document.getElementById('wFav').classList.toggle('on', i<0);
}
function toggleFav(){ favoriteCurrent(); }
function preloadAround(){
  var i=cur.idx;
  [i,i+1,i+2].forEach(function(k){
    var it=cur.items[k]; if(!it) return;
    preloadImg(it);
  });
  var nx=cur.items[i+1]; if(nx) Pron.preload(nx.word);
}

/* ============ 工具函数 ============ */
function shuffle(a){ for(var i=a.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=a[i];a[i]=a[j];a[j]=t; } return a; }
function escapeRegExp(str){ return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

/* ============ AI 动态阅读（列表 + 单篇） ============ */
function escAttr(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function renderNewsList(){
  document.getElementById('newsListWrap').style.display='';
  document.getElementById('newsCardWrap').style.display='none';
  var items=cur.items;
  var raw=rawCache[cur.deck.src]||{};
  var updated=raw.updated||'';
  // 顶部 meta（今日更新日期 / 新增 / 已读 进度）
  var newCnt=items.filter(function(it){return it.is_new||it.date===updated;}).length;
  var readCnt=items.filter(function(it){return G.newsRead.indexOf(newsId(it))>=0;}).length;
  var meta=document.getElementById('newsListMeta');
  meta.innerHTML=
    '<span class="m-pill">📅 今日更新 · '+escAttr(updated||'—')+'</span>'+
    '<span class="m-pill">新增 '+newCnt+' 条</span>'+
    '<span class="m-pill">已读 '+readCnt+' / '+items.length+'</span>'+
    '<span class="m-pill">🔥 重要 '+items.filter(function(c){return c.importance==='high';}).length+'</span>';
  // 标题旁附"今天值得看"提示
  document.getElementById('newsListTitle').textContent='今日 AI / 科技精选';
  // 渲染卡片
  var box=document.getElementById('newsList'); var html='';
  items.forEach(function(it, idx){
    var cat=it.category||'AI';
    var imp=it.importance||'med';
    var isNew=it.is_new || (it.date===updated);
    var read=G.newsRead.indexOf(newsId(it))>=0;
    var src=it.source||it.tag||'';
    var summary=(it.summary||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').slice(0,140);
    html+='<div class="news-list-card'+(read?' read':'')+(imp==='high'?' imp':'')+'" data-idx="'+idx+'">'
      + (read?'<span class="read-mark read"></span>':'<span class="read-mark"></span>')
      +'<div class="top-row">'
        +'<span class="cat-pill cat-'+escAttr(cat)+'">'+escAttr(cat)+'</span>'
        +(imp==='high'?'<span class="imp-high-pill">🔥 重要</span>':'')
        +(isNew?'<span class="m-pill" style="font-size:11px;padding:2px 8px">NEW</span>':'')
      +'</div>'
      +'<div class="ttl">'+escAttr(it.title_cn||it.title||'')+'</div>'
      +'<div class="ex">'+escAttr(summary)+'</div>'
      +'<div class="row-meta"><span class="src">📰 '+escAttr(src)+(it.date?' · '+escAttr(it.date):'')+'</span><span>点击阅读 →</span></div>'
    +'</div>';
  });
  box.innerHTML=html;
  // 列表卡片点击 → 切到单篇
  box.querySelectorAll('.news-list-card').forEach(function(el){
    el.addEventListener('click',function(){
      Sound.play('click');
      var idx=parseInt(el.getAttribute('data-idx'),10)||0;
      cur.idx=idx;
      renderNews();
    });
  });
}

function renderNews(){
  document.getElementById('newsListWrap').style.display='none';
  document.getElementById('newsCardWrap').style.display='';
  var it=cur.items[cur.idx];
  document.getElementById('newsTag').textContent=(it.category?'【'+it.category+'】':'')+(it.tag||'AI');
  document.getElementById('newsTitle').textContent=it.title_cn||it.title||'';
  document.getElementById('newsDate').textContent=it.date?('发布：'+it.date):'';
  // 第15轮：全屏全文版——正文按句分段渲染，impact/uses 做成强调块
  var paras=paraSplit(it.summary||'');
  var h='';
  paras.forEach(function(p){ h+='<div class="np">'+escAttr(p)+'</div>'; });
  if(!paras.length) h+='<div class="np" style="color:var(--mut)">（暂无正文摘要，可点下方原文查看全文）</div>';
  var imp=it.impact||it.why_it_matters||'';
  var use=it.uses||it.how_to_use||'';
  if(imp||use){
    h+='<div class="np-label">划重点</div>';
    if(imp) h+='<div class="nimpact">📌 为什么重要：'+escAttr(imp)+'</div>';
    if(use) h+='<div class="nuses">💡 对我有什么用：'+escAttr(use)+'</div>';
  }
  document.getElementById('newsBody').innerHTML=h;
  var wrap=document.getElementById('newsSrcWrap');
  var src=document.getElementById('newsSrc');
  if(it.source_url){ src.href=it.source_url; wrap.style.display=''; }
  else wrap.style.display='none';
  updateProgress('progNews', cur.idx, cur.items.length);
  document.getElementById('newsPrev').style.visibility=cur.idx>0?'visible':'hidden';
  document.getElementById('newsNext').textContent=cur.idx===cur.items.length-1?'返回列表 ✓':'下一篇 →';
  markNewsRead(it);
  var head=document.getElementById('newsHead');
  var isNew = it.is_new || (it.date===todayStr());
  var read = G.newsRead.indexOf(newsId(it))>=0;
  var raw = rawCache[cur.deck.src];
  var updated = (raw && raw.updated) || it.date || '';
  head.innerHTML='今日更新 · '+updated+(isNew?'<span class="new">NEW</span>':'')+(read?'<span style="color:var(--mut);margin-left:8px">已读</span>':'<span class="dot"></span>未读');
  try{ window.scrollTo(0,0); }catch(e){}
}
/* 第15轮：把一段摘要按句号切成 2~3 个自然段（不依赖 lookbehind 正则，兼容老 WebView） */
function paraSplit(t){
  t=(t||'').replace(/<[^>]+>/g,'').replace(/\s+/g,' ').trim();
  if(!t) return [];
  var out=[],buf='',i,ch;
  for(i=0;i<t.length;i++){
    ch=t.charAt(i); buf+=ch;
    if(ch==='。'||ch==='！'||ch==='？'||ch==='!'||ch==='?'){
      if(buf.trim().length>=70){ out.push(buf.trim()); buf=''; }
    }
  }
  if(buf.trim()) out.push(buf.trim());
  return out;
}
function newsId(it){ return newsIdKey(it); }
function newsIdKey(it){ if(!it) return ''; return it.source_url || (it.title||''); }
function markNewsRead(it){
  var id=newsId(it);
  if(G.newsRead.indexOf(id)<0){ G.newsRead.push(id); zs(NEWSREAD_KEY,G.newsRead); }
  addSeen('ai', idOf(cur.deck, it));
}
document.getElementById('newsNext').addEventListener('click',function(){
  if(cur.idx>=cur.items.length-1){ Sound.play('complete'); renderNewsList(); }
  else { cur.idx++; Sound.play('next'); renderNews(); }
});
document.getElementById('newsPrev').addEventListener('click',function(){ if(cur.idx>0){cur.idx--;Sound.play('back');renderNews();} });

/* ============ 知识卡片阅读（站内全文） ============ */
function renderArticle(){
  var it=cur.items[cur.idx];
  document.getElementById('artCat').textContent=it.cat||'知识';
  document.getElementById('artTitle').textContent=it.title;
  var sum=document.getElementById('artSummary');
  sum.textContent=it.summary||'';
  sum.style.display='';
  var wrap=document.getElementById('artSrcWrap');
  var link=document.getElementById('artLink');
  if(it.href){ link.href=it.href; wrap.style.display=''; }
  else { wrap.style.display='none'; }
  updateProgress('progArt', cur.idx, cur.items.length);
  document.getElementById('artPrev').style.visibility=cur.idx>0?'visible':'hidden';
  document.getElementById('artNext').textContent=cur.idx===cur.items.length-1?'完成阅读 ✓':'下一篇 →';
  loadArticleBody(it);
  addSeen('kn', idOf(cur.deck, it));
}
function loadArticleBody(it){
  var body=document.getElementById('artBody');
  if(!it.href){ body.innerHTML=''; return; }
  body.innerHTML='<div class="loading">正在加载全文…</div>';
  if(artCache[it.href]){ injectArticle(it); return; }
  fetch(it.href).then(function(r){ return r.text(); }).then(function(html){
    try{
      var doc=new DOMParser().parseFromString(html,'text/html');
      var wrap=doc.querySelector('.wrap');
      if(!wrap){ body.innerHTML='<div class="summary">无法解析正文</div>'; return; }
      ['header','.back','.note'].forEach(function(sel){
        wrap.querySelectorAll(sel).forEach(function(e){ e.remove(); });
      });
      var h2=wrap.querySelector('h2'); if(h2) h2.remove();
      wrap.querySelectorAll('blockquote').forEach(function(b){ b.remove(); });
      artCache[it.href]=wrap.innerHTML;
      injectArticle(it);
    }catch(e){ body.innerHTML='<div class="summary">加载失败</div>'; }
  }).catch(function(){ body.innerHTML='<div class="summary">加载失败，请检查网络后重试</div>'; });
}
function injectArticle(it){
  var body=document.getElementById('artBody');
  body.innerHTML=artCache[it.href]||'';
  body.scrollTop=0;
  // 全文已含开头，隐藏摘要避免重复
  var sum=document.getElementById('artSummary');
  if(sum) sum.style.display='none';
}
document.getElementById('artNext').addEventListener('click',function(){
  if(cur.idx>=cur.items.length-1){ toast('知识卡片阅读完成！'); renderHome(); }
  else { cur.idx++; Sound.play('next'); renderArticle(); }
});
document.getElementById('artPrev').addEventListener('click',function(){ if(cur.idx>0){cur.idx--;Sound.play('back');renderArticle();} });

/* ============ 备份 ============ */
function exportData(){
  var data={xp:G.xp,tasks:G.tasks,study:G.study,fav:G.fav,newsRead:G.newsRead,exportedAt:new Date().toISOString()};
  var blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='zheshao-study-backup.json';a.click();
  toast('已导出备份'); Sound.play('click');
}
function importData(file){
  var r=new FileReader();
  r.onload=function(){
    try{
      var d=JSON.parse(r.result);
      if('xp' in d) G.xp=d.xp;
      if('study' in d) G.study=d.study;
      if('tasks' in d) G.tasks=d.tasks;
      if('fav' in d) G.fav=d.fav;
      if('newsRead' in d) G.newsRead=d.newsRead;
      zs(XP_KEY,G.xp); saveStudy(); saveTasks(); zs(FAV_KEY,G.fav); zs(NEWSREAD_KEY,G.newsRead);
      renderHome(); toast('导入成功');
    }catch(e){ toast('文件格式错误'); }
  };
  r.readAsText(file);
}
function clearData(){
  if(!confirm('确定清空所有本地进度（等级/XP/任务/收藏）？此操作不可恢复！'))return;
  [XP_KEY,STUDY_KEY,TASKS_KEY,FAV_KEY,NEWSREAD_KEY,LAST_KEY].forEach(function(k){localStorage.removeItem(ZS_PREFIX+k);});
  location.reload();
}
document.getElementById('gearBtn').addEventListener('click',function(){ Sound.play('click'); openSettings(); });
document.getElementById('impFile').addEventListener('change',function(e){if(e.target.files[0])importData(e.target.files[0]);});

/* ============ 工具 ============ */
var toastTimer;
function toast(msg){var t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');clearTimeout(toastTimer);toastTimer=setTimeout(function(){t.classList.remove('on');},1600);}
/* 第10轮：错误反馈——❌叉叉弹出（拼写错/四选一选错时调用） */
var wrongFlashTimer;
function flashWrong(){
  var el=document.getElementById('wrongFlash');
  if(!el) return;
  el.classList.remove('on'); void el.offsetWidth; el.classList.add('on');
  clearTimeout(wrongFlashTimer);
  wrongFlashTimer=setTimeout(function(){ el.classList.remove('on'); },820);
}
function esc(s){return String(s==null?'':s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}

/* ============ 启动 ============ */
function startFromUrl(){
  var params=new URLSearchParams(window.location.search);
  var deck=params.get('deck');
  if(!deck) return false;
  if(!DECKS.some(function(d){return d.key===deck;})) return false;
  setTimeout(function(){ startDeck(deck); }, 80);
  return true;
}
/* ===== 首次手势解锁：WebAudio 与 <audio> 都要解锁，否则手机浏览器点啥都没声 ===== */
function firstGesture(){
  Sound.unlock(); Pron.unlock();
  window.removeEventListener('pointerdown',firstGesture);
  window.removeEventListener('touchstart',firstGesture);
  window.removeEventListener('mousedown',firstGesture);
  window.removeEventListener('click',firstGesture);
  window.removeEventListener('keydown',firstGesture);
}
window.addEventListener('pointerdown',firstGesture);
window.addEventListener('touchstart',firstGesture);
window.addEventListener('mousedown',firstGesture);
window.addEventListener('click',firstGesture);        // 只触发 click 的环境（部分移动端/键盘）也能解锁
window.addEventListener('keydown',firstGesture);

/* ===== 第12轮：键盘操作 —— 回车=继续/下一词，1~4=四选一，←=上一个（网页端不用一直抓鼠标） ===== */
window.addEventListener('keydown',function(e){
  if(!cur||curView!=='word'||!cur.deck||cur.deck.key!=='en') return;
  var tag=(e.target&&e.target.tagName)?e.target.tagName.toLowerCase():'';
  var typing=(tag==='input'||tag==='textarea');

  if(e.key==='Enter'){
    if(typing) return;   // 拼写输入框自己的 onkeydown 负责提交，这里不处理避免双重触发
    if(cur.stage===STAGE.EXPLAIN){ e.preventDefault(); explainContinue(); return; }
    if(cur.stage===STAGE.SPELL){
      // 拼写完成态：输入框已禁用（3/3 全对），回车=继续下一词
      var inp=document.getElementById('spellInput');
      if(inp&&inp.disabled){ e.preventDefault(); proceedNext(); }
      return;
    }
    return;              // CARD 会自动进 QUIZ；QUIZ 必须先选一个选项
  }
  if(typing) return;

  if(cur.stage===STAGE.QUIZ&&/^[1-4]$/.test(e.key)){
    var opts=document.querySelectorAll('#qgrid .qopt');
    var o=opts[parseInt(e.key,10)-1];
    if(o&&!o.dataset.done){ e.preventDefault(); o.click(); }
    return;
  }
  if(e.key==='ArrowLeft'&&cur.idx>0&&(cur.stage===STAGE.CARD||cur.stage===STAGE.EXPLAIN||cur.stage===STAGE.SPELL)){
    e.preventDefault(); prevWord();
  }
});

/* ===== 全站按钮音效：任何按钮点击都出声；已有专属音效的按钮不重复叠加 ===== */
(function(){
  var SEL='button,.btn,.tbtn,.qopt,.chip,.tile,.card,.nav,.tab,.iconbtn,.opt,.optbtn,[data-key]';
  document.addEventListener('click',function(e){
    if(!G.sound) return;
    var t=e.target;
    if(!t||typeof t.closest!=='function') return;
    if(!t.closest(SEL)) return;
    if(Sound.recentlyPlayed()) return;
    Sound.play('click');
  },false);
})();

Sound.setOn(G.sound);
if(!startFromUrl()) renderHome();
