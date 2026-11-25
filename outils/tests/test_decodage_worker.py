#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du décodage de la carte, du relief et du relief fin dans des Workers, et de leur repli sur le fil principal.
Contrôles : empreintes des tableaux décodés identiques dans les trois modes (Workers, sans Worker, sans OffscreenCanvas), page utilisable, aucune erreur JavaScript.
Usage : python3 test_decodage_worker.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read(); k=s.index("  $('featClose').onclick=")
HOOK="  window.__sums=()=>{ const h=a=>{ let x=2166136261>>>0; for(let i=0;i<a.length;i+=1){ x=Math.imul(x^a[i],16777619)>>>0 } return x }; return {tex:moonTex?[moonTex.w,moonTex.h,h(moonTex.data)]:null, dem:demBase?[demBase.w,demBase.h,h(demBase.data)]:null, fin:demFine?[demFine.w,demFine.h,demFine.ppd,demFine.lon0,h(demFine.data)]:null} };\n"
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write((s[:k]+HOOK+s[k:]).replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8882),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
tz=datetime.timezone(datetime.timedelta(hours=1))
ATTENDU={'tex':[4552,4096,903946043],'dem':[3200,2880,3871169845]}   # empreintes (FNV-1a) de la carte et du relief de base ; le relief fin est comparé entre les modes
MODES=[('Workers',''),('sans Worker','window.Worker=undefined;'),('sans OffscreenCanvas','window.OffscreenCanvas=undefined;')]
fins=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for nom,init in MODES:
        c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        if init: pg.add_init_script(init)
        pg.clock.install(time=datetime.datetime(2026,11,15,16,0,tzinfo=tz)); pg.goto('http://localhost:8882/index.html'); pg.wait_for_timeout(1500)
        pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(12000)
        sm=pg.evaluate("window.__sums()")
        check('(%s) carte de base décodée : empreinte attendue'%nom,sm['tex']==ATTENDU['tex'],sm['tex'])
        check('(%s) relief de base décodé : empreinte attendue'%nom,sm['dem']==ATTENDU['dem'],sm['dem'])
        check('(%s) relief fin décodé (6 400 × 5 760 points, 32 par degré)'%nom,sm['fin'] is not None and sm['fin'][:4]==[6400,5760,32,-100],sm['fin'])
        fins.append(sm['fin'])
        pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(3000)
        etat=pg.evaluate("(()=>{const t=document.getElementById('fineText').textContent; const c=document.getElementById('mapBox'); return {fin:t.slice(0,40),carte:!!c&&c.getBoundingClientRect().height>100}})()")
        check('(%s) onglet Lune : relief fin actif et carte affichée'%nom,etat['fin'].startswith('Relief à 32') and etat['carte'],etat)
        check('(%s) aucune erreur JavaScript'%nom,not errs,errs[:1]); c.close()
    check('relief fin : même empreinte dans les trois modes',all(f==fins[0] for f in fins),fins)
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
