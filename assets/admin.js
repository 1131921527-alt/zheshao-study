/* ===== V2.1 隐藏内容生产工作台（泽少学习中心） =====
 * 入口：长按「我的」页头像，或三击页脚版本号
 * 功能：输入主题 → 一键生成草稿 → 发布到 AI动态 / 知识文章
 * 数据：存 localStorage(zs_custom)，刷新不丢，不影响 XP/等级/徽章
 */
(function () {
  'use strict';

  function load(k, def) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : def; } catch (e) { return def; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function $(id) { return document.getElementById(id); }

  var CAT = { tech: 'AI科技', hist: '历史文明', geo: '地理世界', psy: '心理认知', poem: '文学审美', sport: '运动健康' };
  function catLabel(c) { return CAT[c] || '知识'; }
  function todayStr() { var d = new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }

  // 一键生成草稿（模板法，离线可用；也可复制提示词去真实 AI 生成）
  function genDraft(theme) {
    theme = (theme || '').trim() || '今日主题';
    var titles = [
      '「' + theme + '」到底是怎么回事？',
      '一文读懂 ' + theme + '：小白也能看明白',
      theme + '：你需要知道的几件事',
      theme + ' 入门指南（建议收藏）'
    ];
    var title = titles[Math.floor(Math.random() * titles.length)];
    var summary = theme + '是当下很值得了解的一个话题。本文用通俗语言，帮你快速建立整体认识，并给出今天就能用上的下一步。';
    var body = [
      '<p class="lead">提到' + esc(theme) + '，很多人第一反应是「听起来很厉害，但说不清是什么」。今天我们就把它拆开，从是什么、为什么、怎么用三个角度讲清楚。</p>',
      '<h2>一、' + esc(theme) + ' 是什么</h2><p>用一句话说，' + esc(theme) + '是（在这里填核心定义）。它解决的真实问题是（填痛点）。理解它，先别背概念，先想它帮人省了什么、多了什么。</p>',
      '<h2>二、为什么现在值得关注</h2><p>它不是突然出现的，而是（趋势A）+（趋势B）叠加的结果。对普通人来说，意味着（具体影响）。</p>',
      '<h2>三、三个关键点</h2><p><strong>1) 本质：</strong>（一句话）。<br><strong>2) 边界：</strong>它不擅长（什么）。<br><strong>3) 信号：</strong>怎么判断一个' + esc(theme) + '靠不靠谱（看什么指标）。</p>',
      '<h2>四、常见误区</h2><p>误区一：把「名字好听」当「真有用」。误区二：以为学了就立刻变现。误区三：拿来主义不验证。记住——能落到自己生活里的，才算真懂。</p>',
      '<h2>五、今天能做什么</h2><p>① 用一个具体场景试一次；② 关注 1 个靠谱信源；③ 把今天看懂的讲给一个人听（费曼学习法）。</p>'
    ].join('');
    var quiz = [
      esc(theme) + ' 的核心定义是什么？',
      esc(theme) + ' 最容易被混淆的概念是哪个？',
      '今天你可以怎么用上 ' + esc(theme) + '？'
    ];
    return { title: title, summary: summary, body: body, quiz: quiz };
  }

  function knowledgeHTML(c) {
    return '<article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab(\'s-know\')">← 返回知识中心</a>'
      + '<header class="art-head"><div class="ah-meta">' + esc(catLabel(c.cat)) + ' · 自定义</div><h1>' + esc(c.title) + '</h1></header>'
      + '<div class="body"><p class="lead">' + esc(c.summary) + '</p>' + c.body
      + '<div class="summary"><span class="st">📌 学习问题</span><ul>' + c.quiz.map(function (q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ul></div>'
      + '</div><div class="afoot">泽少学习助手<br>每天进步一点点</div></article>';
  }
  function aiHTML(c) {
    return '<article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab(\'s-news\')">← 返回 AI动态</a>'
      + '<header class="art-head"><div class="ah-meta">AI动态 · 自定义</div><h1>' + esc(c.title) + '</h1></header>'
      + '<div class="body"><p class="lead">' + esc(c.summary) + '</p>' + c.body
      + '<div class="summary"><span class="st">📌 学习问题</span><ul>' + c.quiz.map(function (q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ul></div>'
      + '</div><div class="afoot">泽少学习助手<br>每天进步一点点</div></article>';
  }

  function host() { var a = document.querySelector('.screen'); return a ? a.parentNode : document.body; }

  function injectOne(c) {
    if (document.getElementById(c.id)) return;
    if (c.type === 'know') {
      var sec = document.createElement('section'); sec.className = 'screen'; sec.id = c.id; sec.innerHTML = knowledgeHTML(c);
      host().appendChild(sec);
      if (typeof ATLAS !== 'undefined' && !ATLAS.some(function (a) { return a.id === c.id; })) ATLAS.push({ id: c.id, t: c.title, m: catLabel(c.cat) });
      var kl = $('klist-' + c.cat);
      if (kl) {
        var row = document.createElement('a'); row.className = 'krow'; row.setAttribute('onclick', 'goArt(\'' + c.id + '\')');
        row.innerHTML = '<div><div class="kt">' + esc(c.title) + '<span class="adm-new">新</span></div><div class="km">' + esc(catLabel(c.cat)) + ' · 自定义</div></div><div class="arr">→</div>';
        kl.appendChild(row);
      }
      var cnt = $('kmc-' + c.cat); if (cnt) { var m = /^(\d+)/.exec(cnt.textContent); if (m) cnt.textContent = (parseInt(m[1], 10) + 1) + ' 篇'; }
    } else {
      var s2 = document.createElement('section'); s2.className = 'screen'; s2.id = c.id; s2.innerHTML = aiHTML(c);
      host().appendChild(s2);
      var list = $('aiNewsList');
      if (list) {
        var a = document.createElement('a'); a.className = 'linkcard'; a.href = 'javascript:void(0)'; a.setAttribute('onclick', 'goArt(\'' + c.id + '\')');
        a.innerHTML = '<div class="li">⚡</div><div class="lc"><div class="t">' + esc(c.title) + '<span class="adm-new">新</span></div><div class="d">' + esc(c.date) + ' · 自定义生成</div></div><div class="arr">→</div>';
        list.insertBefore(a, list.firstChild);
      }
    }
  }

  function injectAll() { var data = load('zs_custom', []); data.forEach(injectOne); updateCount(); }
  function updateCount() { var n = load('zs_custom', []).length; var e = $('admCount'); if (e) e.textContent = n; }
  function openAdmin() { $('adminModal').classList.add('show'); updateCount(); }
  function closeAdmin() { $('adminModal').classList.remove('show'); }
  window.admOpen = openAdmin; window.admClose = closeAdmin;

  window.admGenerate = function () {
    var th = $('admTheme').value;
    if (!th.trim()) { toast('先填「今天主题」'); return; }
    var d = genDraft(th);
    $('admTitle').value = d.title;
    $('admSummary').value = d.summary;
    $('admBody').value = d.body.replace(/<[^>]+>/g, '');
    $('admQuiz').value = d.quiz.join('\n');
    toast('已生成草稿，可继续润色');
  };
  window.admCopyPrompt = function () {
    var th = $('admTheme').value || '今日主题';
    var mins = $('admMins').value || '8';
    var prompt = '请围绕主题《' + th + '》写一篇面向大众的通俗科普文章，要求：\n'
      + '1. 标题吸引人且准确\n'
      + '2. 开头用一句话钩子\n'
      + '3. 分 4-5 个小节：是什么 / 为什么重要 / 三个关键点 / 常见误区 / 今天能做什么\n'
      + '4. 全文约 ' + mins + ' 分钟阅读量（800-1200 字）\n'
      + '5. 结尾给出 3 个「学习问题」帮助复习\n'
      + '请用 HTML 片段输出（p/h2/strong/ul 标签），不要外层 html/body。';
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(prompt).then(function () { toast('提示词已复制，去 AI 工具生成正文'); });
    } else { toast('提示词已生成，请手动复制'); }
  };
  window.admPublish = function (type) {
    var th = $('admTheme').value.trim();
    var title = $('admTitle').value.trim();
    var summary = $('admSummary').value.trim();
    var bodyRaw = $('admBody').value.trim();
    var quiz = $('admQuiz').value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean);
    if (!th) { toast('请先填「今天主题」'); return; }
    if (!title) { toast('标题不能为空'); return; }
    var bodyHtml = bodyRaw.split(/\n{2,}/).map(function (p) { return '<p>' + esc(p) + '</p>'; }).join('');
    if (!bodyHtml) { bodyHtml = '<p class="lead">' + esc(summary) + '</p>'; }
    if (!quiz.length) { quiz = ['回顾一下今天这篇《' + title + '》最打动你的一点？']; }
    var cat = $('admCat').value;
    var id = (type === 'know' ? 'art-custom-' : 'ai-custom-') + Date.now();
    var item = { id: id, type: type, cat: cat, date: todayStr(), title: title, summary: summary, body: bodyHtml, quiz: quiz, mins: parseInt($('admMins').value, 10) || 8 };
    var data = load('zs_custom', []); data.push(item); save('zs_custom', data);
    injectOne(item);
    toast(type === 'know' ? '已发布到知识文章 ✓' : '已发布到 AI动态 ✓');
    closeAdmin();
  };
  window.admExport = function () {
    var data = load('zs_custom', []);
    if (!data.length) { toast('还没有生成内容'); return; }
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = 'zheshao-custom-' + todayStr() + '.json';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    toast('已导出 ' + data.length + ' 条，去 update-center 入库');
  };
  window.admList = function () {
    var data = load('zs_custom', []);
    if (!data.length) { toast('暂无自定义内容'); return; }
    alert('已生成 ' + data.length + ' 条：\n' + data.map(function (c) { return (c.type === 'know' ? '[知识] ' : '[动态] ') + c.title; }).join('\n'));
  };

  function bindHidden() {
    var av = document.querySelector('.profile .avatar');
    var t = null;
    function start() { t = setTimeout(openAdmin, 1200); }
    function stop() { if (t) { clearTimeout(t); t = null; } }
    if (av) {
      av.addEventListener('touchstart', start, false); av.addEventListener('touchend', stop, false); av.addEventListener('touchmove', stop, false);
      av.addEventListener('mousedown', start, false); av.addEventListener('mouseup', stop, false); av.addEventListener('mouseleave', stop, false);
    }
    var ft = document.querySelector('.footer'); var clicks = 0, ct = null;
    if (ft) {
      ft.addEventListener('click', function () {
        clicks++; clearTimeout(ct); ct = setTimeout(function () { clicks = 0; }, 700);
        if (clicks >= 3) { clicks = 0; openAdmin(); }
      });
    }
  }

  if (document.readyState !== 'loading') { bindHidden(); injectAll(); }
  else { document.addEventListener('DOMContentLoaded', function () { bindHidden(); injectAll(); }); }
  var modal = $('adminModal');
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeAdmin(); });
})();
