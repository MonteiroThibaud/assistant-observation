#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du message de position du téléphone (Paramètres, « Date et lieu ») avec une géolocalisation simulée : un échec en retard ne doit pas effacer un succès plus récent, le message donne la cause et la date de la dernière position, il n'apparaît pas quand une position récente existe ou quand un lieu mémorisé est utilisé, et il disparaît dès qu'une position est obtenue.
Usage : python3 test_message_position.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 2 minutes)"""
import sys, os, json, shutil, tempfile, threading, http.server, socketserver, time
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:200]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read()
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(s.replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8885),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
def mock(plan): return "window.__geo={calls:0}; navigator.geolocation.getCurrentPosition=(ok,err,opt)=>{ const st=(%s)[window.__geo.calls++]||{kind:'ok',delay:80}; setTimeout(()=>{ if(st.kind==='ok') ok({coords:{latitude:45.7578,longitude:4.8320,accuracy:40}}); else err({code:st.code||3,message:'simulé'}) },st.delay) };"%json.dumps(plan)
def scenario(b,plan,stored=None,sites=None,actions=None,duree=4):
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR')
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    init=mock(plan)
    if stored is not None: init+="localStorage.setItem('lastGps',%s);"%json.dumps(json.dumps(stored))
    if sites: init+="localStorage.setItem('issSites',%s); localStorage.setItem('activeLoc','\"sA\"'); localStorage.setItem('placesV','1');"%json.dumps(json.dumps(sites))
    pg.add_init_script(init); pg.goto('http://localhost:8885/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(400); pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)")
    t0=time.time(); log=[]
    for dt,act in (actions or []):
        pg.wait_for_timeout(max(0,int((dt-(time.time()-t0))*1000)))
        if act=='actualiser': pg.click('#geo')
        elif act.startswith('radio:'): pg.click('#placesList input[data-act="%s"]'%act[6:])
        log.append(act)
    pg.wait_for_timeout(max(0,int((duree-(time.time()-t0))*1000)))
    out={'msg':pg.evaluate("document.getElementById('msg').textContent"),'locText':pg.evaluate("document.getElementById('locText').textContent"),'appels':pg.evaluate("window.__geo.calls"),'errs':errs}
    c.close(); return out
with sync_playwright() as p:
    b=p.chromium.launch()
    # A : course : l'appel du démarrage échoue en retard (9 s après son lancement, donc après le succès) alors qu'un succès a été obtenu entre-temps par « Actualiser »
    r=scenario(b,[{'kind':'err','code':3,'delay':9000},{'kind':'ok','delay':300}],actions=[(1,'actualiser')],duree=11)
    check('A. un échec en retard n\'efface pas un succès plus récent : aucun message',r['msg']=='' and r['appels']==2,r)
    # B : échec sans position connue : cause et position par défaut
    r=scenario(b,[{'kind':'err','code':2,'delay':200}])
    check('B. échec sans position connue : cause et position par défaut dans le message',('position indisponible' in r['msg']) and ('position par défaut' in r['msg']),r['msg'])
    # C : échec avec une ancienne position : cause, dernière position connue et sa date
    old=int((time.time()-3*3600)*1000)
    r=scenario(b,[{'kind':'err','code':1,'delay':200}],stored={'lat':45.7578,'lon':4.8320,'src':'gps','t':old})
    check('C. échec avec une ancienne position : cause, « dernière position connue » et date',('accès à la localisation refusé' in r['msg']) and ('dernière position connue' in r['msg']) and ('obtenue le' in r['msg']),r['msg'])
    # D : échec automatique alors qu'une position de moins de 5 minutes existe : pas de message
    rec=int((time.time()-60)*1000)
    r=scenario(b,[{'kind':'err','code':3,'delay':200}],stored={'lat':45.7578,'lon':4.8320,'src':'gps','t':rec})
    check('D. échec automatique avec une position récente (moins de 5 minutes) : aucun message',r['msg']=='',r['msg'])
    # E : échec puis « Actualiser » réussi : le message disparaît
    r=scenario(b,[{'kind':'err','code':3,'delay':200},{'kind':'ok','delay':200}],actions=[(1.5,'actualiser')],duree=3.5)
    check('E. échec puis « Actualiser » réussi : le message disparaît et la position GPS est celle du téléphone',r['msg']=='' and '(position du téléphone)' in r['locText'],r)
    # F : échec, puis choix d'un lieu mémorisé : le message du téléphone disparaît
    sites=[{'id':'sA','name':'Alpha','lat':46.01,'lon':4.01,'kind':'coord','on':True,'alt':400}]
    r=scenario(b,[{'kind':'err','code':3,'delay':200},{'kind':'err','code':3,'delay':200}],stored={'lat':45.7578,'lon':4.8320,'src':'gps','t':old},sites=sites,actions=[(1.2,'radio:gps'),(2.6,'radio:sA')],duree=3.6)
    check('F. choix d\'un lieu mémorisé : plus de message sur le téléphone',r['msg']=='',r)
    # G : un lieu mémorisé utilisé au démarrage et un échec automatique : aucun message
    r=scenario(b,[{'kind':'err','code':3,'delay':200}],stored={'lat':45.7578,'lon':4.8320,'src':'gps','t':old},sites=sites)
    check('G. lieu mémorisé utilisé : un échec automatique du GPS n\'affiche rien',r['msg']=='',r['msg'])
    # H : « Actualiser » demandé par l'utilisateur qui échoue : message affiché même avec une position récente
    r=scenario(b,[{'kind':'ok','delay':100},{'kind':'err','code':3,'delay':200}],actions=[(1.2,'actualiser')],duree=2.8)
    check('H. « Actualiser » demandé et en échec : le message est affiché',('délai dépassé' in r['msg']) and ('dernière position connue' in r['msg']),r['msg'])
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
