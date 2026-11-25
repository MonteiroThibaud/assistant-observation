# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import json, numpy as np, math, time, sys
from indep import *
EP=Time(f"20{TLE[1][18:20]}-01-01",scale='utc').jd-1+float(TLE[1][20:32])      # époque du TLE (jd)
DAYS=float(sys.argv[1]) if len(sys.argv)>1 else 60; R=40.0; C=(46.0345,4.072,400.0)
t_start=time.time(); jd0=EP; N=int(DAYS*1440)+2
coarse=jd0+np.arange(N)/1440.0                                                       # une position de l'astre par minute
B={}
for name in ('moon','sun'):
    ts=time.time(); B[name]=body_teme(name,coarse); print(name,'éphémérides :',round(time.time()-ts,1),'s',flush=True)
def body_interp(name,jd):                                                            # interpolation cubique entre les minutes
    x=(jd-jd0)*1440.0; i=np.clip(np.floor(x).astype(int),1,N-3); t=x-i; v0,v1,v2,v3=(B[name][i-1],B[name][i],B[name][i+1],B[name][i+2]); t=t[:,None]
    return 0.5*((2*v1)+(-v0+v2)*t+(2*v0-5*v1+4*v2-v3)*t**2+(-v0+3*v1-3*v2+v3)*t**3)
wins={'moon':[],'sun':[]}
for d in range(int(DAYS)+1):
    jd=jd0+d+np.arange(0,86400,1)/86400.0; jd=jd[jd<jd0+DAYS]
    if not len(jd): break
    th=gmst(jd); o=ecef_to_teme(obs_ecef(*C[:2],C[2])[None,:].repeat(len(jd),0),th); iss=iss_teme(jd)-o
    _,eli=azel(iss,th,C[0],C[1])
    for name in ('moon','sun'):
        b=body_interp(name,jd)-o; _,elb=azel(b,th,C[0],C[1]); s=sep_deg(iss,b)
        m=(s<12)&(eli>-3)&(elb>-3)
        if m.any():
            idx=np.where(m)[0]; groups=np.split(idx,np.where(np.diff(idx)>30)[0]+1)
            for g in groups: wins[name].append((jd[g[0]]-20/86400,jd[g[-1]]+20/86400))
print('fenêtres candidates (ISS et astre à moins de 12° l’un de l’autre, au-dessus de l’horizon) :',{k:len(v) for k,v in wins.items()},'| balayage',round(time.time()-t_start),'s',flush=True)
# grille de lieux dans la zone de 40 km (pas de 5 km)
sites=[(x,y) for x in range(-40,41,5) for y in range(-40,41,5) if math.hypot(x,y)<=R]
glat=[C[0]+y/110.574 for x,y in sites]; glon=[C[1]+x/(111.320*math.cos(math.radians(C[0]))) for x,y in sites]
OBS=[obs_ecef(a,b,C[2]) for a,b in zip(glat,glon)]
events=[]
for name in ('moon','sun'):
    for (a,b) in wins[name]:
        jd=np.arange(a,b,0.1/86400.0); th=gmst(jd); iss=iss_teme(jd); bt=body_interp(name,jd)
        hit=[]
        for k,(ox) in enumerate(OBS):
            o=ecef_to_teme(ox[None,:].repeat(len(jd),0),th); i=iss-o; bb=bt-o; s=sep_deg(i,bb); r=radius_deg(name,bb)
            _,eli=azel(i,th,glat[k],glon[k]); _,elb=azel(bb,th,glat[k],glon[k])
            m=(s<r)&(eli>5)&(elb>5)                                                  # transit avec l'ISS et l'astre à plus de 5° au-dessus de l'horizon
            if m.any(): hit.append((k,float(jd[np.argmax(m)])))
        if hit: events.append({'body':name,'t_jd':float(np.mean([h[1] for h in hit])),'sites':[h[0] for h in hit]})
print('transits trouvés par le calcul indépendant sur la grille de',len(sites),'lieux :',len(events),flush=True)
json.dump({'events':events,'sites':sites,'glat':glat,'glon':glon},open('/tmp/ind_events.json','w'))
for e in events: print(' ',e['body'],time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime((e['t_jd']-2440587.5)*86400)),'UTC |',len(e['sites']),'lieux de la grille en transit',flush=True)
