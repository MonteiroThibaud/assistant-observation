#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de la carte de la Lune en mode « Explications allégées » : le cadre devient un rectangle vertical qui récupère la hauteur de l'aide masquée, la Lune entière y est centrée, la couche haute définition couvre tout le cadre ; rien ne change en paysage ; retour au carré en mode détaillé.
Usage : python3 test_lune_allegee_hauteur.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 1 minute 30)"""
import sys, os, re, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:260]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8901),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,14,0,tzinfo=datetime.timezone.utc)
def ouvre(b,W,Hh):
    c=b.new_context(viewport={'width':W,'height':Hh},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8901/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500); return c,pg,errs
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(1500)
MES="""()=>{ const b=document.getElementById('mapBox'), r=b.getBoundingClientRect(), tb=document.querySelector('.tabbar').getBoundingClientRect(), lg=document.querySelector('#tab-moon .legend'), tr=document.getElementById('mapCanvas').style.transform; const m=tr.match(/translate\\(([-\\d.]+)px,\\s*([-\\d.]+)px\\)/); const mc=document.getElementById('mapCanvas').getBoundingClientRect(); return {W:Math.round(b.clientWidth), H:Math.round(b.clientHeight), bas:Math.round(r.bottom), barre:Math.round(tb.top), legende:!!(lg&&lg.offsetParent), legH:lg&&lg.offsetParent?Math.round(lg.offsetHeight):0, ty:m?parseFloat(m[2]):null, tx:m?parseFloat(m[1]):null, canvasCote:Math.round(mc.width), label:document.getElementById('zoomReset').textContent.trim(), haut:Math.round(r.top+scrollY), li:parseFloat(getComputedStyle(document.getElementById('moonInfo')).lineHeight)||22, mt:parseFloat(getComputedStyle(document.getElementById('moonInfo')).marginTop)||0, infoHaut:Math.round(document.getElementById('moonInfo').getBoundingClientRect().top)} }"""
with sync_playwright() as p:
    b=p.chromium.launch(); c,pg,errs=ouvre(b,411,780); tab(pg,'moon')
    a=pg.evaluate(MES)
    check('mode détaillé (411 × 780) : cadre carré, aide de la carte visible',abs(a['W']-a['H'])<=1 and a['legende'],a)
    pg.evaluate("document.getElementById('detailBtn').click()"); pg.wait_for_timeout(1200); z=pg.evaluate(MES)
    check('mode allégé (écran de 780 points de haut) : le cadre devient un rectangle vertical (hauteur > largeur), changement immédiat sans quitter l\'onglet',z['H']>z['W']+8 and not z['legende'],z)
    avail=z['barre']-z['haut']; attendu=max(z['W'],min(z['W']+a['legH'],avail-z['mt']-3*z['li'])); check('la hauteur du cadre est celle de l\'aide masquée (ou de l\'espace libre), qui laisse la place de la ligne vide et de trois lignes de texte (à 2 points près)',abs(z['H']-attendu)<=2,(z['H'],round(attendu),z['li']))
    check('trois lignes du texte d\'information (après la ligne vide) sont entièrement visibles au-dessus de la barre d\'onglets',z['infoHaut']+3*z['li']<=z['barre']+2 and z['infoHaut']-z['bas']>=z['li']-2,(z['bas'],z['barre'],z['infoHaut'],z['li'],z['mt']))
    check('une ligne vide sépare la carte du texte d\'information, en mode détaillé comme en mode allégé',abs((a['infoHaut']-a['bas'])-a['li'])<=3 and abs((z['infoHaut']-z['bas'])-z['li'])<=3,(a['infoHaut']-a['bas'],z['infoHaut']-z['bas'],z['li']))
    check('la Lune entière (carré de la largeur du cadre) est centrée en hauteur ; bouton « Recentrer »',abs(z['canvasCote']-z['W'])<=2 and abs(z['ty']-(z['H']-z['W'])/2)<=1.5 and z['label']=='Recentrer',z)
    # zoom : la couche haute définition couvre tout le cadre
    for _ in range(4): pg.click('#zoomIn'); pg.wait_for_timeout(250)
    try: pg.wait_for_function("document.getElementById('mapHi').classList.contains('on')",timeout=40000)
    except Exception: pass
    pg.wait_for_timeout(3500)
    h=pg.evaluate("""()=>{ const c=document.getElementById('mapHi'), box=document.getElementById('mapBox'); const g=c.getContext('2d'); const w=c.width, hh=c.height; const sc=w/Math.max(box.clientWidth,box.clientHeight); const y0=Math.floor((box.clientHeight*0.82)*sc), y1=Math.floor((box.clientHeight*0.92)*sc); const d=g.getImageData(0,y0,Math.min(w,Math.floor(box.clientWidth*sc)),Math.max(1,y1-y0)).data; let n=0; for(let i=3;i<d.length;i+=4) if(d[i]>0) n++; return {actif:c.classList.contains('on'), cote:Math.round(c.getBoundingClientRect().height), cadreH:box.clientHeight, pixelsBas:n} }""")
    check('zoomé : la couche haute définition est active, aussi haute que le cadre, et peinte dans sa partie basse',h['actif'] and h['cote']>=h['cadreH']-2 and h['pixelsBas']>1000,h)
    pg.evaluate("document.getElementById('detailBtn').click()"); pg.wait_for_timeout(1200); d=pg.evaluate(MES)
    check('retour au mode détaillé : le cadre redevient carré et l\'aide réapparaît',abs(d['W']-d['H'])<=1 and d['legende'],d)
    check('aucune erreur JavaScript (portrait)',not errs,errs[:1]); c.close()
    # écran plus haut (850 points) : le gain est plus grand et trois lignes restent lisibles
    c,pg,errs=ouvre(b,411,850); tab(pg,'moon'); pg.evaluate("document.getElementById('detailBtn').click()"); pg.wait_for_timeout(1500); g=pg.evaluate(MES)
    check('écran de 850 points de haut, mode allégé : cadre nettement plus haut que large et trois lignes de texte entièrement visibles',g['H']>g['W']+30 and g['infoHaut']+3*g['li']<=g['barre']+2,(g['W'],g['H'],g['infoHaut'],g['li'],g['barre']))
    check('aucune erreur JavaScript (850)',not errs,errs[:1]); c.close()
    # paysage : rien ne change
    c,pg,errs=ouvre(b,891,411); tab(pg,'moon'); a=pg.evaluate(MES); pg.evaluate("document.getElementById('detailBtn').click()"); pg.wait_for_timeout(1200); z=pg.evaluate(MES)
    check('paysage (891 × 411) : la hauteur du cadre ne change pas en mode allégé, et aucune ligne vide n\'est ajoutée (grille)',abs(a['H']-z['H'])<=1 and a['H']<=a['W'] and a['mt']==0,(a['W'],a['H'],z['H'],a['mt']))
    check('aucune erreur JavaScript (paysage)',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
