# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys
from playwright.sync_api import sync_playwright
import datetime
from PIL import Image
tz=datetime.timezone(datetime.timedelta(hours=2))
port=int(sys.argv[1]); tag=sys.argv[2]; fine=sys.argv[3]=='fine'
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    c.add_init_script("localStorage.setItem('fineRelief',%s);"%('true' if fine else 'false'))
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,30,0,25,tzinfo=tz)); pg.goto(f'http://localhost:{port}/index.html'); pg.wait_for_timeout(10000)
    pg.click('#redBtn') if pg.evaluate("document.documentElement.dataset.night")=='red' else None
    pg.evaluate("document.querySelectorAll('p').forEach(p=>{if(/Version test/.test(p.textContent)&&p.textContent.length<80)p.style.display='none'})")
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(7000)
    for n in ('Fracastor','Beaumont'):
        pg.evaluate("(n)=>window.__go(n)",n); pg.wait_for_timeout(8000)
        for z in range(2):
            pg.evaluate("[...document.querySelectorAll('.mapctl button')].find(b=>b.textContent.trim()==='+').click()"); pg.wait_for_timeout(3500)
        box=pg.evaluate("(()=>{const r=document.getElementById('mapBox').getBoundingClientRect(); return [r.left,r.top,r.width,r.height]})()")
        f=f'/tmp/t9400_{tag}_{n}.png'; pg.screenshot(path=f,clip={'x':box[0],'y':box[1],'width':box[2],'height':box[3]})
        print(tag,n,'zoom',round(pg.evaluate("window.__mv().s"),1),'| erreurs',errs[:1])
    b.close()
