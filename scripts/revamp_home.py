# -*- coding: utf-8 -*-
"""一键翻新 index.html：首页成长空间 + 知识地图 + 文章阅读体验增强。
不改任何文章正文(.lesson)，只重写 s-home / s-know 结构、追加 CSS、追加运行时 JS。
"""
import re, json, subprocess, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
raw = open(HTML, encoding='utf-8').read()

# ---------- 1. 自动提取 ATLAS（所有 art-* 长文） ----------
arts = []
for m in re.finditer(r'<section class="screen" id="(art-[^"]+)">(.*?)</section>', raw, re.S):
    sid = m.group(1)
    body = m.group(2)
    h1 = re.search(r'<h1>(.*?)</h1>', body, re.S)
    meta = re.search(r'class="ah-meta">([^<]+)</div>', body)
    if not h1:
        continue
    t = re.sub(r'<.*?>', '', h1.group(1)).strip()
    metatxt = meta.group(1).strip() if meta else ''
    arts.append({'id': sid, 't': t, 'm': metatxt})
print('提取到长文 %d 篇' % len(arts))
atlas_js = 'const ATLAS = ' + json.dumps(arts, ensure_ascii=False) + ';'

# ---------- 2. 新首页 s-home ----------
NEWHOME = '''    <section class="screen active" id="s-home">
      <!-- REV-GROWTH-HOME v1 -->
      <div class="gwrap">
        <header class="ghero">
          <div class="ghello">
            <div class="gavatar">喆</div>
            <div class="ghello-txt">
              <div class="gwave" id="gWave">晚上好，泽少 👋</div>
              <div class="gsub">泽少的每日成长空间</div>
            </div>
            <div class="glvl" id="gLvl">Lv.5</div>
          </div>
          <div class="gstats">
            <div class="gstat"><div class="gnum" id="gStreak">38</div><div class="glbl">🔥 连续学习(天)</div></div>
            <div class="gstat"><div class="gnum" id="gRead">12</div><div class="glbl">📚 已读文章</div></div>
            <div class="gstat"><div class="gnum" id="gTotal">120</div><div class="glbl">🧩 收录内容</div></div>
          </div>
          <div class="gprogress">
            <div class="gp-row"><span>今日成长</span><span id="gProgTxt">0 / 3</span></div>
            <div class="gp-track"><div class="gp-bar" id="gProgBar"></div></div>
          </div>
        </header>

        <div class="section-title pad">今日探索 <span class="more">约 15 分钟</span></div>
        <div class="explore">
          <a class="ecard eco-ai" href="ai-news/index.html" onclick="markToday('ai')">
            <div class="ec-cover"><span class="ec-emoji">⚡</span></div>
            <div class="ec-body">
              <div class="ec-kicker">AI 动态</div>
              <div class="ec-title">今日 AI 圈发生了什么</div>
              <div class="ec-meta"><span>📰 10 条精选</span><span>⏱ 2 分钟</span></div>
            </div>
            <span class="ec-go">开始 →</span>
          </a>
          <a class="ecard eco-word" href="ielts/day78.html" onclick="markToday('word')">
            <div class="ec-cover"><span class="ec-emoji">🔤</span></div>
            <div class="ec-body">
              <div class="ec-kicker">英语词海</div>
              <div class="ec-title">20 个高频单词 + 发音</div>
              <div class="ec-meta"><span>🗣 带真人音频</span><span>⏱ 5 分钟</span></div>
            </div>
            <span class="ec-go">开始 →</span>
          </a>
          <a class="ecard eco-art" onclick="goArt('art-tech-llm');markToday('art')">
            <div class="ec-cover"><span class="ec-emoji">📖</span></div>
            <div class="ec-body">
              <div class="ec-kicker">深度阅读</div>
              <div class="ec-title">一篇让你开窍的长文</div>
              <div class="ec-meta"><span>🧠 通识知识</span><span>⏱ 8 分钟</span></div>
            </div>
            <span class="ec-go">开始 →</span>
          </a>
        </div>

        <div class="section-title pad">🗺️ 知识地图 <span class="more" onclick="goTab('s-know')">进入中心</span></div>
        <div class="kmap-mini">
          <div class="km-mini km-ai" onclick="goKnow('tech')"><span class="km-emoji">🤖</span><span class="km-name">AI科技</span></div>
          <div class="km-mini km-hist" onclick="goKnow('hist')"><span class="km-emoji">🏛️</span><span class="km-name">历史文明</span></div>
          <div class="km-mini km-geo" onclick="goKnow('geo')"><span class="km-emoji">🌍</span><span class="km-name">地理世界</span></div>
          <div class="km-mini km-psy" onclick="goKnowPsyEq()"><span class="km-emoji">🧠</span><span class="km-name">心理认知</span></div>
          <div class="km-mini km-poem" onclick="goKnow('poem')"><span class="km-emoji">📜</span><span class="km-name">文学审美</span></div>
          <div class="km-mini km-sport" onclick="goKnowSport()"><span class="km-emoji">🏃</span><span class="km-name">运动健康</span></div>
        </div>

        <div class="section-title pad">💡 今日金句</div>
        <div class="quote-card" id="dailyQuote">加载中...</div>

        <div class="section-title pad">最近更新 <span class="more" onclick="goTab('s-news')">查看全部</span></div>
        <div class="recent-list">
          <a class="recent-row" href="ai-news/ai-news-2026-07-24.html"><div class="ri">🤖</div><div class="rc"><div class="rt">AI 动态 · 精选10条（已核实）</div><div class="rm">全部附官方来源 · 新上线</div></div><div class="ra">›</div></a>
          <a class="recent-row" onclick="goKnowPsyEq()"><div class="ri">🧠</div><div class="rc"><div class="rt">心理学与情商专题</div><div class="rm">认知 · 情绪 · 沟通</div></div><div class="ra">›</div></a>
          <a class="recent-row" onclick="goKnowSport()"><div class="ri">🏃</div><div class="rc"><div class="rt">运动健康专题</div><div class="rm">HYROX · 运动康复</div></div><div class="ra">›</div></a>
        </div>

        <div class="support home-support" id="supportHome">
          <h2>☕ 支持学习助手</h2>
          <p>如果这里对你有帮助，欢迎支持泽少继续把学习资料整理下去。</p>
          <img class="qr" src="assets/wechat.png" alt="微信赞赏码" loading="lazy" onclick="zoomQr(this)" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
          <div class="qr-fallback">微信赞赏码<br>放入 assets/wechat.png</div>
          <span class="label">微信赞赏码</span>
          <button class="wx" onclick="copyWx()">复制微信号 Harryalwayslucky</button>
          <div class="hint">在微信里打开本页，长按上方二维码即可打赏。</div>
        </div>

        <div class="footer">泽少学习助手<br>每天进步一点点</div>
      </div>
    </section>'''

