const HISTORY=[
 {e:"🏺",t:"文明曙光：从部落联盟到早期国家",m:"先秦 · 史前—前1046",b:"<p>新石器时代晚期，黄河、长江流域已出现发达聚落：仰韶、良渚、龙山等文化相继兴起。其中<b>良渚古城</b>（约公元前3300–2300年）拥有大型水利系统与精美玉器礼制，被视为早期国家的雏形。</p><p>相传<b>夏</b>朝（约前2070年起）是中国第一个王朝，二里头文化或与之对应；<b>商</b>朝（约前1600–前1046）留下甲骨文与青铜器，信史由此开端；<b>周</b>朝推行分封与礼乐制度，奠定了「华夏」认同的雏形。</p>"},
 {e:"🏯",t:"秦汉：统一与制度的奠基",m:"秦汉 · 前221—220",b:"<p>公元前221年，<b>秦</b>灭六国，建立中央集权帝国：统一文字（小篆）、度量衡与车轨，废分封、行郡县，修筑长城与驰道，奠定此后两千年政体骨架。</p><p><b>汉</b>承秦制并巩固：文景之治休养生息，汉武帝推恩令削藩、独尊儒术、通西域。<b>张骞出使西域</b>打通丝绸之路，中原与中亚、西亚的贸易文化交流就此展开；造纸术也在汉代萌芽。</p>"},
 {e:"📜",t:"唐宋：盛世、开放与科技高峰",m:"唐宋 · 618—1279",b:"<p><b>唐</b>代贞观之治、开元盛世，国力与文化空前繁荣；科举制日臻完善，社会流动增强，长安成为国际大都会，佛教、胡乐与丝路商货汇聚。</p><p><b>宋</b>代商业兴盛、城市崛起，<b>毕昇活字印刷</b>、指南针、火药等发明走向应用，理学（程朱）体系成型。唐宋诗词更是中华文化的巅峰之一，影响深远。</p>"}
];
const GEO=[
 {e:"🌋",t:"板块构造：为什么大地会“呼吸”",m:"地球科学 · 板块",b:"<p>地球岩石圈被划分为<b>六大板块</b>（亚欧、非洲、美洲、印度洋、太平洋、南极洲），它们漂浮在炽热的软流圈上缓慢移动。</p><p>板块边界是地质活动最剧烈的地带：<b>张裂处</b>（如东非大裂谷）不断生成新洋壳；<b>碰撞处</b>（如喜马拉雅）隆起高山；<b>俯冲带</b>（环太平洋）多火山地震。日本、智利强震频发，正因地处环太平洋火山地震带。</p>"},
 {e:"🌊",t:"大河文明：河流如何孕育人类",m:"人文地理 · 文明起源",b:"<p>四大文明古国皆傍大河而生：<b>尼罗河</b>定期泛滥带来肥沃淤泥，滋养古埃及；<b>两河</b>（幼发拉底、底格里斯）灌溉出新月沃地，孕育古巴比伦；印度河/恒河、黄河/长江同理成就古印度与古中国。</p><p>河流提供饮水、灌溉、航运与沃土，使农业与城市得以兴起——「逐水而居」是人类早期文明的共同逻辑。</p>"},
 {e:"🌳",t:"地球之肺：热带雨林与气候",m:"自然地理 · 生态",b:"<p>热带雨林集中在赤道附近，以<b>亚马逊、刚果、东南亚</b>三大片为代表。亚马逊雨林面积约550万平方公里，储存巨量碳，并调节全球气候与降水。</p><p>雨林物种极丰富，约占已知物种的一半以上。然而毁林与气候变暖正削弱其「碳汇」能力，威胁生物多样性与全球气候稳定，保护雨林已成为紧迫议题。</p>"}
];
const FIN=[
 {e:"💰",t:"钱为什么会“变毛”？——通胀通俗版",m:"财经科普 · 基础",b:"<p>你有没有发现，小时候一根冰棍几毛钱，现在要几块？不是冰棍贵了，是钱「毛了」。<b>通胀</b>就是物价普遍上涨、钱能买的东西变少。</p><p>简单说：市面上的钱变多了，但东西没变多，每块钱的购买力就下降了。温和通胀（每年 2%~3%）其实正常，甚至利于经济；但恶性通胀会让存款悄悄缩水。</p><p>所以「把钱藏床底」长期看会贬值——这也是为什么人们会买资产、做投资来对抗通胀。理财的第一步，是先理解钱为什么越来越「不经花」。</p>"},
 {e:"📈",t:"复利：时间怎么让钱“生小钱”",m:"财经科普 · 基础",b:"<p>复利常被说成「世界第八大奇迹」（虽出处存疑，但道理是真的）。它就是<b>利滚利</b>：你赚到的利息，下次连本带利一起再赚。</p><p>假设年化 5%：1 万块 10 年后约 1.63 万，30 年后约 4.32 万——越往后涨得越快，像滚雪球。关键就两条：<b>早开始</b> + <b>别中断</b>。每月定投一点点，几十年后的差距会吓你一跳。</p><p>这也是养老、教育金要趁早规划的原因：时间，是最便宜的「本金」。</p>"},
 {e:"🏦",t:"股票、基金，到底都是啥？",m:"财经科普 · 入门",b:"<p><b>股票</b>＝你买了一家公司的「一小片所有权」。公司赚钱分红、大家看好它，股价就涨；反之就跌。</p><p><b>基金</b>＝把很多人的钱凑一起，交给经理去买一篮子股票/债券，等于「找个老司机帮你开车」。股票波动大、潜在收益高；基金分散风险、门槛低。</p><p>新手最容易被「追涨杀跌」坑：涨了跟风冲、跌了吓跑。科普一句：先搞懂再下手，别把理财当赌博。</p>"}
];
const PSY=[
 {e:"🐢",t:"拖延症：不是懒，是“情绪管理”",m:"心理学 · 日常",b:"<p>总说「等会儿再做」，结果拖到最后一晚？心理学说，拖延往往<b>不是懒</b>，而是任务让人焦虑/不爽，大脑本能逃避痛苦，跑去刷手机求即时舒服。</p><p>破解法不是「打鸡血」，而是：把大任务拆小、降低启动门槛（「只做 5 分钟」），并接纳不完美——<b>完成比完美重要</b>。番茄钟、两分钟法则都很好用。</p>"},
 {e:"🔍",t:"当局者迷：为什么劝别人一套一套",m:"心理学 · 认知",b:"<p>朋友纠结时你分析得头头是道，自己遇事先慌？这跟「心理距离」有关：别人的事离你远，你看得到大局；自己的事贴脸，细节和情绪被放大，理性就被淹了。</p><p>办法：把「我该怎么办」改写成「如果是好朋友遇到这事，我会怎么劝他」——人为拉远距离，思路瞬间就清了。</p>"},
 {e:"🍬",t:"多巴胺：快乐激素，也是“陷阱”",m:"心理学 · 脑科学",b:"<p>刷短视频停不下来、奶茶非要加满料——背后多是<b>多巴胺</b>。它不等于「快乐」，而是「想要」的冲动：预期奖励时就分泌，推着你去追求。</p><p>麻烦在于：短视频、游戏、甜食能给「高密度、零延迟」的多巴胺，大脑被惯坏，对读书、运动这种「慢奖励」越来越没耐心。</p><p>科普建议：给生活留白，主动制造一点「无聊」，让奖励系统 reset 一下。</p>"}
];

