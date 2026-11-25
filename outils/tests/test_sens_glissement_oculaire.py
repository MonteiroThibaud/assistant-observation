# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, re, sys
tz=datetime.timezone(datetime.timedelta(hours=1))
OBJ="(()=>{const g=[...document.querySelectorAll('#eyeSvg g')].find(x=>/translate\\(150\\.00 150\\.00\\) rotate/.test(x.getAttribute('transform')||'')); if(!g) return null; const r=g.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2]})()"
def run(url,label):
    with sync_playwright() as p:
        b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,11,10,22,0,tzinfo=tz)); pg.goto(url); pg.wait_for_timeout(7000)
        res={}
        for ori in ('dob','sky','rot','mirror'):
            pg.evaluate("window.__eyeSel('M11')"); pg.wait_for_timeout(300); pg.evaluate("window.__eyeSel('M13')"); pg.wait_for_timeout(600)
            pg.select_option('#orient',ori); pg.wait_for_timeout(800)
            box=pg.query_selector('#eyeSvg').bounding_box(); cx,cy=box['x']+box['width']/2,box['y']+box['height']/2
            a=pg.evaluate(OBJ)
            pg.mouse.move(cx,cy); pg.mouse.down(); pg.mouse.move(cx+70,cy+40,steps=6); pg.mouse.up(); pg.wait_for_timeout(500)
            z=pg.evaluate(OBJ)
            res[ori]=(None if not a or not z else (round(z[0]-a[0]),round(z[1]-a[1])))
        print(label,'| déplacement de l’objet pour un glissement du doigt de (+70, +40) px :',res,'| erreurs JS :',errs[:1] or 'aucune',flush=True)
        b.close()
if __name__=='__main__': run(sys.argv[1],sys.argv[2])
