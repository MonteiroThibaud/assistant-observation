# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Test 0.87, partie A : démarrage, menus, polices, requêtes extérieures, débordements, 5 formats d'écran
from playwright.sync_api import sync_playwright
import datetime, json
tz=datetime.timezone(datetime.timedelta(hours=2))
TABS=['sun','planet','dso','eye','loc','moon']
F=[(411,850,2),(360,780,2),(320,568,2),(891,411,2),(1280,800,1)]
with sync_playwright() as p:
    b=p.chromium.launch(); bilan=[]
    for w,h,dpr in F:
        c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; ext=[]; bad=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('request',lambda r: ext.append(r.url.split('?')[0]) if not r.url.startswith(('http://localhost','data:','blob:')) else None)
        pg.on('response',lambda r: bad.append((r.url.split('/')[-1],r.status)) if r.url.startswith('http://localhost') and r.status>=400 else None)
        pg.clock.install(time=datetime.datetime(2026,11,5,22,0,tzinfo=tz)); pg.goto('http://localhost:8870/index.html'); pg.wait_for_timeout(9000)
        tabs=[x for x in pg.evaluate("[...document.querySelectorAll('.tabbar [data-tab]')].map(b=>b.dataset.tab)")]
        deb=[]
        for t in tabs:
            pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(700)
            if pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"): deb.append(t)
        pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400)
        info=pg.evaluate("""(()=>({menus:[...document.querySelectorAll('#tab-loc .about details')].length,ouverts:[...document.querySelectorAll('#tab-loc details')].filter(d=>d.open).length,
          version:document.querySelector('.about .version').textContent,polices:[...document.fonts].filter(f=>f.status==='loaded').length,
          google:document.documentElement.innerHTML.includes('fonts.googleapis')}))()""")
        bilan.append((f'{w}x{h}',info,'débordements :',deb or 'aucun','requêtes extérieures :',sorted(set(ext)) or 'aucune','erreurs JS :',errs[:1] or 'aucune','fichiers en erreur :',bad[:3] or 'aucun'))
        if w==411: pg.screenshot(path='/tmp/v191-demarrage-087.png')
        c.close()
    for x in bilan: print(*x)
    b.close()
