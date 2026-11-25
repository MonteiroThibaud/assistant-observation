// Assistant d'observation : fonctionnement hors ligne et mises à jour incrémentales (0.95).
// À chaque version, la construction publie « manifeste-sw.json » : l'empreinte et la taille de chaque fichier de l'application.
// Deux sortes de caches :
//  - un cache PAR VERSION (assistant-observation-VERSION-BUILD) : la page, les petits fichiers et le manifeste ; à l'installation d'une nouvelle version, les fichiers
//    dont l'empreinte n'a pas changé sont COPIÉS sur place (sans réseau) depuis le cache précédent, les autres sont téléchargés ;
//  - un stockage COMMUN à toutes les versions (assistant-observation-donnees) : les fichiers de données (cartes, relief, étoiles, images : dossier img/), marqués « p » dans le
//    manifeste. Chacun est rangé sous une adresse qui contient son empreinte : une nouvelle version ne télécharge que les fichiers dont l'empreinte a changé, et ne recopie
//    jamais les gros fichiers (le relief fin pèse 31 Mo). L'ancienne version garde ses fichiers jusqu'à l'activation de la nouvelle : une installation interrompue la laisse intacte.
// La première installation (ou le passage d'une version sans manifeste) télécharge tout. Une installation interrompue laisse la version précédente en service ; la suivante
// reprend sans retélécharger ce qui est déjà arrivé. Au premier passage depuis une version sans stockage commun (0.90 à 0.94), les petits fichiers de données inchangés sont copiés
// depuis l'ancien cache et les gros (1,5 Mo et plus : relief fin, carte de base, relief, lieux, étoiles) sont téléchargés une fois.
const VERSION = '@@VERSION@@', BUILD = '@@BUILD@@';   // remplacés à la construction ; BUILD change dès qu'un fichier change : le navigateur voit un nouveau sw.js et lance la mise à jour
const PREFIX = 'assistant-observation-', CACHE = PREFIX + VERSION + '-' + BUILD, DONNEES = PREFIX + 'donnees', MANIFEST = './manifeste-sw.json', PARALLEL = 6, GROS = 1500000;
const SCOPE = self.registration.scope;
const cle = (u, h) => new Request(new URL('__p/' + h + '/' + u.slice(2), SCOPE).href);   // adresse d'un fichier du stockage commun : son empreinte en fait partie

async function installer() {
  const rep = await fetch(MANIFEST, {cache: 'no-store'});
  if (!rep.ok) throw new Error('manifeste absent : ' + rep.status);
  const man = await rep.json(), cache = await caches.open(CACHE), don = await caches.open(DONNEES);
  // dernier cache de version précédent qui possède son manifeste (les caches des anciennes versions n'en ont pas : tout est alors téléchargé)
  let ancien = null, ancienMan = null;
  for (const nom of (await caches.keys()).filter(k => k.startsWith(PREFIX) && k !== CACHE && k !== DONNEES).sort().reverse()) {
    const c = await caches.open(nom), m = await c.match(MANIFEST);
    if (m) { try { ancienMan = await m.json(); ancien = c; break } catch (_) {} }
  }
  const aTelecharger = [];
  for (const [u, f] of Object.entries(man.fichiers)) {
    if (f.p) {                                                                            // fichier de données : jamais copié ; déjà là si son empreinte est la même (ou si l'installation reprend)
      const k = cle(u, f.h);
      if (await don.match(k)) continue;
      const av = ancienMan && ancienMan.fichiers[u];                                       // première fois (version sans stockage commun) : les petits fichiers inchangés sont copiés depuis l'ancien cache ; les gros (1,5 Mo et plus) sont téléchargés, jamais copiés
      if (ancien && av && av.h === f.h && f.t < GROS) { const r = await ancien.match(u); if (r) { await don.put(k, r); continue } }
      aTelecharger.push([u, f, don, k]);
      continue;
    }
    if (await cache.match(u)) continue;                                                    // déjà arrivé (installation reprise)
    const av = ancienMan && ancienMan.fichiers[u];
    if (ancien && av && av.h === f.h) { const r = await ancien.match(u); if (r) { await cache.put(u, r); continue } }   // inchangé : copie locale
    aTelecharger.push([u, f, cache, u]);
  }
  let i = 0, erreur = null;
  const ouvrier = async () => {
    while (i < aTelecharger.length && !erreur) {
      const [u, f, dest, k] = aTelecharger[i++];
      try { const r = await fetch(u, {cache: 'reload'}); if (!r.ok) throw new Error(u + ' : ' + r.status); await dest.put(k, r) }
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
    for (const k of await caches.keys()) if (k.startsWith(PREFIX) && k !== CACHE && k !== DONNEES) await caches.delete(k);   // anciennes versions et installations inachevées
    const m = await manifeste();                                                           // stockage commun : on retire les fichiers que cette version n'utilise plus
    if (m) {
      const voulus = new Set(Object.entries(m.fichiers).filter(([, f]) => f.p).map(([u, f]) => cle(u, f.h).url)), don = await caches.open(DONNEES);
      for (const r of await don.keys()) if (!voulus.has(r.url)) await don.delete(r);
    }
    await self.clients.claim();
  })());
});
let manP = null;                                                                           // manifeste de cette version (relu dans son cache si le service worker a été arrêté)
const manifeste = () => manP || (manP = caches.open(CACHE).then(c => c.match(MANIFEST)).then(r => r ? r.json() : null).catch(() => null).then(m => { if (!m) manP = null; return m }));
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
    const rel = './' + url.pathname.slice(new URL(SCOPE).pathname.length), m = await manifeste(), f = m && m.fichiers[rel];
    if (f && f.p) { const d = await caches.open(DONNEES), h2 = await d.match(cle(rel, f.h)); if (h2) return h2 }   // fichier de données : stockage commun
    try {
      const res = await fetch(req);
      if (res && res.ok) { if (f && f.p) (await caches.open(DONNEES)).put(cle(rel, f.h), res.clone()); else cache.put(key, res.clone()) }
      return res;
    } catch (_) { return Response.error() }
  })());
});
