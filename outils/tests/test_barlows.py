# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Test des barlows (Paramètres, Mes oculaires ; onglet À l'oculaire) et du bouton « Noter dans le carnet » de l'en-tête de l'onglet À l'oculaire.
Usage : python3 test_barlows.py [ADRESSE]  (le serveur de test doit tourner). Aucun crochet de test dans la page : interface et mémoire du navigateur seulement.
Code de retour 0 si tout est réussi."""
import sys, datetime, json, re
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8896/index.html'
tz=datetime.timezone(datetime.timedelta(hours=1)); res=[]
def check(nom,ok,detail=''):
    res.append(bool(ok)); print(('RÉUSSI ' if ok else 'ÉCHEC  ')+nom+((' : '+str(detail)) if detail!='' else ''),flush=True)
INIT="if(!localStorage.getItem('t0')){localStorage.setItem('placesV','1');localStorage.setItem('lastGps',JSON.stringify({lat:46.0345,lon:4.072,src:'gps'}));localStorage.setItem('t0','1')}"
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script(INIT)
    pg.clock.install(time=datetime.datetime(2026,11,21,20,30,tzinfo=tz)); pg.goto(URL); pg.wait_for_timeout(8000)
    ev=lambda js: pg.evaluate(js)
    def tab(t): ev("document.querySelector('.tabbar [data-tab=%s]').click()"%t); pg.wait_for_timeout(700)
    def efface(sel):                         # effacement d'une barlow : confirmation dans la fenêtre de l'application
        pg.click('#'+sel); pg.wait_for_timeout(250); pg.click('.orgpop [data-act="ok"]'); pg.wait_for_timeout(250)
    def ouvre_ep():
        tab('loc'); ev("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); (b=>{for(let d=b;d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true})(document.getElementById('epBox'))"); pg.wait_for_timeout(300)
    def barlows(*specs):                   # specs : (nom, facteur) ou None par place
        ouvre_ep()
        for i in range(3):
            s=specs[i] if i<len(specs) else None
            pg.fill('#bl%dn'%(i+1),s[0] if s else ''); pg.fill('#bl%dm'%(i+1),str(s[1]) if s else '')
    chips=lambda: ev("[...document.querySelectorAll('#epChips button')].map(b=>b.textContent)")
    info=lambda: ev("document.getElementById('eyeInfo').textContent")
    strong=lambda: ev("(document.querySelector('#eyeInfo strong')||{}).textContent||''")
    def press(ep):
        pg.click('#epChips [data-ep="%s"]'%ep); pg.wait_for_timeout(500)
    ouvre_ep()
    check('zone Barlows : trois places vides au départ',ev("[1,2,3].every(i=>document.getElementById('bl'+i+'n').value===''&&document.getElementById('bl'+i+'m').value==='')")
          and ev("!!document.querySelector('#epBox .fhead')"))
    tab('eye'); pg.wait_for_timeout(600)
    s0=strong(); check('sans barlow : vue inchangée (Ethos 17 mm, ×88)','grossissement ×88' in s0 and 'avec' not in s0,s0)
    press('e17'); check('sans barlow : un deuxième appui garde le comportement actuel (recentrage, pas de changement)',strong()==s0 and chips()==['31 mm','17 mm','8 mm','5 mm','Chercheur','Telrad'],(strong(),chips()))
    # barlows 1 et 2
    barlows(('Barlow Tele Vue',2),('Powermate',3)); eb=json.loads(ev("localStorage.getItem('eyeCfg4')"))['bars']
    check('deux barlows enregistrées (la troisième vide)',eb[0]['n']=='Barlow Tele Vue' and eb[0]['m']==2 and eb[1]['m']==3 and eb[2]['m']==0,eb)
    tab('eye'); press('e17'); s1=strong()
    check('2e appui sur « 17 mm » : barlow 1 (×2) : grossissement ×176, champ réel 34′','avec Barlow Tele Vue ×2' in s1 and 'grossissement ×176' in s1 and 'champ réel 34′' in info(),info()[:90])
    check('puce « 17 ×2 » (sur téléphone, « mm » est omis quand la puce est trop étroite), avec ×2 en évidence',chips()[1]=='17×2' and ev("!!document.querySelector('#epChips .bx')"),chips())
    press('e17'); s2=strong(); check('3e appui : barlow 2 (×3) : ×265, champ réel 23′','avec Powermate ×3' in s2 and 'grossissement ×265' in s2 and 'champ réel 23′' in info() and chips()[1]=='17×3',(info()[:90],chips()[1]))
    press('e17'); s3=strong(); check('4e appui : retour sans barlow (×88, 1,1°)','grossissement ×88' in s3 and 'avec' not in s3 and chips()[1]=='17 mm',s3)
    # changer d'oculaire remet « sans barlow »
    press('e17'); press('e8'); check('changer d\'oculaire remet « sans barlow » (8 mm : ×188)','grossissement ×188' in strong() and not ev("!!document.querySelector('#epChips .bx')"),strong())
    press('e8'); check('8 mm puis un deuxième appui : barlow 1 (×375)','grossissement ×375' in strong() and chips()[2]=='8 mm×2',(strong(),chips()))
    # Chercheur et Telrad : aucune barlow
    press('finder'); check('Chercheur : barlow sans effet (pas de puce ×, pas de texte barlow)',not ev("!!document.querySelector('#epChips .bx')") and 'barlow' not in info().lower(),info()[:80])
    press('finder'); check('Chercheur : un nouvel appui ne déclenche pas de barlow',not ev("!!document.querySelector('#epChips .bx')"))
    press('telrad'); press('telrad'); check('Telrad : le cycle 10° → 20° garde son comportement',chips()[-1]=='Telrad 20°',chips()[-1])
    press('telrad'); press('telrad'); press('e17'); check('retour à un oculaire : sans barlow (état remis à zéro)','grossissement ×88' in strong() and 'avec' not in strong(),strong())
    # grossissement maximal utile
    press('h5'); press('h5'); press('h5'); w=info(); check('5 mm avec ×3 (×900) : avertissement du grossissement maximal utile (×600)','grossissement ×900' in w and 'Au-delà du grossissement maximal utile (×600)' in w,w[:140])
    press('h5'); press('h5'); w2=info()      # barlow 2 -> sans barlow -> barlow 1 (×600) : pas d'avertissement à ×600
    check('5 mm avec ×2 (×600) : pas d\'avertissement (limite non dépassée)','grossissement ×600' in w2 and 'Au-delà' not in w2,w2[:120])
    press('e17'); check('sans barlow, jamais d\'avertissement (×88 ; 5 mm seul : ×300)','Au-delà' not in info())
    # une seule barlow, en troisième place
    barlows(None,None,('Triplet',2.5)); tab('eye'); press('e17'); sT=strong()
    check('barlow en place 3 seule : le premier appui l\'active (×221)','avec Triplet ×2,5' in sT and 'grossissement ×221' in sT,sT)
    press('e17'); check('puis retour sans barlow (deux états seulement)','grossissement ×88' in strong() and 'avec' not in strong())
    # saisies invalides
    ouvre_ep(); pg.fill('#bl1m','0,5'); m1=ev("document.getElementById('epMsg').textContent"); eb=json.loads(ev("localStorage.getItem('eyeCfg4')"))['bars']
    check('facteur trop petit (0,5) refusé avec un message, rien d\'enregistré',('entre 1,1 et 10' in m1) and eb[0]['m']==0,(m1[:70],eb[0]))
    pg.fill('#bl1m','11'); check('facteur trop grand (11) refusé',json.loads(ev("localStorage.getItem('eyeCfg4')"))['bars'][0]['m']==0)
    pg.fill('#bl1m','1,1'); pg.fill('#bl2m','10'); eb=json.loads(ev("localStorage.getItem('eyeCfg4')"))['bars']; check('bornes acceptées (1,1 et 10)',eb[0]['m']==1.1 and eb[1]['m']==10,eb[:2])
    efface('bl1x'); efface('bl2x'); eb=json.loads(ev("localStorage.getItem('eyeCfg4')"))['bars']; check('bouton ✕ : la barlow est effacée (nom et facteur)',eb[0]['m']==0 and eb[0]['n']=='' and ev("document.getElementById('bl1m').value===''"),eb[:2])
    # Enregistrer, Restituer, Défaut
    barlows(('A',2),('B',3),('C',4)); pg.click('#epSave'); pg.wait_for_timeout(300); efface('bl2x'); pg.wait_for_timeout(200)
    pg.click('#epLoad'); pg.wait_for_timeout(400); eb=json.loads(ev("localStorage.getItem('eyeCfg4')"))['bars']; check('Enregistrer puis Restituer : les trois barlows reviennent',[x['m'] for x in eb]==[2,3,4] and ev("document.getElementById('bl2m').value")=='3',eb)
    check('état enregistré : le résumé cite les barlows','barlows' in ev("document.getElementById('epSaveStatus').textContent"),ev("document.getElementById('epSaveStatus').textContent")[-70:])
    pg.click('#epReset'); pg.wait_for_timeout(400); eb=json.loads(ev("localStorage.getItem('eyeCfg4')"))['bars']; check('Défaut : aucune barlow',all(x['m']==0 for x in eb),eb)
    # mémorisation après rechargement, état non mémorisé
    barlows(('Barlow Tele Vue',2),('Powermate',3)); tab('eye'); press('e17'); pg.reload(); pg.wait_for_timeout(8000); ouvre_ep()
    check('après rechargement : les barlows sont gardées',ev("document.getElementById('bl1n').value")=='Barlow Tele Vue' and ev("document.getElementById('bl2m').value")=='3')
    tab('eye'); check('après rechargement : l\'application s\'ouvre sans barlow','avec' not in strong() and not ev("!!document.querySelector('#epChips .bx')"),strong())
    # bouton « Noter dans le carnet » (option A)
    geo=ev("(()=>{const n=document.getElementById('eyeNow').getBoundingClientRect(), l=document.querySelector('#eyeLog .logbtn'); if(!l) return null; const r=l.getBoundingClientRect(), nm=document.querySelector('#tab-eye .objname').getBoundingClientRect(); return {nowY:n.bottom,logY:r.top,dx:Math.abs(n.left-r.left),dw:Math.abs(n.width-r.width),txt:l.textContent,overlapNom:!(r.left>nm.right||r.right<nm.left||r.top>nm.bottom||r.bottom<nm.top),overlapNow:!(r.left>n.right||r.right<n.left||r.top>n.bottom||r.bottom<n.top)}})()")
    check('bouton du carnet (« + Noter ») sous « Maintenant », même largeur, sans chevauchement',geo and geo['txt']=='+ Noter' and geo['logY']>=geo['nowY'] and geo['dx']<1.5 and geo['dw']<1.5 and not geo['overlapNom'] and not geo['overlapNow'],geo)
    pg.click('#eyeLog .logbtn'); pg.wait_for_timeout(400); lab=ev("document.querySelector('#eyeLog .logbtn').textContent")
    check('un appui note l\'astre (Lune) et le bouton devient « ✓ HH:MM »',lab.startswith('✓ '),lab)
    tab('loc'); ev("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); document.getElementById('carnetBox').open=true"); pg.wait_for_timeout(400)
    row=ev("(()=>{const l=document.querySelector('#carnetList li'); return l?{nom:l.querySelector('b').textContent,sub:l.querySelector('.clsub').textContent}:null})()")
    check('carnet : entrée « Lune » avec l\'oculaire utilisé (sans barlow)',row and row['nom']=='Lune' and 'Ethos 17 mm (×88)' in row['sub'],row)
    # objet du ciel profond avec barlow active : l'entrée cite la barlow
    tab('deep'); ev("document.querySelector('#deepList article.dso[data-dso=\"M57\"] .dhead').click()"); pg.wait_for_timeout(600); ev("document.querySelector('.eyelink[data-eye=\"M57\"]').click()"); pg.wait_for_timeout(1200)
    check('M57 à l\'oculaire : le bouton est proposé, non encore noté',ev("document.querySelector('#eyeLog .logbtn').textContent")=='+ Noter')
    press('e17'); press('e17'); sx=strong(); pg.click('#eyeLog .logbtn'); pg.wait_for_timeout(400)
    tab('loc'); ev("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); document.getElementById('carnetBox').open=true"); pg.wait_for_timeout(400)
    row=ev("(()=>{const l=document.querySelector('#carnetList li'); return l?{nom:l.querySelector('b').textContent,sub:l.querySelector('.clsub').textContent}:null})()")
    check('carnet : « M57 (Anneau de la Lyre) » avec « Ethos 17 mm avec Powermate ×3 (×265) »',row and row['nom']=='M57 (Anneau de la Lyre)' and 'Ethos 17 mm avec Powermate ×3 (×265)' in row['sub'] and 'avec Powermate ×3' in sx,row)
    tab('deep'); pg.wait_for_timeout(300)
    check('la fiche du ciel profond montre aussi « Noté à … ✓ » pour M57 (notée depuis l\'oculaire)',ev("(()=>{const b=document.querySelector('#deepList article.dso[data-dso=\"M57\"] .logbtn'); return !!b&&/^Noté à .* ✓$/.test(b.textContent)})()"))
    # carnet : noté depuis une fiche du ciel profond, aucun matériel n'est précisé
    tab('deep'); ev("document.querySelector('#deepList article.dso[data-dso=\"M13\"] .dhead')&&document.querySelector('#deepList article.dso[data-dso=\"M13\"] .dhead').click()"); pg.wait_for_timeout(500)
    ev("localStorage.setItem('deepLists',JSON.stringify(['m']))"); pg.reload(); pg.wait_for_timeout(8000); tab('deep'); ev("document.querySelector('#deepList article.dso[data-dso=\"M13\"] .dhead').click()"); pg.wait_for_timeout(600)
    ev("document.querySelector('#deepList article.dso[data-dso=\"M13\"] .logbtn').click()"); pg.wait_for_timeout(500)
    tab('loc'); ev("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); document.getElementById('carnetBox').open=true"); pg.wait_for_timeout(400)
    row=ev("(()=>{const l=[...document.querySelectorAll('#carnetList li')].find(x=>/M13/.test(x.querySelector('b').textContent)); return l?{nom:l.querySelector('b').textContent,sub:l.querySelector('.clsub').textContent}:null})()")
    check('carnet : noté depuis la fiche du ciel profond (M13), aucune mention du matériel',row and 'Ethos' not in row['sub'] and 'Barlow' not in row['sub'] and 'mm' not in row['sub'] and not row['sub'].rstrip().endswith(','),row)
    carnet_txt=ev("(()=>{const l=[...document.querySelectorAll('#carnetList li')].find(x=>/M57/.test(x.querySelector('b').textContent)); return l?l.querySelector('.clsub').textContent:''})()")
    check('carnet : l\'entrée notée depuis l\'oculaire (M57) garde l\'oculaire et la barlow','Powermate' in carnet_txt or 'Barlow' in carnet_txt,carnet_txt)
    # mise en page de l'en-tête à 320 points (nouveau contexte : la fenêtre ne peut plus être redimensionnée en plein écran)
    c2=b.new_context(viewport={'width':320,'height':568},device_scale_factor=1,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation']); q=c2.new_page(); q.add_init_script(INIT); q.clock.install(time=datetime.datetime(2026,11,21,20,30,tzinfo=tz)); q.goto(URL); q.wait_for_timeout(8000)
    q.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); q.wait_for_timeout(1200)
    g2=q.evaluate("(()=>{const n=document.getElementById('eyeNow').getBoundingClientRect(), l=document.querySelector('#eyeLog .logbtn').getBoundingClientRect(), nm=document.querySelector('#tab-eye .objname').getBoundingClientRect(); return {horsEcran:Math.max(n.right,l.right)>document.documentElement.clientWidth+1, chevauche:!(l.left>nm.right||l.right<nm.left||l.top>nm.bottom||l.bottom<nm.top), debord:document.documentElement.scrollWidth>document.documentElement.clientWidth+1}})()")
    check('en-tête à 320 points : rien ne déborde ni ne se chevauche',not g2['horsEcran'] and not g2['chevauche'] and not g2['debord'],g2)
    # libellé de la puce avec barlow : « 17 ×2 » quand les puces ne tiennent pas sur une ligne
    q.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); q.wait_for_timeout(500); q.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); (b=>{for(let d=b;d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true})(document.getElementById('epBox'))"); q.wait_for_timeout(300)
    q.fill('#bl1n','Barlow'); q.fill('#bl1m','2'); q.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); q.wait_for_timeout(800); q.click('#epChips [data-ep=\"e17\"]'); q.wait_for_timeout(600)
    pt0=q.evaluate("(()=>{const c=document.getElementById('epChips'), k=[...c.children]; return {lib:k[1].textContent, deborde:k[1].scrollWidth>k[1].clientWidth}})()")
    check('320 points, barlow active : la puce est « 17 ×2 » (sans « mm »), sans débordement',pt0['lib']=='17×2' and not pt0['deborde'],pt0)
    c3=b.new_context(viewport={'width':1280,'height':800},device_scale_factor=1,timezone_id='Europe/Paris',locale='fr-FR'); w3=c3.new_page(); w3.add_init_script(INIT); w3.clock.install(time=datetime.datetime(2026,11,21,20,30,tzinfo=tz)); w3.goto(URL); w3.wait_for_timeout(8000)
    w3.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); w3.wait_for_timeout(500); w3.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false); (b=>{for(let d=b;d;d=d.parentElement&&d.parentElement.closest('details'))d.open=true})(document.getElementById('epBox'))"); w3.wait_for_timeout(300)
    w3.fill('#bl1n','Barlow'); w3.fill('#bl1m','2'); w3.evaluate("document.querySelector('.tabbar [data-tab=eye]').click()"); w3.wait_for_timeout(800); w3.click('#epChips [data-ep=\"e17\"]'); w3.wait_for_timeout(600)
    lib3=w3.evaluate("(()=>{const k=document.querySelectorAll('#epChips button')[1]; return k.textContent+'|'+(k.scrollWidth>k.clientWidth)})()")
    check('grand écran (1280 points), barlow active : la place suffit, la puce garde « 17 mm ×2 »',lib3=='17 mm×2|false',lib3)
    q.click('#epChips [data-ep=\"e17\"]'); q.wait_for_timeout(600); check('320 points, sans barlow : « 17 mm » (jamais raccourci)',q.evaluate("document.querySelectorAll('#epChips button')[1].textContent")=='17 mm')
    # noter depuis la fiche du ciel profond : le bouton de l'oculaire suit
    q.evaluate("document.querySelector('.tabbar [data-tab=deep]').click()"); q.wait_for_timeout(800); q.evaluate("document.querySelector('#deepList article.dso[data-dso=\"M13\"] .dhead').click()"); q.wait_for_timeout(600)
    q.evaluate("document.querySelector('#deepList article.dso[data-dso=\"M13\"] .logbtn').click()"); q.wait_for_timeout(400)
    q.evaluate("document.querySelector('.eyelink[data-eye=\"M13\"]').click()"); q.wait_for_timeout(1200)
    check('noté depuis la fiche du ciel profond : le bouton de l\'oculaire montre « ✓ HH:MM »',q.evaluate("/^✓ \\d{2}:\\d{2}$/.test(document.querySelector('#eyeLog .logbtn').textContent)"),q.evaluate("document.querySelector('#eyeLog .logbtn').textContent"))
    check('aucune erreur JavaScript',not errs,errs[:1] or 'aucune')
    b.close()
ok=all(res); print('\nBILAN : %d réussis sur %d'%(sum(res),len(res))); sys.exit(0 if ok else 1)
