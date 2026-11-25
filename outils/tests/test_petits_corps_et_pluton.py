#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Tests du 24 novembre 2026 : (1) Détail planète : aucune fiche (Pluton comprise) n'a de filet bas ; (2) les listes « Comètes » et « Petites planètes » ne se cochent qu'une fois leurs éléments d'orbite importés ;
(3) oculaire en mode allégé : étoile double (informations conservées), comète (nom, magnitude estimée, distance, élongation conservés ; phrase sur la coma masquée), petite planète (tout conservé).
Usage : python3 test_petits_corps_et_pluton.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 2 minutes)"""
import sys, os, re, shutil, tempfile, threading, http.server, socketserver, datetime, json
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:360]) if detail!='' else ''),flush=True)
def put(L,i,s):
    for k,ch in enumerate(s): L[i+k]=ch
def comete():
    L=[' ']*160; put(L,0,'  12'); put(L,4,'P'); put(L,14,'2026'); put(L,19,'12'); put(L,22,'20.123'); put(L,30,'0.780000'); put(L,41,'0.954000'); put(L,51,'199.0000'); put(L,61,'255.9000'); put(L,71,' 74.2000'); put(L,91,'5.0'); put(L,96,'4.0'); put(L,102,'Pons-Brooks (12P)'); return ''.join(L).rstrip()+' '*(160-len(''.join(L).rstrip()))
def asteroide():
    L=[' ']*200; put(L,0,'00001'); put(L,8,' 3.34'); put(L,14,' 0.12'); put(L,20,'K25BN'); put(L,26,'  60.07000'); put(L,37,'  73.29000'); put(L,48,'  80.25000'); put(L,59,'  10.58000'); put(L,70,'0.0793000'); put(L,80,' 0.21399000'); put(L,92,'  2.7656000'); put(L,166,'(1) Ceres'); return ''.join(L).rstrip()
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8919),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,24,16,40,tzinfo=datetime.timezone.utc)
def neuf(init=None):
    c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    if init: pg.add_init_script(init)
    pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8919/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4000); return c,pg,errs
with sync_playwright() as p:
    b=p.chromium.launch()
    tabf=lambda pg,t:(pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t), pg.wait_for_timeout(900))
    # 1. filets des fiches de planètes
    c,pg,errs=neuf(); tabf(pg,'det'); bords=[]; noms=[]
    for k in range(9):
        pg.evaluate("(()=>{const b=[...document.querySelectorAll('#tab-det button')].find(x=>/Astre précédent/.test(x.getAttribute('aria-label')||'')); b.click()})()"); pg.wait_for_timeout(700)
        noms.append(pg.evaluate("([...document.querySelectorAll('#tab-det article.planet')].find(x=>x.offsetParent)||{innerText:''}).innerText.split('\\n').filter(x=>x.trim()&&x.trim()!=='‹')[0]"))
        bords.append(pg.evaluate("parseFloat(getComputedStyle([...document.querySelectorAll('#tab-det article.planet')].find(x=>x.offsetParent)).borderBottomWidth)"))
    check('Détail planète : aucune des 9 fiches (Pluton comprise) n\'a de filet bas',all(x==0 for x in bords) and len(set(noms))==9 and 'Pluton' in noms,list(zip(noms,bords)))
    c.close()
    # 2. listes de petits corps
    c,pg,errs=neuf("localStorage.setItem('deepLists',JSON.stringify(['m','c','a']))")
    def listes(): return pg.evaluate("(()=>{const o={}; ['c','a','d','m'].forEach(i=>{const x=document.querySelector('#listChecks input[data-list=\"'+i+'\"]'); o[i]={dis:x.disabled,chk:x.checked,txt:x.parentNode.querySelector('small').textContent}}); return o})()")
    def ouvre_listes(): tabf(pg,'loc'); pg.evaluate("(b=>{for(let d=b;d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true})(document.getElementById('listDeepBox'))"); pg.wait_for_timeout(300)
    ouvre_listes(); l0=listes(); st=json.loads(pg.evaluate("localStorage.getItem('deepLists')"))
    check('sans import : « Comètes » et « Petites planètes » sont grisées, décochées, « à importer » ; une sélection mémorisée est retirée',l0['c']['dis'] and l0['a']['dis'] and not l0['c']['chk'] and not l0['a']['chk'] and 'à importer' in l0['c']['txt'] and 'c' not in st and 'a' not in st and not l0['d']['dis'] and l0['m']['chk'],(l0,st))
    pg.evaluate("document.querySelector('#listChecks input[data-list=\"c\"]').click()"); pg.wait_for_timeout(300)
    check('sans import : un appui sur la case « Comètes » ne coche rien',not listes()['c']['chk'] and 'c' not in json.loads(pg.evaluate("localStorage.getItem('deepLists')")))
    # import
    pg.evaluate("(b=>{for(let d=b;d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true})(document.getElementById('sbBox'))"); pg.evaluate("document.querySelector('#sbBox details.sbpaste').open=true")
    pg.fill('#sbText',comete()+'\n'+asteroide()); pg.click('#sbAdd'); pg.wait_for_timeout(1500); ouvre_listes(); l1=listes()
    check('après l\'import : les deux listes sont cochables, non cochées d\'office, « 1 importées »',not l1['c']['dis'] and not l1['a']['dis'] and not l1['c']['chk'] and not l1['a']['chk'] and '1 importées' in l1['c']['txt'] and '1 importées' in l1['a']['txt'],l1)
    for i in ('c','a','d'): pg.evaluate("(i)=>document.querySelector('#listChecks input[data-list=\"'+i+'\"]').click()",i); pg.wait_for_timeout(300)
    l2=listes(); check('les listes importées se cochent',l2['c']['chk'] and l2['a']['chk'] and l2['d']['chk'])
    # oculaire allégé : étoile double, comète, petite planète
    tabf(pg,'loc'); pg.evaluate("document.getElementById('scrBox').open=true")
    if pg.evaluate("document.documentElement.dataset.detail")!='light': pg.click('#detailBtn')
    pg.wait_for_timeout(500)
    def objet(filtre):
        tabf(pg,'deep'); pg.evaluate("(f)=>{const b=[...document.querySelectorAll('#tab-deep button')].find(x=>x.textContent.trim()===f); if(b) b.click()}",filtre); pg.wait_for_timeout(1200)
        pg.evaluate("(()=>{const a=document.querySelector('#tab-deep article.dso'); const hd=a&&a.querySelector('.dhead'); (hd||a).click()})()"); pg.wait_for_timeout(1800); tabf(pg,'eye'); pg.wait_for_timeout(800)
        return re.sub(r'\s+',' ',pg.evaluate("document.getElementById('eyeInfo').innerText")).strip()
    d=objet('Doubles'); check('oculaire allégé, étoile double : les informations de l\'étoile double sont conservées (magnitudes, écart, détail agrandi)',re.search(r"(étoile double|système multiple), magnitudes",d) and 'écart' in d and 'Le détail agrandi montre' in d and 'Constellation au centre du champ' in d and 'Z : direction du zénith' not in d and 'Fais glisser' not in d,d)
    cm=objet('Comètes'); check('oculaire allégé, comète : nom, magnitude estimée, distance, élongation conservés ; phrase sur la coma masquée',re.search(r"Pons-Brooks[^:]*: comète, magnitude estimée [\d,]+, à [\d,]+ UA, élongation \d+°",cm) and 'Coma et queue' not in cm and 'Constellation au centre du champ' in cm,cm)
    ce=objet('Petites planètes'); check('oculaire allégé, petite planète : toutes les informations conservées (type, magnitude, distance, élongation, déplacement)',re.search(r"Ceres[^:]*: petite planète, magnitude [\d,]+, à [\d,]+ UA, élongation \d+°\. Point d'aspect stellaire qui se déplace",ce) is not None,ce)
    # mode détaillé : la phrase sur la coma est là
    tabf(pg,'loc'); pg.click('#detailBtn'); pg.wait_for_timeout(500); cm2=objet('Comètes')
    check('oculaire détaillé, comète : la phrase « Coma et queue schématiques » est affichée',"Coma et queue schématiques : la queue pointe à l'opposé du Soleil" in cm2,cm2)
    # effacement des éléments : listes décochées et grisées
    tabf(pg,'loc'); pg.evaluate("(b=>{for(let d=b;d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true})(document.getElementById('sbBox'))"); pg.evaluate("document.getElementById('sbClear').click()"); pg.wait_for_timeout(500); etat=pg.evaluate("(()=>{const q=document.querySelector('.orgpop'); return q?{hidden:q.hidden,txt:q.textContent.slice(0,50)}:null})()"); print('  (fenêtre de confirmation :',etat,')'); pg.evaluate("document.querySelector('.orgpop [data-act=ok]').click()"); pg.wait_for_timeout(1000); ouvre_listes(); l3=listes(); st3=json.loads(pg.evaluate("localStorage.getItem('deepLists')"))
    check('après l\'effacement des éléments : listes grisées, décochées et retirées de la sélection mémorisée',l3['c']['dis'] and l3['a']['dis'] and not l3['c']['chk'] and not l3['a']['chk'] and 'c' not in st3 and 'a' not in st3 and 'd' in st3,(l3['c'],st3))
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
