#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du lien vers le site du club dans le menu « À propos » (Informations) : adresse, nouvel onglet, rel noopener, ouverture.
Usage : python3 test_lien_club.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 20 secondes)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:260]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8908),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(args=['--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE localhost']); c=b.new_context(viewport={'width':411,'height':850},locale='fr-FR')
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.goto('http://localhost:8908/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(500)
    r=pg.evaluate("""()=>{ const m=[...document.querySelectorAll('#tab-loc .about details')].find(d=>/propos/i.test(d.querySelector('summary').textContent)); if(!m) return null; m.open=true; const a=[...m.querySelectorAll('a')].find(x=>/Club Astro Jupiter du Roannais/.test(x.textContent)); return a?{href:a.href,target:a.target,rel:a.rel,texte:a.textContent,visible:!!a.offsetParent,menu:m.querySelector('summary').textContent.trim()}:{menu:m.querySelector('summary').textContent.trim(),absent:true} }""")
    check('menu « À propos » : le nom « Club Astro Jupiter du Roannais » est un lien vers https://www.astrojupiter.fr/gs/, en nouvel onglet, avec rel noopener',r and r.get('href')=='https://www.astrojupiter.fr/gs/' and r['target']=='_blank' and 'noopener' in r['rel'] and r['visible'],r)
    demandes=[]; c.on('request',lambda r: demandes.append(r.url))
    with c.expect_page(timeout=10000) as nouvelle:
        pg.evaluate("[...document.querySelectorAll('#tab-loc .about a')].find(x=>/Club Astro Jupiter/.test(x.textContent)).click()")
    pg.wait_for_timeout(1500)
    check('un appui ouvre un nouvel onglet qui demande https://www.astrojupiter.fr/gs/ (le chargement échoue ici : le banc bloque le réseau)',any(u.startswith('https://www.astrojupiter.fr/gs') for u in demandes),[u for u in demandes if 'astrojupiter' in u][:2])
    check('l\'application reste ouverte et sans erreur JavaScript',not errs and pg.evaluate("document.querySelectorAll('.tabbar button').length")==6,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
