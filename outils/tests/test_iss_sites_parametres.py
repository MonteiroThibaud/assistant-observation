# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des lieux et du tableau des transits de l'ISS (Paramètres, « Date et lieu » et « Transits de l'ISS »).
Usage : python3 test_iss_sites_parametres.py [ADRESSE_DE_LA_PAGE]   (par défaut http://localhost:8870/index.html : application installée,
la recherche de commune n'existe que dans l'application installée). Le serveur de test doit tourner. Code de retour 0 si tout est réussi.
Aucun crochet de test dans la page : seules l'interface et la mémoire du navigateur (clé issSites) sont lues."""
import sys, datetime, time, json
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8870/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1))
TLE="ISS (ZARYA)\n1 25544U 98067A   26316.88411739  .00007667  00000-0  14541-3 0  9993\n2 25544  51.6325 284.2547 0007335  19.0494 341.0767 15.49339933594804"
res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,11,14,22,0,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(8000)
    ev=lambda js: pg.evaluate(js)
    sites=lambda: ev("JSON.parse(localStorage.getItem('issSites')||'[]').map(s=>({name:s.name,lat:s.lat,lon:s.lon,kind:s.kind,alt:s.alt}))")
    msg=lambda: ev("document.getElementById('issSiteMsg').textContent")
    def formulaire():      # après un ajout réussi, l'application revient à l'onglet de résultats et referme le formulaire : on le rouvre
        ev("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400)
        ev("document.getElementById('locBox').open=true; document.getElementById('issSitesBox').open=true; document.getElementById('manual').hidden=false"); pg.wait_for_timeout(250)
    formulaire()
    check('sans éléments orbitaux : message d\'aide','Aucun élément orbital' in ev("document.getElementById('issSitesTle').textContent"))
    ev("document.getElementById('impBox').open=true"); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(600); formulaire()
    check('avec éléments orbitaux : date de l\'époque','Éléments orbitaux du 12 novembre 2026' in ev("document.getElementById('issSitesTle').textContent"),ev("document.getElementById('issSitesTle').textContent")[:70])
    # ajout par coordonnées, virgule décimale
    pg.fill('#issSiteName','Roanne test'); pg.fill('#issSiteCoord','46,0345 ; 4,0720'); pg.click('#issSiteAdd'); pg.wait_for_timeout(600)
    s=sites(); check('ajout par coordonnées (virgule décimale)',len(s)==1 and s[0]['name']=='Roanne test' and abs(s[0]['lat']-46.0345)<1e-6 and abs(s[0]['lon']-4.072)<1e-6 and s[0]['alt']==400,s)
    # coordonnées invalides
    formulaire(); pg.fill('#issSiteName','Invalide'); pg.fill('#issSiteCoord','95 ; 4'); pg.click('#issSiteAdd'); pg.wait_for_timeout(400)
    check('coordonnées invalides refusées, message affiché',len(sites())==1 and len(msg())>10,repr(msg()[:80]))
    # position GPS
    pg.fill('#issSiteCoord',''); pg.fill('#issSiteName',''); pg.click('#issSitePos'); pg.wait_for_timeout(400)
    v=ev("[document.getElementById('issSiteName').value,document.getElementById('issSiteCoord').value]")
    check('« Ma position GPS » remplit les coordonnées','46.03' in v[1] and '4.07' in v[1],v)
    # recherche de commune (application installée)
    pg.fill('#issSiteQ','Charlieu'); pg.wait_for_timeout(2500); sug=ev("[...document.querySelectorAll('#issSiteSug button')].map(b=>b.textContent)")
    check('recherche « Charlieu » : suggestion trouvée (application installée)',any('Charlieu' in x for x in sug),sug[:3])
    pg.fill('#issSiteQ','Lyon'); pg.wait_for_timeout(1500)
    if ev("document.querySelectorAll('#issSiteSug button').length"):
        pg.click('#issSiteSug button >> nth=0'); pg.wait_for_timeout(700)
        v=ev("[document.getElementById('issSiteName').value,document.getElementById('issSiteCoord').value,document.getElementById('issSiteAlt').value]")
        check('choix d\'une commune : nom et coordonnées remplis','Lyon' in v[0] and v[1].startswith('45.7'),v)
        pg.click('#issSiteAdd'); pg.wait_for_timeout(900); s=sites()
        check('commune mémorisée (altitude par défaut : 400 m)',len(s)==2 and s[1]['name'].startswith('Lyon') and s[1]['alt']==400 and s[1]['kind']=='commune',s[1:])
    else: check('choix d\'une commune',False,'aucune suggestion pour « Lyon »')
    # deuxième lieu par coordonnées, avec altitude
    formulaire(); pg.fill('#issSiteName','Site du club'); pg.fill('#issSiteCoord','46,2 ; 4,3'); pg.fill('#issSiteAlt','420'); pg.click('#issSiteAdd'); pg.wait_for_timeout(600)
    s=sites(); check('lieu avec altitude saisie',len(s)==3 and s[2]['name']=='Site du club' and s[2]['alt']==420,s[2:])
    # six lieux au plus
    for i in range(3):
        formulaire(); pg.fill('#issSiteName','Lieu %d'%(i+4)); pg.fill('#issSiteCoord','46.%d ; 4.%d'%(i+3,i+4)); pg.click('#issSiteAdd'); pg.wait_for_timeout(500)
    check('six lieux mémorisés au plus',len(sites())==6,len(sites()))
    formulaire(); pg.fill('#issSiteName','Septième'); pg.fill('#issSiteCoord','46.9 ; 4.9'); pg.click('#issSiteAdd'); pg.wait_for_timeout(500)
    check('un septième lieu est refusé avec un message',len(sites())==6 and len(msg())>5,repr(msg()[:90]))
    # tableau des transits : le lieu utilisé puis les lieux cochés
    ev("document.querySelector('.tabbar [data-tab=sys]').click()"); t0=time.time(); n=0
    for i in range(120):
        pg.wait_for_timeout(1000); n=ev("document.querySelectorAll('#issSitesTable .issc').length"); busy=ev("(()=>{const e=document.getElementById('issSitesProg'); return !!(e&&e.textContent.trim())})()")
        if n>=4 and not busy and i>3: break
    titres=ev("[...document.querySelectorAll('#issSitesTable .isssite, #issSitesTable h4')].map(e=>e.textContent.trim().slice(0,28))")
    check('tableau calculé (%.1f s)'%(time.time()-t0),n>=4,'%d cartes de transit'%n)
    check('aucune erreur JavaScript',not errs,errs[:1] or 'aucune')
    b.close()
ok=all(res); print('\nBILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if ok else 1)
