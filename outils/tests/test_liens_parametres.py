#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de l'audit des liens vers Paramètres : invitation de mise à jour du TLE sous le titre « Transits de l'ISS », liens de À l'oculaire vers Télescope, Oculaires et barlows, Chercheur, liens des messages (aucune liste cochée, aucun élément orbital, messages de la zone).
Usage : python3 test_liens_parametres.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 3 minutes)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
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
srv=S(('127.0.0.1',8897),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
TLE="ISS (ZARYA)\n1 25544U 98067A   26316.88411739  .00007667  00000-0  14541-3 0  9993\n2 25544  51.6325 284.2547 0007335  19.0494 341.0767 15.49339933594804"
tz=datetime.timezone(datetime.timedelta(hours=1))
def ouvre(b,quand):
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=quand); pg.goto('http://localhost:8897/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4000); return c,pg,errs
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(700)
def ouvrir(pg,*ids): pg.evaluate("(ids)=>ids.forEach(i=>{ for(let d=document.getElementById(i); d; d=d.parentElement&&d.parentElement.closest('details')) d.open=true })",list(ids))
def fermer(pg): pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false)")
def etat(pg,*ids): return pg.evaluate("(ids)=>Object.fromEntries(ids.map(i=>[i,document.getElementById(i).open]))",list(ids))
with sync_playwright() as p:
    b=p.chromium.launch(); c,pg,errs=ouvre(b,datetime.datetime(2026,11,20,22,0,tzinfo=tz))
    # À l'oculaire : trois liens directs
    tab(pg,'eye'); n=pg.evaluate("[...document.querySelectorAll('#tab-eye .eyeset [data-go]')].map(e=>e.dataset.go)")
    check('À l\'oculaire : trois liens (Télescope, Oculaires et barlows, Chercheur)',n==['par','ep','fi'],n)
    for go,box in (('par','telBox'),('ep','epBox'),('fi','fiBox')):
        tab(pg,'loc'); fermer(pg); tab(pg,'eye'); pg.evaluate("(g)=>document.querySelector('#tab-eye .eyeset [data-go=\"'+g+'\"]').click()",go); pg.wait_for_timeout(500)
        e=etat(pg,'matBox',box); check('lien « %s » de l\'oculaire : ouvre Matériel puis %s'%(go,box),e['matBox'] and e[box] and not pg.evaluate("document.getElementById('tab-loc').hidden"),e)
    # sans éléments orbitaux : messages avec lien
    tab(pg,'loc'); fermer(pg); ouvrir(pg,'issSitesBox'); pg.wait_for_timeout(500)
    a=pg.evaluate("[...document.querySelectorAll('#issSitesTle [data-go]')].map(e=>e.dataset.go)"); check('sans TLE : le message de Transits de l\'ISS renvoie vers les éléments orbitaux',a==['iss'],a)
    pg.click('#iszRun'); pg.wait_for_timeout(600); a=pg.evaluate("[...document.querySelectorAll('#iszMsg [data-go]')].map(e=>e.dataset.go)"); check('sans TLE : le message de la zone renvoie vers les éléments orbitaux',a==['iss'],a)
    fermer(pg); tab(pg,'loc'); ouvrir(pg,'issSitesBox'); pg.evaluate("document.querySelector('#issSitesTle [data-go=\"iss\"]').click()"); pg.wait_for_timeout(600); e=etat(pg,'impBox'); check('ce lien ouvre Paramètres › Imports',e['impBox'],e)
    # aucune liste cochée
    tab(pg,'loc'); fermer(pg); ouvrir(pg,'listDeepBox'); pg.evaluate("document.querySelectorAll('#listChecks input[data-list]:checked').forEach(i=>i.click())"); pg.wait_for_timeout(500); tab(pg,'deep'); pg.wait_for_timeout(700)
    a=pg.evaluate("[...document.querySelectorAll('#deepList .empty [data-go]')].map(e=>e.dataset.go)"); check('ciel profond sans liste cochée : lien « Choisir les listes › »',a==['lists'],a)
    fermer(pg); pg.evaluate("document.querySelector('#deepList .empty [data-go=\"lists\"]').click()"); pg.wait_for_timeout(600); e=etat(pg,'listBox','listDeepBox'); check('ce lien ouvre Listes d\'objets › Ciel profond',e['listBox'] and e['listDeepBox'],e)
    check('aucune erreur JavaScript (sans TLE)',not errs,errs[:1])
    # TLE de 8 jours
    tab(pg,'loc'); ouvrir(pg,'impBox'); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(800); tab(pg,'sys')
    ok=False
    try: pg.wait_for_selector('#issTleAlert',state='attached',timeout=120000); ok=True
    except Exception: ok=False
    z=pg.evaluate("""()=>{const a=document.getElementById('issTleAlert'); if(!a) return null; const h=a.previousElementSibling; return {titre:h&&h.textContent.trim(), texte:a.textContent.trim(), lien:!!a.querySelector('[data-go="iss"]'), suit:a.nextElementSibling&&a.nextElementSibling.id}}""")
    check('TLE de 8 jours : invitation avec lien juste sous le titre « Transits de l\'ISS », avant le tableau',ok and z and z['titre']=="Transits de l'ISS" and 'Le TLE a 8 jours' in z['texte'] and z['lien'] and z['suit']=='issSitesTable',z)
    nb=pg.evaluate("[...document.querySelectorAll('#tab-sys .nightq')].filter(e=>/Le TLE a \\d+ jours/.test(e.textContent)).length"); check('une seule invitation dans la partie Transits de l\'ISS du tableau (pas de doublon dans le texte du bas)',nb==1,nb)
    fermer(pg); pg.evaluate("document.querySelector('#issTleAlert [data-go=\"iss\"]').click()"); pg.wait_for_timeout(700); e=etat(pg,'impBox'); r=pg.evaluate("({loc:!document.getElementById('tab-loc').hidden, vis:!!document.getElementById('issBox').offsetParent})")
    check('un appui ouvre Paramètres, Imports et la partie « Station spatiale (ISS) »',e['impBox'] and r['loc'] and r['vis'],(e,r))
    check('aucune erreur JavaScript (TLE de 8 jours)',not errs,errs[:1]); c.close()
    # TLE de moins de 3 jours : pas d'invitation
    c,pg,errs=ouvre(b,datetime.datetime(2026,11,14,22,0,tzinfo=tz)); tab(pg,'loc'); ouvrir(pg,'impBox'); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(800); tab(pg,'sys')
    try: pg.wait_for_selector('#tab-sys .evtitle',state='attached',timeout=120000)
    except Exception: pass
    pg.wait_for_timeout(2500); z=pg.evaluate("({titre:!![...document.querySelectorAll('#tab-sys .evtitle')].find(h=>h.textContent.trim()==='Transits de l\\'ISS'), alerte:!!document.getElementById('issTleAlert')})")
    check('TLE de moins de 3 jours : le tableau est affiché, sans invitation',z['titre'] and not z['alerte'],z); check('aucune erreur JavaScript (TLE récent)',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
