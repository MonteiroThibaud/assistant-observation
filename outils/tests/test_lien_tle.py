#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du lien « Paramètres › » du message « Le TLE a N jours » en bas de Système solaire (résultats de zone) : il ouvre Paramètres, Imports, Station spatiale ; le message reste visible en mode allégé.
Usage : python3 test_lien_tle.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 2 minutes)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
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
srv=S(('127.0.0.1',8896),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
TLE="ISS (ZARYA)\n1 25544U 98067A   26316.88411739  .00007667  00000-0  14541-3 0  9993\n2 25544  51.6325 284.2547 0007335  19.0494 341.0767 15.49339933594804"
tz=datetime.timezone(datetime.timedelta(hours=1)); FIX=datetime.datetime(2026,11,20,22,0,tzinfo=tz)
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(700)
def ouvrir(pg,*ids): pg.evaluate("(ids)=>ids.forEach(i=>{ for(let d=document.getElementById(i); d; d=d.parentElement&&d.parentElement.closest('details')) d.open=true })",list(ids))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=FIX); pg.goto('http://localhost:8896/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4000)
    tab(pg,'loc'); ouvrir(pg,'impBox'); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(800)
    ouvrir(pg,'issSitesBox'); pg.click('#iszRun'); ok=False
    try: pg.wait_for_selector('#iszEvMsg',state='attached',timeout=170000); ok=True
    except Exception: ok=False
    pg.wait_for_timeout(1500); tab(pg,'sys'); pg.wait_for_timeout(1000)
    z=pg.evaluate("""()=>{const q=[...document.querySelectorAll('#tab-sys .nightq')].find(e=>/Le TLE a \\d+ jours/.test(e.textContent)); if(!q) return null; const l=q.querySelector('[data-go="iss"]'); return {texte:(q.textContent.match(/Le TLE a \\d+ jours[^.]*\\./)||[''])[0], lien:!!l, libelle:l&&l.textContent.trim(), bas:Math.round(q.getBoundingClientRect().top+scrollY)}}""")
    check('résultats de zone : « Le TLE a N jours : mets-le à jour dans Paramètres › », avec un lien',ok and z and z['lien'] and z['libelle']=='Paramètres ›',z)
    pg.evaluate("document.querySelector('#tab-sys .nightq [data-go=\"iss\"]').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('#tab-sys .nightq [data-go=\"iss\"]').click()"); pg.wait_for_timeout(900)
    r=pg.evaluate("({loc:!document.getElementById('tab-loc').hidden, imp:document.getElementById('impBox').open, vis:!!document.getElementById('issBox').offsetParent, haut:Math.round(document.getElementById('issBox').getBoundingClientRect().top)})")
    check('un appui ouvre Paramètres, Imports et la partie « Station spatiale (ISS) », qui s\'affiche en haut de l\'écran',r['loc'] and r['imp'] and r['vis'] and r['haut']<300,r)
    tab(pg,'loc'); ouvrir(pg,'scrBox'); pg.click('#detailBtn'); pg.wait_for_timeout(300); tab(pg,'sys'); pg.wait_for_timeout(600)
    z2=pg.evaluate("""()=>{const q=[...document.querySelectorAll('#tab-sys .nightq')].find(e=>/Le TLE a \\d+ jours/.test(e.textContent)); const l=q&&q.querySelector('[data-go="iss"]'); return {lienVisible:!!(l&&l.offsetParent), mode:document.documentElement.dataset.detail}}""")
    check('en mode allégé, le message sur l\'âge du TLE et son lien restent visibles',z2['lienVisible'] and z2['mode']=='light',z2)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
