# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Fabrique « departements.bin.gz » : les limites des départements de France métropolitaine, pour le fond de la carte de zone de l'ISS au-delà du fond détaillé.
Entrée : img/lieux.bin.gz (contours des communes et département de chacune, voir fabrique_lieux.py). Une limite de département est une arête portée par deux
communes de départements différents (la côte et les frontières ne sont pas des limites de département : comme dans le fond détaillé, on ne les trace pas).
Les arêtes sont chaînées en lignes, simplifiées (Douglas-Peucker, 4 unités de 1/10 000° : environ 44 m), puis écrites : magique 'DEPT', nombre de lignes (u32),
puis pour chaque ligne : nombre de points (varint), premier point (zigzag x, y) et écarts (zigzag), en unités de 1/10 000°.
Usage : python3 fabrique_departements.py LIEUX.bin.gz SORTIE.bin.gz"""
import sys, gzip, struct, numpy as np
src,dst=sys.argv[1:3]; TOL=4
buf=gzip.open(src).read(); u8=np.frombuffer(buf,dtype=np.uint8)
assert struct.unpack_from('<I',buf,0)[0]==0x5545494C
nCom,nl=struct.unpack_from('<II',buf,8); p=16+nl; p=(p+3)&~3
meta=np.frombuffer(buf,dtype=np.int32,count=nCom*6,offset=p).reshape(nCom,6); p+=24*nCom
gl=struct.unpack_from('<I',buf,p)[0]; p+=4; g0=p; p+=gl; p=(p+3)&~3
nP=struct.unpack_from('<I',buf,p)[0]; p+=4; p+=4*nP; p=(p+3)&~3; p+=2*nP; p=(p+3)&~3
pl=struct.unpack_from('<I',buf,p)[0]; p+=4; p+=pl; p=(p+3)&~3
nd=struct.unpack_from('<I',buf,p)[0]; assert nd==nCom; p+=4; dep=np.frombuffer(buf,dtype=np.uint8,count=nd,offset=p)
def rings(off):
    i=g0+off; out=[]
    def rv():
        nonlocal i
        v=0; sh=0
        while True:
            c=buf[i]; i+=1; v|=(c&127)<<sh; sh+=7
            if c<128: return v
    nr=rv()
    for _ in range(nr):
        m=rv(); px=py=0; pts=[]
        for _ in range(m):
            a=rv(); b=rv(); px+=(a>>1)^-(a&1); py+=(b>>1)^-(b&1); pts.append((px,py))
        out.append(pts)
    return out
E0=[]; E1=[]; D=[]
for k in range(nCom):
    for pts in rings(int(meta[k,5])):
        m=len(pts)
        for i in range(m):
            a=pts[i]; b=pts[(i+1)%m]
            if a==b: continue
            pa=(a[0]+400000)*2000000+(a[1]+100000); pb=(b[0]+400000)*2000000+(b[1]+100000)
            if pa>pb: pa,pb=pb,pa
            E0.append(pa); E1.append(pb); D.append(int(dep[k]))
E0=np.array(E0,dtype=np.int64); E1=np.array(E1,dtype=np.int64); D=np.array(D,dtype=np.int16)
o=np.lexsort((E1,E0)); E0=E0[o]; E1=E1[o]; D=D[o]
same=(E0[1:]==E0[:-1])&(E1[1:]==E1[:-1])&(D[1:]!=D[:-1])
idx=np.nonzero(same)[0]
bord=set((int(E0[i]),int(E1[i])) for i in idx)
print('communes',nCom,'arêtes',len(E0),'arêtes de limite de département',len(bord))
adj={}
for a,b in bord: adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
def pt(v): return (v//2000000-400000, v%2000000-100000)
used=set(); chains=[]
def walk(start,first):
    ch=[start,first]; used.add((min(start,first),max(start,first))); prev,cur=start,first
    while True:
        nx=[n for n in adj[cur] if (min(cur,n),max(cur,n)) not in used]
        if len(adj[cur])!=2 or not nx: break
        n=nx[0]; used.add((min(cur,n),max(cur,n))); ch.append(n); prev,cur=cur,n
        if cur==start: break
    return ch
for v in adj:                                                         # d'abord les lignes qui partent d'un nœud (jonction ou extrémité), puis les boucles
    if len(adj[v])!=2:
        for n in adj[v]:
            if (min(v,n),max(v,n)) not in used: chains.append(walk(v,n))
for v in adj:
    for n in adj[v]:
        if (min(v,n),max(v,n)) not in used: chains.append(walk(v,n))
def dp(pts,tol):
    if len(pts)<3: return pts
    keep=np.zeros(len(pts),bool); keep[0]=keep[-1]=True; stack=[(0,len(pts)-1)]; P=np.array(pts,dtype=float)
    while stack:
        a,b=stack.pop()
        if b<=a+1: continue
        A=P[a]; B=P[b]; d=B-A; L=np.hypot(*d)
        seg=P[a+1:b]
        dist=np.hypot(*(seg-A).T) if L==0 else np.abs(d[0]*(seg[:,1]-A[1])-d[1]*(seg[:,0]-A[0]))/L
        j=int(np.argmax(dist))
        if dist[j]>tol: m=a+1+j; keep[m]=True; stack.append((a,m)); stack.append((m,b))
    return [pts[i] for i in range(len(pts)) if keep[i]]
out=bytearray(b'DEPT'); out+=struct.pack('<I',len(chains)); tot=0
def varint(n):
    b=bytearray()
    while True:
        x=n&127; n>>=7
        if n: b.append(x|128)
        else: b.append(x); break
    return b
def zz(n): return (n<<1)^(n>>63)
for ch in chains:
    pts=dp([pt(v) for v in ch],TOL); tot+=len(pts)
    out+=varint(len(pts)); px=py=0
    for x,y in pts: out+=varint(zz(x-px)); out+=varint(zz(y-py)); px,py=x,y
gzip.open(dst,'wb',9).write(bytes(out))
import os; print('lignes',len(chains),'points',tot,'octets (gz) :',os.path.getsize(dst))
