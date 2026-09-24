const VERSION = 'v3';
const CACHE = `finlite:${self.registration.scope}:${VERSION}`;
const ASSETS = ['./', './index.html', './styles.css', './app.js', './engine.js', './db.js', './i18n.js', './manifest.json', './icon.svg', './icons/icon-192.png', './icons/icon-512.png'];
self.addEventListener('install', event => {
    event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS.map(path => new Request(new URL(path, self.location), { cache: 'reload' })))));
});
self.addEventListener('message', event => {
    if (event.data?.type === 'ACTIVATE') self.skipWaiting();
    if (event.data?.type === 'OFFLINE_STATUS' && event.ports[0]) {
        event.waitUntil((async () => {
            const cache = await caches.open(CACHE);
            const assets = await Promise.all(ASSETS.map(path => cache.match(new URL(path, self.location).href)));
            event.ports[0].postMessage({ ready: assets.every(Boolean) });
        })());
    }
});
self.addEventListener('activate', event => {
    const prefix = `finlite:${self.registration.scope}:`;
    event.waitUntil((async () => {
        const keys = await caches.keys();
        await Promise.all(keys.filter(key => key !== CACHE && (key.startsWith(prefix) || /^finlite-v-\d+$/.test(key))).map(key => caches.delete(key)));
        await self.clients.claim();
    })());
});
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    if (event.request.method !== 'GET' || url.origin !== self.location.origin || !url.href.startsWith(self.registration.scope)) return;
    event.respondWith((async () => {
        const cache = await caches.open(CACHE);
        // Keep all code on the same installed version, even while an update waits.
        const cached = await cache.match(event.request.mode === 'navigate' ? new URL('./index.html', self.location).href : event.request, { ignoreSearch: true });
        return cached || fetch(event.request);
    })());
});
