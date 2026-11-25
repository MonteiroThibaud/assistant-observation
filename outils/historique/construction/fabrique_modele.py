# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 7 (1/2) : fabrique le MODÈLE de page (src/modele-page.html) à partir d'une page complète :
#  - les données JSON de donnees/ sont remplacées par des marques @@DATA:NOM@@ (tables), @@DSOIMGWEB@@ (images DSS de la page web), @@TEXTE:informations@@ ;
#  - les blocs base64 (polices, photos, cartes, étoiles) sont extraits en fichiers dans donnees/binaires/web/ et remplacés par @@B64:fichier@@.
# Usage : python3 fabrique_modele.py PAGE_COMPLETE.html DONNEES_DIR SORTIE_MODELE.html
import sys, re, os, json, base64, hashlib, importlib.util
ICI=os.path.dirname(os.path.abspath(__file__))
def mod(nom):
    sp=importlib.util.spec_from_file_location(nom,os.path.join(ICI,nom+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
page,don,sortie=sys.argv[1:4]; s=open(page,encoding='utf-8').read()
cp,dc,dl,di,ct=mod('construit_ciel_profond'),mod('donnees_ciel'),mod('donnees_lune_final'),mod('donnees_images_dss'),mod('construit_textes')
# 1) tables de données
tables={}; tables.update(cp.charge(don)); tables.update(dc.charge(don)); tables.update(dl.charge(don))
js=lambda v: json.dumps(v,ensure_ascii=False,separators=(',',':'))
for nom,val in tables.items():
    txt=js(val); assert s.count('='+txt)==1,(nom,s.count('='+txt)); s=s.replace('='+txt,'=@@DATA:'+nom+'@@')
# 2) images DSS de la page web
web=di.objet_web(don); assert s.count('='+web)==1; s=s.replace('='+web,'=@@DSOIMGWEB@@')
# 3) section Informations
a,b=ct.section(s); assert ct.genere(don)==s[a:b]; s=s[:a]+'@@TEXTE:informations@@'+s[b:]
# 4) binaires
out=os.path.join(don,'binaires','web'); os.makedirs(out,exist_ok=True); man={}
def sauve(nom,b64,role):
    raw=base64.b64decode(b64); assert base64.b64encode(raw).decode()==b64
    open(os.path.join(out,nom),'wb').write(raw); man[nom]={'octets':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'role':role}; return '@@B64:'+nom+'@@'
polices=[('AlegreyaL',500),('AlegreyaL',700),('AlegreyaSansL',400),('AlegreyaSansL',500),('AlegreyaSansL',700)]
def pol(m):
    fam,w=re.search(r"font-family:'(\w+)';font-weight:(\d+)",m.group(1)).groups()
    return m.group(1)+sauve('police-%s-%s.woff2'%(fam,w),m.group(2),"police Alegreya intégrée (%s %s)"%(fam,w))
s=re.sub(r"(@font-face\{[^}]*?src:url\(data:font/woff2;base64,)([A-Za-z0-9+/=]{3000,})",pol,s)
def cst(m):
    nom=m.group(2); fich={'ORION_IMG':'photo-ORION.jpg','MOON_MAP':'carte-lune.jpg','DEM_MAP':'relief-lune.webp','FIELD_C64':'etoiles-champ.bin','STAR_INFO_C64':'etoiles-info.bin.gz'}.get(nom, 'photo-'+nom[3:]+'.jpg' if nom.startswith('PH_') else None)
    assert fich,nom
    return m.group(1)+sauve(fich,m.group(3),{'ORION_IMG':'photo de l\'auteur','MOON_MAP':'texture de la Lune (page web)','DEM_MAP':'relief de la Lune (page web)','FIELD_C64':'étoiles du champ (page web)','STAR_INFO_C64':'informations stellaires (page web)'}.get(nom,'photo de l\'auteur'))
s=re.sub(r"(const (ORION_IMG|PH_\w+|MOON_MAP|DEM_MAP|FIELD_C64|STAR_INFO_C64)=(?:'data:image/(?:jpeg|webp);base64,|'))([A-Za-z0-9+/=]{3000,})",cst,s)
reste=re.findall(r"[A-Za-z0-9+/=]{3000,}",s); assert not reste,'blocs base64 restants : %d'%len(reste)
json.dump(man,open(os.path.join(out,'MANIFESTE.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
open(sortie,'w',encoding='utf-8').write(s)
print('modèle : %.3f Mo ; %d binaires extraits (%.2f Mo)'%(len(s.encode())/1e6,len(man),sum(v['octets'] for v in man.values())/1e6))
