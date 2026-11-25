# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Version 0.89 : intégration du lot « Sélection 300 mm » (97 objets NGC/IC) : classiques.json, liste s300, retouches de fiches M51 et NGC 6992.
# Usage : python3 migre_ajouts_089.py DONNEES_DIR LOT_AJOUTS.json LISTE_SELECTION.json
import sys, json, os
don,lot,sel=sys.argv[1:4]; P=lambda *a: os.path.join(don,*a)
ld=lambda p: json.load(open(p,encoding='utf-8')); dump=lambda o,p: json.dump(o,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
c=ld(P('ciel-profond','classiques.json')); assert len(c['objets'])==70, 'déjà intégré ?'
ajouts=ld(lot)['objets']; exist={o['designation'] for o in c['objets']}; assert not any(o['designation'] in exist for o in ajouts)
for o in ajouts:
    o=dict(o); o['nom']=o['nom'] or ''; c['objets'].append(o)
for o in c['objets']:
    if o['designation']=='NGC 6992': o['nom']='Dentelles du Cygne, partie est (avec NGC 6995)'
dump(c,P('ciel-profond','classiques.json'))
m=ld(P('ciel-profond','messier.json'))
for o in m['objets']:
    if o['designation']=='M51': o['nom']='Galaxie du Tourbillon (avec NGC 5195)'
dump(m,P('ciel-profond','messier.json'))
s=ld(sel); L=s['listes'][0]
out={'schema':'listes-v1','description':"Sélection personnelle pour un Dobson de 300 mm depuis Roanne : objets du ciel profond ajoutés en 0.89 (données OpenNGC). Liste sans numéros de page (`pages:false`).",
 'ensemble':{'id':'selection-300mm','titre':'Sélection 300 mm','auteurs':'Thibaud Monteiro (Club Astro Jupiter du Roannais)'},'libre':True,'licence':s['licence'],
 'listes':[{'id':L['id'],'nom':L['nom'],'nom_complet':L['nom_complet'],'pages':False,'objets':[{'objet':x['objet'],'page':0} for x in L['objets']]}]}
dump(out,P('ciel-profond','listes','selection-300mm.json'))
print(len(c['objets']),'objets classiques ;',len(out['listes'][0]['objets']),'objets dans la liste s300')
