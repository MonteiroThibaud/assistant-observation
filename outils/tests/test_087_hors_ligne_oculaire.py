# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Test 0.87, partie B : service worker et hors ligne ; C : oculaire (images DSS, Telrad) ; D : sites ISS
from playwright.sync_api import sync_playwright
import datetime, time
tz=datetime.timezone(datetime.timedelta(hours=2))
TLE="ISS (ZARYA)\n1 25544U 98067A   26309.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'],service_workers='allow')
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8872/index.html'); pg.wait_for_timeout(5000)
    # --- B : service worker
    sw=pg.evaluate("navigator.serviceWorker.ready.then(r=>!!r.active)"); print('service worker actif :',sw)
    t0=time.time(); n=0
    while time.time()-t0<110:
        n=pg.evaluate("caches.keys().then(async k=>{const o={};for(const x of k){o[x]=(await (await caches.open(x)).keys()).length}return o})"); 
        if any(v>=470 for v in n.values()): break
        pg.wait_for_timeout(5000)
    print('caches :',n,'| attente %.0f s'%(time.time()-t0))
    has=pg.evaluate("caches.open('assistant-observation-087').then(c=>c.match('./LICENCES-TIERCES.txt')).then(r=>!!r)"); print('LICENCES-TIERCES.txt en cache :',has)
    c.set_offline(True); pg.reload(); pg.wait_for_timeout(8000)
    print('hors ligne : titre =',pg.title(),'| version =',pg.evaluate("document.querySelector('.about .version').textContent"),'| polices =',pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').length"))
    # --- C : oculaire
    pg.evaluate("(id)=>window.__eyeSel(id)",'M13'); pg.wait_for_timeout(1500); pg.click('#epChips .chip >> nth=1'); pg.wait_for_timeout(800)
    print('M13 à l’oculaire : images dans la vue =',pg.evaluate("document.querySelectorAll('#eyeSvg image').length"))
    pg.screenshot(path='/tmp/v191-oculaire-M13.png')
    lab=[]
    pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(500); lab.append(pg.evaluate("document.querySelector('#epChips [data-ep=telrad]').textContent.trim()"))
    for i in range(3):
        pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(500); lab.append(pg.evaluate("document.querySelector('#epChips [data-ep=telrad]').textContent.trim()"))
    cercles=pg.evaluate("[...document.querySelectorAll('#eyeSvg circle')].filter(c=>/#?(c0|ff|e0|d0|f0|e5|ef)/i.test(c.getAttribute('stroke')||'')).length")
    print('Telrad, libellés successifs :',lab,'| aucun libellé « Chercheur » :',pg.evaluate("![...document.querySelectorAll('#eyeSvg text')].some(x=>/^Chercheur/.test(x.textContent))"))
    # --- D : sites ISS (interface)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400)
    pg.evaluate("document.getElementById('impBox').open=true"); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(600)
    pg.evaluate("document.getElementById('issSitesBox').open=true; document.getElementById('locBox').open=true; document.getElementById('manual').hidden=false"); pg.wait_for_timeout(300)
    pg.fill('#issSiteName','Paris test'); pg.fill('#issSiteCoord','48,8566 ; 2,3522'); pg.click('#issSiteAdd'); pg.wait_for_timeout(1500)
    print('site ajouté :',pg.evaluate("document.getElementById('issSiteMsg').textContent"),'| lignes de la liste =',pg.evaluate("document.querySelectorAll('#issSitesList li').length"))
    pg.evaluate("document.querySelector('.tabbar [data-tab=sys]').click()"); pg.wait_for_timeout(9000)
    txt=pg.evaluate("(document.getElementById('issSitesTable')||document.body).textContent.replace(/\\s+/g,' ').slice(0,260)")
    print('tableau ISS :',txt)
    print('cartes du tableau (Position GPS + sites) :',pg.evaluate("(document.getElementById('issSitesTable')||document.body).textContent.includes('Position GPS')"),'| Paris test présent :',pg.evaluate("(document.getElementById('issSitesTable')||document.body).textContent.includes('Paris test')"))
    # --- E : Lune, relief fin, listes
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(7000)
    print('Lune : canvas non vide =',pg.evaluate("(()=>{const c=document.querySelector('#tab-moon canvas'); if(!c) return 'pas de canvas'; const x=c.getContext('2d'); const d=x.getImageData(0,0,c.width,c.height).data; let n=0; for(let i=0;i<d.length;i+=400) if(d[i]>20) n++; return n})()"))
    pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(1500)
    print('Ciel profond : onglet affiché, listes proposées =',pg.evaluate("document.querySelectorAll('#listChecks label').length"))
    print('erreurs JS :',errs[:2] or 'aucune'); b.close()