# ---------- 3. 新知识中心 s-know ----------
NEWKNOW = '''    <section class="screen" id="s-know">
      <!-- REV-GROWTH-KNOW v1 -->
      <div class="topbar" style="position:static"><div class="brand"><div class="logo">🧠</div><div><div class="sub">六大领域 · 自由探索</div><h1>知识地图</h1></div></div></div>
      <div class="pad" style="margin-top:16px">
        <div class="kmap-banner">🗺️ 把知识当成一片大陆去探索 —— 点一张卡片，钻进对应领域</div>
        <div class="kmap-grid">
          <div class="kmap-card km-ai" onclick="goKnow('tech')">
            <div class="km-cover"><span>🤖</span></div>
            <div class="km-title">AI 科技</div>
            <div class="km-desc">大模型 · 算力 · 机器学习</div>
            <div class="km-foot"><span class="km-count" id="kmc-tech">3 篇</span><span class="km-enter">探索 →</span></div>
          </div>
          <div class="kmap-card km-hist" onclick="goKnow('hist')">
            <div class="km-cover"><span>🏛️</span></div>
            <div class="km-title">历史文明</div>
            <div class="km-desc">帝王将相 · 文明来路</div>
            <div class="km-foot"><span class="km-count" id="kmc-hist">10 篇</span><span class="km-enter">探索 →</span></div>
          </div>
          <div class="kmap-card km-geo" onclick="goKnow('geo')">
            <div class="km-cover"><span>🌍</span></div>
            <div class="km-title">地理世界</div>
            <div class="km-desc">板块 · 气候 · 城市</div>
            <div class="km-foot"><span class="km-count" id="kmc-geo">9 篇</span><span class="km-enter">探索 →</span></div>
          </div>
          <div class="kmap-card km-psy" onclick="goKnowPsyEq()">
            <div class="km-cover"><span>🧠</span></div>
            <div class="km-title">心理认知</div>
            <div class="km-desc">心理学 · 情商沟通</div>
            <div class="km-foot"><span class="km-count" id="kmc-psy">26 篇</span><span class="km-enter">探索 →</span></div>
          </div>
          <div class="kmap-card km-poem" onclick="goKnow('poem')">
            <div class="km-cover"><span>📜</span></div>
            <div class="km-title">文学审美</div>
            <div class="km-desc">诗词 · 楚辞 · 元曲</div>
            <div class="km-foot"><span class="km-count" id="kmc-poem">7 篇</span><span class="km-enter">探索 →</span></div>
          </div>
          <div class="kmap-card km-sport" onclick="goKnowSport()">
            <div class="km-cover"><span>🏃</span></div>
            <div class="km-title">运动健康</div>
            <div class="km-desc">HYROX · 康复 · 撸铁</div>
            <div class="km-foot"><span class="km-count" id="kmc-sport">15 篇</span><span class="km-enter">探索 →</span></div>
          </div>
          <div class="kmap-card km-ielts" onclick="goKnow('ielts')">
            <div class="km-cover"><span>📖</span></div>
            <div class="km-title">雅思单词</div>
            <div class="km-desc">77 天 · 1151 词 · 带音频</div>
            <div class="km-foot"><span class="km-count">77 天</span><span class="km-enter">背词 →</span></div>
          </div>
        </div>

        <!-- 展开容器（renderK 依赖，必须保留） -->
        <div class="klist hidden" id="klist-tech"></div>
        <div class="klist hidden" id="klist-poem"></div>
        <div class="klist hidden" id="klist-geo"></div>
        <div class="klist hidden" id="klist-psy"></div>
        <div class="klist hidden" id="klist-eq"></div>
        <div class="klist hidden" id="klist-ielts"></div>
        <div class="klist hidden" id="klist-sport"></div>
        <div class="klist hidden" id="klist-hist"></div>
      </div>
    </section>'''

