# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 6 : contrôles des données (schémas JSON, doublons, bornes, références, fichiers, complétude des sources).
# Usage : python3 controle_donnees.py DONNEES_DIR [RAPPORT.md]     (code de sortie 1 s'il y a des ERREURS ; les AVERTISSEMENTS n'arrêtent pas)
import sys, json, os, collections
from jsonschema import Draft202012Validator
D=sys.argv[1]; err=[]; avert=[]; info=[]
HG=os.path.join(os.path.dirname(os.path.abspath(D)),'donnees-hors-gpl'); DSS=os.path.join(HG,'dss'); STV=os.path.join(HG,'stelvision')   # éléments hors licence GPL
ld=lambda *p: json.load(open(os.path.join(D,*p),encoding='utf-8'))
def schema(fich,sch):
    v=Draft202012Validator(ld('schemas',sch)); e=sorted(v.iter_errors(ld(*fich)),key=lambda x:list(x.path))
    for x in e[:5]: err.append('%s : %s (%s)'%('/'.join(fich),x.message[:120],'/'.join(map(str,x.path))))
    info.append('%s : %d erreur(s) de schéma'%('/'.join(fich),len(e)))
for f,s in (('messier.json','dso'),('classiques.json','dso'),('doubles.json','dso')): schema(('ciel-profond',f),s+'.schema.json')
schema(('lune','formations.json'),'formations.schema.json'); schema(('sources.json',),'sources.schema.json'); schema(('ciel-profond','images-dss.json'),'images-dss.schema.json')
schema(('ciel','constellations.json'),'constellations.schema.json'); schema(('ciel-profond','asterismes.json'),'asterismes.schema.json')
# identifiants uniques
ids=collections.Counter()
types=ld('ciel-profond','types.json')['types']
for f in ('messier.json','classiques.json','doubles.json'):
    for o in ld('ciel-profond',f)['objets']:
        ids[o['id']]+=1
        if o['type'] not in types: err.append('%s : type inconnu « %s »'%(o['id'],o['type']))
        if o['mag'] is not None and not -2<=o['mag']<=16: avert.append('%s : magnitude %s hors de -2..16'%(o['id'],o['mag']))
        if o['taille_grand_arcmin']<o['taille_petit_arcmin']-1e-9: avert.append('%s : grand axe < petit axe'%o['id'])
for k,v in ids.items():
    if v>1: err.append('identifiant dupliqué : '+k)
F=ld('lune','formations.json'); nom=[f['nom'] for f in F['formations']]
for k,v in collections.Counter(nom).items():
    if v>1: err.append('formation dupliquée : '+k)
mes=[f['nom'] for f in F['formations'] if 'mesures' in f]
for f in F['formations']:
    m=f.get('mesures',{})
    if 'd' in m and not 0<m['d']<3500: err.append('%s : taille %s hors de 0..3500 km'%(f['nom'],m['d']))
    if 'dp' in m and 'dpm' in m and m['dpm']<m['dp']-1: avert.append('%s : profondeur maximale %s inférieure à la moyenne %s'%(f['nom'],m['dpm'],m['dp']))
    if 'dp' in m and not 0<=m['dp']<12000: avert.append('%s : profondeur %s hors de 0..12000 m'%(f['nom'],m['dp']))
info.append('formations : %d ; avec mesures : %d ; sans mesures : %d'%(len(nom),len(mes),len(nom)-len(mes)))
# références : images -> objets ; astérismes -> objets
objets=set(ids)
for r in ld('ciel-profond','images-dss.json')['images']:
    if r['id'] not in objets: err.append('image sans objet : '+r['id'])
    for k in ('fichier_512','fichier_256'):
        if k in r and not os.path.exists(os.path.join(DSS,r[k])): err.append('fichier absent : '+r[k])
for a in ld('ciel-profond','asterismes.json')['objets']:
    if 'trace' in a:
        n=len(a['etoiles']); idx=[i for t in a['trace'] for i in (t if isinstance(t,list) else [t])]
        if max(idx)>=n: err.append('%s : indice de tracé %d hors des %d étoiles'%(a['id'],max(idx),n))
    if 'dso:'+a['nom'] not in objets: err.append('astérisme sans objet du même nom dans les catalogues : '+a['id'])
    for ln in a.get('contour',[]):
        if len(ln)<4 or ln[0]!=ln[-1]: err.append('%s : contour non fermé (au moins 4 points, premier point répété à la fin)'%a['id'])
        if any(not(0<=p[0]<=360 and -90<=p[1]<=90) for p in ln): err.append('%s : point de contour hors bornes'%a['id'])

