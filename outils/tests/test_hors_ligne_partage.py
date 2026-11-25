#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Test de bout en bout du site installé avec le stockage commun : installation par le service worker, puis hors ligne complet.
# Usage : python3 test_hors_ligne_partage.py DOSSIER_DU_SITE_INSTALLE   (le dossier doit contenir manifeste-sw.json et sw.js construits)
import re, sys, os, shutil, tempfile, threading, http.server, socketserver, datetime, json
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read(); k=s.index("  $('featClose').onclick=")
a="location.protocol==='https:'&&"; assert a in s
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write((s[:k]+"  window.__go=goMoonMap;\n"+s[k:]).replace(a,''))
man=json.load(open(os.path.join(SITE,'manifeste-sw.json')))['fichiers']; npers=sum(1 for f in man.values() if f.get('p')); nver=len(man)-npers
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=T,**k)
    def log_message(self,*a): pass
    def end_headers(self): self.send_header('Cache-Control','no-cache'); super().end_headers()
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8880),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
tz=datetime.timezone(datetime.timedelta(hours=1))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'],service_workers='allow')
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); sw=[]; ko=[]
    pg.on('response',lambda r:sw.append(r.url) if r.from_service_worker else None); pg.on('requestfailed',lambda r:ko.append(r.url))
    pg.clock.install(time=datetime.datetime(2026,11,15,16,0,tzinfo=tz)); pg.goto('http://localhost:8880/index.html'); pg.wait_for_timeout(6000)
    info=lambda:pg.evaluate("""async()=>{ const ks=await caches.keys(), o={}; for(const k of ks){ o[k]=(await (await caches.open(k)).keys()).length } return o }""")
    import time; t0=time.time(); e={}
    while time.time()-t0<240:
        e=info()
        if e.get('assistant-observation-donnees')==npers and any(re.match(r'assistant-observation-\d+\.\d+-',k) and v==nver+1 for k,v in e.items()): break
        pg.wait_for_timeout(1000)
    check('installation : cache de version (%d) et stockage commun (%d) complets'%(nver+1,npers),e.get('assistant-observation-donnees')==npers and any(re.match(r'assistant-observation-\d+\.\d+-',k) and v==nver+1 for k,v in e.items()),e)
    pg.reload(); pg.wait_for_timeout(3000); c.set_offline(True)
    pg.reload(); pg.wait_for_timeout(9000)
    check('hors ligne : la page s\'ouvre',pg.title()!='' and pg.evaluate("document.querySelectorAll('.tabbar button').length")==6,pg.title())
    gros=sorted(((f['t'],u) for u,f in man.items() if f.get('p')),reverse=True)[:3]
    for t,u in gros:
        n=pg.evaluate("(u)=>fetch(u).then(r=>r.ok?r.arrayBuffer().then(b=>b.byteLength):-1).catch(()=>-2)",u[2:]); check('hors ligne : %s servi par le stockage commun (%.1f Mo)'%(u,t/1e6),n==t,(n,t))
    tuile=next(u for u in man if '/tuiles/t_' in u); dss=next(u for u in man if u.startswith('./img/') and u.endswith('.jpg') and '/tuiles/' not in u)
    for u in (tuile,dss):
        n=pg.evaluate("(u)=>fetch(u).then(r=>r.ok?r.arrayBuffer().then(b=>b.byteLength):-1).catch(()=>-2)",u[2:]); check('hors ligne : %s servi (%d octets)'%(u,man[u]['t']),n==man[u]['t'],(n,man[u]['t']))
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(4000); pg.click('#mapNow'); pg.wait_for_timeout(2000)
    pg.evaluate("window.__go('Copernic')"); pg.wait_for_timeout(3000)
    for _ in range(3): pg.click('#zoomIn'); pg.wait_for_timeout(700)
    pg.wait_for_timeout(8000)
    tuiles=[u for u in sw if '/img/tuiles/t_' in u]; check('hors ligne : les tuiles de la carte de la Lune à fort grossissement viennent du service worker',len(tuiles)>0,len(tuiles))
    fin=pg.evaluate("document.getElementById('fineBtn').textContent"); check('hors ligne : relief fin actif',fin=='Relief fin : activé',fin)
    check('hors ligne : aucune requête en échec vers le site',not [u for u in ko if u.startswith('http://localhost:8880')],[u for u in ko if u.startswith('http://localhost:8880')][:3])
    check('aucune erreur JavaScript',not errs,errs[:1]); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
