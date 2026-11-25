#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de l'organisation des lieux (Paramètres, « Transits de l'ISS ») et de la suppression avec confirmation (« Date et lieu »).
Usage : python3 test_organisation_lieux.py [ADRESSE_DE_LA_PAGE]  (par défaut http://localhost:8870/index.html). Le serveur de test doit tourner.
Aucun crochet de test dans la page : interface et mémoire du navigateur (clés issSites, activeLoc) seulement."""
import sys, datetime, json
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8870/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1)); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
SITES=[{'id':'sA','name':'Alpha','lat':46.01,'lon':4.01,'kind':'coord','on':True,'alt':400},{'id':'sB','name':'Bravo','lat':46.02,'lon':4.02,'kind':'coord','on':True,'alt':410},{'id':'sC','name':'Charlie','lat':46.03,'lon':4.03,'kind':'coord','on':False,'alt':420}]
INIT="localStorage.setItem('issSites',%s); localStorage.setItem('placesV','1'); localStorage.setItem('activeLoc','\"gps\"');"%json.dumps(json.dumps(SITES))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script("if(!sessionStorage.getItem('lieuxInit')){ "+INIT+" sessionStorage.setItem('lieuxInit','1') }")
    pg.clock.install(time=datetime.datetime(2026,11,14,22,0,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(7000)
    ev=lambda js: pg.evaluate(js)
    def ouvre():
        ev("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(500)
        ev("document.getElementById('locBox').open=true; document.getElementById('issSitesBox').open=true"); pg.wait_for_timeout(300)
    ordre=lambda: ev("JSON.parse(localStorage.getItem('issSites')||'[]').map(s=>s.name)")
    ordre_ui=lambda: ev("[...document.querySelectorAll('#issSitesList .siterow[data-id]')].map(r=>r.querySelector('.sitetxt b').textContent)")
    ordre_lieu=lambda: ev("[...document.querySelectorAll('#placesList [data-sitedel]')].map(b=>b.closest('.siterow').querySelector('.sitetxt b').textContent)")
    msg=lambda: ev("document.getElementById('issOrgMsg').textContent")
    def clic(sel):                                   # la page défile d'abord (un défilement referme la fenêtre d'actions), puis on touche
        pg.evaluate("(s)=>document.querySelector(s).scrollIntoView({block:'center'})",sel); pg.wait_for_timeout(700); pg.click(sel)   # élément au centre de l'écran : Playwright n'a plus à défiler au moment du clic
    ouvre()
    check('trois lieux de départ',ordre()==['Alpha','Bravo','Charlie'],ordre())
    check('liste des transits : chaque lieu a une poignée ≡ et un menu ⋯',ev("document.querySelectorAll('#issSitesList .siterow[data-id] .orgh').length")==3 and ev("document.querySelectorAll('#issSitesList .siterow[data-id] .orgmore').length")==3)
    check('liste des transits : la position GPS (si présente) n\'a ni poignée ni menu',ev("[...document.querySelectorAll('#issSitesList .siterow:not([data-id])')].every(r=>!r.querySelector('.orgh')&&!r.querySelector('.orgmore'))"))
    # suppression avec confirmation, depuis « Date et lieu »
    clic('#placesList [data-sitedel="sB"]'); pg.wait_for_timeout(300)
    pop=ev("(()=>{const p=document.querySelector('.orgpop'); return {vis:!p.hidden,txt:p.textContent,focus:document.activeElement&&document.activeElement.dataset.act}})()")
    check('« Date et lieu » : le × ouvre une confirmation (« Supprimer ce lieu ? », nom du lieu), « Garder » est le choix par défaut','Supprimer ce lieu ?' in pop['txt'] and 'Bravo' in pop['txt'] and pop['vis'] and pop['focus']=='del-no',pop)
    check('rien n\'est supprimé tant qu\'on ne confirme pas',ordre()==['Alpha','Bravo','Charlie'])
    pg.click('.orgpop [data-act="del-no"]'); pg.wait_for_timeout(300)
    check('« Garder » ferme la fenêtre et conserve le lieu',ev("document.querySelector('.orgpop').hidden") and ordre()==['Alpha','Bravo','Charlie'])
    clic('#placesList [data-sitedel="sB"]'); pg.wait_for_timeout(300); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    check('Échap referme la confirmation sans supprimer',ev("document.querySelector('.orgpop').hidden") and ordre()==['Alpha','Bravo','Charlie'])
    # ordre : menu ⋯
    clic('#issSitesList .siterow[data-id="sA"] .orgmore'); pg.wait_for_timeout(300)
    etat=ev("[...document.querySelectorAll('.orgpop button[data-act]')].map(b=>b.dataset.act+(b.disabled?':off':''))")
    check('menu ⋯ du premier lieu : « premier » et « monter » inactifs',etat==['first:off','last','up:off','down','del'],etat)
    pg.click('.orgpop [data-act="last"]'); pg.wait_for_timeout(400)
    check('« Mettre en dernier » : Alpha passe en dernier, mémorisé',ordre()==['Bravo','Charlie','Alpha'] and ordre_ui()==['Bravo','Charlie','Alpha'],ordre())
    check('« Date et lieu » suit le même ordre',ordre_lieu()==['Bravo','Charlie','Alpha'],ordre_lieu())
    check('message avec « Annuler »','position 3' in msg() and 'Annuler' in msg(),msg())
    pg.click('#issOrgUndo'); pg.wait_for_timeout(400)
    check('« Annuler » rétablit l\'ordre précédent',ordre()==['Alpha','Bravo','Charlie'] and ordre_ui()==['Alpha','Bravo','Charlie'],ordre())
    # clavier
    pg.focus('#issSitesList .siterow[data-id="sC"] .orgh'); pg.keyboard.press('ArrowUp'); pg.wait_for_timeout(300)
    check('flèche haut : Charlie monte d\'un rang',ordre()==['Alpha','Charlie','Bravo'],ordre())
    check('le focus reste sur la poignée du lieu déplacé',ev("document.activeElement.closest('.siterow')&&document.activeElement.closest('.siterow').dataset.id")=='sC')
    pg.keyboard.press('Home'); pg.wait_for_timeout(300); check('Début : Charlie en premier',ordre()==['Charlie','Alpha','Bravo'],ordre())
    pg.keyboard.press('End'); pg.wait_for_timeout(300); check('Fin : Charlie en dernier',ordre()==['Alpha','Bravo','Charlie'],ordre())
    # glisser-déposer à la souris/au doigt sur la poignée
    ev("document.getElementById('issSitesList').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    h=pg.locator('#issSitesList .siterow[data-id="sA"] .orgh').bounding_box(); last=pg.locator('#issSitesList .siterow[data-id="sC"]').bounding_box()
    pg.mouse.move(h['x']+h['width']/2,h['y']+h['height']/2); pg.mouse.down(); pg.mouse.move(h['x']+h['width']/2,(h['y']+last['y']+last['height'])/2,steps=6); pg.mouse.move(h['x']+h['width']/2,last['y']+last['height']-3,steps=6); pg.wait_for_timeout(200); pg.mouse.up(); pg.wait_for_timeout(500)
    check('glisser la poignée d\'Alpha sous Charlie : ordre Bravo, Charlie, Alpha',ordre()==['Bravo','Charlie','Alpha'],ordre())
    # persistance
    pg.reload(); pg.wait_for_timeout(6000); ouvre()
    check('après rechargement, l\'ordre est conservé',ordre_ui()==['Bravo','Charlie','Alpha'] and ordre_lieu()==['Bravo','Charlie','Alpha'],(ordre_ui(),ordre_lieu()))
    # suppression avec confirmation depuis le menu ⋯ de la liste des transits
    clic('#issSitesList .siterow[data-id="sB"] .orgmore'); pg.wait_for_timeout(300); pg.click('.orgpop [data-act="del"]'); pg.wait_for_timeout(300)
    conf=ev("(()=>{const p=document.querySelector('.orgpop'); return {txt:p.textContent,focus:document.activeElement&&document.activeElement.dataset.act}})()")
    check('menu ⋯ : « Supprimer ce lieu… » demande confirmation, « Garder » par défaut','Supprimer ce lieu ?' in conf['txt'] and 'Bravo' in conf['txt'] and conf['focus']=='del-no',conf)
    pg.click('.orgpop [data-act="del-no"]'); pg.wait_for_timeout(200); check('« Garder » : rien n\'est supprimé',len(ordre())==3)
    clic('#issSitesList .siterow[data-id="sB"] .orgmore'); pg.wait_for_timeout(300); pg.click('.orgpop [data-act="del"]'); pg.wait_for_timeout(200); pg.click('.orgpop [data-act="del-ok"]'); pg.wait_for_timeout(500)
    check('« Supprimer » : Bravo est supprimé des deux listes',ordre()==['Charlie','Alpha'] and ordre_ui()==['Charlie','Alpha'] and ordre_lieu()==['Charlie','Alpha'],(ordre(),ordre_ui(),ordre_lieu()))
    # suppression du lieu utilisé : retour à la position GPS
    clic('#placesList [data-act="sC"]'); pg.wait_for_timeout(800); ouvre()
    check('Charlie est le lieu utilisé',ev("JSON.parse(localStorage.getItem('activeLoc'))")=='sC')
    clic('#placesList [data-sitedel="sC"]'); pg.wait_for_timeout(300); pg.click('.orgpop [data-act="del-ok"]'); pg.wait_for_timeout(1500)
    check('suppression du lieu utilisé confirmée : retour à la position GPS',ev("JSON.parse(localStorage.getItem('activeLoc'))")=='gps' and ordre()==['Alpha'],(ev("localStorage.getItem('activeLoc')"),ordre()))
    # petits écrans (nouveaux contextes : la taille de la fenêtre d'un navigateur mobile simulé ne se change pas)
    check('aucune erreur JavaScript (largeur 411)',not errs,errs[:1] or 'aucune')
    for w,hh in ((360,780),(320,568)):
        c2=b.new_context(viewport={'width':w,'height':hh},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR'); p2=c2.new_page(); e2=[]; p2.on('pageerror',lambda e:e2.append(str(e))); p2.add_init_script(INIT)
        p2.clock.install(time=datetime.datetime(2026,11,14,22,0,tzinfo=tz)); p2.goto(URL); p2.wait_for_timeout(6500)
        p2.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); p2.wait_for_timeout(500); p2.evaluate("document.getElementById('locBox').open=true; document.getElementById('issSitesBox').open=true"); p2.wait_for_timeout(400)
        d=p2.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"); r=p2.evaluate("(()=>{const r=document.querySelector('#issSitesList .siterow[data-id]'); if(!r) return null; const b=r.getBoundingClientRect(), m=r.querySelector('.orgmore').getBoundingClientRect(), h=r.querySelector('.orgh').getBoundingClientRect(), t=r.querySelector('.sitetxt').getBoundingClientRect(); return {w:Math.round(b.width),dx:Math.round(m.right-b.right),dh:Math.round(h.left-b.left),texte:Math.round(t.width)}})()")
        check('largeur %d : pas de défilement horizontal, poignée et menu ⋯ dans la ligne, texte lisible'%w,(not d) and r and r['dx']<=1 and r['dh']>=-1 and r['texte']>=110,(d,r))
        check('largeur %d : aucune erreur JavaScript'%w,not e2,e2[:1] or 'aucune'); c2.close()
    b.close()
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
