# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime,re
tz=datetime.timezone(datetime.timedelta(hours=2))
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    c.add_init_script("localStorage.setItem('deepLists',JSON.stringify(['m','x']));")
    pg=c.new_page(); errs=[]; reqs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('request',lambda r: reqs.append(r.url.split('/img/')[-1]) if '/img/' in r.url else None)
    pg.clock.install(time=datetime.datetime(2026,10,29,22,0,tzinfo=tz)); pg.goto('http://localhost:8810/index.html'); pg.wait_for_timeout(10000)
    print('version :',pg.evaluate("document.querySelector('.about .version')?document.querySelector('.about .version').textContent:(document.body.innerText.match(/Version 0\\.\\d+ du [^\\n]*/)||[''])[0]"))
    for t in ('sys','det','deep','eye','moon','loc'):
        pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(500)
    print('relief fin et étoiles : fichiers demandés :',sorted(set(r for r in reqs if r.startswith(('relief-fin','etoiles'))))[:6])
    # Moon zoom ×10 : tuiles
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(5000)
    pg.evaluate("(n)=>window.__go(n)",'Tycho'); pg.wait_for_timeout(6000)
    print('zoom Tycho :',round(pg.evaluate("window.__mv().s"),1),'| tuiles :',pg.evaluate("window.__HC()"))
    # images du ciel : NGC 4565 et M79 à l'oculaire
    pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelector('#deepFilter [data-f=\"all\"]').click()"); pg.evaluate("document.querySelector('#deepSort [data-s=\"num\"]').click()"); pg.wait_for_timeout(300)
    for did in ('NGC 4565','M79'):
        ok=pg.evaluate("""(id)=>{document.querySelectorAll('#deepList details').forEach(d=>d.open=true); const e=document.querySelector('[data-dso="'+id+'"]'); if(!e) return false; if(!e.classList.contains('open')) e.querySelector('.dhead').click(); document.querySelector('[data-dso="'+id+'"] [data-eye]').click(); return true}""",did); pg.wait_for_timeout(1500)
        pg.evaluate("document.querySelectorAll('#epChips .chip')[1].click()"); pg.wait_for_timeout(1500)
        print(did,'à l\'oculaire :',ok)
        pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(400)
    print('images du ciel demandées :',[r for r in reqs if r.startswith(('NGC_4565','M79'))])
    # fiche d'étoile (table jusqu'à la magnitude 9)
    pg.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); pg.wait_for_timeout(1500)
    hits=pg.evaluate("window.__hits()"); print('étoiles touchables à l\'oculaire :',len(hits))
    if hits:
        h=sorted(hits,key=lambda h:-h['m'])[0]
        xy=pg.evaluate("(()=>{const s=document.getElementById('eyeSvg'); const pt=s.createSVGPoint(); pt.x=%f; pt.y=%f; const q=pt.matrixTransform(s.getScreenCTM()); return [q.x,q.y]})()"%(h['sx'],h['sy']))
        pg.mouse.click(xy[0],xy[1]); pg.wait_for_timeout(4000)
        print('fiche (magnitude %.1f) : %s | table : %s étoiles'%(h['m'],pg.evaluate("document.getElementById('eyeStarInfo').textContent")[:150],pg.evaluate("window.__SI()")))
    print('Paramètres écran :',pg.evaluate("(()=>{const b=document.getElementById('scrRot'); return b?[b.textContent,document.getElementById('scrFull').textContent]:null})()"))
    print('erreurs JS :',errs[:3]); b.close()
