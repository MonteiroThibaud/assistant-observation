#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de la présentation de la 0.97 : plus de mention « version test », titres des onglets Ciel profond et À l'oculaire cachés, menu Matériel (Télescope, Chercheur, Mes oculaires), menu Listes d'objets à trois sous-menus, liens qui ouvrent le bon menu, boutons de 44 points, traits horizontaux à égale distance.
Usage : python3 test_parametres_menus_traits.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 2 minutes)"""
import sys, os, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:230]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8891),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
def ouvre(b,W,H):
    c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); d=datetime.datetime(2026,11,21,21,0,tzinfo=datetime.timezone.utc); pg.clock.install(time=d); pg.clock.set_fixed_time(d)
    pg.goto('http://localhost:8891/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3500); return c,pg,errs
def tab(pg,t): pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t); pg.wait_for_timeout(600)
with sync_playwright() as p:
    b=p.chromium.launch()
    c,pg,errs=ouvre(b,411,850)
    # 1. version test
    inf=pg.evaluate("({note:!!document.querySelector('.testnote'), ver:(document.querySelector('p.version')||{}).textContent||'', texte:/version test|à ne pas diffuser/i.test(document.body.textContent)})")
    check('aucune mention « version test » dans la page, ligne de version sans parenthèses',not inf['note'] and not inf['texte'] and __import__('re').match(r'^Version \d+\.\d+ du [^()]+$',inf['ver'].strip()),inf)
    # 2. titres cachés mais présents
    for t,nom in (('deep','Ciel profond et petits corps'),('eye',"À l'oculaire")):
        tab(pg,t); r=pg.evaluate("(t)=>{const h=[...document.querySelectorAll('#tab-'+t+' h2')].find(x=>x.classList.contains('sronly')); const r=h&&h.getBoundingClientRect(); return {present:!!h, txt:h&&h.textContent, visible:r&&(r.width>2||r.height>2)}}",t)
        check('titre « %s » : présent pour les lecteurs d\'écran, invisible à l\'écran'%nom,r['present'] and r['txt']==nom and not r['visible'],r)
    tab(pg,'loc'); r=pg.evaluate("(()=>{const h=document.querySelector('#tab-loc .tabtitle'); const r=h.getBoundingClientRect(); return {txt:h.textContent, visible:r.width>20}})()")
    check('le titre « Paramètres » reste affiché',r['visible'] and r['txt']=='Paramètres',r)
    # 3. structure des menus
    s=pg.evaluate("""()=>{const q=id=>document.getElementById(id); const kids=id=>[...q(id).querySelectorAll(':scope > .setbody > details')].map(d=>d.id); const ouverts=[...document.querySelectorAll('#tab-loc details.setdet')].filter(d=>d.open).length;
      return {mat:kids('matBox'), list:kids('listBox'), ouverts, ep:['ep1n','ep4n','bl1n','bl3n'].every(i=>q('matBox').contains(q(i))&&q('epBox').contains(q(i))), epSous:q('epBox').querySelectorAll('details').length, deep:q('listDeepBox').contains(q('listChecks')), lun:q('listLunBox').contains(q('lunChecks')), org:['orgList','orgRange','orgRows','orgMsg'].every(i=>q('listOrgBox').contains(q(i))), ordre:[...document.querySelectorAll('#tab-loc > details.setdet')].slice(0,3).map(d=>d.id)}}""")
    check('Paramètres : Date et lieu, Matériel, Listes d\'objets dans cet ordre ; tous les menus sont refermés au départ',s['ordre']==['locBox','matBox','listBox'] and s['ouverts']==0,s)
    check('Matériel contient Télescope, Chercheur et Mes oculaires ; Mes oculaires garde oculaires et barlows, sans sous-menu',s['mat']==['telBox','fiBox','epBox'] and s['ep'] and s['epSous']==0,s)
    check('Listes d\'objets : sous-menus Ciel profond, Lune et Organisation des listes, avec leur contenu',s['list']==['listDeepBox','listLunBox','listOrgBox'] and s['deep'] and s['lun'] and s['org'],s)
    nb=pg.evaluate("[document.querySelectorAll('#listChecks input[data-list]').length, document.querySelectorAll('#lunChecks input[data-mlist]').length, document.querySelectorAll('#listChecks input[data-mlist]').length]")
    check('les cases du ciel profond et celles de la Lune sont dans leur propre sous-menu',nb[0]>=10 and nb[1]>=10 and nb[2]==0,nb)
    # 4. liens qui ouvrent le bon menu
    def etat(): return pg.evaluate("Object.fromEntries(['matBox','telBox','listBox','listDeepBox','listLunBox','listOrgBox'].map(i=>[i,document.getElementById(i).open]))")
    pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false)"); tab(pg,'eye'); pg.evaluate("document.querySelector('[data-go=\"par\"]') && document.querySelector('[data-go=\"par\"]').click()"); pg.wait_for_timeout(500); e1=etat()
    check('le lien « Régler » de l\'oculaire ouvre Matériel puis Télescope',e1['matBox'] and e1['telBox'] and not e1['listBox'],e1)
    pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false)"); tab(pg,'deep'); pg.evaluate("document.querySelector('#tab-deep [data-go=\"lists\"]').click()"); pg.wait_for_timeout(500); e2=etat()
    check('« Choisir les listes › » du ciel profond ouvre Listes d\'objets puis Ciel profond seulement',e2['listBox'] and e2['listDeepBox'] and not e2['listLunBox'] and not e2['listOrgBox'],e2)
    pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false)"); tab(pg,'det'); pg.evaluate("window.scrollTo(0,0)")
    ok=pg.evaluate("(()=>{const l=document.querySelector('#moonLists [data-go=\"lists\"]'); if(!l) return false; l.click(); return true})()"); pg.wait_for_timeout(500); e3=etat()
    check('« Choisir les listes › » de la Lune ouvre Listes d\'objets puis Lune seulement',ok and e3['listBox'] and e3['listLunBox'] and not e3['listDeepBox'],(ok,e3))
    # 5. boutons de 44 points
    pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)"); pg.wait_for_timeout(500)
    h=pg.evaluate("""()=>{const o={}; for(const s of ['#telBox','#fiBox','#epBox','#listBox','#impBox']) o[s]=[...document.querySelectorAll(s+' .sbbtns button')].filter(b=>b.offsetParent).map(b=>Math.round(b.getBoundingClientRect().height*10)/10); o.autres=[...document.querySelectorAll('#locBox .locbtns button, #scrBox .sbbtns button')].filter(b=>b.offsetParent).map(b=>Math.round(b.getBoundingClientRect().height)); return o}""")
    check('Enregistrer, Restituer, Défaut, Ranger et les boutons des Imports : 44 points de haut',all(abs(v-44)<=1 for k in ('#telBox','#fiBox','#epBox','#listBox','#impBox') for v in h[k]) and len(h['#telBox'])==3 and len(h['#impBox'])>=3,h)
    check('les autres boutons de Paramètres (Actualiser, Saisir une position, Rotation…) sont aussi à 44 points depuis le 20 novembre',all(abs(v-44)<=1 for v in h['autres']) and len(h['autres'])>=3,h['autres'])
    check('aucune erreur JavaScript (411)',not errs,errs[:1]); c.close()
    # 6. traits équidistants, à plusieurs formats
    for W,H in ((411,850),(360,780),(320,568),(891,411),(1280,800)):
        c,pg,errs=ouvre(b,W,H); tab(pg,'det')
        r=pg.evaluate("""()=>{const nb=document.querySelector('#tab-det .nightbar').getBoundingClientRect(), pl=document.querySelector('#list .planet:not([hidden])'), r=pl.getBoundingClientRect(), phead=pl.querySelector('.phead').getBoundingClientRect(); return [r.top-nb.bottom, phead.top-(r.top+1)]}""")
        check('%dx%d : trait de Détail planète à égale distance de la date et du nom (écart de 1 point au plus)'%(W,H),abs(r[0]-r[1])<=1,[round(x,1) for x in r])
        tab(pg,'loc'); r2=pg.evaluate("""()=>['.carnet','.about'].map(s=>{const e=document.querySelector('#tab-loc '+s), r=e.getBoundingClientRect(), h=e.querySelector('h2').getBoundingClientRect(); const prevEls=s==='.carnet'?[...document.querySelectorAll('#tab-loc > details.setdet')]:[document.querySelector('#tab-loc .carnet')]; const bas=Math.max(...prevEls.map(x=>x.getBoundingClientRect().bottom)); return [r.top-bas, h.top-(r.top+1)]})""")
        check('%dx%d : traits devant « Carnet d\'observation » et « Informations » à égale distance (1 point au plus)'%(W,H),all(abs(a-b)<=1 for a,b in r2),[[round(x,1) for x in y] for y in r2])
        check('%dx%d : aucune erreur JavaScript'%(W,H),not errs,errs[:1]); c.close()
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
