# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 3A : reconstruit les 13 littéraux de données lunaires de la page depuis donnees/lune/*.json (la logique du code ne change pas).
# Usage : python3 construit_lune.py DONNEES_DIR PAGE_ENTREE.html PAGE_SORTIE.html
import sys, re, json, os
ORDRE=['FEATURES','DESC','FEAT_M','FIX','MONS','ST','HH_CH','SP_CH','S1H','LUN_EXTRA','MEAS2','EX2','DPM']
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
def localise(page):
    pos={}; cur=0
    for n in ORDRE:
        m=re.compile(r"(?<![\w$.])"+n+r"\s*=\s*([\[{])").search(page,cur if n!='FEATURES' else 0)
        st=m.end()-1; e=lit_end(page,st); pos[n]=(st,e); cur=e+1
    return pos
def charge(don):
    ld=lambda f: json.load(open(os.path.join(don,'lune',f),encoding='utf-8'))
    V={}
    V['FEATURES']=[[f['nom'],f['lon_deg'],f['lat_deg']]+([f['priorite']] if 'priorite' in f else []) for f in ld('formations-base.json')['formations']]
    V['DESC']=ld('descriptions-base.json')['descriptions']; V['FEAT_M']=ld('mesures-base.json')['mesures']
    c=ld('corrections-0.76.json'); V['FIX']={k:c[k] for k in ('pos','d','meas','repl','rename','remove') if k in c}
    m=ld('montagnes.json'); [V.__setitem__(k,m[k]) for k in ('MONS','ST','HH_CH','SP_CH','S1H')]
    cr=ld('extra-craters.json')['craters']; do=ld('extra-domes.json'); autres={k:v for k,v in do.items() if k not in('schema','description','domes')}
    V['LUN_EXTRA']={'craters':[[x['nom'],x['lon_deg'],x['lat_deg'],x['diametre_km']] for x in cr],'domes':[[x['nom'],x['lon_deg'],x['lat_deg'],x['diametre_km'],x['fiabilite']] for x in do['domes']],**autres}
    V['MEAS2']=ld('mesures-relief.json')['mesures']
    V['EX2']=[[x['nom'],x['lon_deg'],x['lat_deg'],x['diametre_km']]+([x['profondeur_m'],x['rempart_m'],x['fond_m'],x['pic_central_m']] if 'profondeur_m' in x else []) for x in ld('extra-craters-mesures.json')['craters']]
    V['DPM']=ld('profondeurs-maximales.json')['dpm']; return V
def js(v): return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def remplace(page,V):
    pos=localise(page)
    for n in reversed(ORDRE):
        a,b=pos[n]; page=page[:a]+js(V[n])+page[b+1:]
    return page
if __name__=='__main__':
    V=charge(sys.argv[1]); p=open(sys.argv[2],encoding='utf-8').read(); n=remplace(p,V); open(sys.argv[3],'w',encoding='utf-8').write(n)
    print('page : %d -> %d octets'%(len(p.encode()),len(n.encode())))
