# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de la carte de zone de l'ISS (application installée) : zoom arrière jusqu'à ×0,25, limites de départements sur toute la vue, couloirs prolongés.
Usage : python3 test_zone_carte.py ADRESSE  (le serveur de test doit tourner). Code de retour 0 si tout est réussi."""
import sys, datetime, re
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8870/index.html'
TLE="ISS (ZARYA)\n1 25544U 98067A   26316.88411739  .00007667  00000-0  14541-3 0  9993\n2 25544  51.6325 284.2547 0007335  19.0494 341.0767 15.49339933594804"; res=[]
tz=datetime.timezone(datetime.timedelta(hours=1))
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script("if(!localStorage.getItem('t0')){localStorage.setItem('placesV','1');localStorage.setItem('lastGps',JSON.stringify({lat:46.0345,lon:4.072,src:'gps'}));localStorage.setItem('t0','1')}")
    pg.clock.install(time=datetime.datetime(2026,11,14,22,0,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(7000)
    ev=lambda js: pg.evaluate(js)
    tab=lambda t:(ev("document.querySelector('.tabbar [data-tab=%s]').click()"%t),pg.wait_for_timeout(700))
    tab('loc'); ev("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); document.getElementById('impBox').open=true"); pg.wait_for_timeout(300)
    pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(800); pg.reload(); pg.wait_for_timeout(9000); tab('sys')
    for i in range(60):
        pg.wait_for_timeout(1000)
        if ev("!!document.getElementById('iszMapBox')"): break
    check('la carte de zone s\'affiche après le calcul automatique',ev("!!document.getElementById('iszMapBox')"))
    pg.wait_for_timeout(2500)
    ev("document.getElementById('iszMapBox').scrollIntoView({block:'center'})"); pg.wait_for_timeout(400)
    check('fond détaillé (communes) tracé',ev("(document.querySelector('#iszBase path')||{getAttribute:()=>''}).getAttribute('d').length>2000"))
    check('limites de départements du fichier tracées',ev("(document.querySelector('#iszDep path')||{getAttribute:()=>''}).getAttribute('d').length>500"))
    check('les limites du fichier ne sont pas retracées sous le fond détaillé (découpe)',ev("document.getElementById('iszDep').getAttribute('clip-path')==='url(#iszDepClip)'"))
    ev("document.getElementById('iszZoomReset').click()"); pg.wait_for_timeout(300)
    lab=[]
    for i in range(7): pg.click('#iszZoomOut'); pg.wait_for_timeout(200); lab.append(ev("document.getElementById('iszZoomLbl').textContent"))
    check('zoom arrière : ×0,67 puis ×0,44, ×0,3 et plafond à ×0,25',lab[:4]==['×0,67','×0,44','×0,3','×0,25'] and set(lab[3:])=={'×0,25'},lab)
    vb=[float(x) for x in ev("document.querySelector('#iszMapBox svg').getAttribute('viewBox')").split()]
    check('vue la plus large : 1 200 unités (4 fois la vue de départ)',abs(vb[2]-1200)<1 and abs(vb[3]-1200)<1,vb)
    # couverture : des limites dans les quatre quarts de la vue
    d=ev("document.querySelector('#iszDep path').getAttribute('d')"); pts=[tuple(map(float,m)) for m in re.findall(r'[ML]([-\d.]+) ([-\d.]+)',d)]
    cx,cy=vb[0]+vb[2]/2,vb[1]+vb[3]/2; quart={(a,b):0 for a in (True,False) for b in (True,False)}
    for x,y in pts:
        if vb[0]<=x<=vb[0]+vb[2] and vb[1]<=y<=vb[1]+vb[3]: quart[(x<cx,y<cy)]=quart.get((x<cx,y<cy),0)+1
    check('limites de départements dans les quatre quarts de la vue à ×0,25',all(v>20 for v in quart.values()),quart)
    # couloirs : chaque extrémité est au-delà des coins de la vue
    ext=ev("(()=>{const L=[...document.querySelectorAll('#iszMapBox line.iszc')]; return L.map(l=>[+l.getAttribute('x1'),+l.getAttribute('y1'),+l.getAttribute('x2'),+l.getAttribute('y2')])})()")
    demi=((vb[2]/2)**2+(vb[3]/2)**2)**.5
    ok=bool(ext) and all(min(((x1-cx)**2+(y1-cy)**2)**.5,((x2-cx)**2+(y2-cy)**2)**.5)>=demi*0.99 for x1,y1,x2,y2 in ext)
    check('couloirs prolongés au-delà des coins de la vue à ×0,25 (%d couloirs)'%len(ext),ok,[round(min(((x1-cx)**2+(y1-cy)**2)**.5,((x2-cx)**2+(y2-cy)**2)**.5)) for x1,y1,x2,y2 in ext][:4])
    pg.wait_for_timeout(500); fl=ev("document.querySelectorAll('#iszArr path').length")
    check('flèches de sens le long des couloirs dans la vue large',fl>5,fl)
    pg.screenshot(path='/tmp/zone-025.png')
    check('aucune erreur JavaScript',not errs,errs[:1] or 'aucune')
    b.close()
ok=all(res); print('\nBILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if ok else 1)
