# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
CAS=[('Roanne (GPS)',46.0345,4.0720),('Paris',48.8566,2.3522),('Lyon',45.7640,4.8357),('Genève',46.2044,6.1432),('Tokyo',35.6762,139.6503),('Ajaccio',41.9192,8.7386),('Mer Méditerranée',42.5,5.0),('Saint-Denis (La Réunion)',-20.8789,55.4481),('Position refusée (défaut)',None,None)]
with sync_playwright() as p:
    b=p.chromium.launch()
    for nom,la,lo in CAS:
        kw=dict(viewport={'width':411,'height':850},timezone_id='Europe/Paris',locale='fr-FR')
        if la is not None: kw.update(geolocation={'latitude':la,'longitude':lo},permissions=['geolocation'])
        c=b.new_context(**kw); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8890/index.html'); pg.wait_for_timeout(7000)
        pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.getElementById('carnetBox').open=true"); pg.wait_for_timeout(300)
        etat0=pg.evaluate("[document.getElementById('carnetPlaceBtn').textContent,document.getElementById('carnetPlaceBtn').disabled]")
        # sans autorisation : aucun lieu
        pg.evaluate("window.__addLog('dso','M13')"); pg.wait_for_timeout(1200)
        sans=pg.evaluate("window.__carnet()[0].place||null")
        pg.click('#carnetPlaceBtn'); pg.wait_for_timeout(2500)
        etat1=pg.evaluate("[document.getElementById('carnetPlaceBtn').textContent,document.getElementById('carnetPlaceBtn').getAttribute('aria-pressed')]")
        pg.evaluate("window.__addLog('dso','M31')"); pg.wait_for_timeout(2500)
        avec=pg.evaluate("window.__carnet()[0].place||null"); src=pg.evaluate("window.__pos().src")
        aff=pg.evaluate("document.querySelector('#carnetList li .clsub').textContent")
        print('%-28s source %-7s | bouton %s | sans autorisation : %s | avec : %s | ligne : %s | erreurs %s'%(nom,src,etat0[0],sans,avec,aff,errs[:1]))
        c.close()
    # persistance du réglage et copie
    c=b.new_context(viewport={'width':411,'height':850},timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8890/index.html'); pg.wait_for_timeout(6000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.getElementById('carnetBox').open=true"); pg.click('#carnetPlaceBtn'); pg.wait_for_timeout(1500)
    pg.evaluate("window.__addLog('dso','M45')"); pg.wait_for_timeout(2500)
    pg.reload(); pg.wait_for_timeout(6000); pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.getElementById('carnetBox').open=true")
    print('après rechargement : bouton =',pg.evaluate("document.getElementById('carnetPlaceBtn').textContent"),'| entrée :',pg.evaluate("document.querySelector('#carnetList li .clsub').textContent"))
    pg.click('#carnetCopy'); pg.wait_for_timeout(500); print('texte copié :',pg.evaluate("document.getElementById('carnetText').value"))
    pg.screenshot(path='/tmp/carnet_lieu.png'); c.close(); b.close()