# ---------- 4. 新增 CSS ----------
NEWCSS = '''
/* REV-GROWTH-CSS v1 */
.gwrap{padding-bottom:24px}
.ghero{margin:14px 16px 0;background:linear-gradient(135deg,#1c2742 0%,#0d1220 70%);border:1px solid var(--border);border-radius:var(--r-xl);padding:18px 16px 16px;position:relative;overflow:hidden;box-shadow:var(--sh-1)}
.ghero:before{content:"";position:absolute;right:-40px;top:-40px;width:160px;height:160px;background:radial-gradient(circle,rgba(201,168,106,.22),transparent 70%);pointer-events:none}
.ghello{display:flex;align-items:center;gap:12px}
.gavatar{width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,var(--gold),#8a5a2b);display:grid;place-items:center;font-weight:800;font-size:20px;color:#0B0F17;flex:none}
.ghello-txt{flex:1;min-width:0}
.gwave{font-size:17px;font-weight:800;color:var(--text-1);letter-spacing:.3px}
.gsub{font-size:12px;color:var(--text-3);margin-top:2px}
.glvl{font-size:13px;font-weight:800;color:#0B0F17;background:linear-gradient(135deg,var(--gold),#caa15a);padding:5px 11px;border-radius:var(--r-pill);flex:none;box-shadow:0 2px 8px rgba(201,168,106,.35)}
.gstats{display:flex;gap:8px;margin-top:16px}
.gstat{flex:1;background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:10px 4px;text-align:center}
.gnum{font-size:22px;font-weight:800;color:var(--gold);font-variant-numeric:tabular-nums;line-height:1.1}
.glbl{font-size:10.5px;color:var(--text-3);margin-top:4px;font-weight:600}
.gprogress{margin-top:14px}
.gp-row{display:flex;justify-content:space-between;font-size:12px;color:var(--text-2);margin-bottom:6px;font-weight:600}
.gp-track{height:8px;background:var(--surface-2);border-radius:var(--r-pill);overflow:hidden}
.gp-bar{height:100%;width:0;background:linear-gradient(90deg,var(--gold),#ffd98a);border-radius:var(--r-pill);transition:width .5s cubic-bezier(.4,0,.2,1)}
/* 今日探索卡片 */
.explore{margin:6px 16px 0;display:grid;gap:12px}
.ecard{display:flex;align-items:center;gap:14px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:14px;position:relative;overflow:hidden;transition:transform var(--t-fast),border-color var(--t-fast);text-decoration:none;color:inherit}
.ecard:active{transform:scale(.98);border-color:var(--border-strong)}
.ec-cover{width:54px;height:54px;border-radius:14px;display:grid;place-items:center;flex:none;box-shadow:var(--sh-1)}
.ec-emoji{font-size:26px}
.eco-ai .ec-cover{background:linear-gradient(135deg,#4F8DFF,#7C5CFF)}
.eco-word .ec-cover{background:linear-gradient(135deg,#2bb6a8,#1f7a8c)}
.eco-art .ec-cover{background:linear-gradient(135deg,#ff8a3d,#ff5252)}
.ec-body{flex:1;min-width:0}
.ec-kicker{font-size:11px;font-weight:700;color:var(--gold);letter-spacing:.5px}
.ec-title{font-size:15px;font-weight:700;color:var(--text-1);margin-top:3px}
.ec-meta{font-size:11px;color:var(--text-3);margin-top:4px;display:flex;gap:10px;flex-wrap:wrap}
.ec-go{font-size:13px;font-weight:800;color:var(--gold);flex:none;white-space:nowrap}
/* 首页知识地图迷你卡 */
.kmap-mini{margin:8px 16px 0;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.km-mini{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:14px 8px;text-align:center;cursor:pointer;transition:transform var(--t-fast),border-color var(--t-fast)}
.km-mini:active{transform:scale(.96);border-color:var(--border-strong)}
.km-emoji{font-size:26px;display:block}
.km-name{font-size:12px;font-weight:700;color:var(--text-1);margin-top:6px;display:block}
/* 知识中心大卡片 */
.kmap-banner{margin:0 16px 14px;font-size:12.5px;color:var(--text-2);background:var(--gold-soft);border:1px solid var(--border);border-radius:var(--r-md);padding:10px 14px}
.kmap-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:0 16px}
.kmap-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);overflow:hidden;cursor:pointer;position:relative;transition:transform var(--t-fast),box-shadow var(--t-fast);min-height:150px;display:flex;flex-direction:column}
.kmap-card:active{transform:scale(.98);box-shadow:var(--sh-2)}
.km-cover{height:78px;display:grid;place-items:center;font-size:38px}
.km-ai .km-cover{background:linear-gradient(135deg,#4F8DFF,#7C5CFF)}
.km-hist .km-cover{background:linear-gradient(135deg,#C9A86A,#8a5a2b)}
.km-geo .km-cover{background:linear-gradient(135deg,#2bb6a8,#1f7a8c)}
.km-psy .km-cover{background:linear-gradient(135deg,#ff7eb3,#b06ab3)}
.km-poem .km-cover{background:linear-gradient(135deg,#d6336c,#7048e8)}
.km-sport .km-cover{background:linear-gradient(135deg,#ff8a3d,#ff5252)}
.km-ielts .km-cover{background:linear-gradient(135deg,#3ecf8e,#1f9d6b)}
.km-title{font-size:16px;font-weight:800;color:var(--text-1);padding:10px 12px 2px}
.km-desc{font-size:11.5px;color:var(--text-3);padding:0 12px;line-height:1.4}
.km-foot{margin-top:auto;display:flex;justify-content:space-between;align-items:center;padding:10px 12px 12px}
.km-count{font-size:11px;font-weight:700;color:var(--text-2);background:var(--surface-2);padding:3px 8px;border-radius:var(--r-pill)}
.km-enter{font-size:12px;font-weight:800;color:var(--gold)}
@media(max-width:360px){.kmap-grid{grid-template-columns:1fr}.kmap-mini{grid-template-columns:repeat(3,1fr)}}
/* 阅读进度条 */
.read-bar{position:fixed;top:0;left:0;right:0;height:3px;background:transparent;z-index:30;display:none;pointer-events:none}
.read-bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--gold),#ffd98a);transition:width .12s linear}
/* 收藏按钮 */
.art-fav{position:fixed;top:56px;right:14px;z-index:30;width:40px;height:40px;border-radius:50%;border:1px solid var(--border-strong);background:rgba(21,27,43,.9);backdrop-filter:blur(8px);color:var(--text-2);font-size:20px;display:none;place-items:center;cursor:pointer;box-shadow:var(--sh-2)}
.art-fav.on{color:var(--gold);border-color:var(--gold)}
/* 文章推荐 */
.art-rec{margin:26px 0 12px;padding:18px 16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg)}
.ar-h{font-size:13px;font-weight:800;color:var(--gold);margin:0 0 10px;letter-spacing:.4px}
.ar-h:nth-of-type(2){margin-top:18px}
.ar-next{display:block;background:linear-gradient(135deg,#1c2742,#0d1220);border:1px solid var(--border);border-radius:var(--r-md);padding:13px 14px;margin-bottom:14px;text-decoration:none;color:inherit;cursor:pointer}
.ar-next:active{transform:scale(.99)}
.ar-ne{display:block;font-size:14px;font-weight:700;color:var(--text-1);line-height:1.4}
.ar-ng{display:block;font-size:11px;color:var(--gold);margin-top:5px;font-weight:600}
.ar-rel{display:flex;flex-direction:column;gap:8px}
.ar-chip{display:block;font-size:12.5px;color:var(--text-2);background:var(--surface-2);border:1px solid var(--border);border-radius:var(--r-md);padding:10px 12px;text-decoration:none;cursor:pointer;line-height:1.4}
.ar-chip:active{transform:scale(.99);border-color:var(--border-strong)}
'''

