#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de la Lune à l'oculaire à fort grossissement : avec l'oculaire de 5 mm (Hyperion, 68°) et une barlow ×2 (×600) la Lune doit être dessinée (et non remplacée par un disque blanc), de même avec une barlow plus forte ; au-delà de la limite de rendu, un message le dit sur l'image (essayé sur une copie dont la limite est abaissée).
Usage : python3 test_lune_oculaire_fort_grossissement.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 1 minute 30)"""
import sys, os, json, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:220]) if detail!='' else ''),flush=True)
def prepare(limite=None):
    T=tempfile.mkdtemp()
    for n in os.listdir(SITE):
        if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
    s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",'')
    if limite: assert s.count("const EYE_MOON_MAX=20000;")==1; s=s.replace("const EYE_MOON_MAX=20000;","const EYE_MOON_MAX=%d;"%limite)
    open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(s); return T
def serve(T,port):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
        def log_message(self,*a): pass
    class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
    srv=S(('127.0.0.1',port),H); threading.Thread(target=srv.serve_forever,daemon=True).start(); return srv
INFO="""(()=>{const t=document.getElementById('eyeInfo').textContent, img=document.querySelector('#mSlot image'); let sd=null, moy=null;
  if(img){ const im=new Image(); im.src=img.getAttribute('href'); const c=document.createElement('canvas'); c.width=300; c.height=300; const g=c.getContext('2d'); g.drawImage(im,0,0,300,300); const d=g.getImageData(0,0,300,300).data; let s=0,s2=0,n=0; for(let i=0;i<d.length;i+=4){ if(d[i+3]>200){ const v=(d[i]+d[i+1]+d[i+2])/3; s+=v; s2+=v*v; n++ } } moy=s/n; sd=Math.sqrt(Math.max(0,s2/n-moy*moy)) }
  return {gros:+(((t.match(/grossissement ×([\\d\\s\\u202f\\u00a0]+)/)||[])[1]||'0').replace(/[^\\d]/g,'')), image:!!img, placeholder:!!document.querySelector('#mPh circle, #mPh path, #mPh ellipse'), message:!!document.querySelector('.moonwarn'), sd:sd&&Math.round(sd), moy:moy&&Math.round(moy)}})()"""
def vue(pg,barlow):
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(300); pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)")
    pg.fill('#bl1n','Powermate'); pg.fill('#bl1m',str(barlow)); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); pg.wait_for_timeout(1500)
def ouvre(b,port):
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR')
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); d=datetime.datetime(2026,11,20,21,0,tzinfo=datetime.timezone.utc); pg.clock.install(time=d); pg.clock.set_fixed_time(d)
    pg.goto('http://localhost:%d/index.html'%port); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3000); return c,pg,errs
T1=prepare(); T2=prepare(900); s1=serve(T1,8887); s2=serve(T2,8888)
with sync_playwright() as p:
    b=p.chromium.launch()
    c,pg,errs=ouvre(b,8887); vue(pg,2)
    pg.click('button[data-ep=h5]'); pg.wait_for_timeout(4500); i=pg.evaluate(INFO)
    check('5 mm sans barlow (×300) : la Lune est dessinée, avec du relief visible',i['gros']==300 and i['image'] and not i['placeholder'] and (i['sd'] or 0)>8,i)
    pg.click('button[data-ep=h5]'); pg.wait_for_timeout(5500); i=pg.evaluate(INFO)
    check('5 mm avec la barlow ×2 (×600) : la Lune est dessinée (et non un disque blanc)',i['gros']==600 and i['image'] and not i['placeholder'] and not i['message'] and (i['sd'] or 0)>8 and (i['moy'] or 255)<235,i)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(300); pg.fill('#bl1m','4'); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); pg.wait_for_timeout(6500); i=pg.evaluate(INFO)   # la barlow 1 reste choisie : le grossissement passe à ×1200
    check('grossissement encore plus fort (barlow ×4 : ×1200) : la Lune est dessinée',i['gros']>=1200 and i['image'] and not i['placeholder'] and (i['sd'] or 0)>5,i)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close()
    c,pg,errs=ouvre(b,8888); vue(pg,2)
    pg.click('button[data-ep=h5]'); pg.wait_for_timeout(4500); i=pg.evaluate(INFO)
    check('copie à limite abaissée, ×300 : pas de message, la Lune est dessinée',i['image'] and not i['message'],i)
    pg.click('button[data-ep=h5]'); pg.wait_for_timeout(4500); i=pg.evaluate(INFO)
    msg=pg.evaluate("(document.querySelector('.moonwarn')||{}).textContent||''")
    check('copie à limite abaissée, ×600 : le message « trop élevé » est affiché sur l\'image et le grossissement y figure',i['message'] and not i['image'] and 'trop élevé' in msg and '×600' in msg,msg)
    c.close(); b.close()
s1.shutdown(); s2.shutdown(); shutil.rmtree(T1,ignore_errors=True); shutil.rmtree(T2,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
