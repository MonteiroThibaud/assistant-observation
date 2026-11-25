# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des mises à jour incrémentales du service worker.
Usage : python3 test_service_worker_incremental.py SITE_INSTALLE_DIR GABARIT_SW.js [DOSSIER_DE_TRAVAIL]
SITE_INSTALLE_DIR : le site construit (dossier « site »). GABARIT_SW.js : site-statique/sw.js (avec ses marques). Le test fabrique plusieurs versions du site dans le dossier de travail
(liens physiques : peu d'espace), les sert avec un petit serveur qui note chaque demande, et vérifie : première installation complète, mise à jour qui ne télécharge que les fichiers
modifiés, hors ligne après la mise à jour, installation interrompue (l'ancienne version reste en service, la reprise ne retélécharge pas ce qui est arrivé), migration depuis
l'ancien service worker (sans manifeste). Le service worker ne s'enregistre qu'en https dans la page : le test lève cette condition dans ses copies. Code de retour 0 si tout est réussi."""
import sys, os, shutil, json, threading, http.server, socketserver, time, re, datetime
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__))))
import importlib.util
from playwright.sync_api import sync_playwright
SITE,GAB=sys.argv[1],sys.argv[2]; TRAV=sys.argv[3] if len(sys.argv)>3 else '/tmp/swtest'
here=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('msw',os.path.join(here,'manifeste_sw.py')); msw=importlib.util.module_from_spec(sp); sp.loader.exec_module(msw)
gabarit=open(GAB,encoding='utf-8').read(); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
def copie(src,dst):
    shutil.rmtree(dst,ignore_errors=True); shutil.copytree(src,dst,copy_function=os.link)
def ecrire(dst,rel,data):          # écrit un nouveau fichier (le lien physique avec l'original est rompu d'abord)
    p=os.path.join(dst,rel); os.makedirs(os.path.dirname(p),exist_ok=True)
    if os.path.exists(p): os.unlink(p)
    open(p,'wb').write(data)
