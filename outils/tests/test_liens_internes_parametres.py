#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des liens à l'intérieur de l'onglet Paramètres (aides et section Informations) : chaque repère de lien ouvre le bon menu (et ses menus parents), l'amène à l'écran, sans quitter Paramètres.
Usage : python3 test_liens_internes_parametres.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 1 minute 30)"""
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
srv=S(('127.0.0.1',8898),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
CIBLES={'loc':'locBox','par':'telBox','fi':'fiBox','ep':'epBox','mat':'matBox','deeplists':'listDeepBox','lunlists':'listLunBox','orglists':'listOrgBox','listbox':'listBox','imp':'impBox','smallbodies':'sbBox','iss':'issBox','issSites':'issSitesBox','zone':'issZoneTitle','scr':'scrBox','carnet':'carnetBox'}
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,11,20,22,0,tzinfo=datetime.timezone(datetime.timedelta(hours=1)))); pg.goto('http://localhost:8898/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(600)
    pr=pg.evaluate("(()=>{const o={}; document.querySelectorAll('#tab-loc [data-go]').forEach(e=>{o[e.dataset.go]=(o[e.dataset.go]||0)+1}); return o})()")
    inf=pg.evaluate("document.querySelectorAll('#tab-loc .about [data-go]').length")
    check('l\'onglet Paramètres contient des liens internes, dont plus de 20 dans la section Informations',sum(pr.values())>=25 and inf>=20,{'total':sum(pr.values()),'informations':inf})
    manque=[k for k in CIBLES if k not in pr and k not in ('iss','issSites','zone','lunlists')]
    for go,cible in CIBLES.items():
        n=pg.evaluate("(g)=>document.querySelectorAll('#tab-loc [data-go=\"'+g+'\"]').length",go)
        if not n: check('repère « %s » : aucun lien dans Paramètres (non testé)'%go,go in ('lunlists',),n); continue
        pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); window.scrollTo(0,0)"); pg.wait_for_timeout(300)
        pg.evaluate("(g)=>{ const e=[...document.querySelectorAll('#tab-loc [data-go=\"'+g+'\"]')].find(x=>x.offsetParent!==null)||document.querySelector('#tab-loc [data-go=\"'+g+'\"]'); if(!e.offsetParent){ for(let d=e.closest('details'); d; d=d.parentElement&&d.parentElement.closest('details')) d.open=true } e.click() }",go); pg.wait_for_timeout(900)
        r=pg.evaluate("""(id)=>{ const el=document.getElementById(id); const chain=[]; for(let d=el.closest('details'); d; d=d.parentElement&&d.parentElement.closest('details')) chain.push(d.open); const r=el.getBoundingClientRect(); return {ouverts:chain.every(Boolean), visible:!!el.offsetParent, haut:Math.round(r.top), loc:!document.getElementById('tab-loc').hidden} }""",cible)
        check('lien « %s » (%d dans Paramètres) : ouvre %s et ses menus parents, l\'affiche à l\'écran, reste dans Paramètres'%(go,n,cible),r['ouverts'] and r['visible'] and 0<=r['haut']<600 and r['loc'],r)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
