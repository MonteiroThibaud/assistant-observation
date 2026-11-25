#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du texte d'information du Telrad en mode allégé : « Telrad : cercles rouges de 0,5°, 2° et 4° au centre, vue comme à l'œil nu (zénith en haut). Constellation au centre du champ : X. Vue à HH:MM. »
Usage : python3 test_allege_telrad.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 30 secondes)"""
import sys, os, re, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:300]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8903),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,22,10,tzinfo=datetime.timezone.utc)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8903/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500)
    tab=lambda t:(pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t), pg.wait_for_timeout(900))
    def info():
        tab('eye'); pg.evaluate("document.querySelector('button[data-ep=telrad]').click()"); pg.wait_for_timeout(1200)
        return re.sub(r'\s+',' ',pg.evaluate("document.getElementById('eyeInfo').innerText")).strip()
    a=info()
    check('mode détaillé : le texte du Telrad garde le cadre, la phrase d\'aide au doigt et « Z : direction du zénith »','cadre de' in a and 'Fais glisser le ciel' in a and 'un nouvel appui sur « Telrad »' in a and 'Z : direction du zénith' in a,a)
    tab('loc'); pg.evaluate("document.getElementById('scrBox').open=true"); pg.click('#detailBtn'); pg.wait_for_timeout(500)
    z=info()
    motif=r"^Telrad : cadre de \d+° sur \d+°, cercles rouges de 0,5°, 2° et 4° au centre, vue comme à l'œil nu \(zénith en haut\)\. Constellation au centre du champ : [^.]+\. Vue à \d\d:\d\d\.$"
    check('mode allégé : « Telrad : cadre de 11° sur 11°, cercles rouges de 0,5°, 2° et 4° au centre, vue comme à l\'œil nu (zénith en haut). Constellation au centre du champ : … Vue à … » (le cadre reste affiché)',re.match(motif,z.replace('’',"'")),z)
    # le centre du Telrad déplacé (donnée) reste affiché
    pg.evaluate("(()=>{ const e=document.getElementById('eyeSvg')||document.querySelector('#tab-eye svg'); const r=e.getBoundingClientRect(); const o={bubbles:true,pointerId:1,pointerType:'touch',isPrimary:true}; e.dispatchEvent(new PointerEvent('pointerdown',{...o,clientX:r.left+r.width/2,clientY:r.top+r.height/2})); e.dispatchEvent(new PointerEvent('pointermove',{...o,clientX:r.left+r.width/2+90,clientY:r.top+r.height/2+60})); e.dispatchEvent(new PointerEvent('pointerup',{...o,clientX:r.left+r.width/2+90,clientY:r.top+r.height/2+60})) })()"); pg.wait_for_timeout(1000)
    d=re.sub(r'\s+',' ',pg.evaluate("document.getElementById('eyeInfo').innerText")).strip()
    check('mode allégé, ciel déplacé : « Le centre du champ est à … de Lune (direction …) » reste affiché (donnée), après la phrase d\'introduction',bool(re.search(r"zénith en haut\)\. Le centre du champ est à [\d,]+° de Lune \(direction [A-Z]+\)\. Constellation au centre du champ : [^.]+\. Vue à \d\d:\d\d\.$",d)),d)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
