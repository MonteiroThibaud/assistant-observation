# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, re, time
tz=datetime.timezone(datetime.timedelta(hours=2))
TLE="ISS (ZARYA)\n1 25544U 98067A   26295.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'],accept_downloads=True)
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8897/index.html'); pg.wait_for_timeout(7000)
    # --- Telrad : cercle du champ du chercheur
    pg.evaluate("(id)=>window.__eyeSel(id)",'M31'); pg.wait_for_timeout(1200); pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(800)
    def fc():
        return pg.evaluate("(()=>{const c=[...document.querySelectorAll('#eyeSvg circle[stroke-dasharray=\"5 4\"]')]; const t=[...document.querySelectorAll('#eyeSvg text')].find(x=>/^Chercheur/.test(x.textContent)); return c.length?[+(+c[0].getAttribute('r')).toFixed(1), t?t.textContent:null]:null})()")
    r0=fc(); pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(600); r1=fc(); pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(600); r2=fc()
    print('cercle du chercheur (rayon dessin, étiquette) : 10° :',r0,'| 20° :',r1,'| 40° :',r2)
    pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(500); pg.evaluate("window.__setfov(8)"); pg.wait_for_timeout(500); print('chercheur réglé à 8° :',fc(),'| texte :',re.search(r'cercle pointillé[^.]*',pg.evaluate("document.getElementById('eyeInfo').textContent")).group(0)[:70])
    pg.evaluate("window.__setfov(5.6)")
    # --- ISS : tableau unique
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.getElementById('impBox').open=true"); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('issSitesBox').open=true; document.getElementById('locBox').open=true; document.getElementById('manual').hidden=false")
    pg.fill('#issSiteName','Site du club'); pg.fill('#issSiteCoord','46,2 ; 4,3'); pg.click('#issSiteAdd'); pg.wait_for_timeout(300)
    pg.fill('#issSiteQ','Lyon'); pg.wait_for_timeout(1800); pg.click('#issSiteSug button >> nth=0'); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('.tabbar [data-tab=sys]').click()")
    for i in range(80):
        pg.wait_for_timeout(1000); st=pg.evaluate("window.__iss()")
        if st['main'] and not st['busy'] and len(st['res'])==2: break
    pg.wait_for_timeout(1500)
    txt=pg.evaluate("document.getElementById('sysNight') ? document.getElementById('sysNight').innerText : document.body.innerText")
    print('anciennes listes « Deux prochains transits » encore affichées :','Deux prochains transits' in pg.evaluate("document.body.innerText"))
    cards=pg.evaluate("[...document.querySelectorAll('#issSitesTable .issc')].map(c=>c.querySelector('.isshead b').textContent+' | '+c.querySelector('.isshead span').textContent)"); print('cartes dans l\'ordre :',cards)
    hl=pg.evaluate("[...document.querySelectorAll('#issSitesTable .issc .issr.next')].map(r=>r.closest('.issc').querySelector('.isshead b').textContent+' : '+r.innerText.replace(/\\s+/g,' '))"); print('lignes en doré :',hl)
    allev=pg.evaluate("[...document.querySelectorAll('#issSitesTable .issc .issr:not(.issh):not(.none)')].length"); print('lignes de transit au total :',allev)
    col=pg.evaluate("(()=>{const q=s=>getComputedStyle(document.querySelector(s)).color; const rows=[...document.querySelectorAll('#issSitesTable .issc')][0].querySelectorAll('.issr:not(.issh)'); return {lune:getComputedStyle(rows[0].querySelector('.issa')).color, soleil:getComputedStyle(rows[2].querySelector('.issa')).color, doree:getComputedStyle(document.querySelector('#issSitesTable .issr.next .issa')).color}})()"); print('couleurs : Lune',col['lune'],'| Soleil',col['soleil'],'| ligne en doré',col['doree'])
    print('note :',pg.evaluate("document.querySelector('#issSitesTable .eyehint').innerText")[:200])
    pg.evaluate("document.getElementById('issSitesTable').scrollIntoView()")
    with pg.expect_download() as dl: pg.click('[data-iss-site=cur]')
    d=dl.value; t=open(d.path(),encoding='utf-8').read(); print('calendrier « Position GPS » :',d.suggested_filename,'| événements',t.count('BEGIN:VEVENT'))
    pg.screenshot(path='/tmp/iss_fusion.png'); print('erreurs JS :',errs[:1]); b.close()