# ---------- 5. 新增 JS ----------
NEWJS = '''<script>
/* REV-GROWTH-JS v1 */
__ATLAS__
(function(){
  'use strict';
  var ART_CAT={'art-hist':'历史文明','art-geo':'地理世界','art-psy':'心理认知','art-eq':'心理认知','art-poem':'文学审美','art-sport':'运动健康','art-tech':'AI科技'};
  function catOf(id){for(var k in ART_CAT){if(id.indexOf(k)===0)return ART_CAT[k];}return '其他';}
  function tStr(){var d=new Date();return d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();}
  function yStr(){var d=new Date(Date.now()-864e5);return d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();}
  function load(k,def){try{var v=localStorage.getItem(k);return v?JSON.parse(v):def;}catch(e){return def;}}
  function save(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(e){}}

  // 成长统计
  var readSet=load('zs_read',['art-tech-llm','art-hist-qinshihuang','art-psy-procrastination','art-sport-hyrox-what','art-poem-shijing','art-geo-plate','art-eq-basics']);
  var streak=load('zs_streak',38);var last=load('zs_last','');var t=tStr();
  if(last!==t){if(last===yStr()){streak=streak+1;}else if(last===''){streak=38;}else{streak=1;}last=t;save('zs_streak',streak);save('zs_last',last);}
  var total=ATLAS.length+77+38;
  var level=Math.max(1,Math.floor(streak/7)+Math.floor(readSet.length/10));
  function setT(id,x){var e=document.getElementById(id);if(e)e.textContent=x;}
  setT('gStreak',streak);setT('gRead',readSet.length);setT('gTotal',total);setT('gLvl','Lv.'+level);

  // 问候语
  var h=new Date().getHours();var w='你好，泽少';if(h<6)w='夜深了，泽少';else if(h<12)w='早上好，泽少';else if(h<14)w='中午好，泽少';else if(h<18)w='下午好，泽少';else w='晚上好，泽少';
  setT('gWave',w+' 👋');

  // 知识地图卡片计数
  ['tech','hist','geo','psy','poem','sport'].forEach(function(c){var n=ATLAS.filter(function(a){return catOf(a.id)===({tech:'AI科技',hist:'历史文明',geo:'地理世界',psy:'心理认知',poem:'文学审美',sport:'运动健康'}[c]);}).length;var e=document.getElementById('kmc-'+c);if(e)e.textContent=n+' 篇';});

  // 今日进度
  var todayData=load('zs_today',{d:'',items:[]});
  if(todayData.d!==t){todayData={d:t,items:[]};save('zs_today',todayData);}
  function renderToday(){var n=todayData.items.length;setT('gProgTxt',n+' / 3');var b=document.getElementById('gProgBar');if(b)b.style.width=Math.round(n/3*100)+'%';if(n>=3&&!todayData._c){todayData._c=true;save('zs_today',todayData);toast('🎉 今日三连达成，成长 +1！');}}
  renderToday();
  window.markToday=function(type){if(todayData.items.indexOf(type)<0){todayData.items.push(type);save('zs_today',todayData);renderToday();}};
  window.markArtRead=function(id){if(readSet.indexOf(id)<0){readSet.push(id);save('zs_read',readSet);setT('gRead',readSet.length);}};

  // 进度条 + 收藏 + 推荐
  var barEl=document.createElement('div');barEl.className='read-bar';barEl.innerHTML='<i id="readBarFill"></i>';document.body.appendChild(barEl);
  var favEl=document.createElement('button');favEl.className='art-fav';favEl.id='artFav';favEl.type='button';favEl.textContent='☆';document.body.appendChild(favEl);
  var favSet=load('zs_fav',[]);
  function updateBar(){var sc=document.querySelector('.screen.active');if(!sc)return;var max=sc.scrollHeight-sc.clientHeight;var p=max>0?sc.scrollTop/max:0;if(p>1)p=1;var f=document.getElementById('readBarFill');if(f)f.style.width=(p*100)+'%';}
  function bindScroll(sec){if(sec.dataset.sb)return;sec.dataset.sb='1';sec.addEventListener('scroll',updateBar,{passive:true});updateBar();}
  function updateFav(id){var faved=favSet.indexOf(id)>=0;favEl.style.display='grid';favEl.textContent=faved?'★':'☆';favEl.classList.toggle('on',faved);favEl.onclick=function(){var i=favSet.indexOf(id);if(i>=0){favSet.splice(i,1);favEl.textContent='☆';favEl.classList.remove('on');toast('已取消收藏');}else{favSet.push(id);favEl.textContent='★';favEl.classList.add('on');toast('⭐ 已收藏');}save('zs_fav',favSet);};}
  function initArticle(sec,id){
    if(sec.dataset.inited)return;sec.dataset.inited='1';
    var art=sec.querySelector('article.lesson');if(!art)return;
    if(art.querySelector('.art-rec'))return;
    var idx=-1;for(var i=0;i<ATLAS.length;i++){if(ATLAS[i].id===id){idx=i;break;}}
    if(idx<0)return;
    var next=ATLAS[(idx+1)%ATLAS.length];
    var same=ATLAS.filter(function(a){return a.id!==id&&catOf(a.id)===catOf(id);});
    if(same.length<3){ATLAS.forEach(function(a){if(a.id!==id&&same.indexOf(a)<0&&catOf(a.id)!==catOf(id))same.push(a);});}
    var rel=same.slice(0,3);
    var Q=String.fromCharCode(39);
    var html='<div class="art-rec"><div class="ar-h">下一篇 · 接着读</div>'
      +'<a class="ar-next" onclick="goArt('+Q+next.id+Q+')"><span class="ar-ne">'+next.t+'</span><span class="ar-ng">'+catOf(next.id)+' · 阅读 →</span></a>'
      +'<div class="ar-h">相关推荐</div><div class="ar-rel">';
    rel.forEach(function(a){html+='<a class="ar-chip" onclick="goArt('+Q+a.id+Q+')">'+catOf(a.id)+' · '+a.t+'</a>';});
    html+='</div></div>';
    art.insertAdjacentHTML('beforeend',html);
    markArtRead(id);
  }
  var obs=new MutationObserver(function(muts){muts.forEach(function(mu){if(mu.target.classList&&mu.target.classList.contains('active')){var id=mu.target.id||'';if(id.indexOf('art-')===0){updateFav(id);initArticle(mu.target,id);bindScroll(mu.target);}else{favEl.style.display='none';barEl.style.display='none';}}});});
  document.querySelectorAll('.screen').forEach(function(s){obs.observe(s,{attributes:true,attributeFilter:['class']});});
  var cur=document.querySelector('.screen.active');if(cur&&cur.id&&cur.id.indexOf('art-')===0){updateFav(cur.id);initArticle(cur,cur.id);bindScroll(cur);}
})();
</script>'''

