# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 2b : images du ciel profond (DSS, via SkyView) : paramètres dans donnees/ciel-profond/images-dss.json, fichiers JPEG dans
# images-dss-512/ (application installée) et images-dss-256/ (page web), et reconstruction exacte des deux tables DSO_IMG.
# Usage : python3 donnees_images_dss.py migre PAGE_EN_LIGNE.html INDEX_INSTALLE.html DONNEES_DIR SITE_INSTALLE_DIR
#         python3 donnees_images_dss.py verifie DONNEES_DIR PAGE_EN_LIGNE.html INDEX_INSTALLE.html
import sys, json, os, re, base64, shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import nettoie_binaires as nb
def objet(txt,debut):
    a=txt.index(debut)+len(debut); depth=0;q=None;i=a
    while True:
        c=txt[i]
        if q:
            if c=='\\': i+=2; continue
            if c==q: q=None
        elif c=='"': q=c
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return a,i
        i+=1
def slug(k): return k.replace(' ','_')
def migre(web,inst,don,site):
    W=open(web,encoding='utf-8').read(); I=open(inst,encoding='utf-8').read()
    a,b=objet(W,'  const DSO_IMG='); ow=json.loads(W[a:b+1]); a,b=objet(I,'  const DSO_IMG='); oi=json.loads(I[a:b+1])
    base=os.path.join(don,'ciel-profond'); recs=[]
    for k,v in oi.items():
        shutil.copy(os.path.join(site,v[5]),os.path.join(base,'images-dss-512',slug(k)+'.jpg'))
        r={'id':'dso:'+k,'fov_deg':v[0],'ra_deg':v[1],'dec_deg':v[2],'fichier_512':'images-dss-512/'+slug(k)+'.jpg'}
        if k in ow:
            w=ow[k]; assert w[:3]==v[:3],k
            open(os.path.join(base,'images-dss-256',slug(k)+'.jpg'),'wb').write(base64.b64decode(w[5])); r['fichier_256']='images-dss-256/'+slug(k)+'.jpg'
        r['source']='Digitized Sky Survey (STScI) via SkyView (NASA), retraité'; recs.append(r)
    assert [k for k in ow]==[k for k in oi if k in ow],'ordre des images de la page web différent'
    json.dump({'schema':'images-dss-v1','description':"Images du ciel profond (DSS) : champ (degrés), ascension droite et déclinaison du centre (J2000, degrés), fichier de 512 points (application installée) et, pour 96 objets, de 256 points (page web). Retraitées : niveaux de gris, fond assombri, détails faibles atténués.",'images':recs},open(os.path.join(base,'images-dss.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(len(recs),'images,',sum(1 for r in recs if 'fichier_256' in r),'en 256 points')
def charge(don):
    # paramètres : donnees/ciel-profond/images-dss.json ; fichiers JPEG : donnees-hors-gpl/dss/ (images non couvertes par la GPL, avec leur avis)
    base=os.path.join(os.path.dirname(os.path.abspath(don)),'donnees-hors-gpl','dss'); return json.load(open(os.path.join(don,'ciel-profond','images-dss.json'),encoding='utf-8'))['images'],base
def objet_web(don):
    recs,base=charge(don); o={}
    for r in recs:
        if 'fichier_256' in r: o[r['id'][4:]]=[r['fov_deg'],r['ra_deg'],r['dec_deg'],256,256,base64.b64encode(nb.lit(os.path.join(base,r['fichier_256']))).decode()]
    return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def objet_installe(don):
    recs,base=charge(don); o={r['id'][4:]:[r['fov_deg'],r['ra_deg'],r['dec_deg'],512,512,'img/'+os.path.basename(r['fichier_512'])] for r in recs}
    return json.dumps(o,ensure_ascii=False,separators=(',',':'))
if __name__=='__main__':
    if sys.argv[1]=='migre': migre(*sys.argv[2:6])
    else:
        don,web,inst=sys.argv[2:5]; W=open(web,encoding='utf-8').read(); I=open(inst,encoding='utf-8').read()
        a,b=objet(W,'  const DSO_IMG='); print('table de la page web :','IDENTIQUE' if W[a:b+1]==objet_web(don) else 'DIFFÉRENTE')
        a,b=objet(I,'  const DSO_IMG='); print('table de l\'application installée :','IDENTIQUE' if I[a:b+1]==objet_installe(don) else 'DIFFÉRENTE')
