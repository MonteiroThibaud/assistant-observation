# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 7 : assemble le site installé (application hors ligne) = modèle de page + donnees/ + site-statique/. Aucune autre source.
# Usage : python3 assemble_site_installe.py DONNEES_DIR MODELE.html SITE_STATIQUE_DIR SORTIE_DIR
import sys, os, re, json, shutil, subprocess
ICI=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,ICI); import nettoie_binaires as nb
import importlib.util
def mod(n):
    sp=importlib.util.spec_from_file_location(n,os.path.join(ICI,n+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
don,modele,statique,sortie=sys.argv[1:5]
tmp=sortie.rstrip('/')+'_page_web.html'; subprocess.run([sys.executable,os.path.join(ICI,'assemble_page_web.py'),don,modele,tmp],check=True,stdout=subprocess.DEVNULL)
w=open(tmp,encoding='utf-8').read(); os.remove(tmp); di=mod('donnees_images_dss')
dp=mod('donnees_photos'); suite,lignes=dp.bloc_installee(don)
L=w.split('\n'); i=[n for n,l in enumerate(L) if l.startswith('  const DSO_IMG=')][0]; last=max(n for n,l in enumerate(L) if re.match(r"  DSO_IMG\[",l))
L[i:last+1]=('  const DSO_IMG='+di.objet_installe(don)+suite+'\n'+'\n'.join(lignes)).split('\n'); w='\n'.join(L)
w,n1=re.subn(r"const MOON_MAP='data:image/jpeg;base64,[A-Za-z0-9+/=]+'","const MOON_MAP=''",w,count=1); w,n2=re.subn(r"const DEM_MAP='data:image/webp;base64,[A-Za-z0-9+/=]+'","const DEM_MAP=''",w,count=1); assert n1==1 and n2==1
# (la page en ligne n'embarque aucun fond de carte ni aucune adresse de démonstration)
o="window.FIELD_URL='img/etoiles.bin.gz';"; assert w.count(o)==1
w=w.replace(o,o+" window.STARINFO_URL='img/etoiles-info.bin.gz'; window.PLACES_URL='img/lieux.bin.gz'; window.TEX_TILES_URL='img/tuiles/manifest.json'; window.MOON_MAP_URL='img/moon-texture.jpg'; window.DEM_MAP_URL='img/relief.webp'; window.DEPS_URL='img/departements.bin.gz';")
k=w.index('<script id="listes-saisonnieres">'); e=w.index('</script>',k)
shutil.rmtree(sortie,ignore_errors=True); os.makedirs(sortie)
open(os.path.join(sortie,'listes-saisonnieres.js'),'w',encoding='utf-8').write(w[k+len('<script id="listes-saisonnieres">'):e].strip()+'\n')
w=w[:k]+'<script src="listes-saisonnieres.js"></script>'+w[e+len('</script>'):]
open(os.path.join(sortie,'index.html'),'w',encoding='utf-8').write(w)
for root,_,fs in os.walk(statique):
    for f in fs:
        p=os.path.join(root,f); rel=os.path.relpath(p,statique); d=os.path.join(sortie,rel); os.makedirs(os.path.dirname(d),exist_ok=True); open(d,'wb').write(nb.lit(p))
img,DSS=di.charge(don)   # paramètres dans donnees/, fichiers JPEG dans donnees-hors-gpl/dss/
for r in img: shutil.copyfile(os.path.join(DSS,r['fichier_512']),os.path.join(sortie,'img',os.path.basename(r['fichier_512']))); open(os.path.join(sortie,'img',os.path.basename(r['fichier_512'])),'wb').write(nb.lit(os.path.join(DSS,r['fichier_512'])))
for f in dp.fichiers_installee(don): open(os.path.join(sortie,'img',f),'wb').write(nb.lit(os.path.join(don,'binaires','installee','photos',f)))
# service worker incrémental (0.90) : manifeste des fichiers (empreinte et taille), puis sw.js avec la version et l'empreinte de la construction (voir manifeste_sw.py)
numero=json.load(open(os.path.join(don,'version.json'),encoding='utf-8'))['numero']
build,nfich=mod('manifeste_sw').produire(sortie,numero); fichiers=range(nfich)
manque=[]
print('site assemblé :',sum(len(f) for _,_,f in os.walk(sortie)),'fichiers ; manifeste du service worker :',len(fichiers),'fichiers, construction',build)
