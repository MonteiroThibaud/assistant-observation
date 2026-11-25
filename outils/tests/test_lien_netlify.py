#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du lien « This site is powered by Netlify » : texte exact, adresse, nouvel onglet, placé tout en bas de l'onglet Système solaire (après le contenu), absent des autres onglets, visible en mode allégé, discret (petit texte).
Usage : python3 test_lien_netlify.py DOSSIER_DU_SITE_INSTALLE [PAGE_WEB.html]   (le serveur est démarré par le test ; durée : environ 40 secondes)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; WEB=sys.argv[2] if len(sys.argv)>2 else None; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:260]) if detail!='' else ''),flush=True)
def serveur(cible,port,web=False):
    T=tempfile.mkdtemp()
    if web: shutil.copy(cible,T+'/index.html')
    else:
        for n in os.listdir(cible):
            if n!='index.html': os.symlink(os.path.abspath(os.path.join(cible,n)),os.path.join(T,n))
        open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(cible,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
        def log_message(self,*a): pass
    class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
    s=S(('127.0.0.1',port),H); threading.Thread(target=s.serve_forever,daemon=True).start(); return s,T
cas=[('site installé',SITE,8913,False)]+([('page web',WEB,8914,True)] if WEB else [])
FIX=datetime.datetime(2026,11,21,22,0,tzinfo=datetime.timezone.utc)
with sync_playwright() as p:
    b=p.chromium.launch()
    for nom,cible,port,web in cas:
        s,T=serveur(cible,port,web)
        c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation']); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:%d/index.html'%port); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500)
        tab=lambda t:(pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t), pg.wait_for_timeout(800))
        tab('sys'); pg.wait_for_timeout(1500)
        r=pg.evaluate("""()=>{ const a=document.querySelector('#tab-sys .poweredby a'); if(!a) return null; const tab=document.getElementById('tab-sys'); const tous=[...tab.querySelectorAll('*')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height>0&&!e.closest('.poweredby')); const bas=Math.max(...tous.map(e=>e.getBoundingClientRect().bottom)); const r=a.getBoundingClientRect(); return {texte:a.textContent.trim(), href:a.href, cible:a.target, rel:a.rel, visible:!!a.offsetParent, hautLien:Math.round(r.top+scrollY), basContenu:Math.round(bas+scrollY), police:parseFloat(getComputedStyle(a).fontSize), dernier:tab.lastElementChild.className} }""")
        check('%s : lien « This site is powered by Netlify » vers https://www.netlify.com, en nouvel onglet, avec rel noopener'%nom,r and r['texte']=='This site is powered by Netlify' and r['href']=='https://www.netlify.com/' and r['cible']=='_blank' and 'noopener' in r['rel'] and r['visible'],r)
        check('%s : le lien est tout en bas de l\'onglet Système solaire, sous tout le contenu, en petit texte'%nom,r and r['dernier']=='poweredby' and r['hautLien']>=r['basContenu']-2 and r['police']<=13.5,r)
        n=[t for t in ('det','deep','eye','moon','loc') if (tab(t) or True) and pg.evaluate("document.querySelectorAll('.poweredby').length && !!document.querySelector('.poweredby').offsetParent")]
        check('%s : le lien n\'apparaît dans aucun autre onglet'%nom,n==[],n)
        tab('loc'); pg.evaluate("document.getElementById('scrBox').open=true"); pg.click('#detailBtn'); pg.wait_for_timeout(400); tab('sys'); pg.wait_for_timeout(500)
        check('%s : le lien reste visible en mode allégé'%nom,pg.evaluate("!!(document.querySelector('#tab-sys .poweredby a')&&document.querySelector('#tab-sys .poweredby a').offsetParent)"))
        check('%s : aucune erreur JavaScript'%nom,not errs,errs[:1]); c.close(); s.shutdown(); shutil.rmtree(T,ignore_errors=True)
    b.close()
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
