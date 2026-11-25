# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, io, sys
from PIL import Image, ImageChops
tz=datetime.timezone(datetime.timedelta(hours=1))
store={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for nom,port in (('a',8841),('b',8842)):
        c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1.5,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,11,5,22,0,tzinfo=tz)); pg.goto(f'http://localhost:{port}/index.html'); pg.wait_for_timeout(8000)
        sh={}
        for tab in ('sys','det','deep','loc'):
            pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",tab); pg.wait_for_timeout(1500); sh[tab]=pg.screenshot()
        pg.evaluate("document.querySelector('.tabbar [data-tab=det]').click()"); pg.wait_for_timeout(800)
        pg.evaluate("document.querySelectorAll('#tab-det details').forEach(d=>d.open=true)"); pg.wait_for_timeout(1500); sh['det_open']=pg.screenshot(full_page=True)
        for id_,chip in (('M13',1),('M45',0),('M42',2)):
            pg.evaluate("(id)=>window.__eyeSel(id)",id_); pg.wait_for_timeout(1200)
            pg.evaluate("(i)=>document.querySelectorAll('#epChips .chip')[i].click()",chip); pg.wait_for_timeout(1500); sh['eye_'+id_]=pg.screenshot()
        pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(5000)
        sh['moon']=pg.screenshot()
        for n in ('Tycho','Mons Piton','Abel'):
            pg.evaluate("(n)=>window.__show(n)",n); pg.wait_for_timeout(1200); sh['lune_'+n]=pg.screenshot()
        store[nom]=sh; print(nom,'erreurs JS :',errs[:1] or 'aucune',flush=True); c.close()
    b.close()
bad=[k for k in store['a'] if ImageChops.difference(Image.open(io.BytesIO(store['a'][k])).convert('RGB'),Image.open(io.BytesIO(store['b'][k])).convert('RGB')).getbbox() is not None]
print('vues comparées :',len(store['a']),'| différentes :',bad or 'aucune')
