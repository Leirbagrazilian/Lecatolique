/* Sub Tuum Praesidium — service worker
   App: cache primeiro, com atualização em segundo plano. Fontes do Google: guardadas na primeira visita.
   Ao mudar qualquer arquivo do app, aumente VERSAO para forçar a atualização. */
const VERSAO = 'stp-v4';
const APP = ['./', './index.html', './manifest.json', './icons/icon.svg', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-180.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSAO).then(c => c.addAll(APP)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const fonte = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (url.origin !== location.origin && !fonte) return; // YouTube, Divinum Officium etc.: sempre pela rede
  e.respondWith(caches.open(VERSAO).then(async cache => {
    const chave = req.mode === 'navigate' ? './index.html' : req;
    const guardado = await cache.match(chave, { ignoreSearch: req.mode === 'navigate' });
    const rede = fetch(req).then(r => { if (r && (r.ok || r.type === 'opaque')) cache.put(chave, r.clone()); return r; }).catch(() => guardado);
    return guardado || rede;
  }));
});
