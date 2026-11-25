# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in ((411,850),(360,780),(320,568)):
        c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8880/index.html'); pg.wait_for_timeout(8000)
        pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(600)
        pg.evaluate("document.querySelector('#deepFilter [data-f=\"all\"]').click()"); pg.wait_for_timeout(300)
        r=pg.evaluate("""()=>{const e=document.querySelector('#deepList [data-dso]'); if(!e) return null; if(!e.classList.contains('open')) e.querySelector('.dhead').click(); return e.dataset.dso}""")
        pg.wait_for_timeout(900)
        g=pg.evaluate("""()=>{const hd=document.querySelector('#deepList .finderbox .findhead'); if(!hd) return null; hd.scrollIntoView({block:'center'}); const par=hd.getBoundingClientRect(); const kids=[...hd.children].map(k=>{const q=k.getBoundingClientRect(); return [k.tagName+(k.className?'.'+String(k.className).split(' ')[0]:''),Math.round(q.top),Math.round(q.left),Math.round(q.right)]}); return {objet:null,conteneur:[Math.round(par.left),Math.round(par.right)],enfants:kids,debordement:hd.scrollWidth>hd.clientWidth+1}}""")
        print('%d × %d : objet %s | ligne : %s'%(w,h,r,g)); 
        if w==360: pg.screenshot(path='/tmp/ciel_profond_ligne.png')
        # appui sur Maintenant dans la ligne
        pg.click('#deepList .finderbox .findhead .nowbtn'); pg.wait_for_timeout(1200)
        print('   après appui : aria-pressed =',pg.evaluate("document.querySelector('#deepList .finderbox .findhead .nowbtn').getAttribute('aria-pressed')"),'| texte d\'aide :',pg.evaluate("(document.querySelector('#deepList .finderhelp')||{}).textContent").split('.')[0][:60],'| erreurs',errs[:1])
        c.close()
    # fiche de la Lune plus haute
    c=b.new_context(viewport={'width':360,'height':780},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8880/index.html'); pg.wait_for_timeout(8000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(5000)
    pg.evaluate("window.__show('Tycho')"); pg.wait_for_timeout(1200)
    r=pg.evaluate("(()=>{const f=document.getElementById('featCard').getBoundingClientRect(), m=document.getElementById('mapBox').getBoundingClientRect(), z=document.querySelector('.mapctl').getBoundingClientRect(); return {carteHaut:Math.round(m.top),carteBas:Math.round(m.bottom),ficheHaut:Math.round(f.top),ficheBas:Math.round(f.bottom),boutonsZoomHaut:Math.round(z.top),hauteurFiche:Math.round(f.height),margeHaut:Math.round(f.top-m.top),margeBasAuxBoutons:Math.round(z.top-f.bottom)}})()")
    print('fiche de Tycho (360 × 780) :',r)
    pg.screenshot(path='/tmp/fiche_haute.png'); print('erreurs JS :',errs[:2]); b.close()
