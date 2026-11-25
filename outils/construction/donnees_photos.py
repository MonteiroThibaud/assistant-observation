# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Photos de l'auteur : donnees/ciel-profond/photos.json -> lignes de code de la table DSO_IMG (page web et application installée).
# Usage (essai) : python3 donnees_photos.py DONNEES_DIR  -> affiche les deux blocs
import sys, os, json
def charge(don): return json.load(open(os.path.join(don,'ciel-profond','photos.json'),encoding='utf-8'))
q=lambda s: json.dumps(s,ensure_ascii=False)
def objets(p): return ''.join('DSO_IMG[%s]='%q(o) for o in p['objets'])
def nombres(v): return '%s,%s,%s,%d,%d'%(repr(v['champ']),repr(v['ra']),repr(v['dec']),v['largeur'],v['hauteur'])
def bloc_web(don):
    L=[]
    for p in charge(don)['photos']:
        if 'web' not in p: continue                      # photo seulement dans l'application installée
        c='PH_'+p['id']
        if p.get('commentaire'): L.append('  // '+p['commentaire'])
        L.append("  const %s='@@B64:%s@@';"%(c,p['web']['fichier']))
        L.append('  %s[%s,%s,%s];'%(objets(p),nombres(p['web']),c,q(p['legende'])))
    return '\n'.join(L).lstrip(' ')
def bloc_installee(don):
    d=charge(don)
    return d['commentaire_installee'], ['  %s[%s,%s,%s];'%(objets(p),nombres(p['installee']),q(p['installee']['fichier']),q(p['legende'])) for p in d['photos']]
def fichiers_installee(don): return [os.path.basename(p['installee']['fichier']) for p in charge(don)['photos']]
if __name__=='__main__':
    print(bloc_web(sys.argv[1])[:900]); c,l=bloc_installee(sys.argv[1]); print(c); print('\n'.join(l[:3]))
