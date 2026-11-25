#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des remerciements aux bêta-testeurs (À propos) et de l'œuf de Pâques « Jupiter » : le bouton manu / nina (nuages et ventilateur) est absent par défaut, apparaît au premier appui sur « Jupiter », disparaît au second (en arrêtant nuages et ventilateur), état mémorisé.
Usage : python3 test_oeuf_manu_nina.py DOSSIER_DU_SITE_INSTALLE [PAGE_WEB.html]   (le serveur est démarré par le test ; durée : environ 40 secondes)"""
import sys, os, re, shutil, tempfile, threading, http.server, socketserver
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; WEB=sys.argv[2] if len(sys.argv)>2 else None; res=[]
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
srv=S(('127.0.0.1',8909),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},locale='fr-FR'); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    def ouvre():
        pg.goto('http://localhost:8909/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3000)
    def visible(): return pg.evaluate("(()=>{const b=document.getElementById('manuBtn'); return !!(b&&b.offsetParent)})()")
    def aPropos():
        pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400)
        pg.evaluate("[...document.querySelectorAll('#tab-loc .about details')].find(d=>/propos/i.test(d.querySelector('summary').textContent)).open=true"); pg.wait_for_timeout(300)
    def jupiter(): pg.evaluate("document.querySelector('#tab-loc .about [data-egg=\"manu\"]').click()"); pg.wait_for_timeout(500)
    ouvre()
    check('par défaut : le bouton « manu » est absent de l\'en-tête, dans tous les onglets',not any((pg.evaluate("(t)=>{document.querySelector('.tabbar [data-tab='+t+']').click(); const b=document.getElementById('manuBtn'); return !!(b&&b.offsetParent)}",t)) for t in ('sys','det','deep','eye','moon','loc')))
    aPropos()
    r=pg.evaluate("""()=>{ const d=[...document.querySelectorAll('#tab-loc .about details')].find(d=>/propos/i.test(d.querySelector('summary').textContent)); const ps=[...d.querySelectorAll('p')]; const i=ps.findIndex(p=>/Je tiens à remercier/.test(p.textContent)); const j=ps.findIndex(p=>/Une remarque, une erreur/.test(p.textContent)); return {i,j,texte:i>=0?ps[i].textContent.trim():'',egg:i>=0?ps[i].querySelector('[data-egg="manu"]').textContent:null} }""")
    attendu="Je tiens à remercier ici les bêta-testeurs du club Astro Jupiter du Roannais et, en particulier Nina, Manu, Stéphane et Claire pour leurs retours qui ont permis d’améliorer l’outil proposé aujourd’hui."
    check('« À propos » : la phrase de remerciement est présente, mot pour mot, juste avant la phrase sur les remarques et les erreurs',r['i']>=0 and r['texte']==attendu and r['j']==r['i']+1 and r['egg']=='Jupiter',r)
    jupiter(); tab=lambda t:pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t)
    tab('sys'); pg.wait_for_timeout(400); check('premier appui sur « Jupiter » : le bouton « manu » apparaît dans l\'en-tête',visible() and pg.evaluate("document.getElementById('manuBtn').textContent.trim()")=='manu')
    pg.click('#manuBtn'); pg.wait_for_timeout(2800); n=pg.evaluate("document.querySelectorAll('#clouds .cl').length"); t1=pg.evaluate("document.getElementById('manuBtn').textContent.trim()")
    check('le bouton fonctionne comme avant : « manu » amène des nuages et devient « nina »',n>=6 and t1=='nina',(n,t1))
    aPropos(); jupiter(); tab('sys'); pg.wait_for_timeout(500)
    z=pg.evaluate("({visible:!!(document.getElementById('manuBtn')&&document.getElementById('manuBtn').offsetParent), nuages:!!document.getElementById('clouds'), ventilo:!!document.getElementById('fan'), texte:document.getElementById('manuBtn').textContent.trim()})")
    check('second appui sur « Jupiter » : le bouton disparaît, les nuages sont retirés et l\'état revient à « manu »',not z['visible'] and not z['nuages'] and not z['ventilo'] and z['texte']=='manu',z)
    pg.reload(); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(2500)
    check('après rechargement : toujours absent (état mémorisé : désactivé)',not visible() and pg.evaluate("localStorage.getItem('manunina')")=='false')
    aPropos(); jupiter(); pg.reload(); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(2500)
    check('activé puis rechargé : le bouton reste présent (état mémorisé : activé)',visible() and pg.evaluate("localStorage.getItem('manunina')")=='true')
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close()
    # stockage du navigateur indisponible (cadre de la page en ligne, navigation privée) : l'œuf doit fonctionner pendant la session
    c=b.new_context(viewport={'width':411,'height':850},locale='fr-FR'); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('blocked','SecurityError')}})")
    ouvre(); aPropos(); abs1=not visible(); jupiter(); tab=lambda t:pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); tab('sys'); pg.wait_for_timeout(300); on=visible()
    pg.click('#manuBtn'); pg.wait_for_timeout(2500); nu=pg.evaluate("document.querySelectorAll('#clouds .cl').length")
    aPropos(); jupiter(); tab('sys'); pg.wait_for_timeout(400); off=not visible() and not pg.evaluate("!!document.getElementById('clouds')")
    check('stockage indisponible : absent au départ, apparaît au premier appui sur « Jupiter », fonctionne (nuages), disparaît au second',abs1 and on and nu>=6 and off,(abs1,on,nu,off))
    check('stockage indisponible : aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
if WEB:
    T2=tempfile.mkdtemp(); shutil.copy(WEB,T2+'/index.html')
    class H2(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw): super().__init__(*a,directory=T2,**kw)
        def log_message(self,*a): pass
    srv2=S(('127.0.0.1',8911),H2); threading.Thread(target=srv2.serve_forever,daemon=True).start()
    with sync_playwright() as p:
        b=p.chromium.launch()
        for nom,init in (('page web, stockage disponible',''),('page web, stockage indisponible',"Object.defineProperty(window,'localStorage',{get(){throw new DOMException('blocked','SecurityError')}})")):
            c=b.new_context(viewport={'width':411,'height':850},locale='fr-FR'); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
            if init: pg.add_init_script(init)
            pg.goto('http://localhost:8911/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3000)
            vis=lambda: pg.evaluate("(()=>{const b=document.getElementById('manuBtn'); return !!(b&&b.offsetParent)})()")
            tb=lambda t:pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t)
            tb('loc'); pg.wait_for_timeout(400); pg.evaluate("[...document.querySelectorAll('#tab-loc .about details')].find(d=>/propos/i.test(d.querySelector('summary').textContent)).open=true")
            a0=vis(); pg.evaluate("document.querySelector('#tab-loc .about [data-egg=\"manu\"]').click()"); pg.wait_for_timeout(400); tb('sys'); pg.wait_for_timeout(300); a1=vis()
            tb('loc'); pg.evaluate("document.querySelector('#tab-loc .about [data-egg=\"manu\"]').click()"); pg.wait_for_timeout(400); tb('sys'); pg.wait_for_timeout(300); a2=vis()
            check('%s : absent, présent au premier appui sur « Jupiter », absent au second'%nom,(not a0) and a1 and (not a2),(a0,a1,a2))
            check('%s : aucune erreur JavaScript'%nom,not errs,errs[:1]); c.close()
        b.close()
    srv2.shutdown(); shutil.rmtree(T2,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
