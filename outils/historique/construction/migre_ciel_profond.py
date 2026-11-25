# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 2 de la migration : tables du ciel profond (Messier, objets classiques, étoiles doubles, types, astérismes)
# passent du code à donnees/ciel-profond/*.json (champs nommés). Les valeurs viennent de l'instantané de référence 0.87.
# Usage : python3 migre_ciel_profond.py REFERENCE_DIR DONNEES_DIR   (écrit les JSON)
import sys, json, os
REF,DON=sys.argv[1:3]
ld=lambda n: json.load(open(os.path.join(REF,n+'.json'),encoding='utf-8'))
out=os.path.join(DON,'ciel-profond'); os.makedirs(out,exist_ok=True)
def sauve(nom,obj): json.dump(obj,open(os.path.join(out,nom),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
CHAMPS_DSO=['designation','ra_deg','dec_deg','type','mag','taille_grand_arcmin','taille_petit_arcmin','nom']
def dso(rows,source):
    return {'schema':'dso-v1','description':source,'objets':[dict([('id','dso:'+r[0])]+list(zip(CHAMPS_DSO,r[:8]))) for r in rows]}
sauve('messier.json',dso(ld('MESSIER'),"Catalogue de Messier : 110 objets (positions J2000 en degrés, taille en minutes d'arc)."))
sauve('classiques.json',dso(ld('DSO_EXTRA'),"Objets classiques (NGC, IC, Collinder, Melotte et autres) : positions J2000 en degrés, taille en minutes d'arc ; magnitude absente (null) si inconnue."))
info=ld('DOUBLE_INFO'); doubles=[]
for r in ld('DSO_DOUBLE'):
    e=dict([('id','dso:'+r[0])]+list(zip(CHAMPS_DSO,r[:8]))); x=r[8]
    e['couleur_principale']=x['ca']; e['couleurs']=x['col']
    e['compagnons']=[{'mag':c[0],'separation_arcsec':c[1],'angle_position_deg':c[2],'couleur':c[3]} for c in x['c']]
    extra={k:v for k,v in x.items() if k not in('ca','c','col')}
    if extra: e['autres']=extra
    i=info.get(r[0])
    if i is not None:
        e['infos']={'types_spectraux':i['sp'],'distance_pc':i['pc'],'source_distance':i['src'],'magnitude_absolue':i['M'],'types_compagnons':i['B']}
        bizarre=set(i)-{'sp','pc','src','M','B'}
        if bizarre: e['infos']['autres']={k:i[k] for k in bizarre}
    doubles.append(e)
assert list(info)==[r[0] for r in ld('DSO_DOUBLE')], "ordre de DOUBLE_INFO différent de DSO_DOUBLE"
sauve('doubles.json',{'schema':'doubles-v1','description':"Étoiles doubles : position J2000, magnitude de la principale, compagnons (magnitude, écart en secondes d'arc, angle de position) et informations astrophysiques (types spectraux, distance en parsecs, magnitude absolue visuelle).",'objets':doubles})
sauve('types.json',{'schema':'types-v1','description':"Codes des types d'objets du ciel profond et leurs libellés français.",'types':ld('DSO_TYPE')})
NOTES={
 'Picot 1':"Positions SIMBAD (CDS, Gaia EDR3) reprises de Deep Sky Corner (CC BY 4.0) ; tracé schématique reliant les étoiles voisines (indicatif).",
 'M40':"Winnecke 4 : catalogue Hipparcos et Tycho-2 (ESA).",
 'M73':"Les quatre étoiles (ascension droite et déclinaison J2000, magnitude V) d'après Wikipédia en français (références SIMBAD) ; la troisième (BD−13 5809) coïncide à 0,02″ avec le catalogue Tycho-2 de l'application ; tracé schématique en Y (jonction à la deuxième étoile).",
 'Calvet 1':"Point d'interrogation inversé : vingt-six étoiles du crochet (vingt pointées à la main par l'utilisateur dans Stellarium et six étoiles brillantes voisines ajoutées d'après son trait) et deux étoiles du « point » ; positions et magnitudes du catalogue Hipparcos et Tycho-2 pour les étoiles de magnitude 10,5 ou moins ; pour les plus faibles, position calculée sur la capture (calée sur 17 étoiles du catalogue, résidu de 2″) et magnitude estimée à 11,0 ; tracé de l'extrémité est du crochet à son extrémité ouest.",
 'NGC 2169':"Amas « 37 » : treize étoiles du « 3 » (est) et du « 7 » (ouest), repérées sur une photo de l'amas dont les positions ont été calculées par ajustement sur 11 étoiles du catalogue Hipparcos et Tycho-2 (résidu moyen de 0,8″) ; magnitudes du catalogue pour sept étoiles (dont la double Struve 848, 6,95 en lumière combinée), estimées plus faibles que 10,5 (10,6 à 11,4) pour les six autres ; deux tracés.",
 'Kemble 2':"Mini-Cassiopée : cinq étoiles du « W » (positions J2000 en degrés et magnitudes d'après Hipparcos et Tycho-2, ESA), repérées en comparant une capture de carte du ciel au catalogue ; tracé en W de l'ouest à l'est."}
ast=[]
for nom,v in ld('ASTERISMS').items():
    e={'id':'ast:'+nom,'nom':nom,'etoiles':[{'ra_deg':a,'dec_deg':b,'mag':c} for a,b,c in v['stars']],'source':NOTES[nom]}
    if 'line' in v: e['trace']=v['line']
    extra={k:x for k,x in v.items() if k not in('stars','line')}
    if extra: e['autres']=extra
    ast.append(e)
sauve('asterismes.json',{'schema':'asterismes-v1','description':"Astérismes tracés étoile par étoile à l'oculaire : liste explicite d'étoiles (ascension droite et déclinaison J2000 en degrés, magnitude) ; « trace » donne l'ordre du tracé schématique (une suite d'indices, ou plusieurs suites).",'objets':ast})
print('écrit :',sorted(os.listdir(out)))
