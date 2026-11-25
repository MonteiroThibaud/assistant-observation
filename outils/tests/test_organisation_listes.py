# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test de « Organisation des listes » (Paramètres, Listes d'objets) : choix de la liste, objets dans l'ordre actuel, menu ⋯ (monter, descendre, premier, dernier, retirer),
glisser-déposer par la poignée ≡, clavier, « Ranger » (heure conseillée, constellation, magnitude, nom, numéro, inverser), « Annuler », « Rétablir l'ordre prévu »,
effet sur l'onglet Ciel profond (mode « Par liste »), mémorisation après rechargement. Usage : python3 test_organisation_listes.py [ADRESSE]  (le serveur de test doit tourner).
Aucun crochet de test dans la page : l'interface et la mémoire du navigateur seulement. Code de retour 0 si tout est réussi."""
import sys, datetime, json, re, unicodedata
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8896/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1)); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
SEL=['M31','M13','M42','M45','NGC 457','β Cyg','M57']
INIT="if(!localStorage.getItem('t0')){localStorage.setItem('placesV','1');localStorage.setItem('lastGps',JSON.stringify({lat:46.0345,lon:4.072,src:'gps'}));localStorage.setItem('mySel',JSON.stringify(%s));localStorage.setItem('deepLists',JSON.stringify(['sel']));localStorage.setItem('deepSort',JSON.stringify('num'));localStorage.setItem('t0','1')}"%json.dumps(SEL)
def fr(s): return unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode()
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script(INIT)
    pg.clock.install(time=datetime.datetime(2026,11,21,20,0,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(8000)
    ev=lambda js: pg.evaluate(js)
    tab=lambda t: (ev("document.querySelector('.tabbar [data-tab=%s]').click()"%t), pg.wait_for_timeout(900))
    mysel=lambda: ev("JSON.parse(localStorage.getItem('mySel')||'[]')")
    lorder=lambda: ev("JSON.parse(localStorage.getItem('listOrder')||'{}')")
    org=lambda: ev("[...document.querySelectorAll('#orgRows .orgrow')].map(r=>r.dataset.id)")
    nums=lambda: ev("[...document.querySelectorAll('#orgRows .orgn')].map(r=>+r.textContent)")
    msg=lambda: ev("document.getElementById('orgMsg').textContent")
    def ouvre():
        tab('loc'); ev("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); document.querySelectorAll('#listBox, #listBox details').forEach(d=>d.open=true)"); pg.wait_for_timeout(500)
        ev("document.getElementById('orgTitle').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
    def deep_ids():
        tab('deep'); pg.wait_for_timeout(600); return ev("[...document.querySelectorAll('#deepList article.dso')].map(a=>a.dataset.dso)")
    def menu_row(i,act):
        ev("document.getElementById('orgRows').children[%d].scrollIntoView({block:'center'})"%i); pg.wait_for_timeout(200)
        pg.click('#orgRows .orgrow:nth-child(%d) .orgmore'%(i+1)); pg.wait_for_timeout(250); pg.click('.orgpop button[data-act="%s"]'%act); pg.wait_for_timeout(350)
    def range_(act):
        ev("document.getElementById('orgRange').scrollIntoView({block:'center'})"); pg.wait_for_timeout(200)
        pg.click('#orgRange'); pg.wait_for_timeout(250); pg.click('.orgpop button[data-act="%s"]'%act); pg.wait_for_timeout(500)
    ouvre()
    check('la partie « Organisation des listes » existe, avec son menu déroulant',ev("!!document.getElementById('orgTitle')&&!!document.querySelector('#orgList')&&!!document.querySelector('.dd #dd-orgList, #dd-orgList')"))
    check('liste choisie au départ : Sélection personnelle, avec son nombre d\'objets',ev("document.getElementById('dd-orgList').parentNode.querySelector('.ddt').textContent.includes('Sélection personnelle')"),ev("document.getElementById('dd-orgList').parentNode.querySelector('.ddt').textContent"))
    check('objets de la sélection dans l\'ordre actuel (ordre d\'ajout)',org()==SEL,org())
    check('numéros 1 à 7',nums()==list(range(1,8)))
    check('« Rétablir l\'ordre prévu » masqué pour la sélection personnelle',ev("document.getElementById('orgReset').hidden"))
    # menu d'actions
    pg.click('#orgRows .orgrow:nth-child(1) .orgmore'); pg.wait_for_timeout(250)
    check('menu ⋯ du premier objet : Monter et Mettre en premier désactivés, Retirer proposé pour la sélection',ev("(()=>{const d=a=>document.querySelector('.orgpop button[data-act=\"'+a+'\"]'); return d('up').disabled&&d('first').disabled&&!d('down').disabled&&!!d('remove')})()"))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    menu_row(2,'first'); check('Mettre en premier (M42)',org()[0]=='M42' and mysel()==org(),org())
    check('message avec « Annuler »',ev("!!document.getElementById('orgUndo')") and 'premier' in msg(),msg())
    ids=deep_ids(); check('onglet Ciel profond (Par liste) : même ordre que la sélection',ids==mysel(),ids)
    ouvre(); menu_row(0,'last'); check('Mettre en dernier (M42)',org()[-1]=='M42',org())
    menu_row(6,'up'); check('Monter (M42 d\'un rang)',org()[-2]=='M42',org())
    menu_row(0,'down'); check('Descendre (M31 d\'un rang)',org()[1]=='M31',org())
    pg.click('#orgUndo'); pg.wait_for_timeout(300); check('Annuler remet l\'ordre précédent (M31 en premier)',org()[0]=='M31',org())
    # glisser-déposer par la poignée
    def drag_row(i_from,i_to,after=False):
        ev("document.getElementById('orgRows').children[0].scrollIntoView({block:'start'})"); ev("window.scrollBy(0,-120)"); pg.wait_for_timeout(200)
        h=pg.locator('#orgRows .orgrow').nth(i_from).locator('.orgh').bounding_box(); t=pg.locator('#orgRows .orgrow').nth(i_to).bounding_box()
        y1=h['y']+h['height']/2; y2=t['y']+(t['height']*0.75 if after else t['height']*0.25)
        pg.mouse.move(h['x']+h['width']/2,y1); pg.mouse.down(); pg.mouse.move(h['x']+h['width']/2,(y1+y2)/2,steps=6); pg.mouse.move(h['x']+h['width']/2,y2,steps=6); pg.wait_for_timeout(120)
        lift=ev("!!document.querySelector('#orgRows .orgrow.lift')"); ligne=ev("!!document.querySelector('#orgRows .orgline')")
        pg.mouse.up(); pg.wait_for_timeout(400); return lift,ligne
    before=org(); lift,ligne=drag_row(4,1); after=org()
    check('glisser : rangée soulevée et ligne d\'insertion pendant le geste',lift and ligne)
    check('glisser NGC 457 de la 5e à la 2e place',after==[before[0],before[4],before[1],before[2],before[3],before[5],before[6]],after)
    check('glisser : mémorisé dans la sélection',mysel()==after)
    before=org(); drag_row(1,6,after=True); after=org(); check('glisser vers la fin (2e → dernière place)',after[-1]==before[1],after)
    # clavier
    ev("document.querySelector('#orgRows .orgrow:last-child .orgh').focus()"); pg.keyboard.press('ArrowUp'); pg.wait_for_timeout(300); a2=org(); check('clavier : flèche haut déplace l\'objet d\'un rang',a2[-2]==after[-1],a2)
    pg.keyboard.press('Home'); pg.wait_for_timeout(300); check('clavier : Début place l\'objet en premier',org()[0]==after[-1],org())
    # Ranger
    def txt_list():  # ordre de l'onglet Ciel profond, avec les textes affichés
        tab('deep'); pg.wait_for_timeout(600)
        return ev("[...document.querySelectorAll('#deepList article.dso')].map(a=>({id:a.dataset.dso,nom:(a.querySelector('.dname')||{}).textContent||'',best:(a.querySelector('.dbest')||{}).textContent||'',meta:(a.querySelector('.dmeta')||{}).textContent||''}))")
    num_fr=lambda s: float(s.replace(',','.'))
    ouvre(); range_('num'); check('Ranger par numéro de catalogue',org()==['M13','M31','M42','M45','M57','NGC 457','β Cyg'],org())
    range_('mag'); L=txt_list(); mg=[num_fr(re.search(r'magnitudes? (\d+(?:,\d+)?)',x['meta']).group(1)) for x in L]; check('Ranger du plus brillant au plus faible : magnitudes croissantes',mg==sorted(mg),mg)
    ouvre(); range_('cons'); L=txt_list(); cs=[re.search(r'dans ([^.]+)\.',x['meta']).group(1) for x in L]; check('Ranger par constellation : ordre alphabétique des constellations',[fr(x) for x in cs]==sorted(fr(x) for x in cs),cs)
    ouvre(); range_('name'); L=txt_list(); nm=[fr(x['nom'] or x['id']) for x in L]; check('Ranger par nom : ordre alphabétique',nm==sorted(nm),[x['nom'] or x['id'] for x in L])
    ouvre(); range_('time'); L=txt_list(); hs=[]
    for x in L:
        m=re.match(r'(\d+):(\d+)',x['best']); hs.append(((int(m.group(1))+(24 if int(m.group(1))<12 else 0))*60+int(m.group(2))) if m else 99999)
    check('Ranger par heure conseillée : heures croissantes dans la nuit, objets trop bas à la fin',hs==sorted(hs),[x['best'] for x in L])
    ouvre(); before=org(); range_('rev'); check('Inverser l\'ordre',org()==before[::-1],org())
    pg.click('#orgUndo'); pg.wait_for_timeout(300); check('Annuler après un rangement',org()==before,org())
    # mode « Par heure conseillée » : l'ordre manuel ne s'applique pas
    ev("localStorage.setItem('deepSort',JSON.stringify('time'))"); pg.reload(); pg.wait_for_timeout(8000); L=txt_list(); hs=[]
    for x in L:
        m=re.match(r'(\d+):(\d+)',x['best']); hs.append(((int(m.group(1))+(24 if int(m.group(1))<12 else 0))*60+int(m.group(2))) if m else 99999)
    check('mode « Par heure conseillée » inchangé (tri par heure, indépendant de l\'ordre réglé)',hs==sorted(hs) and len(L)==7)
    ev("localStorage.setItem('deepSort',JSON.stringify('num'))"); pg.reload(); pg.wait_for_timeout(8000)
    # ordre des entrées du menu ⋯ : premier, dernier, monter, descendre, puis tout en bas « Retirer »
    ouvre(); ev("document.getElementById('orgRows').children[3].scrollIntoView({block:'center'})"); pg.wait_for_timeout(200); pg.click('#orgRows .orgrow:nth-child(4) .orgmore'); pg.wait_for_timeout(250)
    ordre=ev("[...document.querySelectorAll('.orgpop button[data-act]')].map(b=>b.dataset.act)"); check('menu ⋯ : premier, dernier, monter, descendre, puis Retirer tout en bas',ordre==['first','last','up','down','remove'],ordre)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    # retrait de la sélection : confirmation demandée avant de retirer
    compte=lambda: ev("(()=>{const c=document.querySelector('#listChecks input[data-list=\"sel\"]'); return {menu:document.getElementById('dd-orgList').parentNode.querySelector('.ddt').textContent, case:c?c.parentNode.querySelector('small').textContent:null}})()")
    n0=len(org()); first=org()[0]; c0=compte(); check('compteurs de la sélection au départ : %d objets'%n0,('(%d)'%n0) in c0['menu'] and c0['case']=='%d objets'%n0,c0)
    ev("document.getElementById('orgRows').children[0].scrollIntoView({block:'center'})"); pg.wait_for_timeout(200); pg.click('#orgRows .orgrow:nth-child(1) .orgmore'); pg.wait_for_timeout(250); pg.click('.orgpop button[data-act="remove"]'); pg.wait_for_timeout(250)
    check('Retirer : une confirmation est demandée, rien n\'est encore retiré',ev("!!document.querySelector('.orgpop button[data-act=\"remove-ok\"]')&&!!document.querySelector('.orgpop button[data-act=\"remove-no\"]')&&document.querySelector('.orgpop .orgconf').textContent.includes('%s')"%first) and len(org())==n0 and first in mysel(),ev("document.querySelector('.orgpop').textContent")[:80])
    check('la confirmation propose « Garder » en premier choix (focus)',ev("document.activeElement&&document.activeElement.dataset.act==='remove-no'"))
    pg.click('.orgpop button[data-act="remove-no"]'); pg.wait_for_timeout(250); check('Garder : rien n\'est retiré, la fenêtre se ferme',len(org())==n0 and org()[0]==first and ev("document.querySelector('.orgpop').hidden"))
    pg.click('#orgRows .orgrow:nth-child(1) .orgmore'); pg.wait_for_timeout(250); pg.click('.orgpop button[data-act="remove"]'); pg.wait_for_timeout(250); pg.click('.orgpop button[data-act="remove-ok"]'); pg.wait_for_timeout(400)
    c1=compte(); check('Retirer, puis confirmer : l\'objet est retiré de la liste et de la sélection',len(org())==n0-1 and first not in org() and first not in mysel(),org())
    check('compteurs mis à jour après le retrait (%d objets)'%(n0-1),('(%d)'%(n0-1)) in c1['menu'] and c1['case']=='%d objets'%(n0-1),c1)
    pg.click('#orgUndo'); pg.wait_for_timeout(300); c2=compte(); check('Annuler le retrait remet l\'objet et les compteurs',len(org())==n0 and org()[0]==first and ('(%d)'%n0) in c2['menu'] and c2['case']=='%d objets'%n0,c2)
    # étoile d'une fiche (onglet Ciel profond) : les compteurs et la liste se mettent à jour sans rouvrir le menu
    ev("localStorage.setItem('deepLists',JSON.stringify(['m','sel']))"); pg.reload(); pg.wait_for_timeout(8000); ouvre()
    tab('deep'); pg.wait_for_timeout(500); ev("document.querySelector('#deepList article.dso[data-dso=\"M1\"] .dhead').click()"); pg.wait_for_timeout(500); ev("document.querySelector('.starbtn[data-star=\"M1\"]').click()"); pg.wait_for_timeout(500)
    tab('loc'); c3=compte(); check('étoile ajoutée dans une fiche : compteurs à jour dans Paramètres (%d objets)'%(n0+1),('(%d)'%(n0+1)) in c3['menu'] and c3['case']=='%d objets'%(n0+1),c3)
    check('étoile ajoutée : l\'objet apparaît en fin de liste dans l\'organisation',org()[-1]=='M1' and len(org())==n0+1,org()[-2:])
    tab('deep'); ev("document.querySelector('.starbtn[data-star=\"M1\"]').click()"); pg.wait_for_timeout(500); tab('loc'); c4=compte(); check('étoile retirée dans une fiche : compteurs et liste à jour',('(%d)'%n0) in c4['menu'] and c4['case']=='%d objets'%n0 and 'M1' not in org(),c4)
    ev("localStorage.setItem('deepLists',JSON.stringify(['sel']))"); pg.reload(); pg.wait_for_timeout(8000); ouvre()
    # autre liste : Catalogue de Messier
    pg.click('#dd-orgList >> xpath=../button'); pg.wait_for_timeout(300); pg.click('#dd-orgList .ddopt:has-text("Catalogue de Messier")'); pg.wait_for_timeout(500)
    o=org(); check('autre liste (Messier) : 110 objets dans l\'ordre prévu',len(o)==110 and o[0]=='M1' and o[-1]=='M110',(len(o),o[:2],o[-1:]))
    check('autre liste : « Rétablir l\'ordre prévu » masqué tant que rien n\'est réglé',ev("document.getElementById('orgReset').hidden"))
    menu_row(0,'last'); check('Messier : M1 placé en dernier, ordre mémorisé par liste',org()[-1]=='M1' and org()[0]=='M2' and lorder().get('m',[None])[-1]=='M1',(org()[:2],org()[-1]))
    pg.click('#orgRows .orgrow:nth-child(3) .orgmore'); pg.wait_for_timeout(250); check('autre liste : pas de « Retirer » (réservé à la sélection personnelle)',ev("!document.querySelector('.orgpop button[data-act=\"remove\"]')")); pg.keyboard.press('Escape')
    check('« Rétablir l\'ordre prévu » proposé après un réglage',not ev("document.getElementById('orgReset').hidden"))
    ev("localStorage.setItem('deepLists',JSON.stringify(['m']))"); pg.reload(); pg.wait_for_timeout(8000); ids=deep_ids(); check('Ciel profond (Par liste) : Messier suit l\'ordre réglé (M2 … M110, M1)',ids[0]=='M2' and ids[-1]=='M1' and len(ids)==110,(ids[:2],ids[-1:]))
    ouvre(); pg.click('#dd-orgList >> xpath=../button'); pg.wait_for_timeout(300); pg.click('#dd-orgList .ddopt:has-text("Catalogue de Messier")'); pg.wait_for_timeout(400); pg.click('#orgReset'); pg.wait_for_timeout(400)
    check('Rétablir l\'ordre prévu (Messier)',org()[0]=='M1' and org()[-1]=='M110' and 'm' not in lorder(),lorder())
    # mémorisation après rechargement (sélection)
    ouvre(); pg.click('#dd-orgList >> xpath=../button'); pg.wait_for_timeout(300); pg.click('#dd-orgList .ddopt:has-text("Sélection personnelle")'); pg.wait_for_timeout(400); menu_row(3,'first'); mem=org(); pg.reload(); pg.wait_for_timeout(8000); ouvre()
    check('ordre de la sélection gardé après rechargement',org()==mem,org())
    check('listes dynamiques absentes du menu (comètes, petites planètes)',ev("![...document.querySelectorAll('#orgList option')].some(o=>/Comètes|Petites planètes/.test(o.textContent))"))
    check('aucune erreur JavaScript',not errs,errs[:1] or 'aucune')
    # sélection vide
    c2=b.new_context(viewport={'width':411,'height':850},is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation']); q=c2.new_page(); q.clock.install(time=datetime.datetime(2026,11,21,20,0,tzinfo=tz)); q.goto(URL); q.wait_for_timeout(8000)
    q.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); q.wait_for_timeout(600); q.evaluate("document.querySelectorAll('#listBox, #listBox details').forEach(d=>d.open=true)"); q.wait_for_timeout(400)
    check('sélection vide : message d\'aide, bouton Ranger désactivé',q.evaluate("document.querySelector('#orgRows .orgempty')&&document.getElementById('orgRange').disabled"),q.evaluate("(document.querySelector('#orgRows .orgempty')||{}).textContent"))
    b.close()
ok=all(res); print('\nBILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if ok else 1)
