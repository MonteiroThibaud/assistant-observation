#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de la suppression d'une entrée du carnet d'observation : confirmation dans la fenêtre de l'application (thème et mode nuit), « Garder » par défaut, aucune boîte native du navigateur.
Usage : python3 test_carnet_suppression.py [ADRESSE_DE_LA_PAGE]  (par défaut http://localhost:8870/index.html). Le serveur de test doit tourner."""
import sys, json, datetime
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8870/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1)); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
t0=int(datetime.datetime(2026,11,14,21,0,tzinfo=tz).timestamp()*1000)
CARNET=[{'id':'c1','name':'M31','kind':'ciel profond','t':t0,'note':'beau'},{'id':'c2','name':'Tycho','kind':'lune','t':t0+60000,'note':''},{'id':'c3','name':'Jupiter','kind':'planète','t':t0+120000,'note':''}]
INIT="if(!sessionStorage.getItem('ci')){ localStorage.setItem('carnet',%s); sessionStorage.setItem('ci','1') }"%json.dumps(json.dumps(CARNET))
with sync_playwright() as p:
    b=p.chromium.launch()
    for (w,h,dpr) in ((411,850,2),(360,780,2),(320,568,2)):
        c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; dlg=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:(dlg.append(d.message),d.dismiss())); pg.add_init_script(INIT)
        pg.clock.install(time=datetime.datetime(2026,11,14,22,0,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(7000); tag='%dx%d'%(w,h)
        pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(500)
        pg.evaluate("(()=>{const d=document.getElementById('carnetList').closest('details'); if(d) d.open=true})()"); pg.wait_for_timeout(300)
        noms=lambda: pg.evaluate("JSON.parse(localStorage.getItem('carnet')||'[]').map(e=>e.name)")
        def clic(sel):
            pg.evaluate("(s)=>document.querySelector(s).scrollIntoView({block:'center'})",sel); pg.wait_for_timeout(700); pg.click(sel)
        check('(%s) trois entrées au départ, trois boutons ×'%tag,noms()==['M31','Tycho','Jupiter'] and pg.evaluate("document.querySelectorAll('#carnetList .cldel').length")==3,noms())
        clic('#carnetList li[data-id="c2"] .cldel'); pg.wait_for_timeout(300)
        pop=pg.evaluate("(()=>{const p=document.querySelector('.orgpop'); return {vis:!p.hidden,txt:p.textContent,focus:document.activeElement&&document.activeElement.dataset.act}})()")
        check('(%s) le × ouvre la confirmation de l\'application (« Supprimer cette observation ? », nom et date), « Garder » par défaut'%tag,pop['vis'] and 'Supprimer cette observation ?' in pop['txt'] and 'Tycho' in pop['txt'] and pop['focus']=='del-no',pop)
        check('(%s) aucune boîte de dialogue native du navigateur'%tag,not dlg,dlg)
        check('(%s) rien n\'est supprimé tant qu\'on ne confirme pas'%tag,noms()==['M31','Tycho','Jupiter'])
        if w==411:
            # mode nuit : la fenêtre suit le thème de l'application
            f=lambda: pg.evaluate("(()=>{const q=getComputedStyle(document.querySelector('.orgpop')); return q.backgroundColor+'|'+q.color})()")
            pg.evaluate("delete document.documentElement.dataset.night"); pg.wait_for_timeout(200); jour=f(); pg.evaluate("document.documentElement.dataset.night='red'"); pg.wait_for_timeout(200); nuit=f()
            check('(411) la fenêtre de confirmation suit le thème (couleurs différentes en mode nuit)',jour!=nuit,(jour,nuit))
        pg.click('.orgpop [data-act="del-no"]'); pg.wait_for_timeout(300)
        check('(%s) « Garder » ferme la fenêtre et conserve l\'observation'%tag,pg.evaluate("document.querySelector('.orgpop').hidden") and noms()==['M31','Tycho','Jupiter'])
        clic('#carnetList li[data-id="c2"] .cldel'); pg.wait_for_timeout(300); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        check('(%s) Échap referme la confirmation sans supprimer'%tag,pg.evaluate("document.querySelector('.orgpop').hidden") and noms()==['M31','Tycho','Jupiter'])
        clic('#carnetList li[data-id="c2"] .cldel'); pg.wait_for_timeout(300); pg.click('.orgpop [data-act="del-ok"]'); pg.wait_for_timeout(500)
        txt=pg.evaluate("document.getElementById('carnetCount').textContent")
        check('(%s) « Supprimer » retire Tycho (mémoire, liste et compteur)'%tag,noms()==['M31','Jupiter'] and pg.evaluate("document.querySelectorAll('#carnetList li').length")==2 and txt.startswith('2 observations'),(noms(),txt))
        check('(%s) la note des autres observations est conservée'%tag,pg.evaluate("JSON.parse(localStorage.getItem('carnet')).find(e=>e.name==='M31').note")=='beau')
        check('(%s) toujours aucune boîte native, aucune erreur JavaScript'%tag,not dlg and not errs,(dlg,errs[:1])); c.close()
    b.close()
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
