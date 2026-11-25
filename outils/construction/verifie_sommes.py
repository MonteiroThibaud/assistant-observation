# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Vérifie que les fichiers de donnees/ n'ont pas changé depuis le manifeste (somme SHA-256) ; avec --ecrit, réécrit le manifeste.
# Les JPEG et WebP sont comparés SANS leurs métadonnées de provenance C2PA (ajoutées par la plateforme entre deux tours : voir nettoie_binaires.py).
# Contexte : le 5 novembre 2026, les JPEG de donnees/ciel-profond/ ont été modifiés (+5 771 octets chacun) entre deux tours de travail
# sans commande de ma part : toute construction commence donc par cette vérification.
import sys, os, json, hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import nettoie_binaires as nb
D=sys.argv[1]; ecrit='--ecrit' in sys.argv; mp=os.path.join(D,'manifeste.json'); man=json.load(open(mp,encoding='utf-8'))
cur={}
for root,_,fs in os.walk(D):
    for f in sorted(fs):
        p=os.path.join(root,f); rel=os.path.relpath(p,D)
        if rel=='manifeste.json': continue
        b=nb.nettoie(open(p,'rb').read(),rel); cur[rel]={'octets':len(b),'sha256':hashlib.sha256(b).hexdigest()}
if ecrit: man['fichiers']=cur; json.dump(man,open(mp,'w',encoding='utf-8'),ensure_ascii=False,indent=1); print('manifeste écrit :',len(cur),'fichiers')
else:
    ref=man['fichiers']; ch=[k for k in ref if k in cur and ref[k]['sha256']!=cur[k]['sha256']]; ab=[k for k in ref if k not in cur]; nv=[k for k in cur if k not in ref]
    print('modifiés :',len(ch),'| absents :',len(ab),'| nouveaux :',len(nv)); print(ch[:10],ab[:5],nv[:5]); sys.exit(1 if (ch or ab) else 0)
