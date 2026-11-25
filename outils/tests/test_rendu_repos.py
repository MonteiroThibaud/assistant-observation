#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Test du rendu de repos et de l'interpolation bicubique de la carte de la Lune (copie de test : aucune modification de l'application).
# Usage : python3 test_rendu_repos.py DOSSIER_DU_SITE_INSTALLE
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime, time
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(ok); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp(); 
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read(); k=s.index("  $('featClose').onclick=")
a="    (function step(){ if(paintTok[slot]!==tok) return; if(job.run(12)) done(job.cv); else setTimeout(step,0) })();"; assert s.count(a)==1
s=(s[:k]+"  window.__go=goMoonMap;\n"+s[k:]).replace("location.protocol==='https:'&&",'').replace(a,"    (function step(){ if(paintTok[slot]!==tok) return; if(job.run(12)){ (window.__paints=window.__paints||[]).push({slot,n:args[0],t:Date.now()}); done(job.cv) } else setTimeout(step,0) })();")
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(s)
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=T,**k)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8879),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
tz=datetime.timezone(datetime.timedelta(hours=1))
def ouvre(p,heure=(2026,11,15,16,0)):
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2.625,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=datetime.datetime(*heure,tzinfo=tz)); pg.goto('http://localhost:8879/index.html'); pg.wait_for_timeout(8000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(3000); pg.click('#mapNow'); pg.wait_for_timeout(2500); return b,pg,errs
def zoome(pg,nom='Al-Bakri',clics=3):
    pg.evaluate("(n)=>window.__go(n)",nom); pg.wait_for_timeout(2500)
    for _ in range(clics): pg.click('#zoomIn'); pg.wait_for_timeout(600)
paints=lambda pg:pg.evaluate("(window.__paints||[]).filter(x=>x.slot==='hi').map(x=>x.n)")
cw=lambda pg:pg.evaluate("document.getElementById('mapHi').width")
with sync_playwright() as p:
    # 1. à ×30 : passage rapide, passage complet, puis rendu de repos à la résolution réelle de l'écran
    b,pg,errs=ouvre(p); zoome(pg); pg.evaluate("window.__paints=[]"); pg.click('#zoomOut'); pg.wait_for_timeout(300); pg.click('#zoomIn'); pg.wait_for_timeout(9000)
    ns=paints(pg); check('à ×30 : passage complet puis rendu de repos',any(600<=x<=640 for x in ns) and 1079 in ns and ns.index(1079)>max(i for i,x in enumerate(ns) if 600<=x<=640),ns)
    check('à ×30 : la carte affichée est celle du rendu de repos (1 079 points)',cw(pg)==1079,cw(pg))
    # 2. un geste annule le rendu de repos et la vue suivante est bien celle du nouveau cadrage
    pg.evaluate("window.__paints=[]"); pg.click('#zoomOut'); pg.wait_for_timeout(300); pg.click('#zoomIn')
    t0=time.time()
    while time.time()-t0<8 and not any(600<=x<=640 for x in paints(pg)): pg.wait_for_timeout(100)
    pg.wait_for_timeout(250)                                  # le rendu de repos est programmé 0,5 s après le passage complet : on le dérange avant
    bb=pg.locator('#mapBox').bounding_box(); x,y=bb['x']+bb['width']*0.8,bb['y']+bb['height']*0.5
    pg.mouse.move(x,y); pg.mouse.down(); pg.mouse.move(x-120,y+40,steps=8); pg.mouse.up(); pg.wait_for_timeout(1800)
    ns=paints(pg); check('un geste annule le rendu de repos en attente (aucun 1 079 avant le nouveau passage complet)',not (1079 in ns and ns.index(1079)<len(ns)-1 and not any(600<=x<=640 for x in ns[ns.index(1079):])),ns)
    pg.wait_for_timeout(8000); ns=paints(pg); check('après le geste : le rendu de repos revient pour le nouveau cadrage',ns[-1]==1079 and cw(pg)==1079,ns[-3:])
    check('aucune erreur JavaScript',not errs,errs[:1]); b.close()
    # 3. à faible grossissement : pas de rendu de repos
    b,pg,errs=ouvre(p); pg.wait_for_timeout(1500); pg.evaluate("window.__paints=[]"); pg.click('#zoomIn'); pg.wait_for_timeout(7000)   # vue entière (×1 puis ×1,5), sans passer par la carte à ×10
    ns=paints(pg); check('à faible grossissement : le passage complet est déjà à la résolution de l\'écran (1 079 points), donc aucun rendu de repos en plus',ns.count(1079)==1 and len(ns)>0,ns); b.close()
    # 4. réglage REST_PASS = 0
    b,pg,errs=ouvre(p); pg.evaluate("window.REST_PASS=0"); zoome(pg); pg.evaluate("window.__paints=[]"); pg.click('#zoomOut'); pg.wait_for_timeout(300); pg.click('#zoomIn'); pg.wait_for_timeout(7000)
    ns=paints(pg); check('REST_PASS = 0 : pas de rendu de repos',1079 not in ns and len(ns)>0,ns); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
