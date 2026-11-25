# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys
from playwright.sync_api import sync_playwright
import datetime
from PIL import Image
tz=datetime.timezone(datetime.timedelta(hours=2))
W,H=int(sys.argv[1]),int(sys.argv[2]); night=len(sys.argv)>3
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=1,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    c.route("**/*",lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,29,22,0,tzinfo=tz)); pg.goto('file:///home/claude/work.html'); pg.wait_for_timeout(8000)
    if night: pg.click('#redBtn') if pg.evaluate("document.documentElement.dataset.night")!='red' else None
    else: pg.click('#redBtn') if pg.evaluate("document.documentElement.dataset.night")=='red' else None
    pg.evaluate("document.querySelectorAll('p').forEach(p=>{if(/Version test/.test(p.textContent)&&p.textContent.length<80)p.style.display='none'})")
    t=lambda: pg.evaluate("document.getElementById('manuBtn').textContent")
    print(W,'×',H,'| départ :',t(),'| en-tête sans débordement :',pg.evaluate("(()=>{const h=document.querySelector('.top'); return h.scrollWidth<=h.clientWidth+1})()"),'| page sans débordement :',pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"))
    pg.click('#manuBtn'); pg.wait_for_timeout(2800); print('après « manu » :',t(),'| nuages :',pg.evaluate("document.querySelectorAll('#clouds .cl').length"))
    cov=pg.screenshot(path=f'/home/claude/t7000_nuages_{W}.png')
    pg.click('#manuBtn'); print('cliquable sous les nuages : oui')
    pg.wait_for_timeout(1300); print('après « nina » :',t(),'| ventilateur :',pg.evaluate("!!document.getElementById('fan')")); pg.screenshot(path=f'/home/claude/t7000_ventilo_{W}.png')
    pg.wait_for_timeout(5500); print('fin : nuages :',pg.evaluate("!!document.getElementById('clouds')"),'| ventilateur :',pg.evaluate("!!document.getElementById('fan')"),'| bouton :',t(),'| erreurs JS :',errs[:2])
    c.close(); b.close()
a=Image.open(f'/home/claude/t7000_nuages_{W}.png'); b_=Image.open(f'/home/claude/t7000_ventilo_{W}.png'); o=Image.new('RGB',(a.width+b_.width+10,a.height),'#111'); o.paste(a,(0,0)); o.paste(b_,(a.width+10,0)); o.save(f'/home/claude/t7000_{W}{"n" if night else ""}.png')
