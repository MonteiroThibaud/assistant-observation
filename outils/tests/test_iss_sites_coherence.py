# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime, time, json
tz=datetime.timezone(datetime.timedelta(hours=2))
TLE="ISS (ZARYA)\n1 25544U 98067A   26295.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'],accept_downloads=True)
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8897/index.html'); pg.wait_for_timeout(7000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.getElementById('impBox').open=true"); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('issSitesBox').open=true; document.getElementById('locBox').open=true; document.getElementById('manual').hidden=false")
    pg.fill('#issSiteName','Roanne'); pg.click('#issSitePos'); pg.click('#issSiteAdd'); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('.tabbar [data-tab=sys]').click()")
    for i in range(60):
        pg.wait_for_timeout(1000); st=pg.evaluate("window.__iss()"); 
        if not st['busy'] and len(st['res'])==1: break
    pg.wait_for_timeout(8000)   # laisse le calcul du lieu de l'utilisateur (issEnsure) se terminer
    sid=pg.evaluate("window.__sites()[0].id"); a=pg.evaluate("window.__issMain()"); bb=pg.evaluate("window.__issSite(arguments[0])" if False else "(id)=>window.__issSite(id)",sid) if False else pg.evaluate("(id)=>window.__issSite(id)",sid)
    print('lieu de l\'utilisateur : %d transits ; site « Roanne » : %d transits'%(len(a),len(bb)))
    ok=len(a)==len(bb) and all(x[0]==y[0] and abs(x[1]-y[1])<2000 for x,y in zip(sorted(a,key=lambda z:(z[0],z[1])),sorted(bb,key=lambda z:(z[0],z[1]))))
    print('mêmes transits que le calcul du lieu de l\'utilisateur (écart < 2 s) :',ok)
    # calendrier par site
    pg.evaluate("document.getElementById('issSitesTable').scrollIntoView()")
    with pg.expect_download() as dl: pg.click('[data-iss-site]:not([data-iss-site=cur])')
    d=dl.value; path=d.path(); txt=open(path,encoding='utf-8').read()
    print('calendrier : fichier',d.suggested_filename,'| événements :',txt.count('BEGIN:VEVENT'),'| site cité :','Site : Roanne' in txt,'| UID avec identifiant de site :',('UID:iss-'+sid) in txt)
    # persistance
    pg.reload(); pg.wait_for_timeout(7000); pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.getElementById('issSitesBox').open=true; document.getElementById('locBox').open=true; document.getElementById('manual').hidden=false")
    print('après rechargement : sites =',pg.evaluate("window.__sites().length"),'| menus ouverts avant ouverture manuelle :',pg.evaluate("[...document.querySelectorAll('#tab-loc details')].filter(d=>d.open&&d.id!=='issSitesBox').length"))
    # limite de six sites
    for i in range(7):
        pg.fill('#issSiteName','S%d'%i); pg.fill('#issSiteCoord','4%d,1 ; %d,5'%(i,i+1)); pg.click('#issSiteAdd'); pg.wait_for_timeout(150)
    print('limite : sites =',pg.evaluate("window.__sites().length"),'| message :',pg.evaluate("document.getElementById('issSiteMsg').textContent"))
    # décocher et supprimer pendant le calcul
    pg.evaluate("document.querySelector('.tabbar [data-tab=sys]').click()"); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.querySelector('[data-site]').click()"); pg.click('[data-sitedel] >> nth=1'); pg.wait_for_timeout(500)
    t0=time.time()
    for i in range(120):
        pg.wait_for_timeout(1000); st=pg.evaluate("window.__iss()")
        if not st['busy']: break
    print('après coche retirée et suppression : sites =',pg.evaluate("window.__sites().length"),'| calcul terminé en %.1f s | erreurs JS %s'%(time.time()-t0,errs[:1]))
    # oublier
    pg.click('#issSitesForget'); pg.click('#issSitesForget'); pg.wait_for_timeout(300); print('oublier tout : sites =',pg.evaluate("window.__sites().length"))
    b.close()
