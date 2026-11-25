# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Manifeste des fichiers du site installé et service worker incrémental.
produire(sortie, numero, gabarit=None, partages=True) : écrit manifeste-sw.json (empreinte et taille de chaque fichier que le service worker garde) et remplace dans sw.js les
marques @@VERSION@@ et @@BUILD@@ (gabarit : texte de sw.js avec ses marques ; à défaut, le sw.js de la sortie). Retourne (empreinte de la construction, nombre de fichiers)."""
import os, json, hashlib
EXCLUS={'sw.js','manifeste-sw.json','_redirects','LICENSE','LICENCE-LISTES-SAISONNIERES.txt'}
PARTAGES='./img/'      # les fichiers de ce dossier vont dans le stockage commun (marque « p » du manifeste)
FACULTATIFS={'./img/relief-fin.bin.gz','./img/etoiles.bin.gz'}     # gardés s'ils sont présents, sans bloquer l'installation sinon
def produire(sortie,numero,gabarit=None,partages=True):
    fichiers={}
    for root,_,fs in os.walk(sortie):
        for f in sorted(fs):
            p=os.path.join(root,f); rel='./'+os.path.relpath(p,sortie).replace(os.sep,'/')
            if f in EXCLUS or rel.startswith('./well-known/'): continue
            b=open(p,'rb').read(); fichiers[rel]={'h':hashlib.sha256(b).hexdigest()[:16],'t':len(b)}
            if rel in FACULTATIFS: fichiers[rel]['o']=1
            if partages and rel.startswith('./img/'): fichiers[rel]['p']=1       # fichier de données : rangé dans le stockage commun à toutes les versions (jamais recopié d'une version à l'autre)
    fichiers=dict(sorted(fichiers.items())); build=hashlib.sha256(json.dumps(fichiers,sort_keys=True).encode()).hexdigest()[:12]
    def ecrire(nom,texte):                     # écriture par remplacement (et non sur place) : un lien physique avec une autre copie du site n'est pas modifié
        tmp=os.path.join(sortie,nom+'.tmp'); open(tmp,'w',encoding='utf-8').write(texte); os.replace(tmp,os.path.join(sortie,nom))
    ecrire('manifeste-sw.json',json.dumps({'version':numero,'build':build,'fichiers':fichiers},ensure_ascii=False,separators=(',',':')))
    sw=gabarit if gabarit is not None else open(os.path.join(sortie,'sw.js'),encoding='utf-8').read()
    assert '@@VERSION@@' in sw and '@@BUILD@@' in sw
    ecrire('sw.js',sw.replace('@@VERSION@@',numero).replace('@@BUILD@@',build))
    return build,len(fichiers)