# listes d'objets : schéma, objets existants, identifiants uniques, pas de doublon dans une liste
RESERVES={'m','x','xg','xa','xp','xn','xt','xl','xm','xf','sel','s300','d','c','a'}; vus=set(); designations={x[4:] for x in objets}
for dossier in (os.path.join(D,'ciel-profond','listes'),STV):
  for f in sorted(os.listdir(dossier)):
    if not f.endswith('.json'): continue
    chemin=os.path.join(dossier,f); L=json.load(open(chemin,encoding='utf-8'))
    for x in sorted(Draft202012Validator(ld('schemas','listes.schema.json')).iter_errors(L),key=lambda x:list(x.path))[:5]: err.append('%s : %s (%s)'%(f,x.message[:120],'/'.join(map(str,x.path))))
    if (dossier==STV)==bool(L.get('libre')): err.append('%s : une liste protégée (libre : false) va dans donnees-hors-gpl/stelvision/, une liste libre dans donnees/ciel-profond/listes/'%f)
    for l in L['listes']:
        if l['id'] in RESERVES or l['id'] in vus: err.append('%s : identifiant de liste « %s » déjà pris'%(f,l['id']))
        vus.add(l['id']); noms=[o['objet'] for o in l['objets']]
        for n,c in collections.Counter(noms).items():
            if c>1: avert.append('%s / %s : objet en double « %s »'%(f,l['id'],n))
        for n in noms:
            if n not in designations: err.append('%s / %s : objet inconnu des catalogues « %s »'%(f,l['id'],n))
        if l.get('pages',True) and any(o['page']==0 for o in l['objets']): avert.append('%s / %s : numéro de page absent pour certains objets'%(f,l['id']))
    info.append('liste(s) %s : %d (libre : %s)'%(f,len(L['listes']),L['libre']))

# dossier hors licence GPL : avis présents, aucune image sans entrée, copie de l'avis de Stelvision identique à celle du site installé
for avis in (os.path.join(DSS,'LICENCE-DSS.txt'),os.path.join(STV,'LICENCE-LISTES-SAISONNIERES.txt'),os.path.join(HG,'LISEZ-MOI.md')):
    if not os.path.exists(avis): err.append('avis absent : '+os.path.relpath(avis,os.path.dirname(HG)))
cp_site=os.path.join(os.path.dirname(HG),'site-statique','LICENCE-LISTES-SAISONNIERES.txt')
if os.path.exists(cp_site) and os.path.exists(os.path.join(STV,'LICENCE-LISTES-SAISONNIERES.txt')) and open(cp_site,'rb').read()!=open(os.path.join(STV,'LICENCE-LISTES-SAISONNIERES.txt'),'rb').read(): err.append('site-statique/LICENCE-LISTES-SAISONNIERES.txt diffère de donnees-hors-gpl/stelvision/LICENCE-LISTES-SAISONNIERES.txt')
refs={r['fichier_512'] for r in ld('ciel-profond','images-dss.json')['images']}
orphelins=[f for f in os.listdir(os.path.join(DSS,'images-dss-512')) if 'images-dss-512/'+f not in refs]
if orphelins: avert.append('images sans entrée dans images-dss.json : %d (%s…)'%(len(orphelins),orphelins[0]))
info.append('images du ciel profond (hors GPL) : %d fichiers, %d entrées'%(len(os.listdir(os.path.join(DSS,'images-dss-512'))),len(refs)))

# listes de formations lunaires : schéma, formations existantes, identifiants uniques
RESERVES_L={'all','tonight','libr','must','big','pic','deep','high','i1','i2','i3','i4'}; vusl=set(); noms_f={f['nom'] for f in ld('lune','formations.json')['formations']}
dl=os.path.join(D,'lune','listes')
for f in (sorted(os.listdir(dl)) if os.path.isdir(dl) else []):
    if not f.endswith('.json'): continue
    schema(('lune','listes',f),'listes-lune.schema.json'); L=ld('lune','listes',f)
    for l in L['listes']:
        if l['id'] in RESERVES_L or l['id'] in vusl: err.append('lune/listes/%s : identifiant « %s » déjà pris'%(f,l['id']))
        vusl.add(l['id'])
        for n in l['formations']:
            if n not in noms_f: err.append('lune/listes/%s / %s : formation inconnue « %s »'%(f,l['id'],n))
        for n,c in collections.Counter(l['formations']).items():
            if c>1: avert.append('lune/listes/%s / %s : formation en double « %s »'%(f,l['id'],n))
    info.append('listes lunaires %s : %d (libre : %s)'%(f,len(L['listes']),L['libre']))

