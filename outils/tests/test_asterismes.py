# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, sys
from PIL import Image
tz=datetime.timezone(datetime.timedelta(hours=2))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=3,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8870/index.html'); pg.wait_for_timeout(9000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelector('#deepFilter [data-f=\"all\"]').click()"); pg.evaluate("document.querySelector('#deepSort [data-s=\"num\"]').click()"); pg.wait_for_timeout(300)
    for did,chip,name in (('M73',3,'m73_5mm'),('M73',2,'m73_8mm'),('M40',2,'m40_8mm'),('Picot 1',1,'picot_17mm')):
        pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(400)
        ok=pg.evaluate("""(id)=>{document.querySelectorAll('#deepList details').forEach(d=>d.open=true); const e=document.querySelector('[data-dso="'+id+'"]'); if(!e) return false; if(!e.classList.contains('open')) e.querySelector('.dhead').click(); document.querySelector('[data-dso="'+id+'"] [data-eye]').click(); return true}""",did); pg.wait_for_timeout(2500)
        pg.evaluate("(i)=>document.querySelectorAll('#epChips .chip')[i].click()",chip); pg.wait_for_timeout(3000)
        box=pg.evaluate("(()=>{const r=document.getElementById('eyeSvg').getBoundingClientRect(); return [r.left,r.top,r.width,r.height]})()")
        f=f'/tmp/{name}.png'; pg.screenshot(path=f,clip={'x':box[0]+box[2]*0.2,'y':box[1]+box[3]*0.2,'width':box[2]*0.6,'height':box[3]*0.6}); print(did,ok,'| note :',pg.evaluate("(document.getElementById('eyeStars')||{}).textContent")[:140])
    print('erreurs',errs[:1]); b.close()
ims=[Image.open(f'/tmp/{n}.png').convert('RGB').resize((420,420)) for n in ('m73_5mm','m73_8mm','m40_8mm','picot_17mm')]
o=Image.new('RGB',(420*4+30,420),'#111')
for k,im in enumerate(ims): o.paste(im,(k*430,0))
o.save('/tmp/m73_cmp.png')
