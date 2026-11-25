#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test du bouton du carnet de l'onglet « Ciel profond et petits corps » : dans l'en-tête du cadre « Pour trouver l'objet », à gauche de « Maintenant »,
mêmes taille, police et hauteur ; libellé complet si la largeur le permet, sinon « + Noter » ; « Voir à l'oculaire › » sous le cadre.
Usage : python3 test_carnet_ciel_profond.py [ADRESSE_DE_LA_PAGE]  (par défaut http://localhost:8870/index.html). Le serveur de test doit tourner."""
import sys, datetime
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8870/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1)); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
MESURE="""()=>{ const f=document.querySelector('#tab-deep .finderbox .findhead'); if(!f) return null; const lg=f.querySelector('.logbtn'), nw=f.querySelector('.nowbtn'), ar=document.querySelector('#tab-deep article.dso.open');
  const R=e=>{const r=e.getBoundingClientRect(); return {x:r.x,r:r.right,w:r.width,h:r.height}}; const S=e=>{const c=getComputedStyle(e); return [c.fontSize,c.fontFamily,c.paddingTop,c.paddingBottom,c.paddingLeft,c.paddingRight,c.minHeight,c.lineHeight,c.fontWeight,c.borderRadius].join('|')};
  const ordre=[...f.children].map(e=>e.tagName+(e.className?'.'+String(e.className).split(' ').pop():''));
  return {log:R(lg),now:R(nw),sl:S(lg),sn:S(nw),txt:lg.textContent,coupe:lg.scrollWidth>lg.clientWidth+1,deb:f.scrollWidth>f.clientWidth+1,ordre,
    eyeDansTete:!!f.querySelector('.eyelink'),lien:(()=>{const e=f.parentNode.querySelector('.findeye .eyelink'), sv=f.parentNode.querySelector('svg'); if(!e||!sv) return null; const r=e.getBoundingClientRect(), h=f.getBoundingClientRect(), v=sv.getBoundingClientRect(); return {apresEntete:r.top>=h.bottom-1, avantCarte:r.bottom<=v.top+1, ecart:Math.round(v.top-r.bottom)} })(),cardbtns:!!ar.querySelector('.cardbtns'),page:document.documentElement.scrollWidth>document.documentElement.clientWidth} }"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for (w,h,dpr,court) in ((411,850,2.625,True),(360,780,3,True),(320,568,2,True),(891,411,2.625,False)):
        c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,is_mobile=w<600,has_touch=w<600,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.clock.install(time=datetime.datetime(2026,11,21,21,30,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(7000)
        pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(2500)
        pg.evaluate("(()=>{const a=document.querySelector('#tab-deep article.dso'); const hd=a&&a.querySelector('.dhead'); (hd||a).click()})()"); pg.wait_for_timeout(2500)
        m=pg.evaluate(MESURE); tag='%dx%d'%(w,h)
        if not m: check('fiche ouverte avec son cadre (%s)'%tag,False); c.close(); continue
        check('(%s) l\'en-tête contient le titre, le bouton du carnet puis « Maintenant »'%tag,m['ordre'][-2:]==['BUTTON.logbtn','BUTTON.nowbtn'] and m['ordre'][0]=='H4' and not m['eyeDansTete'],m['ordre'])
        check('(%s) le bouton du carnet est à gauche de « Maintenant »'%tag,m['log']['r']<=m['now']['x']+0.5,(m['log'],m['now']))
        check('(%s) mêmes taille de police, police, marges et hauteur de ligne que « Maintenant »'%tag,m['sl']==m['sn'],(m['sl'],m['sn']))
        check('(%s) même hauteur que « Maintenant »'%tag,abs(m['log']['h']-m['now']['h'])<0.6,(m['log']['h'],m['now']['h']))
        check('(%s) libellé %s, texte entier, en-tête sans débordement'%(tag,'court « + Noter » (la largeur ne permet pas le texte complet)' if court else 'complet (la largeur le permet)'),(m['txt']=='+ Noter' if court else m['txt']=='+ Noter dans le carnet') and not m['coupe'] and not m['deb'] and not m['page'],m)
        check('(%s) « Voir à l\'oculaire › » est juste au-dessus de la carte (sous l\'en-tête), et il n\'y a plus de ligne de boutons sous la fiche'%tag,m['lien'] is not None and m['lien']['apresEntete'] and m['lien']['avantCarte'] and m['lien']['ecart']<=12 and not m['cardbtns'],(m['lien'],m['cardbtns']))
        pg.click('#tab-deep .findhead .logbtn'); pg.wait_for_timeout(500)
        m2=pg.evaluate(MESURE)
        check('(%s) après avoir noté : libellé « Noté à HH:MM ✓ » (s\'il tient) ou « ✓ HH:MM », sans coupure ni débordement'%tag,(m2['txt'].startswith('Noté à ') or m2['txt'].startswith('✓ ')) and not m2['coupe'] and not m2['deb'],m2['txt'])
        n=pg.evaluate("JSON.parse(localStorage.getItem('carnet')||'[]').length"); check('(%s) l\'entrée est dans le carnet'%tag,n==1,n)
        if w==411:
            pg.click('#tab-deep .findeye .eyelink'); pg.wait_for_timeout(1200)
            check('le lien « Voir à l\'oculaire › » ouvre l\'onglet À l\'oculaire',pg.evaluate("!document.getElementById('tab-eye').hidden"))
            pg.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); pg.wait_for_timeout(800)
        if w==411:
            pg.evaluate("document.querySelector('.tabbar [data-tab=det]').click()"); pg.wait_for_timeout(1500)
            d=pg.evaluate("(()=>{const l=document.querySelector('#tab-det .cardbtns .logbtn'); return l?{txt:l.textContent,dansTete:!!l.closest('.findhead')}:null})()")
            check('Détail planète : le bouton du carnet reste sous le cadre, libellé complet',d is not None and not d['dansTete'] and d['txt']=='+ Noter dans le carnet' or (d is not None and d['txt'].startswith('Noté')),d)
        check('(%s) aucune erreur JavaScript'%tag,not errs,errs[:1]); c.close()
    b.close()
print('BILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
