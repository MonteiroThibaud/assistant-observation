# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, numpy as np
from PIL import Image
tz=datetime.timezone(datetime.timedelta(hours=2))
SITES=[('Fracastor',(2026,10,30,0,25)),('Tycho',(2026,10,30,0,25)),('Copernic',(2026,10,30,0,25))]
import sys, json
TAG=sys.argv[1]; PORT=int(sys.argv[2]); res={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for nom,t in SITES:
        c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2.8125,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(*t,tzinfo=tz)); pg.goto(f'http://localhost:{PORT}/index.html'); pg.wait_for_timeout(9000)
        pg.click('#redBtn') if pg.evaluate("document.documentElement.dataset.night")=='red' else None
        pg.evaluate("document.querySelectorAll('p').forEach(p=>{if(/Version test/.test(p.textContent)&&p.textContent.length<80)p.style.display='none'})")
        pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(4000)
        pg.evaluate("window.__cpu=0; window.__np=0; window.__sz=[]"); pg.evaluate("(n)=>window.__go(n)",nom); pg.wait_for_timeout(8000)
        cpu=round(pg.evaluate("window.__cpu")); npaint=pg.evaluate("window.__np||0"); tailles=pg.evaluate("window.__sz||[]")
        box=pg.evaluate("(()=>{const r=document.getElementById('mapBox').getBoundingClientRect(); return [r.left,r.top,r.width,r.height]})()")
        f=f'/tmp/t9992_{TAG}_{nom}_{t[2]}.png'; pg.screenshot(path=f,clip={'x':box[0],'y':box[1],'width':box[2],'height':box[3]-80})
        res[nom+'_'+str(t[2])]=cpu; print(TAG,nom,t[2:4],'calcul %d ms'%cpu,'peintures :',npaint,tailles,'| erreurs',errs[:1],flush=True); c.close()
    b.close()
json.dump(res,open(f'/tmp/t9992_{TAG}.json','w'))
