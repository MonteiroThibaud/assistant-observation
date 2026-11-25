#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du texte d'information de l'oculaire (avec ou sans barlow) en mode allégé : « <oculaire> : grossissement ×N, champ réel X. <objet> : <taille>. Constellation au centre du champ : Y. Vue à HH:MM. »
Usage : python3 test_allege_oculaire.py DOSSIER_DU_SITE_INSTALLE   (le serveur est démarré par le test ; durée : environ 60 secondes)"""
import sys, os, re, shutil, tempfile, threading, http.server, socketserver, datetime
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)[:330]) if detail!='' else ''),flush=True)
T=tempfile.mkdtemp()
for n in os.listdir(SITE):
    if n!='index.html': os.symlink(os.path.abspath(os.path.join(SITE,n)),os.path.join(T,n))
open(os.path.join(T,'index.html'),'w',encoding='utf-8').write(open(os.path.join(SITE,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",''))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=T,**kw)
    def log_message(self,*a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address=True; daemon_threads=True
srv=S(('127.0.0.1',8916),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
FIX=datetime.datetime(2026,11,21,22,10,tzinfo=datetime.timezone.utc)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=FIX); pg.clock.set_fixed_time(FIX); pg.goto('http://localhost:8916/index.html'); pg.wait_for_function("document.querySelectorAll('.tabbar button').length===6",timeout=60000); pg.wait_for_timeout(4000)
    tab=lambda t:(pg.evaluate("(t)=>document.querySelector('.tabbar [data-tab='+t+']').click()",t), pg.wait_for_timeout(900))
    txt=lambda: re.sub(r'\s+',' ',pg.evaluate("document.getElementById('eyeInfo').innerText")).strip()
    press=lambda ep:(pg.click('#epChips [data-ep="%s"]'%ep), pg.wait_for_timeout(700))
    def mode(light):
        tab('loc'); pg.evaluate("document.getElementById('scrBox').open=true"); cur=pg.evaluate("document.documentElement.dataset.detail||'full'")
        if (cur=='light')!=light: pg.click('#detailBtn')
        pg.wait_for_timeout(500)
    def barlows(*specs):
        tab('loc'); pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); (b=>{for(let d=b;d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true})(document.getElementById('epBox'))"); pg.wait_for_timeout(300)
        for i in range(3):
            s=specs[i] if i<len(specs) else None
            pg.fill('#bl%dn'%(i+1),s[0] if s else ''); pg.fill('#bl%dm'%(i+1),str(s[1]) if s else '')
    motif=lambda objet: r"^[^:]+ : grossissement ×\d+, champ réel [\d,]+[°′″]\. "+objet+r" : [^.]+\. Constellation au centre du champ : [^.]+\. Vue à \d\d:\d\d\.$"
    # Lune, 17 mm
    mode(False); tab('eye'); press('e17'); d=txt()
    check('mode détaillé, Lune : le texte complet est conservé (« vue comme un objet », repères du terminateur, Z, aide au doigt)','vue comme un objet de' in d and 'Repères à observer' in d and 'Z : direction du zénith' in d and 'Fais glisser le ciel' in d and re.match(r"^Ethos 17 mm : grossissement ×88, champ réel 1,1°\. Lune : 32′, vue comme",d),d[:200])
    mode(True); tab('eye'); a=txt()
    check('mode allégé, Lune : « … grossissement ×88, champ réel 1,1°. Lune : 32′. Constellation … Vue à … »',re.match(motif('Lune'),a) and 'Ethos 17 mm : grossissement ×88, champ réel 1,1°. Lune : 32′.' in a,a)
    # objet du ciel profond
    mode(False); tab('deep'); pg.evaluate("(()=>{const a=document.querySelector('#tab-deep article.dso'); const hd=a&&a.querySelector('.dhead'); (hd||a).click()})()"); pg.wait_for_timeout(2000)
    pg.evaluate("(()=>{const b=[...document.querySelectorAll('#tab-deep button, #tab-deep a')].find(x=>/Voir à l.oculaire/.test(x.textContent)); if(b) b.click()})()"); pg.wait_for_timeout(2500)
    tab('eye'); d2=txt(); check('mode détaillé, objet du ciel profond : type, magnitude, photo et aide conservés, sans le point réservé au mode allégé',re.search(r"M\d+ : [^,]+, magnitude [\d,]+, \d+′ \(photo",d2) and 'Fais glisser le ciel' in d2,d2[:220])
    mode(True); tab('eye'); a2=txt()
    check('mode allégé, objet du ciel profond : « M2 : 13′. » (ni type, ni magnitude, ni photo)',re.match(motif(r'M\d+'),a2) and 'magnitude' not in a2 and 'photo' not in a2 and 'amas' not in a2,a2)
    # barlow : grossissement trop fort
    mode(False); barlows(('Barlow test',4)); tab('eye'); press('e8'); press('e8'); d3=txt()
    check('mode détaillé, 8 mm avec barlow ×4 : l\'avertissement du grossissement maximal utile est affiché','Au-delà du grossissement maximal utile' in d3 and 'avec Barlow test ×4' in d3,d3[:200])
    mode(True); tab('eye'); a3=txt()
    check('mode allégé, oculaire avec barlow : texte court sans l\'avertissement (champ réel et taille de l\'objet conservés ; l\'objet est celui de l\'essai précédent)',re.match(motif(r'M\d+'),a3) and 'avec Barlow test ×4' in a3 and 'Au-delà' not in a3,a3)
    # Telrad et chercheur : toujours courts
    tab('eye'); pg.evaluate("document.querySelector('button[data-ep=telrad]').click()"); pg.wait_for_timeout(1000); t1=txt()
    check('mode allégé, Telrad : toujours « Telrad : cadre de … Constellation … Vue à … »',re.match(r"^Telrad : cadre de \d+° sur \d+°, cercles rouges de 0,5°, 2° et 4° au centre, vue comme à l.œil nu \(zénith en haut\)\. Constellation au centre du champ : [^.]+\. Vue à \d\d:\d\d\.$",t1),t1)
    pg.evaluate("document.querySelector('button[data-ep=finder]').click()"); pg.wait_for_timeout(1000); t2=txt()
    check('mode allégé, chercheur : toujours « Chercheur 9×50 : champ réel de 5,6° sur le ciel. Constellation … Vue à … »',re.match(r"^Chercheur 9×50 : champ réel de 5,6° sur le ciel\. Constellation au centre du champ : [^.]+\. Vue à \d\d:\d\d\.$",t2),t2)
    check('aucune erreur JavaScript',not errs,errs[:1]); c.close(); b.close()
srv.shutdown(); shutil.rmtree(T,ignore_errors=True)
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
