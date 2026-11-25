#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Non-régression de la borne régionale des ombres de la Lune : pour chaque cas (date, région, zoom), la carte rendue avec la borne régionale (réglage par défaut) est comparée, point par point, à celle rendue avec la borne globale (window.RAY_REGIONAL = 0) ; elles doivent être identiques. Vérifie aussi que le Worker a bien construit la carte du relief maximal (sinon le test serait vide).
Usage : python3 test_borne_regionale.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 3 minutes)"""
import sys, os, io, shutil, tempfile, threading, http.server, socketserver, datetime
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read(); k=s.index("  $('featClose').onclick=")
HOOK="  window.__go=goMoonMap; window.__demInfo=()=>({rmx:!!(dem&&dem.rmx),bw:dem&&dem.rmx?dem.rmx.bw:0,fin:fineState,ppd:dem&&dem.ppd});\n"
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write((s[:k]+HOOK+s[k:]).replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8884),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
CAS=[('2026-11-17T12:00:00Z','Tycho','x10'),('2026-11-20T12:00:00Z','Clavius','x30'),('2026-11-24T15:00:00Z',None,'x1'),('2026-11-24T03:00:00Z','Cabeus','x10'),('2026-12-01T06:00:00Z','Mare Imbrium','x10'),('2026-12-04T04:00:00Z','Grignard','x10'),('2026-11-28T14:00:00Z','Grimaldi','xmax'),('2026-12-15T12:00:00Z','Phillips','x3')]
def zl(pg): return float(pg.evaluate("document.getElementById('zoomLbl').textContent").replace('×','').replace(',','.') or 1)
def shot(pg):
    pg.evaluate("document.getElementById('featCard').hidden=true"); bb=pg.locator('#mapBox').bounding_box(); return np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=bb))).convert('RGB'),dtype=int)
with sync_playwright() as p:
    b=p.chromium.launch()
    for t,reg,plan in CAS:
        c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2.625,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); d=datetime.datetime.fromisoformat(t.replace('Z','+00:00')); pg.clock.install(time=d); pg.clock.set_fixed_time(d)
        pg.goto('http://localhost:8884/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(9000)
        info=pg.evaluate("window.__demInfo()")
        pg.evaluate("delete document.documentElement.dataset.night"); pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(2500); pg.click('#mapNow'); pg.wait_for_timeout(1500)
        if reg:
            pg.evaluate("(n)=>window.__go(n)",reg); pg.wait_for_timeout(1500)
            if plan=='x3':
                for _ in range(4):
                    if zl(pg)<=3.6: break
                    pg.click('#zoomOut'); pg.wait_for_timeout(250)
            elif plan in ('x30','xmax'):
                for _ in range(8 if plan=='xmax' else 4):
                    if plan=='x30' and zl(pg)>=28: break
                    pg.click('#zoomIn'); pg.wait_for_timeout(250)
        def rendu(flag):
            pg.evaluate("(f)=>{ window.RAY_REGIONAL=f }",flag); pg.click('#zoomIn'); pg.wait_for_timeout(350); pg.click('#zoomOut'); pg.wait_for_timeout(6500); return shot(pg)
        A=rendu(1); B=rendu(0); diff=int((np.abs(A-B).max(axis=2)>0).sum()); disque=int((A.max(axis=2)>25).sum())
        nom='%s %s %s (zoom ×%g)'%(t[:10],reg or 'disque entier',plan,zl(pg))
        check('%s : carte du relief maximal construite par le Worker (relief fin)'%nom,info['rmx'] and info['fin']=='ready' and info['ppd']==32,info)
        check('%s : image identique avec la borne régionale et avec la borne globale'%nom,diff==0 and disque>1000,'%d points différents sur %d points du disque'%(diff,disque))
        check('%s : aucune erreur JavaScript'%nom,not errs,errs[:1]); c.close()
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
