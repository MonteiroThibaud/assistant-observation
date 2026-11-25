# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 7 : sépare un site installé existant en (1) fichiers statiques non générés -> site-statique/ ; (2) photos de l'auteur (haute résolution) -> donnees/binaires/installee/photos/.
# Le fichier index.html, listes-saisonnieres.js et les images DSS sont fabriqués à la construction depuis le modèle de page et donnees/.
# Les JPEG et WebP sont nettoyés de leurs métadonnées C2PA à la copie. Usage : python3 prepare_site_statique.py SITE_DIR DONNEES_DIR SORTIE_STATIQUE
import sys, os, json, shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import nettoie_binaires as nb
site,don,out=sys.argv[1:4]
img=json.load(open(os.path.join(don,'ciel-profond','images-dss.json'),encoding='utf-8'))['images']; dss={os.path.basename(r['fichier_512']) for r in img}
photos={os.path.basename(p['installee']['fichier']) for p in json.load(open(os.path.join(don,'ciel-profond','photos.json'),encoding='utf-8'))['photos']}
pdir=os.path.join(don,'binaires','installee','photos'); os.makedirs(pdir,exist_ok=True); n=0; tot=0
for root,_,fs in os.walk(site):
    for f in sorted(fs):
        rel=os.path.relpath(os.path.join(root,f),site)
        if rel in('index.html','listes-saisonnieres.js'): continue
        if rel.startswith('img'+os.sep) and os.path.dirname(rel)=='img' and f in dss: continue
        data=nb.lit(os.path.join(root,f))
        dest=os.path.join(pdir,f) if (rel==os.path.join('img',f) and f in photos) else os.path.join(out,rel)
        os.makedirs(os.path.dirname(dest),exist_ok=True); open(dest,'wb').write(data); n+=1; tot+=len(data)
print(n,'fichiers copiés,',round(tot/1e6,1),'Mo')
