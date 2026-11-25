# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import os
import gzip, struct, math
buf=gzip.decompress(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','site-statique','img','lieux.bin.gz'),'rb').read()); assert buf[:4]==b'LIEU'
nCom,nl=struct.unpack_from('<II',buf,8); p=16; names=buf[p:p+nl].decode('utf-8').split('\n'); p+=nl; p=(p+3)&~3
meta=[struct.unpack_from('<iiiiII',buf,p+24*i) for i in range(nCom)]; p+=24*nCom
gl,=struct.unpack_from('<I',buf,p); p+=4; g0=p; p+=gl; p=(p+3)&~3
nP,=struct.unpack_from('<I',buf,p); p+=4
lat=struct.unpack_from('<%dh'%nP,buf,p); p+=2*nP; lon=struct.unpack_from('<%dh'%nP,buf,p); p+=2*nP; p=(p+3)&~3
cc=buf[p:p+2*nP]; p+=2*nP; p=(p+3)&~3
pl,=struct.unpack_from('<I',buf,p); p+=4; pnames=buf[p:p+pl].decode('utf-8').split('\n')
def rv(b,i):
    x=0;s=0
    while True:
        c=b[i];i+=1; x|=(c&0x7F)<<s; s+=7
        if c<128: return x,i
def rings(off):
    i=g0+off; n,i=rv(buf,i); out=[]
    for _ in range(n):
        m,i=rv(buf,i); px=py=0; r=[]
        for _ in range(m):
            a,i=rv(buf,i); b_,i=rv(buf,i); px+=(a>>1)^-(a&1); py+=(b_>>1)^-(b_&1); r.append((px,py))
        out.append(r)
    return out
def inside(x,y,rs):
    c=False
    for r in rs:
        j=len(r)-1
        for i in range(len(r)):
            xi,yi=r[i]; xj,yj=r[j]
            if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: c=not c
            j=i
    return c
def lieu(la,lo):
    x=round(lo*1e4); y=round(la*1e4)
    for (a,b,c,d,ni,off) in meta:
        if a<=x<=c and b<=y<=d and inside(x,y,rings(off)): return names[ni]+' (France)','commune'
    best=None
    for k in range(nP):
        dy=(lat[k]/100-la); dx=(lon[k]/100-lo)*math.cos(math.radians(la)); d=dx*dx+dy*dy
        if best is None or d<best[0]: best=(d,k)
    km=math.sqrt(best[0])*111.2; k=best[1]
    return (pnames[k]+' ('+cc[2*k:2*k+2].decode()+'), à %.0f km'%km if km<=30 else None),'monde'
tests=[('Roanne',46.0345,4.0720),('Paris',48.8566,2.3522),('Lyon',45.7640,4.8357),('Marseille',43.2965,5.3698),('Saint-Étienne',45.4397,4.3872),('Ajaccio',41.9192,8.7386),('Mer Méditerranée',42.5,5.0),('Bruxelles',50.8503,4.3517),('Genève',46.2044,6.1432),('La Réunion (Saint-Denis)',-20.8789,55.4481),('Tokyo',35.6762,139.6503),('Sahara',25.0,10.0)]
for n,a,b in tests: print('%-26s %.4f %.4f → %s'%(n,a,b,lieu(a,b)))
