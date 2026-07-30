/* 泽少学习助手 · Service Worker（离线缓存 + 可安装） */
const CACHE = 'zheshao-v33';
const ASSETS = [
  './',
  './index.html',
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
  if (e.request.mode === 'navigate' || /\.html?($|\?)/.test(new URL(e.request.url).pathname)) {
    e.respondWith(
      fetch(e.request).then(function (resp) {
        const cp = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(e.request, cp); });
        return resp;
      }).catch(function () {
        return caches.match(e.request).then(function (m) { return m || caches.match('./index.html'); });
      })
    );
    return;
  }
  // 静态资源：cache-first，离线可用
  e.respondWith(
    caches.match(e.request).then(function (cached) {
      if (cached) return cached;
      return fetch(e.request).then(function (resp) {
        const cp = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(e.request, cp); });
        return resp;
      }).catch(function () {
        return caches.match('./index.html');
      });
    })
  );
});
