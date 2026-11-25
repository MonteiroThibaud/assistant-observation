# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
with sync_playwright() as p:
    b=p.chromium.launch()
    for port,tag in ((8820,'avec le fichier des listes'),(8821,'sans le fichier des listes (retiré)')):
        c=b.new_context(viewport={'width':411,'height':850},timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; reqs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('response',lambda r: reqs.append((r.url.split('/')[-1],r.status)) if r.url.split('/')[-1] in ('listes-saisonnieres.js','relief-fin.bin.gz') else None)
        pg.clock.install(time=datetime.datetime(2026,10,29,22,0,tzinfo=tz)); pg.goto(f'http://localhost:{port}/index.html'); pg.wait_for_timeout(10000)
        pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400); pg.evaluate("document.getElementById('listBox').open=true"); pg.evaluate("document.getElementById('scrBox').open=true"); pg.wait_for_timeout(500)
        print('---',tag)
        print('fichiers :',reqs)
        print('listes saisonnières proposées :',pg.evaluate("[...document.querySelectorAll('#listChecks label')].map(l=>l.textContent.trim().split('\\n')[0]).filter(t=>/Printemps|Été|Automne|Hiver/.test(t)).length"),'sur 4')
        print('relief de la Lune : ',pg.evaluate("[document.getElementById('fineBox').hidden,document.getElementById('fineBtn').textContent,document.getElementById('fineText').textContent.slice(0,90)]"))
        pg.click('#fineBtn'); pg.wait_for_timeout(1200); print('après un appui sur le bouton :',pg.evaluate("document.getElementById('fineBtn').textContent"))
        pg.click('#fineBtn'); pg.wait_for_timeout(6000); print('après un second appui :',pg.evaluate("document.getElementById('fineBtn').textContent"),'|',pg.evaluate("document.getElementById('fineText').textContent.slice(0,70)"))
        print('erreurs JS :',errs[:2]); c.close()
    b.close()
