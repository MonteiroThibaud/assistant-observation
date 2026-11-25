# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':360,'height':780},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8880/index.html'); pg.wait_for_timeout(8000)
    # --- menus de Paramètres
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()")
    pg.evaluate("['telBox','scrBox','listBox'].forEach(i=>{for(let d=document.getElementById(i);d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true}); document.querySelectorAll('#listBox details').forEach(d=>d.open=true)"); pg.wait_for_timeout(400)
    print('menus ouverts avant rechargement :',pg.evaluate("[...document.querySelectorAll('details')].filter(d=>d.open).length"))
    pg.reload(); pg.wait_for_timeout(8000); pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400)
    print('menus ouverts après rechargement (tous les menus de Paramètres et d\'Informations) :',pg.evaluate("[...document.querySelectorAll('#tab-loc details')].filter(d=>d.open).length"))
    # --- bulle de la Lune
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(5000)
    vis=lambda: pg.evaluate("!document.getElementById('featCard').hidden")
    pg.evaluate("window.__show('Tycho')"); pg.wait_for_timeout(1200); print('bulle ouverte :',vis())
    box=pg.evaluate("(()=>{const r=document.getElementById('featCard').getBoundingClientRect(); const m=document.getElementById('mapBox').getBoundingClientRect(); return {card:[r.left,r.top,r.width,r.height],map:[m.left,m.top,m.width,m.height]}})()"); print('fiche :',[round(x) for x in box['card']],'| carte :',[round(x) for x in box['map']])
    # appui dans la fiche : reste ouverte
    cx=box['card'][0]+box['card'][2]/2; cy=box['card'][1]+box['card'][3]/2
    pg.mouse.click(cx,cy); pg.wait_for_timeout(500); print('appui dans la fiche : ouverte =',vis())
    # défilement : l'en-tête reste visible
    pg.evaluate("document.getElementById('featCard').scrollTop=400"); pg.wait_for_timeout(400)
    h=pg.evaluate("(()=>{const c=document.getElementById('featCard').getBoundingClientRect(), h=document.querySelector('.feathead').getBoundingClientRect(), x=document.getElementById('featClose').getBoundingClientRect(); return {scroll:document.getElementById('featCard').scrollTop, hauteurContenu:document.getElementById('featCard').scrollHeight, decalageEnTete:Math.round(h.top-c.top), croixVisible:x.top>=c.top-1&&x.bottom<=c.bottom+1}})()")
    print('après défilement :',h)
    pg.screenshot(path='/tmp/bulle_defile.png')
    # appui à côté (carte, hors fiche)
    pg.mouse.click(box['map'][0]+box['map'][2]/2, box['map'][1]+40); pg.wait_for_timeout(600); print('appui sur la carte, hors fiche : ouverte =',vis())
    # glissement de la carte avec bulle ouverte : reste ouverte
    pg.evaluate("window.__show('Tycho')"); pg.wait_for_timeout(1000)
    pg.mouse.move(box['map'][0]+60,box['map'][1]+40); pg.mouse.down(); pg.mouse.move(box['map'][0]+160,box['map'][1]+70,steps=6); pg.mouse.up(); pg.wait_for_timeout(500); print('glissement de la carte : ouverte =',vis())
    # croix
    pg.click('#featClose'); pg.wait_for_timeout(300); print('croix : ouverte =',vis())
    # appui sur un nom de la carte alors qu'une fiche est ouverte : une nouvelle fiche s'ouvre
    pg.evaluate("window.__show('Tycho')"); pg.wait_for_timeout(1000)
    lab=pg.evaluate("(()=>{const L=[...document.querySelectorAll('#mapLabels *')].filter(e=>e.textContent&&e.textContent.trim()&&e.textContent.trim()!=='Tycho'); const r=L.length?L[0].getBoundingClientRect():null; return r?[r.left+r.width/2,r.top+r.height/2,L[0].textContent.trim()]:null})()"); print('nom touché :',lab)
    if lab:
        pg.mouse.click(lab[0],lab[1]); pg.wait_for_timeout(900); print('après appui sur ce nom : ouverte =',vis(),'| titre :',pg.evaluate("document.getElementById('featName').textContent"))
    print('erreurs JS :',errs[:2]); b.close()
