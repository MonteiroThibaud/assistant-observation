# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, time
tz=datetime.timezone(datetime.timedelta(hours=2))
TLE="ISS (ZARYA)\n1 25544U 98067A   26295.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
def prep(pg):
    pg.clock.install(time=datetime.datetime(2026,10,30,13,0,tzinfo=tz)); pg.goto('http://localhost:8897/index.html'); pg.wait_for_timeout(7000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400)
    pg.evaluate("document.getElementById('impBox').open=true"); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('impBox').open=false; document.getElementById('issSitesBox').open=true; document.getElementById('locBox').open=true; document.getElementById('manual').hidden=false")
    pg.fill('#issSiteName','Roanne'); pg.click('#issSitePos'); pg.click('#issSiteAdd'); pg.wait_for_timeout(200)
    pg.fill('#issSiteQ','Lyon'); pg.wait_for_timeout(1800); pg.click('#issSiteSug button >> nth=0'); pg.wait_for_timeout(300)
    pg.fill('#issSiteName','Site du club'); pg.fill('#issSiteCoord','46,2 ; 4,3'); pg.click('#issSiteAdd'); pg.wait_for_timeout(300)
    pg.fill('#issSiteQ','Rég'); pg.wait_for_timeout(1800)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); prep(pg)
    pg.evaluate("document.getElementById('issSitesBox').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/iss_param.png')
    pg.evaluate("document.querySelector('.tabbar [data-tab=sys]').click()")
    for i in range(90):
        pg.wait_for_timeout(1000)
        if not pg.evaluate("window.__iss().busy") and len(pg.evaluate("window.__iss().res"))==3: break
    pg.wait_for_timeout(500); pg.evaluate("document.getElementById('issSitesTable').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
    pg.evaluate("window.scrollBy(0,-60)"); pg.screenshot(path='/tmp/iss_sys_tab.png'); print('étroit : erreurs JS',errs[:1],'| débordement horizontal :',pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"))
    c.close()
    c=b.new_context(viewport={'width':1280,'height':900},device_scale_factor=1.5,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); prep(pg)
    pg.evaluate("document.querySelector('.tabbar [data-tab=sys]').click()")
    for i in range(90):
        pg.wait_for_timeout(1000)
        if not pg.evaluate("window.__iss().busy") and len(pg.evaluate("window.__iss().res"))==3: break
    pg.wait_for_timeout(500); pg.evaluate("document.getElementById('issSitesTable').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
    r=pg.evaluate("(()=>{const w=document.getElementById('issSitesTable'); return [Math.round(w.getBoundingClientRect().width), getComputedStyle(w.querySelector('.issx')).display, getComputedStyle(w.querySelector('.issc')).display]})()"); print('large : conteneur',r)
    pg.screenshot(path='/tmp/iss_sys_large.png'); print('large : erreurs JS',errs[:1]); b.close()
