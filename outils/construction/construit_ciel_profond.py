# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 2 : reconstruit, à partir de donnees/ciel-profond/*.json, les déclarations MESSIER, DSO_EXTRA, DSO_DOUBLE, DOUBLE_INFO, DSO_TYPE
# et ASTERISMS de la page (tableaux et objets exactement comme le code les lit) et les remplace dans une page HTML.
# Usage : python3 construit_ciel_profond.py DONNEES_DIR PAGE_ENTREE.html PAGE_SORTIE.html
import sys, json, os
CHAMPS=['designation','ra_deg','dec_deg','type','mag','taille_grand_arcmin','taille_petit_arcmin','nom']
def charge(don):
    ld=lambda n: json.load(open(os.path.join(don,'ciel-profond',n),encoding='utf-8'))
    ligne=lambda o: [o[c] for c in CHAMPS]
    T={}
    T['MESSIER']=[ligne(o) for o in ld('messier.json')['objets']]
    T['DSO_EXTRA']=[ligne(o) for o in ld('classiques.json')['objets']]
    dbl=ld('doubles.json')['objets']; rows=[]; info={}
    for o in dbl:
        x={'ca':o['couleur_principale'],'c':[[c['mag'],c['separation_arcsec'],c['angle_position_deg'],c['couleur']] for c in o['compagnons']],'col':o['couleurs']}
        x.update(o.get('autres',{})); rows.append(ligne(o)+[x])
        i=o.get('infos')
        if i is not None:
            d={'sp':i['types_spectraux'],'pc':i['distance_pc'],'src':i['source_distance'],'M':i['magnitude_absolue'],'B':i['types_compagnons']}; d.update(i.get('autres',{})); info[o['designation']]=d
    T['DSO_DOUBLE']=rows; T['DOUBLE_INFO']=info
    T['DSO_TYPE']=ld('types.json')['types']
    ast={}
    for o in ld('asterismes.json')['objets']:
        v={'stars':[[e['ra_deg'],e['dec_deg'],e['mag']] for e in o['etoiles']]}
        if 'trace' in o: v['line']=o['trace']
        if 'contour' in o: v['contour']=o['contour']
        v.update(o.get('autres',{})); ast[o['nom']]=v
    T['ASTERISMS']=ast
    return T
def js(v): return json.dumps(v,ensure_ascii=False,separators=(',',':'))
SRC={'MESSIER':'ciel-profond/messier.json','DSO_EXTRA':'ciel-profond/classiques.json','DSO_DOUBLE':'ciel-profond/doubles.json','DOUBLE_INFO':'ciel-profond/doubles.json','DSO_TYPE':'ciel-profond/types.json','ASTERISMS':'ciel-profond/asterismes.json'}
def remplace(page,T):
    for nom,val in T.items():
        deb='  const '+nom+'='; a=page.index(deb); assert page.count(deb)==1,nom
        if nom=='ASTERISMS': b=page.index('\n  };\n',a)+len('\n  };')
        elif nom=='DSO_TYPE': b=page.index('};\n',a)+1
        else:
            b=page.index(';\n',a); assert '\n' not in page[a:b],nom+' : déclaration sur plusieurs lignes'
        page=page[:a]+'  // Données : donnees/'+SRC[nom]+' (assemblées à la construction)\n  const '+nom+'='+js(val)+page[b:]
    return page
if __name__=='__main__':
    T=charge(sys.argv[1]); p=open(sys.argv[2],encoding='utf-8').read(); n=remplace(p,T); open(sys.argv[3],'w',encoding='utf-8').write(n)
    print('page : %d -> %d octets'%(len(p.encode()),len(n.encode())))