def lire(dst,rel): return open(os.path.join(dst,rel),'rb').read()
shutil.rmtree(TRAV,ignore_errors=True); os.makedirs(TRAV)
# A : version 0.90 de l'essai (condition https levée) ; B : 0.91 ; C : 0.92 ; L : ancien service worker
A=os.path.join(TRAV,'A'); copie(SITE,A)
h=lire(A,'index.html').decode('utf-8'); assert "location.protocol==='https:'&&" in h
ecrire(A,'index.html',h.replace("location.protocol==='https:'&&",'').encode('utf-8')); msw.produire(A,'0.90',gabarit)
B=os.path.join(TRAV,'B'); copie(A,B)
ecrire(B,'index.html',lire(A,'index.html').replace(b'</body>',b'<script>window.__B=1</script></body>',1)); ecrire(B,'img/M1.jpg',lire(A,'img/M1.jpg')+b'\x00'); ecrire(B,'img/nouveau-essai.bin',b'nouveau'*100)
os.unlink(os.path.join(B,'img/M2.jpg')); msw.produire(B,'0.91',gabarit)
C=os.path.join(TRAV,'C'); copie(B,C)
ecrire(C,'index.html',lire(B,'index.html').replace(b'window.__B=1',b'window.__B=1;window.__C=1')); ecrire(C,'img/M4.jpg',lire(B,'img/M4.jpg')+b'\x00'); ecrire(C,'img/M5.jpg',lire(B,'img/M5.jpg')+b'\x00'); msw.produire(C,'0.92',gabarit)
mA=json.load(open(os.path.join(A,'manifeste-sw.json')))['fichiers']; mB=json.load(open(os.path.join(B,'manifeste-sw.json')))['fichiers']; mC=json.load(open(os.path.join(C,'manifeste-sw.json')))['fichiers']
DON='assistant-observation-donnees'      # stockage commun à toutes les versions (fichiers de img/)
npart=lambda m:sum(1 for f in m.values() if f.get('p')); nver=lambda m:sum(1 for f in m.values() if not f.get('p'))
vers=lambda e:{k:v for k,v in e.items() if k!=DON}
# serveur qui note les demandes
STATE={'root':A,'log':[],'fail':set(),'down':False}      # down : le serveur coupe les connexions (hors ligne simulé côté serveur, sans toucher au navigateur)
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=path.split('?',1)[0].split('#',1)[0]; return os.path.join(STATE['root'],path.lstrip('/').replace('/',os.sep) or 'index.html')
    def do_GET(self):
        for h in ('If-Modified-Since','If-None-Match'):      # le serveur d'essai répond toujours le fichier entier (les fichiers de l'essai sont créés dans la même seconde : sans cela, des réponses 304 masqueraient les changements)
            if h in self.headers: del self.headers[h]
        p=self.path.split('?',1)[0]
        if STATE['down']:
            try: self.connection.shutdown(2)
            except Exception: pass
            self.close_connection=True; return
        STATE['log'].append(p)
        if p in STATE['fail']: self.send_error(500,'panne simulée'); return
        return super().do_GET()
    def end_headers(self): self.send_header('Cache-Control','no-cache'); super().end_headers()
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
PORT=8899; srv=S(('127.0.0.1',PORT),H); threading.Thread(target=srv.serve_forever,daemon=True).start(); URL='http://localhost:%d/index.html'%PORT
def demandes(): l=STATE['log'][:]; STATE['log'].clear(); return l
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},timezone_id='Europe/Paris',locale='fr-FR'); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,11,21,20,30,tzinfo=datetime.timezone(datetime.timedelta(hours=1))))
    def etat():
        return pg.evaluate("""async()=>{ const ks=await caches.keys(), out={}; for(const k of ks){ const c=await caches.open(k); out[k]={n:(await c.keys()).length, man:!!(await c.match('./manifeste-sw.json'))} } return out }""")
    def attendre(cond,delai=240):
        t0=time.time()
        while time.time()-t0<delai:
            try:
                e=etat()
                if cond(e): return e
            except Exception: pass
            pg.wait_for_timeout(500)
        return etat()
    # 1. première installation
    STATE['root']=A; pg.goto(URL); e1=attendre(lambda e:any(v['man'] for v in e.values()))
    e1=attendre(lambda e:any(v['man'] for v in vers(e).values()) and e.get(DON,{}).get('n')==npart(mA)); l1=demandes(); noms=list(vers(e1))
    check('première installation : un cache de version (0.90, avec son manifeste) et le stockage commun',len(noms)==1 and noms[0].startswith('assistant-observation-0.90-') and e1[noms[0]]['man'] and DON in e1,list(e1))
    check('première installation : %d fichiers dans le cache de version, %d dans le stockage commun'%(nver(mA)+1,npart(mA)),e1[noms[0]]['n']==nver(mA)+1 and e1[DON]['n']==npart(mA),(e1[noms[0]]['n'],nver(mA)+1,e1[DON]['n'],npart(mA)))
    vus={x for x in l1}; manquants=[u for u in mA if u[1:] not in vus]
    check('première installation : chaque fichier a été demandé au réseau',not manquants,manquants[:3])
    pg.wait_for_timeout(1500); controle=pg.evaluate("!!navigator.serviceWorker.controller") or pg.reload() is None and pg.evaluate("!!navigator.serviceWorker.controller")
    # 2. mise à jour A -> B : seuls les fichiers modifiés sont téléchargés
    STATE['root']=B; demandes(); pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())")
    e2=attendre(lambda e:len(vers(e))==1 and list(vers(e))[0].startswith('assistant-observation-0.91-') and list(vers(e).values())[0]['man'] and e.get(DON,{}).get('n')==npart(mB))
    l2=demandes(); u2=set(l2); noms2=list(vers(e2))
    attendu={'/sw.js','/manifeste-sw.json','/index.html','/img/M1.jpg','/img/nouveau-essai.bin'}
    check('mise à jour 0.90 → 0.91 : l\'ancien cache est supprimé, le nouveau est complet et le stockage commun est à jour (fichier retiré supprimé)',len(noms2)==1 and noms2[0].startswith('assistant-observation-0.91-') and e2[noms2[0]]['n']==nver(mB)+1 and e2[DON]['n']==npart(mB),(noms2,e2.get(noms2[0]) if noms2 else None,e2.get(DON)))
    check('mise à jour : seuls le service worker, le manifeste et les 3 fichiers modifiés ou nouveaux sont demandés',u2<=attendu|{'/'} and attendu-{'/sw.js'}<=u2,sorted(u2)[:8])
    octets=sum(len(lire(B,x[1:])) for x in u2 if os.path.exists(os.path.join(B,x[1:])) and x not in('/',))
    check('mise à jour : volume téléchargé réduit (%.2f Mo au lieu de %.1f Mo)'%(octets/1e6,sum(f['t'] for f in mA.values())/1e6),octets<0.1*sum(f['t'] for f in mA.values()),octets)
    # 3. hors ligne après la mise à jour
    pg.reload(); pg.wait_for_timeout(2500); demandes()
    STATE['down']=True; pg.reload(); pg.wait_for_timeout(4000)
    check('hors ligne : la page de la version 0.91 s\'ouvre depuis le cache',pg.evaluate("window.__B===1"))
    ok_img=pg.evaluate("fetch('img/M3.jpg').then(r=>r.ok).catch(()=>false)"); ko_img=pg.evaluate("fetch('img/M2.jpg').then(r=>r.ok).catch(()=>false)")
    check('hors ligne : fichier inchangé (stockage commun) servi ; fichier supprimé de la version absent',ok_img and not ko_img,(ok_img,ko_img))
    n_m1=pg.evaluate("fetch('img/M1.jpg').then(r=>r.arrayBuffer()).then(b=>b.byteLength).catch(()=>-1)")
    check('hors ligne : le fichier modifié est celui de la nouvelle version',n_m1==len(lire(B,'img/M1.jpg')),(n_m1,len(lire(B,'img/M1.jpg'))))
    STATE['down']=False
    # 4. installation interrompue : B -> C, avec M4 en panne
    STATE['root']=C; STATE['fail']={'/img/M4.jpg'}; demandes(); pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())")
    t0=time.time(); pg.wait_for_timeout(1500)
    while time.time()-t0<300:                                   # on attend que cette première tentative ait échoué (la copie des fichiers inchangés peut prendre plusieurs secondes)
        try:
            if not pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r&&!r.installing)") or not any(k.startswith('assistant-observation-0.92-') for k in etat()): pg.wait_for_timeout(500); continue   # la tentative doit avoir commencé (cache 0.92 créé) puis fini
        except Exception: pg.wait_for_timeout(500); continue
        break
    l4=demandes(); e4=etat()
    check('installation interrompue (fichier en panne) : la version 0.91 reste en service, avec son manifeste',any(k.startswith('assistant-observation-0.91-') and v['man'] for k,v in e4.items()),list(e4))
    STATE['down']=True; pg.reload(); pg.wait_for_timeout(3500); check('installation interrompue : la page reste utilisable hors ligne (0.91, pas encore 0.92)',pg.evaluate("window.__B===1 && !window.__C"))
    n_m4=pg.evaluate("fetch('img/M4.jpg').then(r=>r.arrayBuffer()).then(b=>b.byteLength).catch(()=>-1)")
    check('installation interrompue : l\'ancienne version garde l\'ancien fichier de données (M4 de la 0.91), même si la nouvelle est déjà en partie arrivée',n_m4==len(lire(B,'img/M4.jpg')),(n_m4,len(lire(B,'img/M4.jpg'))))
    STATE['down']=False
    ok4={x for x in l4 if x not in STATE['fail']}-{'/sw.js','/manifeste-sw.json'}
    STATE['fail']=set(); demandes()
    fini=lambda e:len(vers(e))==1 and list(vers(e))[0].startswith('assistant-observation-0.92-') and list(vers(e).values())[0]['man'] and e.get(DON,{}).get('n')==npart(mC)
    for tent in range(1,5):                                    # comme le navigateur aux visites suivantes : une nouvelle vérification de mise à jour si l'installation n'a pas abouti
        pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())")
        e5=attendre(fini,60 if tent<4 else 240)
        if fini(e5): break
    l5=set(demandes()); print('  reprise : vérifications de mise à jour nécessaires :',tent if fini(e5) else 'échec après %d'%tent,flush=True)
    reg5=pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>({installing:!!r.installing,waiting:!!r.waiting,active:!!r.active}))")
    check('reprise : la version 0.92 s\'installe, les anciens caches sont supprimés et le stockage commun est à jour',len(vers(e5))==1 and list(vers(e5))[0].startswith('assistant-observation-0.92-') and list(vers(e5).values())[0]['n']==nver(mC)+1 and e5.get(DON,{}).get('n')==npart(mC),{'caches':e5,'service worker':reg5})
    deja=ok4&l5
    check('reprise : ce qui était déjà arrivé n\'est pas retéléchargé',not (deja-{'/','/index.html'}) ,sorted(deja)[:5])
    check('reprise : le fichier qui était en panne est enfin téléchargé','/img/M4.jpg' in l5)
    # 5. migration depuis l'ancien service worker (sans manifeste)
    ctx2=b.new_context(viewport={'width':411,'height':850}); q=ctx2.new_page()
    L=os.path.join(TRAV,'L'); copie(A,L)
    ancien=open(os.path.join(here,'sw-ancien-0.88.js'),encoding='utf-8').read() if os.path.exists(os.path.join(here,'sw-ancien-0.88.js')) else None
    if ancien:
        fl=["'./"+k[2:]+"'" for k in mA if k!='./index.html']; ancien=re.sub(r"const FILES = \[.*?\];","const FILES = ['./', './index.html', "+', '.join(fl)+"];",ancien,count=1,flags=re.S); ancien=ancien.replace("assistant-observation-088","assistant-observation-085")
        ecrire(L,'sw.js',ancien.encode('utf-8')); STATE['root']=L; demandes(); q.goto(URL); t0=time.time()
        while time.time()-t0<120:
            e=q.evaluate("async()=>{const ks=await caches.keys(),o={};for(const k of ks){o[k]=(await (await caches.open(k)).keys()).length}return o}")
            if any(v>=len(mA) for v in e.values()): break
            q.wait_for_timeout(500)
        check('migration : l\'ancien service worker (sans manifeste) a installé son cache',any(k=='assistant-observation-085' for k in e),list(e)); demandes()
        STATE['root']=A; q.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())"); t0=time.time()
        while time.time()-t0<150:
            e=q.evaluate("async()=>{const ks=await caches.keys(),o={};for(const k of ks){const c=await caches.open(k);o[k]=[(await c.keys()).length,!!(await c.match('./manifeste-sw.json'))]}return o}")
            ev={k:v for k,v in e.items() if k!=DON}
            if len(ev)==1 and list(ev)[0].startswith('assistant-observation-0.90-') and list(ev.values())[0][1] and e.get(DON,[0])[0]==npart(mA): break
            q.wait_for_timeout(500)
        lm=set(demandes()); manq=[u for u in mA if u[1:] not in lm and u!='./index.html']
        ev={k:v for k,v in e.items() if k!=DON}
        check('migration : le premier passage au nouveau service worker télécharge tout une fois, range les données dans le stockage commun et supprime l\'ancien cache',len(ev)==1 and list(ev)[0].startswith('assistant-observation-0.90-') and DON in e and not manq,(list(e),manq[:3]))
    else: print('(migration non testée : sw-ancien-0.88.js absent)')
    # 6. migration depuis la version 0.90 à 0.94 (un cache par version complet, sans stockage commun) : petits fichiers copiés, gros fichiers téléchargés une fois
    ctx3=b.new_context(viewport={'width':411,'height':850}); r3=ctx3.new_page(); errs3=[]; r3.on('pageerror',lambda e:errs3.append(str(e)))
    anc90=os.path.join(here,'sw-ancien-0.90.js')
    if os.path.exists(anc90):
        Dd=os.path.join(TRAV,'D'); copie(A,Dd); msw.produire(Dd,'0.89',open(anc90,encoding='utf-8').read(),partages=False)
        info=lambda:r3.evaluate("""async()=>{ const ks=await caches.keys(), out={}; for(const k of ks){ const c=await caches.open(k); out[k]={n:(await c.keys()).length, man:!!(await c.match('./manifeste-sw.json'))} } return out }""")
        def attendre3(cond,delai=240):
            t0=time.time()
            while time.time()-t0<delai:
                try:
                    e=info()
                    if cond(e): return e
                except Exception: pass
                r3.wait_for_timeout(500)
            return info()
        STATE['root']=Dd; demandes(); r3.goto(URL); e6=attendre3(lambda e:any(v['man'] and v['n']==len(mA)+1 for v in e.values()))
        check('migration depuis la 0.90 : l\'ancien service worker a installé son cache complet (%d fichiers)'%(len(mA)+1),any(k.startswith('assistant-observation-0.89-') and v['n']==len(mA)+1 for k,v in e6.items()),{k:v['n'] for k,v in e6.items()})
        STATE['root']=A; demandes(); r3.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())")
        e7=attendre3(lambda e:len(vers(e))==1 and list(vers(e))[0].startswith('assistant-observation-0.90-') and list(vers(e).values())[0]['man'] and e.get(DON,{}).get('n')==npart(mA))
        l7=set(demandes()); gros=[u for u,f in mA.items() if f.get('p') and f['t']>=1500000]; petits=[u for u,f in mA.items() if f.get('p') and f['t']<1500000]
        check('migration depuis la 0.90 : cache de version et stockage commun complets, ancien cache supprimé',len(vers(e7))==1 and list(vers(e7))[0].startswith('assistant-observation-0.90-') and list(vers(e7).values())[0]['n']==nver(mA)+1 and e7.get(DON,{}).get('n')==npart(mA),{k:v['n'] for k,v in e7.items()})
        check('migration depuis la 0.90 : les %d gros fichiers de données sont téléchargés une fois'%len(gros),all(u[1:] in l7 for u in gros),[u for u in gros if u[1:] not in l7][:3])
        check('migration depuis la 0.90 : les %d petits fichiers de données sont copiés sur place (aucune demande au réseau)'%len(petits),not [u for u in petits if u[1:] in l7],[u for u in petits if u[1:] in l7][:3])
        check('migration depuis la 0.90 : aucune erreur JavaScript',not errs3,errs3[:1] or 'aucune')
    else: print('(migration depuis la 0.90 non testée : sw-ancien-0.90.js absent)')
    check('aucune erreur JavaScript dans la page',not errs,errs[:1] or 'aucune')
    b.close()
srv.shutdown(); shutil.rmtree(TRAV,ignore_errors=True)
ok=all(res); print('\nBILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if ok else 1)
