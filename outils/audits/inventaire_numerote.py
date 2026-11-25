#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Planches numérotées des textes d'explication (mode jour) pour choisir ce qu'on enlève en mode allégé.
Usage : python3 inventaire_numerote.py DOSSIER_DU_SITE_INSTALLE ONGLET PREFIXE SORTIE_PNG SORTIE_JSON [iss]   (PREFIXE : S, P, C, O, L : les textes sont numérotés S1, S2…)   (ONGLET : sys, det, deep, eye, moon ; « iss » : TLE d'essai et calcul de zone pour sys)"""
import sys, os, re, json, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE,ONGLET,PREFIXE,PNG,JS=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]; ISS=len(sys.argv)>6 and sys.argv[6]=='iss'
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
s=open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''); k=s.index("  $('featClose').onclick=")
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(s[:k]+"  window.__show=showFeat; window.__eyeSel=id=>{ eyeSel='dso:'+id; drawEye(); showTab('eye') };\n"+s[k:])
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8899),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
TLE="ISS (ZARYA)\n1 25544U 98067A   26316.88411739  .00007667  00000-0  14541-3 0  9993\n2 25544  51.6325 284.2547 0007335  19.0494 341.0767 15.49339933594804"
tz=datetime.timezone(datetime.timedelta(hours=1)); FIX=datetime.datetime(2026,11,20,22,0,tzinfo=tz)
SEL="p,.sub,.featnote,.nightq,.hint,.empty,.eyeinfo,li.siteempty"
MARK="""(pre)=>{ const root=document.querySelector('.tab:not([hidden])')||document.body; const all=[...root.querySelectorAll('%s')].filter(e=>e.offsetParent!==null&&e.getBoundingClientRect().height>6&&e.textContent.replace(/\\s+/g,' ').trim().length>=40&&!e.closest('.tabbar,header,footer,[data-dso],li:not(.siteempty),table,dl,.issr,.issx,.cardbtns'));
 const keep=all.filter(e=>!all.some(o=>o!==e&&o.contains(e))); const out=[]; let n=1;
 keep.forEach(e=>{ const r=e.getBoundingClientRect(); const b=document.createElement('div'); b.textContent=pre+n; b.style.cssText='position:absolute;z-index:99999;left:1px;top:'+(r.top+scrollY-2)+'px;min-width:26px;height:22px;border-radius:11px;background:#d4143c;color:#fff;font:700 13px/22px sans-serif;text-align:center;padding:0 4px;box-shadow:0 0 0 2px #fff'; document.body.appendChild(b);
   const txt=e.textContent.replace(/\\s+/g,' ').trim(); const exp=!!e.closest('.expl')||!!e.querySelector('.expl')||e.classList.contains('expl');
   const ex=[...e.querySelectorAll('.expl')], partiel=ex.length>0&&!e.classList.contains('expl')&&ex.reduce((a,x)=>a+x.textContent.length,0)<txt.length-5; out.push({n:pre+n,classe:e.className||e.tagName,texte:txt,longueur:txt.length,masque_actuel:exp,partiel:partiel,securite:/filtre solaire|Le TLE a \\d+ jours|ne regarde|danger|aveugl/i.test(txt)}); n++ });
 return out }""".replace('%s',SEL)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1.5,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8899/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4500)
    pg.evaluate("delete document.documentElement.dataset.night")
    tab=lambda t: (pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t), pg.wait_for_timeout(900))
    if ISS:
        tab('loc'); pg.evaluate("(ids)=>ids.forEach(i=>{ for(let d=document.getElementById(i); d; d=d.parentElement&&d.parentElement.closest('details')) d.open=true })",['impBox','issSitesBox']); pg.fill('#issText',TLE); pg.click('#issSave'); pg.wait_for_timeout(800); pg.click('#iszRun')
        try: pg.wait_for_selector('#iszEvMsg',state='attached',timeout=170000)
        except Exception: pass
        pg.wait_for_timeout(1500)
    if ONGLET=='moon':
        tab('moon'); pg.wait_for_timeout(1500); pg.evaluate("window.__show('Grimaldi')"); pg.wait_for_timeout(1500); pg.evaluate("(()=>{const d=document.querySelector('.featprof'); if(d) d.open=true})()"); pg.wait_for_timeout(500)
    else: tab(ONGLET)
    if ONGLET=='sys': pg.wait_for_timeout(1500)
    if ONGLET=='deep':
        pass
    pg.evaluate("window.scrollTo(0,0)"); items=pg.evaluate(MARK,PREFIXE); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('.tabbar').forEach(e=>e.style.display='none')"); pg.wait_for_timeout(200); pg.screenshot(path=PNG,full_page=True); json.dump(items,open(JS,'w',encoding='utf-8'),ensure_ascii=False,indent=1); print(ONGLET,len(items),'textes numérotés',PREFIXE+'1','à',PREFIXE+str(len(items)))
    c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
