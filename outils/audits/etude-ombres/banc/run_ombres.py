# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys, os, json, time; sys.path.insert(0,'/home/claude/p2'); from ombres_lib import *
DIR='/mnt/user-data/outputs/etude-ombres/'; BUDGET=float(sys.argv[1]) if len(sys.argv)>1 else 250; T0=time.time()
import math
DATES=json.load(open(DIR+'dates.json')); RES=DIR+'resultats.json'
FORM=json.load(open('/mnt/user-data/outputs/donnees/lune/formations.json',encoding='utf-8')); FORM=FORM['formations'] if isinstance(FORM,dict) else FORM
POS={x['nom']:(float(x['lon_deg']),float(x['lat_deg'])) for x in FORM}
def elev(lo,la,sl,sp):
    r=math.radians; return math.degrees(math.asin(max(-1,min(1,math.sin(r(la))*math.sin(r(sp))+math.cos(r(la))*math.cos(r(sp))*math.cos(r(lo-sl))))))
def dist(lo,la,l2,p2):
    r=math.radians; return math.degrees(math.acos(max(-1,min(1,math.sin(r(la))*math.sin(r(p2))+math.cos(r(la))*math.cos(r(p2))*math.cos(r(lo-l2))))))
res=json.load(open(RES)) if os.path.exists(RES) else {'cas':[]}
faits={(c['date'],c['region'],c['plan']) for c in res['cas']}; ndates={}
for c in res['cas']: ndates[c['date']]=ndates.get(c['date'],0)+1
POOL={'pôle':['Cabeus','Malapert','Newton','Mons Mouton','Byrd','Erlanger','Fibiger','Gore','Grignard'],'bord':['Mare Humboldtianum','Mare Smythii','Mare Marginis','Humboldt','Grimaldi','Mare Orientale','Olbers','Lacus Autumni','Vallis Baade','Langrenus','Mare Crisium'],
 'plateau':['Tycho','Clavius','Maurolycus','Montes Apenninus','Montes Alpes'],'mer':['Mare Serenitatis','Mare Tranquillitatis','Mare Imbrium','Mare Nubium','Mare Fecunditatis','Mare Humorum','Sinus Iridum']}
PLAN=[(None,'x1'),('pôle','x10'),('bord','x3'),('plateau','x30'),('mer','x10'),('bord','xmax'),('pôle','x30'),('plateau','x3'),('mer','x30'),('bord','x10'),('plateau','x10'),('mer','xmax')]
VARS=['ref','perturb','reg','blk1','blk2']; CIBLE=int(sys.argv[2]) if len(sys.argv)>2 else 7
srv=C.serve('/home/claude/ng/ot',9061)
try:
  with sync_playwright() as p:
    for di,dt in enumerate(DATES):
        if ndates.get(dt['t'],0)>=CIBLE: continue
        if time.time()-T0>BUDGET-110: break
        b,pg,errs=ouvre(p,9061,dt['t'])
        try:
            vue(pg,None,'x1'); sun=pg.evaluate("(()=>{const F=window.__argsFull[3], d=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; const sx=d(F.sd,F.Mm), sy=d(F.sd,F.Ym), sz=d(F.sd,F.pl); return [Math.atan2(sy,sx)*180/Math.PI, Math.asin(Math.max(-1,Math.min(1,sz)))*180/Math.PI]})()")
            print('--- %s : Soleil au zénith en lon %.1f lat %.1f ; centre du disque lon %.1f lat %.1f'%(dt['etiquette'],sun[0],sun[1],dt['elon'],dt['elat']),flush=True)
            for si,(cat,plan) in enumerate(PLAN):
                if ndates.get(dt['t'],0)>=CIBLE or time.time()-T0>BUDGET-25: break
                if cat is None: cand=[None]
                else:
                    base=POOL[cat][(di*3+si)%len(POOL[cat]):]+POOL[cat][:(di*3+si)%len(POOL[cat])]
                    cand=[n for n in base if n in POS and dist(POS[n][0],POS[n][1],dt['elon'],dt['elat'])<84 and 1.0<elev(POS[n][0],POS[n][1],sun[0],sun[1])<89]
                    if not cand: print('   aucune région « %s » éclairée et visible'%cat,flush=True); continue
                for reg in cand[:4]:
                    if (dt['t'],reg,plan) in faits: break
                    z=vue(pg,reg,plan)
                    r=pg.evaluate("window.__evalCase(%s,'full')"%json.dumps(VARS))
                    if 'err' in r: continue
                    f=r['ref']['ray']/max(1,r['ref']['disk'])
                    if f<(0.03 if plan=='x1' else 0.15): print('   rejeté (peu éclairé %.0f %%) %s %s'%(100*f,reg,plan),flush=True); continue
                    row={'date':dt['t'],'etiquette':dt['etiquette'],'region':reg,'plan':plan,'categorie':cat,'zoom':z,'passage':'complet','ref':r['ref'],'variantes':{v:r[v] for v in VARS if v!='ref'},'eclaire':round(f,3)}
                    res['cas'].append(row); faits.add((dt['t'],reg,plan)); ndates[dt['t']]=ndates.get(dt['t'],0)+1
                    json.dump(res,open(RES,'w'),ensure_ascii=False)
                    cl=''.join(r[v]['cls'] for v in ('reg','blk1','blk2'))
                    print('%-24s %-20s %-5s x%-4g éclairé %3.0f %% | classes reg/blk1/blk2 : %s | relevés %+.0f %% / %+.0f %% / %+.0f %% | contrôle négatif : %s (écart max %d)'%(dt['etiquette'],reg or 'disque entier',plan,z,100*f,cl,-100*r['reg']['gainSteps'],-100*r['blk1']['gainSteps'],-100*r['blk2']['gainSteps'],r['perturb']['cls'],r['perturb']['maxDiff']),flush=True)
                    break
        finally: b.close()
finally: srv.terminate()
print('total cas enregistrés :',len(res['cas']),'| durée %.0f s'%(time.time()-T0))
