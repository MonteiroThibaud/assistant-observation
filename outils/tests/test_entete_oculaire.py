#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Test de l'en-tête de l'onglet « À l'oculaire » : le nom de l'objet, son étoile et les deux boutons (« Maintenant », « + Noter dans le carnet »).
# Contrôles : boutons de même largeur et alignés, texte des boutons entier, étoile jamais sous les boutons (police normale et agrandie), pas de défilement horizontal à police normale.
# Usage : python3 test_entete_oculaire.py DOSSIER_DU_SITE_INSTALLE
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read(); k=s.index("  $('featClose').onclick=")
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write((s[:k]+"  window.__eyeSel=id=>{ eyeSel='dso:'+id; drawEye(); showTab('eye') };\n"+s[k:]).replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8881),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
tz=datetime.timezone(datetime.timedelta(hours=1))
MESURE="""()=>{ const R=e=>{const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,r:r.right}};
  const st=document.querySelector('#eyeObj .starbtn'), now=document.getElementById('eyeNow'), log=document.querySelector('#eyeLog .logbtn'), col=document.querySelector('.objact');
  const sr=st?R(st):null, c=R(col);
  return {ecart:sr?sr.x+sr.w/2+10.4-c.x:-99, wNow:R(now).w, wLog:R(log).w, xNow:R(now).x, xLog:R(log).x, coupe:[now.scrollWidth>now.clientWidth+1,log.scrollWidth>log.clientWidth+1], defile:document.documentElement.scrollWidth>document.documentElement.clientWidth, lignes:Math.round(document.getElementById('eyeObj').getBoundingClientRect().height/parseFloat(getComputedStyle(document.getElementById('eyeObj')).lineHeight||24))} }"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for (w,h,dpr) in ((411,850,2.625),(360,780,3),(320,568,2),(891,411,2.625)):
        c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,is_mobile=w<600,has_touch=w<600,timezone_id='Europe/Paris',locale='fr-FR'); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,11,21,21,30,tzinfo=tz)); pg.goto('http://localhost:8881/index.html'); pg.wait_for_timeout(7000)
        for echelle in (1.0,1.15):
            pg.evaluate("(s)=>{document.documentElement.style.fontSize=(16*s)+'px'}",echelle)
            for obj in ('M31','NGC 6992','IC 1396'):
                pg.evaluate("(k)=>window.__eyeSel(k)",obj); pg.wait_for_timeout(1000); m=pg.evaluate(MESURE); lab='%dx%d, police %d %%, %s'%(w,h,echelle*100,obj)
                ok=abs(m['wNow']-m['wLog'])<0.6 and abs(m['xNow']-m['xLog'])<0.6 and not any(m['coupe']) and m['ecart']<0
                check('en-tête : '+lab,ok,'' if ok else m)
            st=pg.evaluate("""()=>{ const h=document.createElement('div'); h.innerHTML='<div class="finderbox"><div class="findhead"><button class="ghost nowbtn" id="sondeNow">Maintenant</button></div></div>'; document.body.appendChild(h); const g=e=>{const c=getComputedStyle(e); return [c.fontSize,c.paddingTop,c.paddingRight,c.paddingBottom,c.paddingLeft,c.minHeight,c.borderRadius,c.fontWeight].join(' | ')}; const sz=e=>{const r=e.getBoundingClientRect(); return [Math.round(r.width*10)/10,Math.round(r.height*10)/10]}; const sonde=document.getElementById('sondeNow'), now=document.getElementById('eyeNow'), log=document.querySelector('#eyeLog .logbtn'), carte=document.getElementById('mapNow'); const r={ciel:g(sonde),now:g(now),log:g(log),carte:g(carte),tSonde:sz(sonde),tNow:sz(now),tLog:sz(log),txt:log.textContent,coupe:log.scrollWidth>log.clientWidth+1}; h.remove(); return r }""")
            ok=st['ciel']==st['now']==st['log']==st['carte'] and abs(st['tSonde'][0]-st['tNow'][0])<0.6 and abs(st['tSonde'][1]-st['tNow'][1])<0.6 and abs(st['tNow'][0]-st['tLog'][0])<0.6 and abs(st['tNow'][1]-st['tLog'][1])<0.6 and not st['coupe']
            check('boutons « Maintenant » et carnet : mêmes police, marges et taille que « Maintenant » du ciel profond ; bouton de la Lune : mêmes caractéristiques (%dx%d, police %d %%, %s)'%(w,h,echelle*100,obj),ok,'' if ok else st)
            if echelle==1.0: check('pas de défilement horizontal (%dx%d, police normale)'%(w,h),not m['defile'],m['defile'])
        pg.evaluate("document.documentElement.style.fontSize='16px'"); pg.evaluate("(k)=>window.__eyeSel(k)",'M31'); pg.wait_for_timeout(800)
        pg.click('#eyeLog .logbtn'); pg.wait_for_timeout(400)
        n2=pg.evaluate("""()=>{ const l=document.querySelector('#eyeLog .logbtn'), n=document.getElementById('eyeNow'); return {txt:l.textContent,coupe:l.scrollWidth>l.clientWidth+1,wl:l.getBoundingClientRect().width,wn:n.getBoundingClientRect().width} }""")
        check('état « noté » (%dx%d) : libellé « ✓ HH:MM » sans coupure, même largeur que « Maintenant »'%(w,h),n2['txt'].startswith('✓ ') and not n2['coupe'] and abs(n2['wl']-n2['wn'])<0.6,n2)
        pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(600)
        lune=pg.evaluate("""()=>{ const r=document.getElementById('mapNow').getBoundingClientRect(); return {w:Math.round(r.width*10)/10,h:Math.round(r.height*10)/10} }""")
        pg.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); pg.wait_for_timeout(300)
        check('onglet Lune (%dx%d) : bouton « Maintenant » visible et de la hauteur de celui du ciel profond'%(w,h),lune['w']>40 and lune['h']<=36,lune)
        check('aucune erreur JavaScript (%dx%d)'%(w,h),not errs,errs[:1]); c.close()
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
