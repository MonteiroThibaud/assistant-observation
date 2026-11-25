#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des ajustements 0.97 (étape 6) : ligne « Vue depuis » avec le nom du lieu ou de la commune, libellé du bouton de cadrage de la Lune = état actuel (et bouton d'orientation), menu « Mes oculaires et barlows » avec aides visibles, profils du relief à taille constante.
Usage : python3 test_ajustements_vue_cadrage_profils.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 2 minutes)"""
import sys, os, re, json, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:230]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''); k=s.index("  $('featClose').onclick=")
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(s[:k]+"  window.__show=showFeat;\n"+s[k:])
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8892),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,14,0,tzinfo=datetime.timezone.utc)
def ouvre(b,W,H,init='',geo=None):
    c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',**({'geolocation':geo,'permissions':['geolocation']} if geo else {}))
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    if init: pg.add_init_script(init)
    pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8892/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500); return c,pg,errs
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(800)
def sky(pg): tab(pg,'sys'); pg.wait_for_timeout(1200); return pg.evaluate("document.getElementById('skyPlace').textContent.trim()")
GEO_OFF="navigator.geolocation.getCurrentPosition=(ok,err)=>setTimeout(()=>err({code:1}),50);"
with sync_playwright() as p:
    b=p.chromium.launch()
    # 1. Vue depuis
    c,pg,errs=ouvre(b,411,850,GEO_OFF); t=sky(pg)
    check('position par défaut : « Vue depuis Roanne, position par défaut (46,03° N, 4,07° E) »',re.fullmatch(r'Vue depuis Roanne, position par défaut \(46,03° N, 4,07° E\)',t),t); c.close()
    sites=[{'id':'sA','name':'Site de test','lat':45.4397,'lon':4.3872,'kind':'coord','on':True,'alt':372}]
    c,pg,errs=ouvre(b,411,850,GEO_OFF+"localStorage.setItem('issSites',%s); localStorage.setItem('activeLoc','\"sA\"'); localStorage.setItem('placesV','1');"%json.dumps(json.dumps(sites))); t=sky(pg)
    check('lieu mémorisé : « Vue depuis Site de test (45,44° N, 4,39° E) »',re.fullmatch(r'Vue depuis Site de test \(45,44° N, 4,39° E\)',t),t); c.close()
    c,pg,errs=ouvre(b,411,850,'',{'latitude':46.0345,'longitude':4.0720}); t=sky(pg)
    check('position du téléphone (application installée) : nom de la commune devant les coordonnées',re.fullmatch(r'Vue depuis (près de )?Roanne \(46,03° N, 4,07° E\)',t),t)
    check('aucune erreur JavaScript (Vue depuis)',not errs,errs[:1]); c.close()
    c,pg,errs=ouvre(b,411,850,"Object.defineProperty(window,'PLACES_URL',{get(){return ''},set(){}});",{'latitude':46.0345,'longitude':4.0720}); t=sky(pg)
    check('sans base des communes (page en ligne) : coordonnées seules, comme avant',re.fullmatch(r'Vue depuis 46,03° N, 4,07° E',t),t); c.close()
    # 2. cadrage de la carte de la Lune
    for W,H in ((1280,800),(891,411)):
        c,pg,errs=ouvre(b,W,H); tab(pg,'moon'); pg.wait_for_timeout(2500)
        lab=lambda: pg.evaluate("document.getElementById('zoomReset').textContent.trim()")
        e=[lab()]; pg.click('#zoomReset'); pg.wait_for_timeout(500); e.append(lab()); pg.click('#zoomReset'); pg.wait_for_timeout(500); e.append(lab())
        pg.click('#zoomIn'); pg.wait_for_timeout(500); e.append(lab()); pg.click('#zoomReset'); pg.wait_for_timeout(500); e.append(lab())
        aria=pg.evaluate("document.getElementById('zoomReset').getAttribute('aria-label')")
        check('%dx%d : le bouton de cadrage affiche l\'état : Lune entière, Pleine largeur, Lune entière, Vue libre, Lune entière'%(W,H),e==['Lune entière','Pleine largeur','Lune entière','Vue libre','Lune entière'],e)
        check('%dx%d : étiquette accessible du bouton de cadrage'%(W,H),aria.startswith('Cadrage : Lune entière. Appuie pour passer à la pleine largeur'),aria)
        ori=pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&['Dobson','Nord en haut','Retournée','Inversée'].includes(b.textContent.trim())).map(b=>b.id||b.className)")
        check('%dx%d : aucune erreur JavaScript'%(W,H),not errs,errs[:1]); c.close()
    c,pg,errs=ouvre(b,411,850); tab(pg,'moon'); pg.wait_for_timeout(2000)
    check('écran étroit (cadre carré) : le bouton reste « Recentrer »',pg.evaluate("document.getElementById('zoomReset').textContent.trim()")=='Recentrer')
    OR=pg.evaluate("[...document.querySelectorAll('button')].filter(b=>['Dobson','Nord en haut','Retournée','Inversée'].includes(b.textContent.trim()))[0]")
    ob=pg.evaluate("(()=>{const bs=[...document.querySelectorAll('button')].filter(b=>['Dobson','Nord en haut','Retournée','Inversée'].includes(b.textContent.trim())); return bs.length?bs[0].id:null})()")
    if ob:
        seq=[]
        for _ in range(5):
            seq.append(pg.evaluate("(id)=>{const b=document.getElementById(id); return [b.textContent.trim(), b.getAttribute('aria-label')]}",ob)); tab(pg,pg.evaluate("document.getElementById('%s').closest('.tab').id.replace('tab-','')"%ob)) if False else None; pg.evaluate("(id)=>document.getElementById(id).click()",ob); pg.wait_for_timeout(300)
        check('bouton d\'orientation : le libellé est l\'état actuel (Dobson, Nord en haut, Retournée, Inversée, puis Dobson) et l\'étiquette accessible le répète',[x[0] for x in seq]==['Dobson','Nord en haut','Retournée','Inversée','Dobson'] and all(x[0] in x[1] for x in seq),seq)
    else: check('bouton d\'orientation trouvé',False)
    c.close()
    # 3. Mes oculaires et barlows
    c,pg,errs=ouvre(b,411,850); tab(pg,'loc'); pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)"); pg.wait_for_timeout(500)
    r=pg.evaluate("""()=>({titre:document.querySelector('#epBox > summary').textContent.trim(), ph:[1,2,3].map(i=>[document.getElementById('bl'+i+'n').placeholder, document.getElementById('bl'+i+'m').placeholder, document.getElementById('bl'+i+'n').value, document.getElementById('bl'+i+'m').value]), bars:JSON.parse(localStorage.getItem('eyeCfg4')||'{}').bars||null})""")
    check('menu renommé « Mes oculaires et barlows »',r['titre']=='Mes oculaires et barlows',r['titre'])
    check('champs des barlows : aides visibles « Barlow n » et « 1,1 à 10 », champs vides',r['ph']==[['Barlow 1','1,1 à 10','',''],['Barlow 2','1,1 à 10','',''],['Barlow 3','1,1 à 10','','']],r['ph'])
    tab(pg,'eye'); chips=pg.evaluate("[...document.querySelectorAll('#tab-eye .chips button, #tab-eye .chip')].map(b=>b.textContent.trim()).filter(x=>x)")
    check('les aides n\'activent aucune barlow : aucune puce avec barlow à l\'oculaire',not any('×' in x for x in chips) and len(chips)>=5,chips)
    check('aucune erreur JavaScript (barlows)',not errs,errs[:1]); c.close()
    # 4. profils du relief : taille constante
    for W,H in ((1280,800),(891,411),(411,850)):
        c,pg,errs=ouvre(b,W,H); tab(pg,'moon'); pg.wait_for_timeout(2500); pg.evaluate("window.__show('Grimaldi')"); pg.wait_for_timeout(1500)
        r=pg.evaluate("""()=>{const d=document.querySelector('#featData details.featprof, .featprof'); if(!d) return null; d.open=true; const s=d.querySelector('svg'); if(!s) return null; const vb=s.viewBox.baseVal, w=s.getBoundingClientRect().width, k=w/vb.width, tx=[...s.querySelectorAll('text')], fs=parseFloat(getComputedStyle(tx[0]).fontSize)*k, sw=parseFloat(s.querySelector('polyline').getAttribute('stroke-width'))*k, fd=document.getElementById('featData').clientWidth; return {k:Math.round(k*100)/100, police:Math.round(fs*10)/10, trait:Math.round(sw*100)/100, largeur:Math.round(w), fiche:fd, vb:vb.width, textes:tx.length}}""")
        check('%dx%d : profil du relief de Grimaldi sur toute la largeur de la fiche, à l\'échelle 1 (police de 11 à 14 points, trait de 1,2 à 1,5 point)'%(W,H),r is not None and r['k']<=1.03 and 10.8<=r['police']<=14.2 and 1.15<=r['trait']<=1.55 and r['largeur']>=0.95*min(r['fiche'],1100),r)
        check('%dx%d : aucune erreur JavaScript (profil)'%(W,H),not errs,errs[:1]); c.close()
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
