#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des trois optiques de chercheur (droit, coudé simple, redressé) : choix dans Paramètres, texte de l'oculaire, transformation de l'image (rotation de 180° pour le droit, miroir pour le coudé), anciens réglages, Enregistrer, Restituer et Défaut.
Usage : python3 test_chercheur_optiques.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 1 minute 30)"""
import sys, os, re, json, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:240]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8893),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,20,0,tzinfo=datetime.timezone.utc)
def ouvre(b,init=''):
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    if init: pg.add_init_script(init)
    pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8893/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3500); return c,pg,errs
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(600)
def regle(pg,opt):
    tab(pg,'loc'); pg.evaluate("(o)=>{ for(let d=document.getElementById('fiBox');d;d=d.parentElement&&d.parentElement.closest('details')) d.open=true; const s=document.getElementById('fiInv'); s.value=o; s.dispatchEvent(new Event('change')) }",opt); pg.wait_for_timeout(300)
def vue(pg):
    tab(pg,'eye'); pg.evaluate("document.querySelector('button[data-ep=finder]').click()"); pg.wait_for_timeout(900)
    return pg.evaluate("""()=>{ const g=[...document.querySelectorAll('#tab-eye svg g[transform]')].map(x=>x.getAttribute('transform')).find(x=>/^translate\\([^)]*\\)\\s*rotate\\(/.test(x)); const m=g&&g.match(/rotate\\((-?[\\d.]+)\\)(\\s*scale\\(-1,\\s*1\\))?/); return {phi:m?+m[1]:null, mir:!!(m&&m[2]), info:document.getElementById('eyeInfo').textContent.slice(0,260)}}""")
def mod(x): return ((x%360)+360)%360
with sync_playwright() as p:
    b=p.chromium.launch(); c,pg,errs=ouvre(b)
    opts=pg.evaluate("[...document.getElementById('fiInv').options].map(o=>o.value+'|'+o.textContent)")
    check('le menu Chercheur propose trois optiques : droit, coudé simple, redressé',[o.split('|')[0] for o in opts]==['droit','coude','redresse'] and 'Coudé simple' in opts[1],opts)
    check('optique par défaut : droite (image inversée et renversée)',pg.evaluate("document.getElementById('fiInv').value")=='droit')
    V={}
    for o in ('redresse','droit','coude'): regle(pg,o); V[o]=vue(pg)
    check('redressé : texte « redressée (zénith en haut) », sans miroir',('redressée' in V['redresse']['info']) and not V['redresse']['mir'] and V['redresse']['phi'] is not None,V['redresse'])
    check('droit : texte « inversée … renversée », sans miroir, tourné de 180° par rapport au redressé',('renversée' in V['droit']['info']) and not V['droit']['mir'] and abs(mod(V['droit']['phi']-V['redresse']['phi'])-180)<0.1,(V['droit'],V['redresse']['phi']))
    check('coudé simple : texte « inversée de droite à gauche seulement », miroir, angle opposé à celui du redressé',('droite à gauche seulement' in V['coude']['info']) and V['coude']['mir'] and abs(mod(V['coude']['phi']+V['redresse']['phi']))<0.1,(V['coude'],V['redresse']['phi']))
    # Enregistrer, Restituer, Défaut
    regle(pg,'coude'); pg.evaluate("document.getElementById('fiSave').click()"); pg.wait_for_timeout(300); regle(pg,'droit'); pg.evaluate("document.getElementById('fiLoad').click()"); pg.wait_for_timeout(300)
    r1=pg.evaluate("document.getElementById('fiInv').value"); pg.evaluate("document.getElementById('fiReset').click()"); pg.wait_for_timeout(300); r2=pg.evaluate("document.getElementById('fiInv').value")
    check('Enregistrer, Restituer et Défaut conservent et rétablissent l\'optique (coudé simple puis droit)',r1=='coude' and r2=='droit',(r1,r2))
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close()
    # anciens réglages
    for inv,att in ((False,'redresse'),(True,'droit')):
        init="localStorage.setItem('eyeCfg4',%s);"%json.dumps(json.dumps({'fTel':1500,'fOc':17,'afov':100,'orient':'dob','finder':{'mag':9,'dia':50,'fov':5.6,'inv':inv,'v':2}}))
        c,pg,errs=ouvre(b,init); v=pg.evaluate("document.getElementById('fiInv').value")
        check('ancien réglage enregistré (inv = %s) : optique %s'%(str(inv).lower(),att),v==att and not errs,(v,errs[:1])); c.close()
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
