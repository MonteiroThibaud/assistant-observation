#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du mode allégé sur la fiche d'une formation lunaire : la note de méthode de mesure (L4) est masquée ; la légende du profil (L2) et le lien LROC QuickMap (L3) restent visibles.
Usage : python3 test_allege_fiche_lune.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 40 secondes)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:240]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''); k=s.index("  $('featClose').onclick=")
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(s[:k]+"  window.__show=showFeat;\n"+s[k:])
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8902),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,14,0,tzinfo=datetime.timezone.utc)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':780},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8902/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500)
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(2500); pg.evaluate("window.__show('Grimaldi')"); pg.wait_for_timeout(1500)
    ETAT="""()=>{ const f=[...document.querySelectorAll('#featData .featnote')]; const vis=re=>{ const e=f.find(x=>re.test(x.textContent)); return e?!!e.offsetParent:null }; return {L2:vis(/Quatre axes/), L3:vis(/LROC QuickMap/), L4:vis(/Mesures faites sur le relief/), n:f.length, l4expl:!!(f.find(x=>/Mesures faites/.test(x.textContent))||{classList:{contains:()=>false}}).classList.contains('expl')} }"""
    a=pg.evaluate(ETAT); check('mode détaillé : L2, L3 et L4 sont visibles',a['L2'] and a['L3'] and a['L4'],a)
    pg.evaluate("document.getElementById('detailBtn').click()"); pg.wait_for_timeout(1500); pg.evaluate("window.__show('Grimaldi')"); pg.wait_for_timeout(1500)
    z=pg.evaluate(ETAT); check('mode allégé : L2 (légende du profil) et L3 (lien LROC QuickMap) restent visibles, L4 (méthode de mesure) est masquée',z['L2'] and z['L3'] and z['L4'] is False and z['l4expl'],z)
    pg.evaluate("document.getElementById('detailBtn').click()"); pg.wait_for_timeout(1200); b2=pg.evaluate(ETAT); check('retour au mode détaillé : L4 réapparaît',b2['L4'],b2)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
