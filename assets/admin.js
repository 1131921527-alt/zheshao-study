/* ===== V2.2 内容管理中心（泽少学习中心 · 隐藏入口） =====
 * 入口：长按「我的」页头像，或三击页脚版本号
 * 功能：生成草稿 → 存草稿 / 预览 → 确认发布；草稿箱 + 历史管理 + 今日生产联动
 * 数据：localStorage(zs_custom) = [{id,type,title,summary,content,category,date,status,cat,mins,quiz}]
 *       兼容 V2.1 旧格式（body/quiz/cat 无 status）自动迁移；刷新不丢，不影响 XP/等级/徽章
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
  var LABEL2KEY = {}; Object.keys(CAT).forEach(function (k) { LABEL2KEY[CAT[k]] = k; });
  function catLabel(c) { return CAT[c] || '知识'; }
  function todayStr() { var d = new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }
  function genId(type) { return (type === 'know' ? 'art-custom-' : 'ai-custom-') + Date.now() + '-' + Math.floor(Math.random() * 1e4); }

  // —— 数据结构规范化 + 旧数据迁移 ——
  function normItem(it) {
    if (!it || typeof it !== 'object') it = {};
    var type = it.type || (it.cat ? 'know' : 'ai');
    var catKey = it.cat || (it.category ? (LABEL2KEY[it.category] || 'tech') : 'tech');
    var content = (it.content != null) ? it.content : (it.body != null ? it.body : '');
    var st = (it.status === 'draft' || it.status === 'review' || it.status === 'published') ? it.status : 'published';
    return {
      id: it.id || genId(type),
      type: type,
      title: it.title || '未命名内容',
      summary: it.summary || '',
      content: content,
      quiz: Array.isArray(it.quiz) ? it.quiz : (it.quiz ? [it.quiz] : []),
      category: it.category || catLabel(catKey),
      cat: catKey,
      date: it.date || todayStr(),
      status: st,
      mins: it.mins || 8
    };
  }
  function loadData() { var d = load('zs_custom', []); return (Array.isArray(d) ? d : []).map(normItem); }
  function saveData(items) { save('zs_custom', items); }

  // —— 正文渲染：含 HTML 则原样，否则按段落包裹 ——
  function bodyHtml(c) {
    var s = c.content || '';
    if (/<[a-z][\s\S]*>/i.test(s)) return s;
    var lines = s.split(/\n{2,}/).map(function (p) { return p.trim(); }).filter(Boolean);
    if (!lines.length) return '<p class="lead">' + esc(c.summary || '') + '</p>';
    return lines.map(function (p) { return '<p>' + esc(p).replace(/\n/g, '<br>') + '</p>'; }).join('');
  }

  function knowledgeHTML(c) {
    return '<article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab(\'s-know\')">← 返回知识中心</a>'
      + '<header class="art-head"><div class="ah-meta">' + esc(c.category) + ' · 自定义</div><h1>' + esc(c.title) + '</h1></header>'
      + '<div class="body"><p class="lead">' + esc(c.summary) + '</p>' + bodyHtml(c)
      + '<div class="summary"><span class="st">📌 学习问题</span><ul>' + c.quiz.map(function (q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ul></div>'
      + '</div><div class="afoot">泽少学习助手<br>每天进步一点点</div></article>';
  }
  function aiHTML(c) {
    return '<article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab(\'s-news\')">← 返回 AI动态</a>'
      + '<header class="art-head"><div class="ah-meta">AI动态 · 自定义</div><h1>' + esc(c.title) + '</h1></header>'
      + '<div class="body"><p class="lead">' + esc(c.summary) + '</p>' + bodyHtml(c)
      + '<div class="summary"><span class="st">📌 学习问题</span><ul>' + c.quiz.map(function (q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ul></div>'
      + '</div><div class="afoot">泽少学习助手<br>每天进步一点点</div></article>';
  }

  function host() { var a = document.querySelector('.screen'); return a ? a.parentNode : document.body; }

  function injectOne(c) {
    if (document.getElementById(c.id)) return;
    if (c.type === 'know') {
      var sec = document.createElement('section'); sec.className = 'screen'; sec.id = c.id; sec.innerHTML = knowledgeHTML(c);
      host().appendChild(sec);
      if (typeof ATLAS !== 'undefined' && !ATLAS.some(function (a) { return a.id === c.id; })) ATLAS.push({ id: c.id, t: c.title, m: c.category });
      var kl = $('klist-' + c.cat);
      if (kl) {
        var row = document.createElement('a'); row.className = 'krow'; row.setAttribute('onclick', 'goArt(\'' + c.id + '\')');
        row.innerHTML = '<div><div class="kt">' + esc(c.title) + '<span class="adm-new">新</span></div><div class="km">' + esc(c.category) + ' · 自定义</div></div><div class="arr">→</div>';
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

  // —— 草稿状态/今日生产 渲染 ——
  function badge(st) {
    if (st === 'draft') return '<span class="adm-badge b-draft">📝 草稿</span>';
    if (st === 'review') return '<span class="adm-badge b-review">👀 待审核</span>';
    return '<span class="adm-badge b-pub">✅ 已发布</span>';
  }
  function dayGroup(dateStr) {
    var t = todayStr(); if (dateStr === t) return '今天';
    var y = new Date(); y.setDate(y.getDate() - 1);
    var ys = y.getFullYear() + '-' + (y.getMonth() + 1) + '-' + y.getDate();
    if (dateStr === ys) return '昨天';
    return '更早';
  }
  function renderList() {
    var box = $('admDraftList'); if (!box) return;
    var data = loadData();
    if (!data.length) { box.innerHTML = '<div class="adm-empty">还没有内容。填个主题 → 一键生成草稿 → 存草稿 / 预览发布。</div>'; return; }
    var groups = { '今天': [], '昨天': [], '更早': [] };
    data.forEach(function (c) { groups[dayGroup(c.date)].push(c); });
    var order = ['今天', '昨天', '更早'];
    var html = '';
    order.forEach(function (g) {
      if (!groups[g].length) return;
      html += '<div class="adm-group-h">' + g + '（' + groups[g].length + '）</div>';
      groups[g].forEach(function (c) {
        var typ = c.type === 'ai' ? 'AI动态' : '知识文章';
        var acts = '<button class="adm-dbtn" onclick="admEdit(\'' + c.id + '\')">编辑</button>'
          + '<button class="adm-dbtn" onclick="admPreviewById(\'' + c.id + '\',\'' + c.type + '\')">预览</button>';
        if (c.status === 'published') {
          acts += '<button class="adm-dbtn pri" onclick="admRepublish(\'' + c.id + '\')">重发</button>';
        } else {
          acts += '<button class="adm-dbtn pri" onclick="admRepublish(\'' + c.id + '\')">发布</button>';
        }
        acts += '<button class="adm-dbtn danger" onclick="admDelete(\'' + c.id + '\')">删除</button>';
        html += '<div class="adm-ditem" data-status="' + c.status + '">'
          + '<div class="adm-dtop"><span class="adm-dtitle">' + esc(c.title) + '</span>' + badge(c.status) + '</div>'
          + '<div class="adm-dmeta">' + typ + ' · ' + esc(c.category) + ' · ' + esc(c.date) + '</div>'
          + '<div class="adm-dacts">' + acts + '</div></div>';
      });
    });
    box.innerHTML = html;
  }
  function renderToday() {
    var data = loadData();
    var t = todayStr();
    var ai = data.filter(function (x) { return x.type === 'ai' && x.status === 'published' && x.date === t; }).length;
    var know = data.filter(function (x) { return x.type === 'know' && x.status === 'published' && x.date === t; }).length;
    if ($('admTcAi')) $('admTcAi').textContent = Math.min(ai, 1) + '/1';
    if ($('admTcKnow')) $('admTcKnow').textContent = Math.min(know, 1) + '/1';
    if ($('admTcWord')) $('admTcWord').textContent = '0/20';
    var done = $('admTodayDone');
    if (done) done.style.display = (ai >= 1 && know >= 1) ? 'block' : 'none';
  }

  // —— 表单 <-> 数据 ——
  function formItem() {
    return {
      title: $('admTitle').value.trim(),
      summary: $('admSummary').value.trim(),
      content: $('admBody').value.trim(),
      quiz: $('admQuiz').value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean),
      cat: $('admCat').value,
      mins: parseInt($('admMins').value, 10) || 8,
      theme: $('admTheme').value.trim()
    };
  }
  function clearForm() {
    $('admTheme').value = ''; $('admTitle').value = ''; $('admSummary').value = '';
    $('admBody').value = ''; $('admQuiz').value = ''; $('admCat').value = 'tech'; $('admMins').value = '8';
  }
  function makeItem(f, type, status, id) {
    return normItem({
      id: id || genId(type),
      type: type,
      title: f.title || (f.theme || '未命名主题'),
      summary: f.summary,
      content: f.content,
      quiz: f.quiz,
      cat: f.cat,
      category: catLabel(f.cat),
      date: todayStr(),
      status: status,
      mins: f.mins
    });
  }
  function upsert(it) {
    var data = loadData();
    var idx = -1;
    for (var i = 0; i < data.length; i++) { if (data[i].id === it.id) { idx = i; break; } }
    if (idx >= 0) {
      if (data[idx].status === 'published') { it.id = genId(it.type); data.push(it); }
      else { data[idx] = it; }
    } else { data.push(it); }
    saveData(data);
  }

  // —— 入口/关闭 ——
  function openAdmin() { $('adminModal').classList.add('show'); renderList(); renderToday(); }
  function closeAdmin() { $('adminModal').classList.remove('show'); }
  window.admOpen = openAdmin; window.admClose = closeAdmin;

  // —— 一键生成草稿（模板法，离线可用） ——
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
  window.admGenerate = function () {
    var th = $('admTheme').value;
    if (!th.trim()) { toast('先填「今天主题」'); return; }
    var d = genDraft(th);
    $('admTitle').value = d.title;
    $('admSummary').value = d.summary;
    $('admBody').value = d.body.replace(/<[^>]+>/g, '');
    $('admQuiz').value = d.quiz.join('\n');
    editingId = null; editingIdType = null;
    toast('已生成草稿，可继续润色或预览发布');
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

  // —— 草稿 / 预览 / 发布 ——
  var editingId = null, editingIdType = null;
  var pending = null;

  window.admSaveDraft = function () {
    var f = formItem();
    if (!f.title && !f.theme) { toast('请先填主题或标题'); return; }
    var type = editingIdType || 'know';
    var it = makeItem(f, type, 'draft', editingId);
    upsert(it);
    editingId = it.id; editingIdType = it.type;
    renderList(); renderToday();
    toast('已存草稿 📝');
  };
  window.admPreview = function (type) {
    var f = formItem();
    if (!f.title) { toast('标题不能为空，可点「一键生成草稿」'); return; }
    pending = { type: type, id: editingId, f: f };
    renderPreview();
    $('admPreview').classList.add('show');
  };
  window.admPreviewById = function (id, type) {
    var data = loadData(); var it = null;
    for (var i = 0; i < data.length; i++) { if (data[i].id === id) { it = data[i]; break; } }
    if (!it) return;
    editingId = it.id; editingIdType = it.type;
    $('admTheme').value = ''; $('admTitle').value = it.title; $('admSummary').value = it.summary;
    $('admBody').value = it.content; $('admQuiz').value = it.quiz.join('\n');
    $('admCat').value = it.cat || 'tech'; $('admMins').value = it.mins || 8;
    pending = { type: type || it.type, id: it.id, f: formItem() };
    renderPreview();
    $('admPreview').classList.add('show');
  };
  function renderPreview() {
    var f = pending.f;
    var meta = (pending.type === 'ai' ? 'AI动态' : '知识文章') + ' · ' + catLabel(f.cat) + ' · 约 ' + (f.mins || 8) + ' 分钟';
    if ($('admPrevMeta')) $('admPrevMeta').textContent = meta;
    var html = '<h2 style="margin-top:0">' + esc(f.title || '(无标题)') + '</h2>';
    if (f.summary) html += '<p class="lead">' + esc(f.summary) + '</p>';
    html += bodyHtml(f);
    if (f.quiz && f.quiz.length) html += '<div class="summary"><span class="st">📌 学习问题</span><ul>' + f.quiz.map(function (q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ul></div>';
    if ($('admPrevBody')) $('admPrevBody').innerHTML = html;
  }
  window.admConfirmPublish = function () {
    if (!pending) return;
    var it = makeItem(pending.f, pending.type, 'published', pending.id);
    upsert(it);
    injectOne(it);
    renderList(); renderToday();
    closePreview();
    toast('已发布 ✓');
  };
  window.admSaveAsReview = function () {
    if (!pending) return;
    var it = makeItem(pending.f, pending.type, 'review', pending.id);
    upsert(it);
    renderList(); renderToday();
    closePreview();
    toast('已存为待审核 👀');
  };
  window.admClosePreview = function () { closePreview(); };
  function closePreview() { var p = $('admPreview'); if (p) p.classList.remove('show'); }

  window.admEdit = function (id) {
    var data = loadData(); var it = null;
    for (var i = 0; i < data.length; i++) { if (data[i].id === id) { it = data[i]; break; } }
    if (!it) return;
    editingId = it.id; editingIdType = it.type;
    $('admTheme').value = ''; $('admTitle').value = it.title; $('admSummary').value = it.summary;
    $('admBody').value = it.content; $('admQuiz').value = it.quiz.join('\n');
    $('admCat').value = it.cat || 'tech'; $('admMins').value = it.mins || 8;
    var sheet = document.querySelector('#adminModal .adm-sheet');
    if (sheet) sheet.scrollTop = 0;
    toast('已载入编辑，改完点「存草稿」或「预览」');
  };
  window.admRepublish = function (id) {
    var data = loadData(); var it = null, idx = -1;
    for (var i = 0; i < data.length; i++) { if (data[i].id === id) { it = data[i]; idx = i; break; } }
    if (!it) return;
    it.status = 'published'; it.date = todayStr();
    data[idx] = it; saveData(data);
    injectOne(it);
    renderList(); renderToday();
    toast('已发布 ✓');
  };
  window.admDelete = function (id) {
    var data = loadData().filter(function (x) { return x.id !== id; });
    saveData(data);
    var el = document.getElementById(id); if (el) el.remove();
    if (typeof ATLAS !== 'undefined') { for (var i = ATLAS.length - 1; i >= 0; i--) { if (ATLAS[i].id === id) ATLAS.splice(i, 1); } }
    document.querySelectorAll('[onclick*="' + id + '"]').forEach(function (n) { n.remove(); });
    if (editingId === id) { editingId = null; editingIdType = null; clearForm(); }
    renderList(); renderToday();
    toast('已删除');
  };
  window.admRefreshList = function () { renderList(); renderToday(); toast('已刷新'); };

  window.admExport = function () {
    var data = loadData();
    if (!data.length) { toast('还没有生成内容'); return; }
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = 'zheshao-custom-' + todayStr() + '.json';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    toast('已导出 ' + data.length + ' 条，去 update-center 入库');
  };

  // —— 隐藏入口绑定 ——
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

  function injectAll() { loadData().forEach(function (c) { if (c.status === 'published') injectOne(c); }); }

  if (document.readyState !== 'loading') { bindHidden(); injectAll(); }
  else { document.addEventListener('DOMContentLoaded', function () { bindHidden(); injectAll(); }); }
  var modal = $('adminModal');
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeAdmin(); });
  var pv = $('admPreview');
  if (pv) pv.addEventListener('click', function (e) { if (e.target === pv) closePreview(); });
})();