# ---------- 6. 替换逻辑 ----------
lines = raw.split('\n')

def replace_section(start_marker, new_block):
    start = None
    for i, l in enumerate(lines):
        if start_marker in l:
            start = i
            break
    if start is None:
        raise SystemExit('未找到起始标记: ' + start_marker)
    end = None
    for i in range(start, len(lines)):
        if lines[i].strip() == '</section>':
            end = i
            break
    lines[start:end+1] = new_block.split('\n')
    print('替换区块: %s (行 %d-%d)' % (start_marker, start+1, end+1))

replace_section('id="s-home"', NEWHOME)
replace_section('id="s-know"', NEWKNOW)

# 插入 CSS（</style> 前）
ci = lines.index('</style>')
lines[ci:ci] = NEWCSS.split('\n')
print('插入 CSS 于行 %d' % ci)

# 插入 JS（</body> 前）
bi = lines.index('</body>')
final_js = NEWJS.replace('__ATLAS__', atlas_js)
lines[bi:bi] = final_js.split('\n')
print('插入 JS 于行 %d' % bi)

out = '\n'.join(lines)
open(HTML, 'w', encoding='utf-8').write(out)

# JS 语法检查
js_check = final_js.replace('<script>', '').replace('</script>', '')
tmp = os.path.join(ROOT, 'scripts', '_revamp_check.js')
open(tmp, 'w', encoding='utf-8').write(js_check)
node = r'C:\Users\admin\.workbuddy\binaries\node\versions\22.22.2\node.exe'
if os.path.exists(node):
    r = subprocess.run([node, '--check', tmp], capture_output=True, text=True)
    print('node --check:', 'OK' if r.returncode == 0 else 'FAILED\n' + r.stderr)
else:
    print('未找到 node，跳过语法检查')
try:
    os.remove(tmp)
except Exception:
    pass
print('完成。输出文件:', HTML)