let curLight={e:"",t:""};
function goTab(id){document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',t.dataset.t===id));document.getElementById(id).scrollTop=0;}
function goArt(id){document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));document.getElementById(id).scrollTop=0;}
function goKnow(sec){goTab('s-know');var el=document.getElementById('klist-'+sec);if(el){el.classList.remove('hidden');el.scrollIntoView({behavior:'smooth',block:'start'});}}
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');clearTimeout(t._t);t._t=setTimeout(()=>t.classList.remove('show'),1800);}

const SLUG={hist:["history-preqin","history-qinhan","history-tangsong"],geo:["geo-plate","geo-river","geo-rainforest"],fin:["fin-inflation","fin-compound","fin-stockfund"],psy:["psy-procrastination","psy-bystander","psy-dopamine"]};
function renderK(){
  const maps={hist:HISTORY,geo:GEO,fin:FIN,psy:PSY};
  for(const k in maps){
    document.getElementById('klist-'+k).innerHTML=maps[k].map((a,i)=>`<a class="krow" onclick="goArt('art-${SLUG[k][i]}')"><div><div class="kt">${a.t}</div><div class="km">${a.m}</div></div><div class="arr">→</div></a>`).join('');
  }
}
function toggleK(w){document.getElementById('klist-'+w).classList.toggle('hidden');}
function openArticle(k,i){const a=({hist:HISTORY,geo:GEO,fin:FIN,psy:PSY})[k][i];curLight={e:a.e,t:a.t};document.getElementById('sheet-emoji').textContent=a.e;document.getElementById('sheet-title').textContent=a.t;document.getElementById('sheet-meta').textContent=a.m;document.getElementById('sheet-body').innerHTML=a.b;document.getElementById('sheet-mask').classList.add('show');document.getElementById('sheet').classList.add('show');}
function closeSheet(){document.getElementById('sheet-mask').classList.remove('show');document.getElementById('sheet').classList.remove('show');}
function openLight(){if(!curLight.e)return;document.getElementById('lb-emoji').textContent=curLight.e;document.getElementById('lb-title').textContent=curLight.t;document.getElementById('lightbox').classList.add('show');}
function closeLight(){document.getElementById('lightbox').classList.remove('show');}

function copyWx(){const id='Harryalwayslucky';if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(id).then(()=>toast('微信号已复制：'+id));}else{const t=document.createElement('textarea');t.value=id;document.body.appendChild(t);t.select();try{document.execCommand('copy');toast('微信号已复制：'+id);}catch(e){}document.body.removeChild(t);}}
function copyUrl(){const u=location.href;if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(()=>toast('地址已复制，去浏览器粘贴安装'));}else{toast('请手动复制地址栏链接');}}

let deferredPrompt=null;
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredPrompt=e;document.getElementById('btnInstall').style.display='inline-block';});
function doInstall(){if(deferredPrompt){deferredPrompt.prompt();deferredPrompt.userChoice.then(()=>{deferredPrompt=null;document.getElementById('btnInstall').style.display='none';});}else{toast('请点浏览器菜单「添加到主屏幕」');}}
renderK();

if('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('sw.js').catch(()=>{});});}
