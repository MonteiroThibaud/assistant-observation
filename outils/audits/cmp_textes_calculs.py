#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Compare les textes de cinq onglets (Système solaire, Détail planète, Ciel profond, Lune, À l'oculaire) de deux copies de l'application dans six scénarios (date et lieu) :
preuve que les calculs et les textes affichés sont identiques avant et après une modification qui ne devait pas les changer.
Usage : python3 cmp_textes_calculs.py DOSSIER_A DOSSIER_B [--scenarios N]
  DOSSIER_A, DOSSIER_B : deux dossiers de site installé (contenant index.html), par exemple celui d'avant et celui d'après (voir construire.py) ;
  --scenarios N : ne passer que les N premiers scénarios (essai rapide) ; durée complète : environ 3 minutes par dossier.
Code de sortie : 0 si tous les textes sont identiques, 1 sinon. Prérequis : Python 3, Playwright pour Python."""
import sys, os, datetime, threading, http.server, socketserver, socket
from playwright.sync_api import sync_playwright
argv=sys.argv[1:]; N=6
if '--scenarios' in argv: i=argv.index('--scenarios'); N=int(argv[i+1]); del argv[i:i+2]
args=argv
if len(args)!=2 or not all(os.path.isfile(os.path.join(d,'index.html')) for d in args): sys.exit(__doc__)
tz=datetime.timezone(datetime.timedelta(hours=1))
SCEN=[((2026,3,20,21,0),(46.03,4.07)),((2026,6,21,23,30),(48.85,2.35)),((2026,8,12,3,0),(43.3,5.4)),((2026,11,15,16,0),(46.03,4.07)),((2027,1,3,22,0),(-33.9,151.2)),((2026,12,24,20,0),(64.1,-21.9))][:N]
def serveur(dossier):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw): super().__init__(*a,directory=dossier,**kw)
        def log_message(self,*a): pass
    class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
    s=S(('127.0.0.1',0),H); threading.Thread(target=s.serve_forever,daemon=True).start(); return s,s.server_address[1]
def collecte(dossier):
    srv,port=serveur(dossier); out=[]
    try:
      with sync_playwright() as p:
        b=p.chromium.launch()
        for (t,(lat,lon)) in SCEN:
            c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':lat,'longitude':lon},permissions=['geolocation'])
            pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=datetime.datetime(*t,tzinfo=tz)); pg.goto('http://localhost:%d/index.html'%port); pg.wait_for_timeout(7500)
            txt={}
            for tab in ('sys','det','deep','moon','eye'):
                pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",tab); pg.wait_for_timeout(1500)
                txt[tab]=pg.evaluate("(t)=>document.getElementById('tab-'+t).innerText",tab)
            out.append((t,lat,txt,errs[:1])); c.close()
        b.close()
    finally: srv.shutdown()
    return out
A=collecte(args[0]); B=collecte(args[1])
tot=0; diff=0
for (t,lat,ta,ea),(t2,lat2,tb,eb) in zip(A,B):
    for tab in ta:
        tot+=1
        if ta[tab]!=tb[tab]:
            diff+=1; la=ta[tab].split('\n'); lb=tb[tab].split('\n'); d=[(x,y) for x,y in zip(la,lb) if x!=y][:3]; print('  DIFFÉRENCE',t,lat,tab,d)
    print('scénario',t,'lat',lat,': %d caractères comparés par onglet (%s) ; erreurs JS : %s / %s'%(sum(len(v) for v in ta.values()),', '.join('%s %d'%(k,len(v)) for k,v in ta.items()),ea or 'aucune',eb or 'aucune'))
print('BILAN : %d onglets comparés, %d différents'%(tot,diff)); sys.exit(1 if diff else 0)
