// 第18轮 jsdom 测试：英文文章中文化的渲染
// 验证 list 标题括号格式 + 详情页中文摘要 + 缺失译文兜底行为
const fs = require('fs');
const path = require('path');
const pp = require('path');
const { JSDOM } = require('jsdom');

const root = pp.resolve(process.cwd());
const html = fs.readFileSync(pp.join(root, 'study.html'), 'utf-8');
const dataPath = pp.join(root, 'assets', 'ai_cards.json');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));

const cards = Array.isArray(data.cards) ? data.cards : data;
console.log('cards:', cards.length);

// 简单 fetch stub: 任何 network call 都允许 Jsdom fetchImpl 完成
function fetchImpl(url) {
  return Promise.resolve({ ok: true, json: () => Promise.resolve({}), text: () => Promise.resolve('') });
}

const dom = new JSDOM(html, {
  runScripts: 'outside-only',
  resources: 'usable',
  url: 'http://localhost/study.html',
  beforeParse(window) {
    window.fetch = fetchImpl;
    window.scrollTo = () => {};
    window.confirm = () => true;
    try { window.localStorage.clear(); } catch (e) {}
    window.Sound = { play: () => {}, preload: () => {} };
  },
}).window;

// 找到 study.html 里的 inline <script>
const scripts = dom.document.querySelectorAll('script');
console.log('inline scripts:', scripts.length);
for (const s of scripts) {
  if (s.textContent && s.textContent.length > 1000) {
    try { dom.eval(s.textContent); } catch (e) { console.error('eval err at len=', s.textContent.length, '=>', e.message.slice(0, 200)); }
  }
}

// 重设 cur / rawCache（eval 之后的 var cur=null; 会覆盖）
dom.cur = { items: cards, deck: { src: 'assets/ai_cards.json' }, idx: 0 };
dom.rawCache = { 'assets/ai_cards.json': data };

let errors = 0;
function expect(cond, msg) {
  if (!cond) { console.error('FAIL:', msg); errors++; }
  else { console.log('PASS:', msg); }
}

dom.renderNewsList();
const listHtml = dom.document.getElementById('newsList').innerHTML;
console.log('[list] cards rendered:', (listHtml.match(/news-list-card/g) || []).length);

// 找出英文卡各自对应的列表卡（按 title 短路匹配）
let enCards = 0, enWithCnTitle = 0;
for (const c of cards) {
  if (!c.title) continue;
  const t = c.title;
  const en = (function(s){
    const letters = (s.match(/[A-Za-z]/g) || []).length;
    return letters / Math.max(1, s.length) > 0.5;
  })(t);
  if (!en) continue;
  enCards++;
  const cn = (c.title_cn || '').trim();
  const re = new RegExp(t.split(' ').slice(0, 5).join(' ').replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&').slice(0, 40));
  if (listHtml.match(re)) {
    if (cn && listHtml.includes(cn)) {
      console.log('  OK :', t.slice(0, 40), '→ contains:', cn.slice(0, 30));
      enWithCnTitle++;
    } else if (!cn) {
      console.log('  EN :', t.slice(0, 40), '(no CN, fallback to raw)');
    } else {
      console.log('  MIM?:', t.slice(0, 40), '(CN not in list title)');
    }
  }
}
console.log('[list] en-cards:', enCards, 'with-bracket-cn:', enWithCnTitle);

// 详情页测试：单点几张英文卡，验证正文 + 标题格式
const englishIndices = [];
for (let i = 0; i < cards.length; i++) {
  const t = cards[i].title || '';
  const en = (t.match(/[A-Za-z]/g) || []).length / Math.max(1, t.length) > 0.5;
  if (en) englishIndices.push(i);
}
console.log('[detail] english indices:', englishIndices);

for (const idx of englishIndices) {
  dom.cur.idx = idx;
  try { dom.renderNews(); } catch(e) { console.error('render err', idx, e.message.slice(0,200)); }
  const title = dom.document.getElementById('newsTitle').textContent || '';
  const body = dom.document.getElementById('newsBody').innerHTML || '';
  const card = cards[idx];
  const cn = card.title_cn || '';
  const isEn = (card.title.match(/[A-Za-z]/g) || []).length / Math.max(1, card.title.length) > 0.5;
  // 标题格式断言
  if (cn && isEn) {
    expect(title.includes('（') && title.includes('）'), `[${idx}] title 包含中文括号格式: ${title.slice(0,60)}`);
  }
  // 正文断言
  expect(body.length > 50, `[${idx}] body 渲染成功 (${body.length} chars)`);
  // 看是否提示条
  if (isEn) {
    expect(body.includes('原文') || body.includes('中文'), `[${idx}] body 含中英文提示语`);
  }
}

console.log('ERRORS:', errors);
process.exit(errors ? 1 : 0);
