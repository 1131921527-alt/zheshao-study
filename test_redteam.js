// 第21轮：红队审查 - 加载 6 个页面，检查运行时报错、JS 异常、DOM 不一致
const fs = require('fs');
const pp = require('path');
const { JSDOM, ResourceLoader, VirtualConsole } = require('jsdom');

const ROOT = 'C:/Users/admin/WorkBuddy/2026-08-24-00-30-20/zheshao-study';
const pages = ['index.html','study.html','dashboard.html','library.html','archive.html','update-center.html'];

class FileLoader extends ResourceLoader {
  fetch(url, options) {
    // GitHub Pages URL → 本地文件
    if (url.startsWith('https://1131921527-alt.github.io/zheshao-study/')) {
      const path = url.replace('https://1131921527-alt.github.io/zheshao-study/','');
      const fp = pp.join(ROOT, path);
      if (fs.existsSync(fp)) {
        return Promise.resolve(fs.readFileSync(fp));
      }
    }
    // data: / blob: / inline svg → skip
    if (url.startsWith('data:') || url.startsWith('blob:')) {
      return Promise.resolve(Buffer.from(''));
    }
    // 跳过外部 CDN / ga / gtag
    return Promise.resolve(Buffer.from(''));
  }
}

async function checkPage(page) {
  const fp = pp.join(ROOT, page);
  const html = fs.readFileSync(fp, 'utf-8');
  const errs = [];
  const warns = [];
  const logs = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errs.push('jsdom: ' + (e.message||'').slice(0,200)));
  vc.on('error', (msg, src) => errs.push('error: ' + String(msg||'').slice(0,150)));
  vc.on('warn', (msg) => warns.push('warn: ' + String(msg||'').slice(0,150)));
  vc.on('log', (...args) => logs.push('log: ' + args.map(a=>String(a||'')).join(' ').slice(0,150)));

  const dom = new JSDOM(html, {
    url: 'https://1131921527-alt.github.io/zheshao-study/' + page,
    runScripts: 'dangerously',
    resources: new FileLoader(),
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(window) {
      window.confirm = () => true;
      window.alert = () => {};
      window.scrollTo = () => {};
      try { window.localStorage.clear(); } catch(e) {}
    }
  });

  // 等页面跑一会
  await new Promise(r => setTimeout(r, 1500));
  const win = dom.window;
  // 抓 DOM 状态
  const docInfo = {
    title: win.document.title,
    hasMain: !!win.document.querySelector('main, .main, .app, .screen'),
    scriptTags: win.document.querySelectorAll('script').length,
    visibleTextLen: (win.document.body && (win.document.body.innerText || win.document.body.textContent || '')).length
  };
  dom.window.close();
  return { page, errs: errs.slice(0,8), warns: warns.slice(0,5), logs: logs.slice(0,5), docInfo };
}

(async () => {
  for (const p of pages) {
    try {
      const r = await checkPage(p);
      const status = (r.errs.length === 0) ? '✅' : '❌';
      console.log(`\n${status} ${p}`);
      console.log(`  title: ${r.docInfo.title}`);
      console.log(`  hasMain: ${r.docInfo.hasMain} | scripts: ${r.docInfo.scriptTags} | textLen: ${r.docInfo.visibleTextLen}`);
      if (r.errs.length) {
        console.log(`  ERRORS (${r.errs.length}):`);
        r.errs.forEach(e => console.log('    ' + e));
      }
      if (r.warns.length) {
        console.log(`  WARNS (${r.warns.length}):`);
        r.warns.slice(0,3).forEach(w => console.log('    ' + w));
      }
    } catch (e) {
      console.log(`\n❌ ${p} FAILED: ${e.message}`);
    }
  }
})();