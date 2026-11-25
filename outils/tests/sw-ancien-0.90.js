// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
// Assistant d'observation : fonctionnement hors ligne et mises à jour incrémentales (0.90).
// À chaque version, la construction publie « manifeste-sw.json » : l'empreinte et la taille de chaque fichier de l'application.
// Le service worker garde les fichiers dans un cache propre à la version. Quand une nouvelle version s'installe, il COPIE sur place (sans réseau)
// les fichiers dont l'empreinte n'a pas changé depuis le cache précédent, et ne télécharge que les fichiers nouveaux ou modifiés.
// La première installation (ou le passage d'une version sans manifeste) télécharge tout. Une installation interrompue laisse la version précédente
// en service ; la suivante reprend sans retélécharger ce qui est déjà arrivé.
const VERSION = '@@VERSION@@', BUILD = '@@BUILD@@';   // remplacés à la construction ; BUILD change dès qu'un fichier change : le navigateur voit un nouveau sw.js et lance la mise à jour
const PREFIX = 'assistant-observation-', CACHE = PREFIX + VERSION + '-' + BUILD, MANIFEST = './manifeste-sw.json', PARALLEL = 6;

async function installer() {
  const rep = await fetch(MANIFEST, {cache: 'no-store'});
  if (!rep.ok) throw new Error('manifeste absent : ' + rep.status);
  const man = await rep.json(), cache = await caches.open(CACHE);
  // dernier cache précédent qui possède son manifeste (les caches des anciennes versions n'en ont pas : tout est alors téléchargé)
  let ancien = null, ancienMan = null;
  for (const nom of (await caches.keys()).filter(k => k.startsWith(PREFIX) && k !== CACHE).sort().reverse()) {
    const c = await caches.open(nom), m = await c.match(MANIFEST);
    if (m) { try { ancienMan = await m.json(); ancien = c; break } catch (_) {} }
  }
  const aTelecharger = [];
  for (const [u, f] of Object.entries(man.fichiers)) {
    if (await cache.match(u)) continue;                                                    // déjà arrivé (installation reprise)
    const av = ancienMan && ancienMan.fichiers[u];
    if (ancien && av && av.h === f.h) { const r = await ancien.match(u); if (r) { await cache.put(u, r); continue } }   // inchangé : copie locale
    aTelecharger.push([u, f]);
  }
  let i = 0, erreur = null;
  const ouvrier = async () => {
    while (i < aTelecharger.length && !erreur) {
      const [u, f] = aTelecharger[i++];
      try { const r = await fetch(u, {cache: 'reload'}); if (!r.ok) throw new Error(u + ' : ' + r.status); await cache.put(u, r) }
      catch (x) { if (!f.o) erreur = x }                                                   // les fichiers facultatifs (relief fin, grand catalogue d'étoiles) ne bloquent pas l'installation
    }
  };
  await Promise.all(Array.from({length: PARALLEL}, ouvrier));
  if (erreur) throw erreur;
  await cache.put(MANIFEST, new Response(JSON.stringify(man), {headers: {'Content-Type': 'application/json'}}));   // en dernier : un cache sans manifeste est une installation inachevée
}
self.addEventListener('install', e => { e.waitUntil(installer()); self.skipWaiting(); });
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith(PREFIX) && k !== CACHE) await caches.delete(k);   // anciennes versions et installations inachevées
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Autres sites (par exemple les fichiers d'éléments d'orbite du MPC) : jamais gardés ni servis depuis le cache, pour que la mise à jour donne toujours la version du jour
  if (url.origin !== self.location.origin) return;
  // Pages autres que l'application (par exemple /.well-known/assetlinks.json) : on laisse le réseau répondre
  if (req.mode === 'navigate') {
    const p = url.pathname;
    if (!(p.endsWith('/') || p.endsWith('/index.html'))) return;
  }
  e.respondWith((async () => {
    const cache = await caches.open(CACHE), key = req.mode === 'navigate' ? './index.html' : req;
    const hit = await cache.match(key, {ignoreSearch: true});
    if (hit) return hit;                                                                   // les fichiers ne changent qu'avec une nouvelle version : plus de nouvelle demande au réseau à chaque ouverture
    try { const res = await fetch(req); if (res && res.ok) cache.put(key, res.clone()); return res } catch (_) { return Response.error() }
  })());
});
