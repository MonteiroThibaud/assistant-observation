#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des confirmations (fenêtre d'actions de l'application) pour tous les effacements : oublier la position (lieu utilisé et GPS), oublier tous les lieux,
effacer les éléments importés (petits corps), effacer les éléments de l'ISS, effacer une barlow. Aucune boîte de dialogue native, « Garder » par défaut, Échap annule.
Usage : python3 test_confirmations_effacements.py [ADRESSE_DE_LA_PAGE]  (par défaut http://localhost:8870/index.html). Le serveur de test doit tourner."""
import sys, json, datetime
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8870/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1)); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
SITES=[{'id':'sA','name':'Alpha','lat':46.01,'lon':4.01,'kind':'coord','on':True,'alt':400},{'id':'sB','name':'Bravo','lat':46.02,'lon':4.02,'kind':'coord','on':True,'alt':410},{'id':'sC','name':'Charlie','lat':46.03,'lon':4.03,'kind':'coord','on':False,'alt':420}]
TLE="ISS (ZARYA)\\n1 25544U 98067A   26318.50000000  .00010000  00000-0  18000-3 0  9990\\n2 25544  51.6400 100.0000 0005000 100.0000 260.0000 15.50000000400000"
def init(actif):
    return ("if(!sessionStorage.getItem('ce')){ localStorage.setItem('issSites',%s); localStorage.setItem('placesV','1'); localStorage.setItem('activeLoc',%s); localStorage.setItem('lastGps',JSON.stringify({lat:46.1,lon:4.1,t:Date.now(),acc:20})); localStorage.setItem('sbElems',JSON.stringify({t:'2026-11-01T00:00:00Z'})); localStorage.setItem('issTle',JSON.stringify({text:\"%s\",saved:'2026-11-10T00:00:00Z'})); sessionStorage.setItem('ce','1') }"%(json.dumps(json.dumps(SITES)),json.dumps(json.dumps(actif)),TLE))
with sync_playwright() as p:
    b=p.chromium.launch()
    for actif in ('sB','gps'):
        c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; dlg=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:(dlg.append(d.message),d.dismiss())); pg.add_init_script(init(actif))
        pg.clock.install(time=datetime.datetime(2026,11,14,22,0,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(7000)
        pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(500)
        pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)"); pg.wait_for_timeout(400)
        ls=lambda k: pg.evaluate("(k)=>localStorage.getItem(k)",k)
        def ouvre(sel):
            pg.evaluate("(s)=>document.querySelector(s).scrollIntoView({block:'center'})",sel); pg.wait_for_timeout(700); pg.click(sel); pg.wait_for_timeout(300)
            return pg.evaluate("(()=>{const q=document.querySelector('.orgpop'); return {vis:!q.hidden,txt:q.textContent,focus:document.activeElement&&document.activeElement.dataset.act}})()")
        def parcours(nom,sel,titre,contient,etat_avant,etat_apres,ok_attendu='ok'):
            pop=ouvre(sel)
            check('[%s] le bouton ouvre la confirmation de l\'application (« %s »)'%(nom,titre),pop['vis'] and titre in pop['txt'] and all(x in pop['txt'] for x in contient),pop)
            check('[%s] « Garder » est le choix par défaut'%nom,pop['focus']=='no',pop['focus'])
            check('[%s] rien n\'est effacé tant qu\'on ne confirme pas'%nom,etat_avant(),)
            pg.click('.orgpop [data-act="no"]'); pg.wait_for_timeout(300)
            check('[%s] « Garder » ferme la fenêtre et conserve les données'%nom,pg.evaluate("document.querySelector('.orgpop').hidden") and etat_avant())
            ouvre(sel); pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
            check('[%s] Échap referme la fenêtre sans rien effacer'%nom,pg.evaluate("document.querySelector('.orgpop').hidden") and etat_avant())
            ouvre(sel); pg.click('.orgpop [data-act="ok"]'); pg.wait_for_timeout(700)
            check('[%s] la confirmation exécute l\'effacement'%nom,etat_apres(),)
        if actif=='sB':
            parcours('Oublier le lieu utilisé','#forgetPos','Oublier ce lieu ?',['Bravo'],lambda: len(json.loads(ls('issSites')))==3,lambda: [s['name'] for s in json.loads(ls('issSites'))]==['Alpha','Charlie'] and json.loads(ls('activeLoc'))=='gps')
            pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)"); pg.wait_for_timeout(300)
            parcours('Oublier tous mes lieux','#placesForget','Oublier tous mes lieux ?',['2 lieux'],lambda: len(json.loads(ls('issSites')))==2,lambda: json.loads(ls('issSites'))==[])
            parcours('Effacer les petits corps importés','#sbClear','Effacer les éléments importés ?',['Astéroïdes'],lambda: ls('sbElems')!='{}',lambda: ls('sbElems')=='{}')
            parcours('Effacer les éléments de l\'ISS','#issClear','Effacer les éléments de l\'ISS ?',['CelesTrak'],lambda: ls('issTle') not in (None,'null'),lambda: ls('issTle')=='null')
            # barlows
            pg.fill('#bl1n','Test'); pg.fill('#bl1m','2'); pg.wait_for_timeout(300)
            bars=lambda: json.loads(ls('eyeCfg4'))['bars']
            parcours('Effacer une barlow','#bl1x','Effacer cette barlow ?',['Test','×2'],lambda: bars()[0]['m']==2 and bars()[0]['n']=='Test',lambda: bars()[0]['m']==0 and bars()[0]['n']=='')
            ouvre_vide=ouvre('#bl3x'); check('[Barlow vide] aucun effacement à confirmer : pas de fenêtre',not ouvre_vide['vis'],ouvre_vide)
        else:
            parcours('Oublier la position GPS','#forgetPos','Oublier la position GPS ?',['Roanne'],lambda: ls('lastGps') not in (None,'null'),lambda: ls('lastGps')=='null')
        check('[%s] aucune boîte native, aucune erreur JavaScript'%actif,not dlg and not errs,(dlg,errs[:1])); c.close()
    b.close()
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