# photos de l'auteur : schéma, objets connus et uniques, fichiers présents, dimensions conformes aux images
schema(('ciel-profond','photos.json'),'photos.schema.json'); PH=ld('ciel-profond','photos.json')
desig_ph={o['designation'] for f_ in ('messier','classiques','doubles') for o in ld('ciel-profond',f_+'.json')['objets']}; vus_ph=collections.Counter(); ids_ph=collections.Counter()
try:
    from PIL import Image
except ImportError: Image=None
for ph in PH['photos']:
    ids_ph[ph['id']]+=1
    for o in ph['objets']:
        vus_ph[o]+=1
        if o not in desig_ph: err.append('photos.json / %s : objet inconnu des catalogues « %s »'%(ph['id'],o))
    for ver,rep in (('web',os.path.join(D,'binaires','web')),('installee',os.path.join(D,'binaires','installee','photos'))):
        if ver not in ph: continue                       # la page en ligne n'a qu'une partie des photos
        fch=os.path.join(rep,os.path.basename(ph[ver]['fichier']))
        if not os.path.exists(fch): err.append('photos.json / %s : fichier absent (%s)'%(ph['id'],os.path.relpath(fch,D))); continue
        if Image:
            sz=Image.open(fch).size
            if sz!=(ph[ver]['largeur'],ph[ver]['hauteur']): err.append('photos.json / %s (%s) : dimensions %s différentes de l\'image %s'%(ph['id'],ver,(ph[ver]['largeur'],ph[ver]['hauteur']),sz))
for o,n in vus_ph.items():
    if n>1: err.append('photos.json : objet « %s » dans plusieurs photos'%o)
for i_,n in ids_ph.items():
    if n>1: err.append('photos.json : identifiant « %s » en double'%i_)
info.append('photos de l\'auteur : %d photos pour %d objets'%(len(PH['photos']),len(vus_ph)))
# constellations : polygones fermés, coordonnées
for c in ld('ciel','constellations.json')['constellations']:
    for seg in c['limites']+c['figure']:
        for ra,de in seg:
            if not (0<=ra<=360 and -90<=de<=90): err.append('%s : coordonnées hors bornes (%s, %s)'%(c['id'],ra,de)); break
# sources : complétude
S=ld('sources.json'); LL=[l for c in S['categories'] for l in c['liens']]; sans=[l['titre'] for l in LL if not l.get('licence') and not l.get('statut')]; aver=[l for l in LL if l.get('statut')=='a-verifier']
info.append('sources : %d liens ; statuts : %s ; licence renseignée pour %d'%(len(LL),', '.join('%s %d'%(k,v) for k,v in sorted(collections.Counter(l.get('statut','sans') for l in LL).items())),sum(1 for l in LL if l.get('licence'))))
if sans: avert.append('%d sources sans licence ni statut dans sources.json (à compléter)'%len(sans))
if aver: avert.append('%d sources à vérifier (statut a-verifier) : %s'%(len(aver),' ; '.join(l['titre'][:48] for l in aver)))
urls=collections.Counter(l['url'] for c in S['categories'] for l in c['liens'])
for u,v in urls.items():
    if v>1: avert.append('adresse en double dans les sources : '+u)
# textes : marques non remplacées
T=ld('textes','fr','informations.json'); brut=json.dumps(T,ensure_ascii=False)
import re
inconnues=set(re.findall(r'\{\{(\w+)\}\}',brut))-{'numero','date','mention','licences'}
if inconnues: err.append('marques inconnues dans informations.json : '+', '.join(sorted(inconnues)))
rap=['# Rapport de contrôle des données','',"%d erreur(s), %d avertissement(s)."%(len(err),len(avert)),'']
rap+=['## Informations','']+['- '+x for x in info]+['','## Erreurs','']+(['- '+x for x in err] or ['aucune'])+['','## Avertissements','']+(['- '+x for x in avert[:60]]+(['- … et %d autres'%(len(avert)-60)] if len(avert)>60 else []) or ['aucun'])
txt='\n'.join(rap)+'\n'; print(txt[:3500])
if len(sys.argv)>2: open(sys.argv[2],'w',encoding='utf-8').write(txt)
sys.exit(1 if err else 0)
