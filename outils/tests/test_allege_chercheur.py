#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du texte d'information du chercheur en mode allégé : « Chercheur 9×50 : champ réel de 5,6° sur le ciel. Constellation au centre du champ : X. Vue à HH:MM. »
Usage : python3 test_allege_chercheur.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 30 secondes)"""
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
srv=S(('127.0.0.1',8904),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,22,10,tzinfo=datetime.timezone.utc)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8904/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500)
    tab=lambda t:(pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t), pg.wait_for_timeout(900))
    def info():
        tab('eye'); pg.evaluate("document.querySelector('button[data-ep=finder]').click()"); pg.wait_for_timeout(1200)
        return re.sub(r'\s+',' ',pg.evaluate("document.getElementById('eyeInfo').innerText")).strip()
    a=info()
    check('mode détaillé : le texte du chercheur garde l\'optique, la consigne de pointage, l\'aide au doigt et la direction du zénith','image' in a and 'Place Lune au centre de la croix rouge' in a and 'Fais glisser le ciel' in a and 'Z : direction du zénith' in a,a)
    tab('loc'); pg.evaluate("document.getElementById('scrBox').open=true"); pg.click('#detailBtn'); pg.wait_for_timeout(500)
    z=info(); motif=r"^Chercheur 9×50 : champ réel de 5,6° sur le ciel\. Constellation au centre du champ : [^.]+\. Vue à \d\d:\d\d\.$"
    check('mode allégé : « Chercheur 9×50 : champ réel de 5,6° sur le ciel. Constellation au centre du champ : … Vue à … »',re.match(motif,z),z)
    for opt in ('coude','redresse'):
        tab('loc'); pg.evaluate("(o)=>{ for(let d=document.getElementById('fiBox');d;d=d.parentElement&&d.parentElement.closest('details')) d.open=true; const s=document.getElementById('fiInv'); s.value=o; s.dispatchEvent(new Event('change')) }",opt); pg.wait_for_timeout(300)
        z2=info(); check('mode allégé, optique « %s » : même texte court'%opt,re.match(motif,z2),z2)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
