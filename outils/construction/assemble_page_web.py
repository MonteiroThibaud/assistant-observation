# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 7 (2/2) : assemble la page web à partir du modèle et de donnees/ (aucune autre source).
# Usage : python3 assemble_page_web.py DONNEES_DIR MODELE.html SORTIE.html
import sys, re, os, json, base64, importlib.util
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import nettoie_binaires as nb
ICI=os.path.dirname(os.path.abspath(__file__))
def mod(nom):
    sp=importlib.util.spec_from_file_location(nom,os.path.join(ICI,nom+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
don,modele,sortie=sys.argv[1:4]; s=open(modele,encoding='utf-8').read()
cp,dc,dl,di,ct=mod('construit_ciel_profond'),mod('donnees_ciel'),mod('donnees_lune_final'),mod('donnees_images_dss'),mod('construit_textes')
tables={}; tables.update(cp.charge(don)); tables.update(dc.charge(don)); tables.update(dl.charge(don))
js=lambda v: json.dumps(v,ensure_ascii=False,separators=(',',':'))
dli=mod('donnees_listes'); L_nl,L_lib=dli.genere(don); s=s.replace('@@LISTES:non-libres@@','\n'+L_nl).replace('@@LISTES:libres@@','\n'+L_lib)
s=re.sub(r"@@DATA:(\w+)@@",lambda m: js(tables[m.group(1)]),s)
dp=mod('donnees_photos'); s=s.replace('@@PHOTOSWEB@@',dp.bloc_web(don)); s=s.replace('@@DSOIMGWEB@@',di.objet_web(don)); s=s.replace('@@TEXTE:informations@@',ct.genere(don))
b=os.path.join(don,'binaires','web'); s=re.sub(r"@@B64:([\w.\-]+)@@",lambda m: base64.b64encode(nb.lit(os.path.join(b,m.group(1)))).decode(),s)
assert not re.search(r'@@(DATA|B64|TEXTE|DSOIMGWEB|PHOTOSWEB)',s),'marques non remplacées'
open(sortie,'w',encoding='utf-8').write(s); print('page assemblée : %d octets'%len(s.encode()))
