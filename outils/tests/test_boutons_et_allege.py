#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de la hauteur des boutons de Paramètres (44 points ; champ de date de la hauteur des flèches de sa ligne ; aucun bouton de plus de 48 points dans aucun onglet) et des textes masqués en mode allégé choisis le 20 novembre (légende du tableau de Système solaire, phrase d'aide au doigt de l'oculaire, aide de la carte de la Lune).
Usage : python3 test_boutons_et_allege.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 1 minute)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
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
srv=S(('127.0.0.1',8900),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,14,0,tzinfo=datetime.timezone.utc)
AUDIT="""()=>{ const out=[]; document.querySelectorAll('button,input:not([type=checkbox]):not([type=radio]):not([type=range]),select,[role=button]').forEach(e=>{ if(!e.offsetParent||e.classList.contains('ddn')||e.classList.contains('ddbtn')||e.closest('.tabbar')) return; const r=e.getBoundingClientRect(); if(r.width<20) return; if(r.height>48) out.push((e.id||e.getAttribute('class')||e.tagName)+' : '+Math.round(r.height*10)/10) }); return out }"""
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8900/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500)
    tab=lambda t:(pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t), pg.wait_for_timeout(900))
    tab('eye'); pg.evaluate("(()=>{const b=[...document.querySelectorAll('#tab-eye button')].find(x=>/\\+ Noter/.test(x.textContent)); if(b) b.click()})()"); pg.wait_for_timeout(700)
    hauts={}
    for t in ('sys','det','deep','eye','moon'): tab(t); hauts[t]=pg.evaluate(AUDIT)
    tab('loc'); pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)"); pg.wait_for_timeout(1200); hauts['loc']=pg.evaluate(AUDIT)
    check('aucun bouton ni champ de plus de 48 points dans les six onglets (listes déroulantes de deux lignes exceptées)',all(not v for v in hauts.values()),{k:v for k,v in hauts.items() if v})
    h=pg.evaluate("""()=>{const g=id=>Math.round(document.getElementById(id).getBoundingClientRect().height*10)/10; return {geo:g('geo'),manuel:g('manualBtn'),oublier:g('forgetPos'),carnetCopy:g('carnetCopy'),detail:g('detailBtn'),rot:g('scrRot'),import:[...document.querySelectorAll('#impBox button')].filter(b=>/Importer des fichiers/.test(b.textContent)).map(b=>Math.round(b.getBoundingClientRect().height*10)/10)[0]}}""")
    check('boutons « Actualiser », « Saisir une position », « Oublier la position », « Copier le carnet », « Explications », « Rotation » : 44 points, comme « Importer des fichiers »',all(abs(v-44)<=0.6 for v in h.values()),h)
    row=pg.evaluate("""()=>{const d=document.getElementById('date').parentElement; return [...d.children].filter(e=>/BUTTON|INPUT/.test(e.tagName)).map(e=>e.id+':'+Math.round(e.getBoundingClientRect().height*10)/10)}""")
    check('ligne de date de Date et lieu : flèches, champ de date et « Cette nuit » de la même hauteur',len(set(x.split(':')[1] for x in row))==1 and len(row)==4,row)
    # mode allégé : choix du 20 novembre
    def etat():
        return pg.evaluate("""()=>{ tab=t=>document.querySelector('.tabbar [data-tab='+t+']').click(); const o={}; tab('sys'); o.legende=!!document.querySelector('#tab-sys .legend').offsetParent; tab('eye'); const i=document.getElementById('eyeInfo'); o.eyeAide=[...i.querySelectorAll('.expl')].some(e=>e.offsetParent); o.eyeInfo=i.innerText.length; tab('moon'); const l=[...document.querySelectorAll('#tab-moon .legend')][0]; o.lune=!!(l&&l.offsetParent); return o }""")
    pg.wait_for_timeout(300); a=etat(); pg.wait_for_timeout(300)
    check('mode détaillé : légende du tableau, aide au doigt de l\'oculaire et aide de la carte de la Lune visibles',a['legende'] and a['eyeAide'] and a['lune'],a)
    tab('loc'); pg.evaluate("document.getElementById('scrBox').open=true"); pg.click('#detailBtn'); pg.wait_for_timeout(400)
    z=etat(); pg.wait_for_timeout(400)
    check('mode allégé : ces trois textes sont masqués, le reste du texte de l\'oculaire reste affiché',(not z['legende']) and (not z['eyeAide']) and (not z['lune']) and z['eyeInfo']>150,z)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
