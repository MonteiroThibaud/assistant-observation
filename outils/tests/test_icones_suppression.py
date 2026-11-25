#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des icônes de suppression : poubelle en SVG intégré sur tous les boutons de suppression (carnet, lieux, barlows, fenêtres de confirmation), croix réservée à la fermeture,
couleur de l'icône = couleur du thème (jour et nuit), aucune image ni police extérieure.
Usage : python3 test_icones_suppression.py [ADRESSE_DE_LA_PAGE]  (par défaut http://localhost:8870/index.html). Le serveur de test doit tourner."""
import sys, json, datetime
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8870/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1)); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
t0=int(datetime.datetime(2026,11,14,21,0,tzinfo=tz).timestamp()*1000)
CARNET=[{'id':'c1','name':'M31','kind':'ciel profond','t':t0,'note':''}]
SITES=[{'id':'sA','name':'Alpha','lat':46.01,'lon':4.01,'kind':'coord','on':True,'alt':400}]
INIT="localStorage.setItem('carnet',%s); localStorage.setItem('issSites',%s); localStorage.setItem('placesV','1'); localStorage.setItem('activeLoc','\"gps\"');"%(json.dumps(json.dumps(CARNET)),json.dumps(json.dumps(SITES)))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR')
    pg=c.new_page(); errs=[]; reqs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('request',lambda r:reqs.append(r.url)); pg.add_init_script(INIT)
    pg.clock.install(time=datetime.datetime(2026,11,14,22,0,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(7000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(500); pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)"); pg.wait_for_timeout(400)
    INFO="""(sel)=>{ const b=document.querySelector(sel); if(!b) return null; const s=b.querySelector('svg.ico'); const r=s?s.getBoundingClientRect():null; const cs=s?getComputedStyle(s):null; return {svg:!!s,txt:b.textContent.trim(),w:r?Math.round(r.width*10)/10:0,h:r?Math.round(r.height*10)/10:0,trace:cs?cs.stroke:'',couleur:getComputedStyle(b).color,remplissage:cs?cs.fill:'',formes:s?s.querySelectorAll('path,circle').length:0,aria:b.getAttribute('aria-label')} }"""
    for nom,sel in (('carnet (×)','#carnetList .cldel'),('lieux (×)','#placesList [data-sitedel]'),('barlow 1','#bl1x'),('barlow 2','#bl2x'),('barlow 3','#bl3x')):
        i=pg.evaluate(INFO,sel)
        check('%s : poubelle SVG intégrée, plus de croix en texte, libellé accessible conservé'%nom,i and i['svg'] and i['txt']=='' and i['formes']==5 and i['aria'],i)
        check('%s : icône de 16 à 24 points, au trait (sans remplissage), de la couleur du bouton'%nom,i and 16<=i['w']<=24 and abs(i['w']-i['h'])<0.5 and i['remplissage']=='none' and i['trace']==i['couleur'],i)
    fiche=pg.evaluate("document.getElementById('featClose').textContent.trim()")
    check('la croix reste réservée à la fermeture de la fiche de la Lune',fiche=='×',fiche)
    for nom,sel in (('carnet','#carnetList .cldel'),('lieux','#placesList [data-sitedel]')):
        pg.evaluate("(s)=>document.querySelector(s).scrollIntoView({block:'center'})",sel); pg.wait_for_timeout(700); pg.click(sel); pg.wait_for_timeout(400)
        i=pg.evaluate(INFO,'.orgpop [data-act="del-ok"]')
        check('fenêtre de confirmation (%s) : « Supprimer » précédé de la poubelle'%nom,i and i['svg'] and i['txt']=='Supprimer' and i['formes']==5,i)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    # jour et nuit : la couleur suit le thème
    pg.evaluate("delete document.documentElement.dataset.night"); pg.wait_for_timeout(250); jour=pg.evaluate(INFO,'#carnetList .cldel')
    pg.evaluate("document.documentElement.dataset.night='red'"); pg.wait_for_timeout(250); nuit=pg.evaluate(INFO,'#carnetList .cldel')
    check('la poubelle change de couleur avec le mode nuit (suit currentColor)',jour['trace']==jour['couleur'] and nuit['trace']==nuit['couleur'] and jour['trace']!=nuit['trace'],(jour['trace'],nuit['trace']))
    ext=[u for u in reqs if not u.startswith(('http://localhost','data:','blob:'))]
    check('aucune ressource extérieure (image, police, icônes) : seules les requêtes habituelles',all('celestrak' in u or 'localhost' in u for u in ext),ext[:3])
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
