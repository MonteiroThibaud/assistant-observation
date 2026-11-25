#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du sens de l'image : huit combinaisons (transformations vérifiées sur l'image de l'oculaire), réglage par défaut dans Matériel › Télescope (enregistré, Enregistrer, Restituer, Défaut), changement de session dans « À l'oculaire » et sur la Lune, retour au défaut à chaque lancement, migration de l'ancien réglage.
Usage : python3 test_sens_image.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 2 minutes)"""
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
srv=S(('127.0.0.1',8895),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,20,0,tzinfo=datetime.timezone.utc)
def ouvre(b,init=''):
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    if init: pg.add_init_script(init)
    pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8895/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3500); return c,pg,errs
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(600)
def ouvrir(pg,*ids): pg.evaluate("(ids)=>ids.forEach(i=>{ for(let d=document.getElementById(i); d; d=d.parentElement&&d.parentElement.closest('details')) d.open=true })",list(ids))
def btn(pg): tab(pg,'moon'); pg.wait_for_timeout(800); return pg.evaluate("document.getElementById('orientBtn').textContent.trim()")
def defaut(pg,m): tab(pg,'loc'); ouvrir(pg,'telBox'); pg.evaluate("(m)=>{ const a=document.getElementById('telOri'); a.value=m; a.dispatchEvent(new Event('change')) }",m); pg.wait_for_timeout(500)
def stock(pg): return pg.evaluate("(()=>{const c=JSON.parse(localStorage.getItem('eyeCfg4')||'{}'); return c.oriDef||null})()")
def rot(pg):
    tab(pg,'eye'); pg.wait_for_timeout(900)
    return pg.evaluate("""()=>{ const g=[...document.querySelectorAll('#tab-eye svg g[transform]')].map(x=>x.getAttribute('transform')).find(x=>/^translate\\([^)]*\\)\\s*rotate\\(/.test(x)); const m=g&&g.match(/rotate\\((-?[\\d.]+)\\)(\\s*scale\\(-1,\\s*1\\))?/); return {phi:m?+m[1]:null, mir:!!(m&&m[2])}}""")
def mod(x): return ((x%360)+360)%360
with sync_playwright() as p:
    b=p.chromium.launch(); c,pg,errs=ouvre(b)
    tab(pg,'loc'); ouvrir(pg,'telBox')
    r=pg.evaluate("({d:document.getElementById('telOri').value,o:document.getElementById('orient').value,hint:document.getElementById('telOriHint').textContent})")
    check('défaut d\'origine : Dobson (zénith, retournée), identique dans « À l\'oculaire », et le bouton de la Lune affiche « Dobson »',r['d']=='dob' and r['o']=='dob' and 'Dobson' in r['hint'] and btn(pg)=='Dobson',r)
    tab(pg,'loc'); ouvrir(pg,'telBox')
    L=pg.evaluate("(()=>{const f=id=>[...document.getElementById(id).options].map(o=>o.value+'|'+o.textContent+'|'+(o.dataset.grp||'')); return {tel:f('telOri'), eye:f('orient')}})()")
    check('une seule liste de huit choix, identique (valeurs, libellés, intitulés de groupe) dans Télescope et dans À l\'oculaire',len(L['tel'])==8 and L['tel']==L['eye'] and sum(1 for x in L['tel'] if x.split('|')[2])==2,L['tel'][:2])
    pg.evaluate("document.querySelector('#telBox .dd-field .ddbtn').click()"); pg.wait_for_timeout(400)
    P=pg.evaluate("({grp:[...document.querySelectorAll('#dd-telOri .ddgrp')].map(e=>e.textContent), sep:document.querySelectorAll('#dd-telOri .ddsep').length, opt:document.querySelectorAll('#dd-telOri .ddopt').length, ord:[...document.querySelectorAll('#dd-telOri > *')].map(e=>e.className)})")
    check('la liste ouverte montre deux intitulés (repère zénith, repère nord), un séparateur entre les deux et huit choix',len(P['grp'])==2 and 'zénith' in P['grp'][0] and 'nord' in P['grp'][1] and P['sep']==1 and P['opt']==8,P)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    # huit combinaisons, transformation de l'image de l'oculaire (17 mm, Lune)
    V={}
    for m in ('telrad','dob','coude','zmirud','sky','rot','mirror','nmirud'):
        tab(pg,'eye'); pg.evaluate("(m)=>{const s=document.getElementById('orient'); s.value=m; s.dispatchEvent(new Event('change'))}",m); V[m]=rot(pg)
    z=V['telrad']['phi']
    okz=(not V['telrad']['mir']) and (not V['dob']['mir']) and abs(mod(V['dob']['phi']-z)-180)<0.1 and V['coude']['mir'] and abs(mod(V['coude']['phi']+z))<0.1 and V['zmirud']['mir'] and abs(mod(V['zmirud']['phi']-(180-z)))<0.1
    okn=(not V['sky']['mir']) and abs(mod(V['sky']['phi']))<0.1 and (not V['rot']['mir']) and abs(mod(V['rot']['phi'])-180)<0.1 and V['mirror']['mir'] and abs(mod(V['mirror']['phi']))<0.1 and V['nmirud']['mir'] and abs(mod(V['nmirud']['phi'])-180)<0.1
    check('repère zénith : à l\'endroit, retournée de 180°, miroir gauche/droite, miroir haut/bas (transformations vérifiées)',okz,V)
    check('repère nord : à l\'endroit, retournée de 180°, miroir gauche/droite, miroir haut/bas (transformations vérifiées)',okn,V)
    check('un changement de session n\'est pas enregistré : le défaut mémorisé reste inchangé',stock(pg) in (None,'dob'),stock(pg))
    pg.reload(); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3000)
    check('après relancement, retour au défaut (Dobson)',btn(pg)=='Dobson' and pg.evaluate("document.getElementById('orient').value")=='dob')
    # défaut modifié dans Télescope
    defaut(pg,'mirror'); check('défaut changé dans Matériel › Télescope (nord, inversée gauche/droite) : enregistré, repris par la liste de l\'oculaire et le bouton de la Lune',stock(pg)=='mirror' and pg.evaluate("document.getElementById('orient').value")=='mirror' and btn(pg)=='Inversée',(stock(pg),))
    pg.reload(); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3000); tab(pg,'loc'); ouvrir(pg,'telBox')
    r=pg.evaluate("document.getElementById('telOri').value"); check('le défaut est conservé après relancement',r=='mirror' and btn(pg)=='Inversée',r)
    # bouton de la Lune : cycle de session depuis ce défaut non classique ? (« Inversée » fait partie des quatre : cycle classique)
    seq=[btn(pg)]
    for _ in range(4): pg.click('#orientBtn'); pg.wait_for_timeout(300); seq.append(pg.evaluate("document.getElementById('orientBtn').textContent.trim()"))
    check('bouton de la Lune : Inversée, Dobson, Nord en haut, Retournée, Inversée (retour au défaut)',seq==['Inversée','Dobson','Nord en haut','Retournée','Inversée'],seq)
    # défaut hors des quatre classiques : il ouvre le cycle
    defaut(pg,'telrad'); seq=[btn(pg)]
    for _ in range(5): pg.click('#orientBtn'); pg.wait_for_timeout(300); seq.append(pg.evaluate("document.getElementById('orientBtn').textContent.trim()"))
    check('défaut « zénith en haut » : le cycle commence par lui et y revient (Zénith en haut, Dobson, Nord en haut, Retournée, Inversée, Zénith en haut)',seq==['Zénith en haut','Dobson','Nord en haut','Retournée','Inversée','Zénith en haut'],seq)
    # Enregistrer, Restituer, Défaut
    defaut(pg,'coude'); pg.evaluate("document.getElementById('telSave').click()"); pg.wait_for_timeout(300); defaut(pg,'rot'); st1=stock(pg)
    pg.evaluate("document.getElementById('telLoad').click()"); pg.wait_for_timeout(400); st2=stock(pg); sel2=pg.evaluate("document.getElementById('telOri').value")
    pg.evaluate("document.getElementById('telReset').click()"); pg.wait_for_timeout(400); st3=stock(pg); sel3=pg.evaluate("document.getElementById('telOri').value")
    check('Enregistrer, Restituer et Défaut : coudé (zénith, gauche/droite) restitué puis Dobson rétabli',st1=='rot' and st2=='coude' and sel2=='coude' and st3=='dob' and sel3=='dob',(st1,st2,sel2,st3,sel3))
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close()
    c,pg,errs=ouvre(b,"localStorage.setItem('eyeCfg4',%s);"%json.dumps(json.dumps({'fTel':1500,'fOc':17,'afov':100,'orient':'rot','finder':{'mag':9,'dia':50,'fov':5.6,'inv':True,'opt':'droit','v':2}})))
    check('ancien réglage « orient » (retournée) : devient le défaut',btn(pg)=='Retournée' and stock(pg) in (None,'rot'),btn(pg)); check('aucune erreur JavaScript (migration)',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
