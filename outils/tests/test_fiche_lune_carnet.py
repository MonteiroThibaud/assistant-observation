#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du bouton du carnet de la fiche d'une formation de la Lune : en haut de la fiche, entre le nom et la croix, libellé « + Noter », mêmes caractéristiques que les boutons des autres onglets.
Usage : python3 test_fiche_lune_carnet.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read(); k=s.index("  $('featClose').onclick=")
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write((s[:k]+"  window.__show=showFeat;\n"+s[k:]).replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8883),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
tz=datetime.timezone(datetime.timedelta(hours=1))
MES="""()=>{ const c=document.getElementById('featCard'), hd=c.querySelector('.feathead'), nm=document.getElementById('featName'), lg=document.querySelector('#featLogBox .logbtn'), x=document.getElementById('featClose');
  const R=e=>{const r=e.getBoundingClientRect(); return {x:r.x,r:r.right,w:r.width,h:r.height,cy:(r.top+r.bottom)/2}}; const st=e=>{const q=getComputedStyle(e); return [q.fontSize,q.fontFamily,q.paddingTop,q.paddingBottom,q.paddingLeft,q.paddingRight,q.lineHeight,q.minHeight].join('|')};
  const ordre=[...hd.children].map(e=>e.id||e.tagName);
  return {vis:!c.hidden,ordre,nom:R(nm),log:R(lg),x:R(x),txt:lg.textContent,titre:lg.title,st:st(lg),coupe:lg.scrollWidth>lg.clientWidth+1,deb:hd.scrollWidth>hd.clientWidth+1,logEnBas:!!c.querySelector(':scope > #featLogBox'),sonde:(()=>{const h=document.createElement('div'); h.innerHTML='<div class="finderbox"><div class="findhead"><button class="ghost nowbtn" id="sNow">Maintenant</button></div></div>'; document.body.appendChild(h); const v=st(document.getElementById('sNow')), r=R(document.getElementById('sNow')); h.remove(); return {v,r}})()} }"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for (w,h,dpr) in ((411,850,2.625),(360,780,3),(320,568,2)):
        c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=datetime.datetime(2026,11,21,21,30,tzinfo=tz)); pg.goto('http://localhost:8883/index.html'); pg.wait_for_timeout(7000)
        pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(3500)
        tag='%dx%d'%(w,h)
        for nom in ('Tycho','Rimae Triesnecker','Montes Apenninus'):
            pg.evaluate("(n)=>window.__show(n)",nom); pg.wait_for_timeout(1200); m=pg.evaluate(MES)
            if not m['vis']: check('(%s) fiche de %s ouverte'%(tag,nom),False,m); continue
            check('(%s, %s) en-tête : nom, bouton du carnet, croix (dans cet ordre) ; plus de bouton sous la fiche'%(tag,nom),m['ordre']==['featName','featLogBox','featClose'] and not m['logEnBas'],m['ordre'])
            check('(%s, %s) le bouton est entre le nom et la croix, sans chevauchement'%(tag,nom),m['nom']['r']<=m['log']['x']+1 and m['log']['r']<=m['x']['x']+1,(round(m['nom']['r']),round(m['log']['x']),round(m['log']['r']),round(m['x']['x'])))
            check('(%s, %s) libellé « + Noter », texte entier, en-tête sans débordement'%(tag,nom),m['txt']=='+ Noter' and not m['coupe'] and not m['deb'],m)
            check('(%s, %s) mêmes police, marges et hauteur de ligne que « Maintenant » du ciel profond, même hauteur'%(tag,nom),m['st']==m['sonde']['v'] and abs(m['log']['h']-m['sonde']['r']['h'])<0.6,(m['st'],m['sonde']['v'],m['log']['h'],m['sonde']['r']['h']))
            check('(%s, %s) le bouton et la croix sont alignés verticalement'%(tag,nom),abs(m['log']['cy']-m['x']['cy'])<=3,(round(m['log']['cy'],1),round(m['x']['cy'],1)))
        pg.evaluate("(n)=>window.__show(n)",'Tycho'); pg.wait_for_timeout(1000); pg.click('#featLogBox .logbtn'); pg.wait_for_timeout(400)
        m2=pg.evaluate(MES); n=pg.evaluate("JSON.parse(localStorage.getItem('carnet')||'[]').filter(e=>e.kind==='lune'&&e.name==='Tycho').length")
        check('(%s) après avoir noté : « ✓ HH:MM », sans coupure, entrée dans le carnet'%tag,m2['txt'].startswith('✓ ') and not m2['coupe'] and not m2['deb'] and n==1,(m2['txt'],n))
        pg.evaluate("(n)=>window.__show(n)",'Mare Crisium'); pg.wait_for_timeout(600); pg.evaluate("(n)=>window.__show(n)",'Tycho'); pg.wait_for_timeout(1000); m3=pg.evaluate(MES)
        check('(%s) fiche rouverte : « ✓ Observée », info-bulle « Déjà observée »'%tag,m3['txt']=='✓ Observée' and 'Déjà observée' in m3['titre'],(m3['txt'],m3['titre']))
        check('(%s) aucune erreur JavaScript'%tag,not errs,errs[:1]); c.close()
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
