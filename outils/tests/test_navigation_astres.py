#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des flèches de choix de l'astre dans « Détail planète » : disposition de la ligne (flèche, symbole, nom, J+, lever, flèche), boutons identiques à ceux des dates, aucun débordement aux cinq formats, parcours en boucle (précédent et suivant), étiquettes accessibles, suivi de l'oculaire, clavier (Entrée).
Usage : python3 test_navigation_astres.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 1 minute 30)"""
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
srv=S(('127.0.0.1',8889),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
ORDRE=['moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto']
def ouvre(b,W,H):
    c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); d=datetime.datetime(2026,11,21,21,0,tzinfo=datetime.timezone.utc); pg.clock.install(time=d); pg.clock.set_fixed_time(d)
    pg.goto('http://localhost:8889/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(3500)
    pg.evaluate("document.querySelector('.tabbar [data-tab=det]').click()"); pg.wait_for_timeout(600); return c,pg,errs
def visible(pg): return pg.evaluate("[...document.querySelectorAll('#list .planet')].filter(a=>!a.hidden).map(a=>a.dataset.k)")
with sync_playwright() as p:
    b=p.chromium.launch()
    for W,H in ((411,850),(360,780),(320,568),(891,411),(1280,800)):
        c,pg,errs=ouvre(b,W,H)
        info=pg.evaluate("""()=>{const out=[]; document.querySelectorAll('#list .planet').forEach(a=>{ a.hidden=false; const h=a.querySelector('.phead'), P=a.querySelector('.pnav[data-pnav="-1"]'), N=a.querySelector('.pnav[data-pnav="1"]'), d=a.querySelector('h3 .dot'), t=a.querySelector('h3'), r=a.querySelector('.rise'), A=a.getBoundingClientRect();
          const R=e=>e?e.getBoundingClientRect():null; const hp=R(h), p=R(P), n=R(N), dd=R(d), tt=R(t), rr=R(r);
          out.push({k:a.dataset.k,ordre:!!(P&&N&&p.right<=dd.left+1&&dd.left<tt.right&&tt.right<=rr.left+1&&rr.right<=n.left+1),debord:h.scrollWidth>h.clientWidth+1||n.right>hp.right+1||p.left<hp.left-1,centre:Math.round(Math.abs((p.top+p.bottom)/2-(dd.top+dd.bottom)/2)*10)/10,lignes:Math.round(hp.height),pw:Math.round(p.width)}); a.hidden=(a.dataset.k!=='moon') }); return out}""")
        check('%dx%d : 9 fiches, flèche · symbole · nom · lever · flèche dans cet ordre, sans débordement'%(W,H),len(info)==9 and all(i['ordre'] and not i['debord'] for i in info),[(i['k'],i['ordre'],i['debord']) for i in info if not i['ordre'] or i['debord']])
        check('%dx%d : flèches centrées sur le symbole (écart de 4 points au plus)'%(W,H),all(i['centre']<=4 for i in info),[(i['k'],i['centre']) for i in info if i['centre']>4])
        if W==411:
            cmp=pg.evaluate("""()=>{const d=document.getElementById('prev6'), a=document.querySelector('#list .planet:not([hidden]) .pnav[data-pnav="-1"]'), s=getComputedStyle(d), t=getComputedStyle(a), dn=document.getElementById('next6'), an=document.querySelector('#list .planet:not([hidden]) .pnav[data-pnav="1"]');
              return {gl:[d.textContent,a.textContent,dn.textContent,an.textContent], w:[d.getBoundingClientRect().width,a.getBoundingClientRect().width], fs:[s.fontSize,t.fontSize], bc:[s.borderTopColor,t.borderTopColor], br:[s.borderRadius,t.borderRadius], bg:[s.backgroundColor,t.backgroundColor], ff:[s.fontFamily,t.fontFamily]}}""")
            check('411 : flèches identiques à celles des dates (glyphes, taille, police, bordure, rayon, fond)',cmp['gl']==['‹','‹','›','›'] and cmp['w'][0]==cmp['w'][1] and cmp['fs'][0]==cmp['fs'][1] and cmp['bc'][0]==cmp['bc'][1] and cmp['br'][0]==cmp['br'][1] and cmp['bg'][0]==cmp['bg'][1] and cmp['ff'][0]==cmp['ff'][1],cmp)
            # parcours
            suiv=[]; 
            for _ in range(9):
                suiv.append(visible(pg)); pg.click('#list .planet:not([hidden]) .pnav[data-pnav="1"]'); pg.wait_for_timeout(250)
            check('411 : « suivant » parcourt Lune, Mercure… Pluton puis revient à la Lune, une seule fiche visible à la fois',[v[0] for v in suiv]==ORDRE and all(len(v)==1 for v in suiv) and visible(pg)==['moon'],[v for v in suiv])
            pg.click('#list .planet:not([hidden]) .pnav[data-pnav="-1"]'); pg.wait_for_timeout(250); v1=visible(pg)
            pg.click('#list .planet:not([hidden]) .pnav[data-pnav="-1"]'); pg.wait_for_timeout(250); v2=visible(pg)
            check('411 : « précédent » depuis la Lune va à Pluton puis à Neptune (boucle)',v1==['pluto'] and v2==['neptune'],(v1,v2))
            for _ in range(2): pg.click('#list .planet:not([hidden]) .pnav[data-pnav="1"]'); pg.wait_for_timeout(250)
            lab=pg.evaluate("[...document.querySelectorAll('#list .planet:not([hidden]) .pnav')].map(b=>[b.getAttribute('aria-label'),b.title])")
            check('411 : étiquettes accessibles avec le nom de l\'astre voisin (la Lune : précédent Pluton, suivant Mercure)',lab==[['Astre précédent : Pluton','Pluton'],['Astre suivant : Mercure','Mercure']],lab)
            pg.click('#list .planet:not([hidden]) .pnav[data-pnav="1"]'); pg.wait_for_timeout(250); pg.click('#list .planet:not([hidden]) .pnav[data-pnav="1"]'); pg.wait_for_timeout(250); pg.click('#list .planet:not([hidden]) .pnav[data-pnav="1"]'); pg.wait_for_timeout(250)  # Mars
            tab=pg.evaluate("document.querySelector('.tabbar [aria-selected=true]').dataset.tab"); k=visible(pg)
            pg.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); pg.wait_for_timeout(1500)
            txt=pg.evaluate("document.getElementById('tab-eye').textContent")
            check('411 : les flèches ne changent pas d\'onglet et l\'oculaire suit l\'astre choisi (Mars)',tab=='det' and k==['mars'] and 'Mars' in txt,(tab,k,'Mars' in txt))
            pg.evaluate("document.querySelector('.tabbar [data-tab=det]').click()"); pg.wait_for_timeout(500)
            # clavier : Entrée sur « suivant » passe à la fiche suivante
            pg.focus('#list .planet:not([hidden]) .pnav[data-pnav="1"]'); pg.keyboard.press('Enter'); pg.wait_for_timeout(400); k2=visible(pg)
            check('411 : au clavier, Entrée sur « suivant » passe à Jupiter',k2==['jupiter'],k2)
        check('%dx%d : aucune erreur JavaScript'%(W,H),not errs,errs[:1]); c.close()
    b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
