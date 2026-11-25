# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 3A de la migration : données lunaires (13 littéraux du code) -> donnees/lune/*.json, SANS toucher à la logique du code.
# Chaque littéral est évalué par Node (valeur avant les corrections que le code applique ensuite) puis écrit en JSON à champs nommés.
# Usage : python3 migre_lune.py PAGE.html DONNEES_DIR
import sys, re, json, os, subprocess
PAGE,DON=sys.argv[1:3]; s=open(PAGE,encoding='utf-8').read()
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
ORDRE=['FEATURES','DESC','FEAT_M','FIX','MONS','ST','HH_CH','SP_CH','S1H','LUN_EXTRA','MEAS2','EX2','DPM']
def localise(page):
    """positions (début, fin) de chaque littéral, dans l'ordre du document"""
    pos={}; cur=0
    for n in ORDRE:
        m=re.compile(r"(?<![\w$.])"+n+r"\s*=\s*([\[{])").search(page,cur if n!='FEATURES' else 0)
        st=m.end()-1; e=lit_end(page,st); pos[n]=(st,e); cur=e+1
    return pos
if __name__=='__main__':
    pos=localise(s); val={}
    for n,(a,b) in pos.items():
        js="process.stdout.write(JSON.stringify((function(){return "+s[a:b+1]+"})()))"
        val[n]=json.loads(subprocess.run(['node','-e',js],capture_output=True,text=True,check=True).stdout)
    out=os.path.join(DON,'lune'); os.makedirs(out,exist_ok=True)
    sv=lambda f,o: json.dump(o,open(os.path.join(out,f),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    F=val['FEATURES']
    sv('formations-base.json',{'schema':'lune-formations-v1','description':"Formations lunaires de base : longitude (est positif) et latitude sélénographiques en degrés ; priorité 1 = incontournable (absente : 1 par défaut dans le code).",
        'formations':[dict([('id','lune:'+r[0]),('nom',r[0]),('lon_deg',r[1]),('lat_deg',r[2])]+([('priorite',r[3])] if len(r)>3 else [])) for r in F]})
    sv('descriptions-base.json',{'schema':'lune-descriptions-v1','description':"Descriptions des formations lunaires (texte écrit pour l'application ; les chiffres suivent les valeurs officielles). Clé = nom de la formation.",'descriptions':val['DESC']})
    sv('mesures-base.json',{'schema':'lune-mesures-v1','description':"Mesures de base par formation : d = taille (km) ; rh = hauteur du rempart (m) ; dp = profondeur (m) ; fl = altitude du fond (m) ; pk = hauteur du pic central (m). Mesures faites sur le relief LOLA de la NASA par l'application.",'mesures':val['FEAT_M']})
    sv('corrections-0.76.json',{'schema':'lune-corrections-v1','description':"Corrections des notices lunaires (0.76) : pos = positions et d = tailles du gazetier de nomenclature planétaire de l'UAI et de l'USGS (réseau de contrôle LOLA, fichier du projet LTVT) ; meas = mesures refaites ; repl = remplacements de texte dans les descriptions [nom, ancien, nouveau].",**val['FIX']})
    sv('montagnes.json',{'schema':'lune-montagnes-v1','description':"Hauteurs et altitudes des montagnes : MONS nom -> [hh = hauteur au-dessus de la plaine (m), st = altitude du sommet (m)] ; ST nom -> altitude du sommet ; HH_CH nom -> hauteur ; SP_CH nom -> [longitude, latitude] du sommet ; S1H nom -> hauteur relevée par Jim Singh (LROC QuickMap).",'MONS':val['MONS'],'ST':val['ST'],'HH_CH':val['HH_CH'],'SP_CH':val['SP_CH'],'S1H':val['S1H']})
    E=val['LUN_EXTRA']
    sv('extra-craters.json',{'schema':'lune-extra-craters-v1','description':"Cratères ajoutés (positions et diamètres officiels de l'UAI et de l'USGS) sans mesure de relief : la description dit où chercher.",'craters':[{'id':'lune:'+r[0],'nom':r[0],'lon_deg':r[1],'lat_deg':r[2],'diametre_km':r[3]} for r in E['craters']]})
    sv('extra-domes.json',{'schema':'lune-extra-domes-v1','description':"Dômes ajoutés (Head et Gifford, 1980, via les fichiers de points du projet LTVT) : fiabilité A ou B.",'domes':[{'id':'lune:'+r[0],'nom':r[0],'lon_deg':r[1],'lat_deg':r[2],'diametre_km':r[3],'fiabilite':r[4]} for r in E['domes']],**{k:v for k,v in E.items() if k not in('craters','domes')}})
    sv('mesures-relief.json',{'schema':'lune-mesures-relief-v1','description':"Mesures sur le relief LOLA (MEAS2) : nom -> [dp = profondeur (m), rh = hauteur du rempart (m), fl = altitude du fond (m), pk = pic central (m, 0 = aucun)].",'mesures':val['MEAS2']})
    sv('extra-craters-mesures.json',{'schema':'lune-extra-craters-mesures-v1','description':"Cratères nommés de l'UAI visibles depuis la Terre, avec mesures (EX2).",'craters':[{'id':'lune:'+r[0],'nom':r[0],'lon_deg':r[1],'lat_deg':r[2],'diametre_km':r[3],'profondeur_m':r[4],'rempart_m':r[5],'fond_m':r[6],'pic_central_m':r[7]} if len(r)>4 else {'id':'lune:'+r[0],'nom':r[0],'lon_deg':r[1],'lat_deg':r[2],'diametre_km':r[3]} for r in val['EX2']]})
    sv('profondeurs-maximales.json',{'schema':'lune-profondeurs-max-v1','description':"Profondeur maximale (depuis les crêtes les plus hautes, en m) par cratère (DPM).",'dpm':val['DPM']})
    print({n:(len(v) if hasattr(v,'__len__') else v) for n,v in val.items()}); print(sorted(os.listdir(out)))
