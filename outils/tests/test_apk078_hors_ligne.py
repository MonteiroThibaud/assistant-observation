# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'],service_workers='allow')
    c.add_init_script("localStorage.setItem('deepLists',JSON.stringify(['m']));")
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8811/index.html'); pg.wait_for_timeout(8000)
    ok=pg.evaluate("(async()=>{const r=await navigator.serviceWorker.ready; const ks=await caches.keys(); let n=0; for(const k of ks){ n+=(await (await caches.open(k)).keys()).length } return {actif:!!r.active, caches:ks, entrées:n}})()")
    print('première visite : service worker actif :',ok['actif'],'| caches :',ok['caches'],'| entrées :',ok['entrées'])
    # attendre la fin du précache
    for _ in range(40):
        n=pg.evaluate("(async()=>{const ks=await caches.keys(); let n=0; for(const k of ks){ n+=(await (await caches.open(k)).keys()).length } return n})()")
        if n>=460: break
        pg.wait_for_timeout(1500)
    print('entrées en cache après attente :',n)
    c.set_offline(True)
    pg.clock.install(time=datetime.datetime(2026,10,29,22,0,tzinfo=tz)); pg.reload(); pg.wait_for_timeout(10000)
    print('hors ligne : page rechargée, titre :',pg.title(),'| version affichée :',pg.evaluate("(document.body.innerText.match(/Version 0\\.\\d+ du [^\\n]*/)||[''])[0]"))
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(5000)
    pg.evaluate("(n)=>window.__go(n)",'Copernic'); pg.wait_for_timeout(6000)
    print('hors ligne : zoom',round(pg.evaluate("window.__mv().s"),1),'| tuiles :',pg.evaluate("window.__HC()"))
    pg.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); pg.wait_for_timeout(2000)
    hits=pg.evaluate("window.__hits()"); h=sorted(hits,key=lambda h:-h['m'])[0] if hits else None
    if h:
        xy=pg.evaluate("(()=>{const s=document.getElementById('eyeSvg'); const pt=s.createSVGPoint(); pt.x=%f; pt.y=%f; const q=pt.matrixTransform(s.getScreenCTM()); return [q.x,q.y]})()"%(h['sx'],h['sy']))
        pg.mouse.click(xy[0],xy[1]); pg.wait_for_timeout(4000)
        print('hors ligne : fiche d\'étoile :',pg.evaluate("document.getElementById('eyeStarInfo').textContent")[:110],'| table :',pg.evaluate("window.__SI()"))
    # échec propre de la mise à jour CelesTrak sans réseau
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(500)
    pg.evaluate("document.getElementById('impBox').open=true"); pg.wait_for_timeout(300)
    btn=pg.evaluate("(()=>{const b=[...document.querySelectorAll('#impBox button')].find(x=>/CelesTrak|Mettre à jour|ISS|station/i.test(x.textContent)); return b?b.textContent.trim():null})()")
    print('bouton de mise à jour de l\'ISS :',btn)
    if btn:
        pg.evaluate("[...document.querySelectorAll('#impBox button')].find(x=>/CelesTrak|Mettre à jour|ISS|station/i.test(x.textContent)).click()"); pg.wait_for_timeout(5000)
        print('message sans réseau :',pg.evaluate("[...document.querySelectorAll('#impBox .eyehint, #impBox p')].map(e=>e.textContent.trim()).filter(t=>/échec|impossible|réseau|connexion|erreur/i.test(t)).slice(0,2)"))
    print('erreurs JS :',errs[:3]); b.close()
