#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du réglage « Explications : détaillées / allégées » : bouton dans Paramètres écran, mémorisation, masquage des trois zones d'explication des transits de l'ISS, avertissements conservés (filtre solaire).
Usage : python3 test_explications_allegees.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 2 minutes)"""
import sys, os, re, json, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:240]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8894),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
TLE="ISS (ZARYA)\n1 25544U 98067A   26316.88411739  .00007667  00000-0  14541-3 0  9993\n2 25544  51.6325 284.2547 0007335  19.0494 341.0767 15.49339933594804"
tz=datetime.timezone(datetime.timedelta(hours=1)); FIX=datetime.datetime(2026,11,14,22,0,tzinfo=tz)
def ouvre(b,init=''):
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    if init: pg.add_init_script(init)
    pg.clock.install(time=FIX); pg.goto('http://localhost:8894/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4000); return c,pg,errs
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(700)
def ouvrir(pg,*ids): pg.evaluate("(ids)=>ids.forEach(i=>{ for(let d=document.getElementById(i); d; d=d.parentElement&&d.parentElement.closest('details')) d.open=true })",list(ids))
with sync_playwright() as p:
    b=p.chromium.launch(); c,pg,errs=ouvre(b)
    tab(pg,'loc'); ouvrir(pg,'scrBox')
    r=pg.evaluate("({mode:document.documentElement.dataset.detail, txt:document.getElementById('detailBtn').textContent.trim(), h:Math.round(document.getElementById('detailBtn').getBoundingClientRect().height)})")
    check('réglage d\'origine : « Explications : détaillées », mode complet',r['mode']=='full' and r['txt']=='Explications : détaillées',r)
    ouvrir(pg,'impBox'); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(800)
    tab(pg,'sys'); pg.wait_for_function("document.querySelector('#tab-sys .nightq')",timeout=90000); pg.wait_for_timeout(2500)
    z=pg.evaluate("""()=>{const q=[...document.querySelectorAll('#tab-sys .nightq')].find(e=>/En doré/.test(e.textContent)); if(!q) return null; const ex=q.querySelector('.expl'); return {expl:!!ex, visible:!!(ex&&ex.offsetParent), filtre:/filtre solaire obligatoire/.test(q.textContent), texte:q.textContent.slice(0,120)}}""")
    check('mode détaillé : l\'explication « En doré : le transit le plus proche… » est visible, avec l\'avertissement du filtre solaire',z and z['expl'] and z['visible'] and z['filtre'],z)
    # zone : carte et résultats
    tab(pg,'loc'); ouvrir(pg,'issSitesBox')
    pg.click('#iszRun'); ok=False
    try: pg.wait_for_selector('#iszEvMsg',state='attached',timeout=170000); ok=True
    except Exception: ok=False
    pg.wait_for_timeout(1500); tab(pg,'sys'); pg.wait_for_timeout(1500)
    nz=pg.evaluate("document.querySelectorAll('#tab-sys .expl').length"); vis1=pg.evaluate("[...document.querySelectorAll('#tab-sys .expl')].filter(e=>e.offsetParent).length")
    check('transits sur une zone et tableau : au moins quatre éléments d\'explication marqués dans Système solaire, tous visibles en mode détaillé',ok and nz>=4 and vis1==nz,(ok,nz,vis1))
    tab(pg,'loc')
    pg.evaluate("document.getElementById('scrBox').scrollIntoView()"); ouvrir(pg,'scrBox'); pg.click('#detailBtn'); pg.wait_for_timeout(400)
    r=pg.evaluate("({mode:document.documentElement.dataset.detail, txt:document.getElementById('detailBtn').textContent.trim(), aria:document.getElementById('detailBtn').getAttribute('aria-label'), stock:localStorage.getItem('detailMode')})")
    tab(pg,'sys'); pg.wait_for_timeout(800); r['vis']=pg.evaluate("[...document.querySelectorAll('#tab-sys .expl')].filter(e=>e.offsetParent).length")
    check('mode allégé : bouton « Explications : allégées », zones d\'explication masquées dans Système solaire, réglage mémorisé',r['mode']=='light' and r['txt']=='Explications : allégées' and r['vis']==0 and vis1>=4 and 'allégées' in r['aria'] and r['stock']=='"light"',(vis1,r))
    z=pg.evaluate("""()=>{const q=[...document.querySelectorAll('#tab-sys .nightq')].find(e=>/filtre solaire/.test(e.textContent)); return q?{filtre:!!(q.offsetParent), enDore:/En doré/.test(q.innerText)}:null}""")
    check('mode allégé : l\'avertissement « Soleil : filtre solaire obligatoire » reste affiché, l\'explication « En doré » disparaît',z and z['filtre'] and not z['enDore'],z)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close()
    c,pg,errs=ouvre(b,"localStorage.setItem('detailMode','\"light\"');")
    tab(pg,'loc'); ouvrir(pg,'scrBox'); r=pg.evaluate("({mode:document.documentElement.dataset.detail, txt:document.getElementById('detailBtn').textContent.trim()})")
    check('le mode allégé est conservé au relancement',r['mode']=='light' and r['txt']=='Explications : allégées',r)
    pg.click('#detailBtn'); pg.wait_for_timeout(300); r=pg.evaluate("({mode:document.documentElement.dataset.detail, stock:localStorage.getItem('detailMode')})")
    check('retour au mode détaillé',r['mode']=='full' and r['stock']=='"full"',r); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
