/* 泽少学习助手 · Service Worker（离线缓存 + 可安装） */
const CACHE = 'zheshao-v43';
const ASSETS = [
  './',
  './index.html',
  './study.html',
  './manifest.webmanifest',
  './assets/icon.svg',
  './assets/style.css',
  './knowledge/article.css'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return c.addAll(ASSETS).catch(function () {});
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) {
        return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
    .then(function () {
      return self.clients.matchAll().then(function (cs) {
        cs.forEach(function (c) { try { c.postMessage({ type: 'SW_UPDATED' }); } catch (e) {} });
      });
    })
  );
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  // HTML 页面（含根路径与 .html）：network-first，保证每次拿到最新内容
  // ⚠️ 只缓存 resp.ok（200-299）；Pages 构建/回滚窗口期的 404 错误页绝不能进缓存，
  //    线上异常时优先回退旧缓存，避免用户被缓存的 404 卡死
  if (e.request.mode === 'navigate' || /\.html?($|\?)/.test(new URL(e.request.url).pathname)) {
    e.respondWith(
      fetch(e.request).then(function (resp) {
        if (resp.ok) {
          const cp = resp.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, cp); });
          return resp;
        }
        return caches.match(e.request).then(function (m) { return m || resp; });
      }).catch(function () {
        return caches.match(e.request).then(function (m) { return m || caches.match('./index.html'); });
      })
    );
    return;
  }
  // 数据文件（.json，含 ai_cards.json / ielts_bank.json 等）：network-first，
  // 保证每天自动更新的 AI 新闻、单词库能立即生效，不被旧缓存卡住；离线时回退缓存。
  // 同样只缓存成功响应，防止 404 被缓存后永久污染数据
  if (/\.json($|\?)/.test(new URL(e.request.url).pathname)) {
    e.respondWith(
      fetch(e.request).then(function (resp) {
        if (resp.ok) {
          const cp = resp.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, cp); });
          return resp;
        }
        return caches.match(e.request).then(function (m) { return m || resp; });
      }).catch(function () {
        return caches.match(e.request);
      })
    );
    return;
  }
  // 其余静态资源（css/js/图片/音频）：cache-first，离线可用
  // ⚠️ 只缓存 resp.ok——音频文件名对不上产生 404 时不会把错误缓存住，修复后立即可用
  e.respondWith(
    caches.match(e.request).then(function (cached) {
      if (cached) return cached;
      return fetch(e.request).then(function (resp) {
        if (resp.ok) {
          const cp = resp.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, cp); });
        }
        return resp;
      }).catch(function () {
        return caches.match('./index.html');
      });
    })
  );
});
