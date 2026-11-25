# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 4 de la migration : constellations, étoiles repères, noms français et filtres lunaires -> donnees/ciel/*.json (et donnees/lune/filtres.json)
# Usage : python3 donnees_ciel.py migre  REFERENCE_DIR DONNEES_DIR
#         python3 donnees_ciel.py construit DONNEES_DIR PAGE_ENTREE.html PAGE_SORTIE.html
import sys, json, os
def ld(d,*p): return json.load(open(os.path.join(d,*p),encoding='utf-8'))
def sv(d,f,o):
    os.makedirs(os.path.dirname(os.path.join(d,f)),exist_ok=True); json.dump(o,open(os.path.join(d,f),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
def pairs(flat): return [[flat[i]/20,flat[i+1]/20] for i in range(0,len(flat),2)]
def flat(pts): return [round(v*20) for p in pts for v in p]
def migre(REF,DON):
    S=ld(REF,'SKY_STARS.json'); assert all(round(r[0]/20*20)==r[0] and round(r[1]/20*20)==r[1] and round(r[2]/10*10)==r[2] for r in S)
    sv(DON,'ciel/etoiles-reperes.json',{'schema':'ciel-etoiles-v1','description':"Étoiles repères des cartes du ciel (5 044) : ascension droite et déclinaison J2000 en degrés, magnitude, nom (une étoile sur cinq en a un). Le code lit ces valeurs multipliées par 20 (positions) et par 10 (magnitude).",'colonnes':['ra_deg','dec_deg','mag','nom'],
        'etoiles':[[r[0]/20,r[1]/20,r[2]/10]+([r[3]] if len(r)>3 else []) for r in S]})
    C=ld(REF,'SKY_CONS.json'); out=[]
    for k,v in C.items():
        assert list(v)==['n','d','l','b']
        out.append({'id':'cons:'+k,'abbr':k,'nom':v['n'],'centre_ra_deg':v['d'][0],'centre_dec_deg':v['d'][1],'troisieme_valeur':v['d'][2],
                    'figure':[pairs(seg) for seg in v['l']],'limites':[pairs(seg) for seg in v['b']]})
    sv(DON,'ciel/constellations.json',{'schema':'ciel-constellations-v1','description':"88 constellations : abréviation de l'UAI, nom français, centre (ascension droite et déclinaison en degrés ; la troisième valeur du centre n'est pas lue par le code, probablement l'extension en degrés), figure (segments tracés) et limites (contours de l'UAI), en degrés J2000.",'constellations':out})
    sv(DON,'ciel/noms-francais-constellations.json',{'schema':'ciel-noms-v1','description':"Nom français avec article des constellations citées dans les phrases (CONST), par nom anglais.",'noms':ld(REF,'CONST.json')})
    sv(DON,'lune/filtres.json',{'schema':'lune-filtres-v1','description':"Filtres de type de la liste des formations lunaires : [code, libellé].",'filtres':ld(REF,'MOON_FILTERS.json')})
def charge(DON):
    V={}
    V['SKY_STARS']=[[round(e[0]*20),round(e[1]*20),round(e[2]*10)]+e[3:] for e in ld(DON,'ciel/etoiles-reperes.json')['etoiles']]
    V['SKY_CONS']={c['abbr']:{'n':c['nom'],'d':[c['centre_ra_deg'],c['centre_dec_deg'],c['troisieme_valeur']],'l':[flat(s) for s in c['figure']],'b':[flat(s) for s in c['limites']]} for c in ld(DON,'ciel/constellations.json')['constellations']}
    V['CONST']=ld(DON,'ciel/noms-francais-constellations.json')['noms']; V['MOON_FILTERS']=ld(DON,'lune/filtres.json')['filtres']; return V
def js(v): return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def lit_end(txt,st):
    depth=0;q=None;i=st
    while i<len(txt):
        c=txt[i]
        if q:
            if c=='\\': i+=2; continue
            if c==q: q=None
        elif c in '"\'`': q=c
        elif c in '[{': depth+=1
        elif c in ']}':
            depth-=1
            if depth==0: return i
        i+=1
def remplace(page,V):
    for nom,val in V.items():
        deb='  const '+nom+'='; a=page.index(deb); assert page.count(deb)==1,nom
        st=a+len(deb); assert page[st] in '[{',nom; e=lit_end(page,st)
        page=page[:st]+js(val)+page[e+1:]
    return page
if __name__=='__main__':
    if sys.argv[1]=='migre': migre(sys.argv[2],sys.argv[3]); print('ok')
    else:
        p=open(sys.argv[3],encoding='utf-8').read(); n=remplace(p,charge(sys.argv[2])); open(sys.argv[4],'w',encoding='utf-8').write(n); print('page : %d -> %d octets'%(len(p.encode()),len(n.encode())))
