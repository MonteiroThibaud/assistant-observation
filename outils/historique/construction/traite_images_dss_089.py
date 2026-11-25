# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Version 0.89 : traitement des photos DSS des objets ajoutés (SkyView) -> donnees/ciel-profond/images-dss-512/ + entrées de images-dss.json
# Même traitement que les images 0.72 à 0.77 (dssproc_traitement_images_dss.py : niveaux de gris, fond de ciel abaissé, contraste, bord fondu), JPEG de qualité 76.
# Usage : python3 traite_images_dss_089.py DOSSIER_DSS_IMAGES DONNEES_DIR
import sys, os, json, importlib.util, cv2, numpy as np
ici=os.path.dirname(os.path.abspath(__file__)); dss,don=sys.argv[1:3]
src=open(os.path.join(ici,'dssproc_traitement_images_dss.py'),encoding='utf-8').read()
src=src.replace("T=types()","T={}")   # les types viennent des données JSON, pas d'une page
ns={}; exec(compile(src,'dssproc','exec'),ns)
cp=os.path.join(don,'ciel-profond'); ld=lambda *p: json.load(open(os.path.join(cp,*p),encoding='utf-8'))
for f in ('messier.json','classiques.json'):
    for o in ld(f)['objets']: ns['T'][o['designation']]=(o['type'],o['taille_grand_arcmin'],o['taille_petit_arcmin'])
lst=ld('images-a-ajouter-0.89.json'); J=ld('images-dss.json'); have={x['id'] for x in J['images']}; n=0
for x in lst:
    ident=x['id']; fn=ident.replace(' ','_')+'.jpg'; b,typ=ns['process'](os.path.join(dss,fn),ident)
    ok,buf=cv2.imencode('.jpg',b,[cv2.IMWRITE_JPEG_QUALITY,76]); assert ok
    open(os.path.join(os.path.dirname(os.path.dirname(cp)),'donnees-hors-gpl','dss','images-dss-512',fn),'wb').write(buf.tobytes())
    if 'dso:'+ident not in have:
        J['images'].append({'id':'dso:'+ident,'fov_deg':x['champ'],'ra_deg':x['ra'],'dec_deg':x['dec'],'fichier_512':'images-dss-512/'+fn,'source':'Digitized Sky Survey (STScI) via SkyView (NASA), retraité'}); n+=1
json.dump(J,open(os.path.join(cp,'images-dss.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(lst),'images traitées ;',n,'entrées ajoutées ; total',len(J['images']))
