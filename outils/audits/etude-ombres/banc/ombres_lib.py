# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys, json, datetime, time
sys.path.insert(0,'/home/claude/p2/outils')
import cap_lib as C
from playwright.sync_api import sync_playwright
tz=datetime.timezone.utc
def ouvre(p,port,t):
    b=p.chromium.launch(args=['--js-flags=--max-old-space-size=2048']); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2.625,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    d=datetime.datetime.fromisoformat(t.replace('Z','+00:00')); pg.clock.install(time=d); pg.clock.set_fixed_time(d)
    pg.goto('http://localhost:%d/index.html'%port); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(1800); pg.click('#mapNow'); pg.wait_for_timeout(1500)
    return b,pg,errs
def zoom_label(pg): return float(pg.evaluate("document.getElementById('zoomLbl').textContent").replace('×','').replace(',','.').strip() or 1)
def vue(pg,region,plan):
    """plan : 'x1' disque entier, 'x3', 'x10', 'x30', 'xmax'"""
    if region and plan!='x1':
        pg.evaluate("(n)=>window.__go(n)",region); pg.wait_for_timeout(1200)
        if plan=='x3':
            for _ in range(4):
                if zoom_label(pg)<=3.6: break
                pg.click('#zoomOut'); pg.wait_for_timeout(220)
        elif plan in ('x30','xmax'):
            lim=28 if plan=='x30' else 1e9
            for _ in range(8 if plan=='xmax' else 4):
                z=zoom_label(pg)
                if z>=lim: break
                pg.click('#zoomIn'); pg.wait_for_timeout(220)
    else:
        for _ in range(8):
            if zoom_label(pg)<=1.05: break
            pg.click('#zoomOut'); pg.wait_for_timeout(200)
    pg.evaluate("window.__argsFull=null; window.__argsRest=null"); pg.wait_for_timeout(200)
    pg.click('#zoomIn'); pg.wait_for_timeout(300); pg.click('#zoomOut')    # force un nouveau rendu complet à la même échelle
    for _ in range(25):
        pg.wait_for_timeout(250)
        if pg.evaluate("!!window.__argsFull"): break
    pg.wait_for_timeout(400)
    return zoom_label(pg)
