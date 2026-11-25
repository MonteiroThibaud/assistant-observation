# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, re
from PIL import Image
tz=datetime.timezone(datetime.timedelta(hours=2))
def run(W,H,tag,obj):
    with sync_playwright() as p:
        b=p.chromium.launch(); c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8897/index.html'); pg.wait_for_timeout(8000)
        pg.evaluate("(id)=>window.__eyeSel(id)",obj); pg.wait_for_timeout(1500)
        chip=lambda: pg.evaluate("(()=>{const b=document.querySelector('#epChips [data-ep=telrad]'); return [b.textContent,b.getAttribute('aria-pressed')]})()")
        info=lambda: re.sub(r'\s+',' ',pg.evaluate("document.getElementById('eyeInfo').textContent"))[:75]
        stars=lambda: pg.evaluate("document.getElementById('eyeStars').textContent")[:70]
        res=[]
        pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(900); res.append(('1er appui (Telrad)',chip(),pg.evaluate("window.__telz()"),stars()))
        pg.screenshot(path=f'/tmp/tel_{tag}_0.png')
        for k in range(1,5):
            pg.click('#epChips [data-ep=telrad]'); pg.wait_for_timeout(900); res.append(('appui %d'%(k+1),chip(),pg.evaluate("window.__telz()"),stars()))
            if k<3: pg.screenshot(path=f'/tmp/tel_{tag}_{k}.png')
            if k==1: pg.evaluate("window.__setpan(7200,-3600)"); pg.wait_for_timeout(500)   # décalage du centre pour tester le recentrage au retour
        print('== %d × %d, objet %s'%(W,H,obj))
        for r in res: print('  ',r)
        print('  décalage après le retour au champ de départ :',pg.evaluate("window.__pan()"))
        print('  erreurs JS :',errs[:1]); b.close()
run(411,850,'tel','M31')
