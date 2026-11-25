# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
with sync_playwright() as p:
    b=p.chromium.launch()
    for port,tag in ((8810,'0.81'),(8830,'0.82')):
        c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,10,30,0,25,tzinfo=tz)); pg.goto(f'http://localhost:{port}/index.html'); pg.wait_for_timeout(10000)
        pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(8000)
        res=[]
        for n in ('Tycho','Fracastor','Copernic'):
            pg.evaluate("window.__cpu=0"); pg.evaluate("(n)=>window.__go(n)",n); pg.wait_for_timeout(9000)
            res.append((n,round(pg.evaluate("window.__cpu")),pg.evaluate("window.__HC().charges")))
        print(tag,'temps de calcul cumulé de la peinture à ×10 (ms, navigateur sans affichage) et tuiles :',res,'| erreurs :',errs[:1]); c.close()
    b.close()
