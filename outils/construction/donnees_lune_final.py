# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 3B : une fiche finale par formation lunaire (donnees/lune/formations.json) à la place des couches de correction du code.
# migre : écrit formations.json (valeurs finales de la référence) et notes-sources.md (commentaires de sources du code retiré)
# construit : remplace FEATURES, DESC et FEAT_M par les valeurs finales et SUPPRIME de la page tout le bloc de corrections (13 littéraux et 7 fonctions).
# Usage : python3 donnees_lune_final.py migre PAGE.html REFERENCE_DIR DONNEES_DIR
#         python3 donnees_lune_final.py construit DONNEES_DIR PAGE_ENTREE.html PAGE_SORTIE.html
import sys, json, os, re
DEBUT='\n  // Corrections des notices lunaires (0.76)'; FIN='  const telD='
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
def migre(page,ref,don):
    s=open(page,encoding='utf-8').read(); ld=lambda n: json.load(open(os.path.join(ref,n+'.json'),encoding='utf-8'))
    F,D,M=ld('FEATURES'),ld('DESC'),ld('FEAT_M'); names=[f[0] for f in F]; assert set(D)==set(names) and set(M)<=set(names)
    recs=[]
    for f in F:
        r={'id':'lune:'+f[0],'nom':f[0],'lon_deg':f[1],'lat_deg':f[2]}
        if len(f)>3: r['priorite']=f[3]
        r['description']=D[f[0]]
        if f[0] in M: r['mesures']=M[f[0]]
        recs.append(r)
    out={'schema':'lune-formations-v2','description':"Une fiche finale par formation lunaire (1 161) : position (longitude est positif, latitude nord positive, degrés), priorité (1 = incontournable ; absente = 1), description et mesures (d = taille en km ; rh = hauteur du rempart, dp = profondeur moyenne, dpm = profondeur depuis les crêtes les plus hautes, fl = altitude du fond, pk = pic central, hh = hauteur d'une montagne au-dessus de la plaine, st = altitude du sommet, en mètres ; sp = position [longitude, latitude] du sommet dominant d'une chaîne). Valeurs finales : les corrections successives des versions 0.76 et 0.77 y sont incluses ; leurs sources sont dans notes-sources.md.",
         'formations':recs}
    json.dump(out,open(os.path.join(don,'lune','formations.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    a=s.index(DEBUT); b=s.index(FIN); reg=s[a:b]
    notes=[l.strip()[2:].strip() for l in reg.split('\n') if l.strip().startswith('//')]
    open(os.path.join(don,'lune','notes-sources.md'),'w',encoding='utf-8').write("# Sources et méthodes des données lunaires\n\nCes notes sont les commentaires du code retiré à l'étape 3B (les corrections qu'il appliquait sont maintenant dans `formations.json`). Elles documentent l'origine de chaque correction.\n\n"+'\n\n'.join('- '+n for n in notes)+'\n')
    print(len(recs),'fiches ;',len(notes),'notes de sources ;','région du code retirée :',b-a,'octets')
def charge(don):
    j=json.load(open(os.path.join(don,'lune','formations.json'),encoding='utf-8')); R={f['nom']:f for f in j['formations']}
    F=[[f['nom'],f['lon_deg'],f['lat_deg']]+([f['priorite']] if 'priorite' in f else []) for f in j['formations']]
    return {'FEATURES':F,'DESC':{f['nom']:f['description'] for f in j['formations']},'FEAT_M':{f['nom']:f['mesures'] for f in j['formations'] if 'mesures' in f}}
def js(v): return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def construit(don,page):
    s=open(page,encoding='utf-8').read(); a=s.index(DEBUT); b=s.index(FIN); assert s.count(DEBUT)==1
    s=s[:a]+'\n'+s[b:]
    V=charge(don)
    for n in ('FEAT_M','DESC','FEATURES'):   # de la fin vers le début
        m=re.compile(r"(?<![\w$.])"+n+r"\s*=\s*([\[{])").search(s if n!='FEATURES' else s,0 if n=='FEATURES' else 15300000)
        st=m.end()-1; e=lit_end(s,st); s=s[:st]+js(V[n])+s[e+1:]
    return s
if __name__=='__main__':
    if sys.argv[1]=='migre': migre(*sys.argv[2:5])
    else:
        n=construit(sys.argv[2],sys.argv[3]); open(sys.argv[4],'w',encoding='utf-8').write(n); print('page -> %d octets'%len(n.encode()))
