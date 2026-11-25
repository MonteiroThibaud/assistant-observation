# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Fabrique le fichier « lieux.bin.gz » de l'application : contours des communes de France (IGN Admin Express 2018 via france-geojson,
# noms mis à jour d'après le découpage administratif actuel d'Etalab) et lieux habités du monde (GeoNames, plus de 1 000 habitants).
import json, struct, gzip, csv, sys, collections
GJ='/home/claude/geo/communes.geojson'; ET='/home/claude/geo/et/package/data/communes.json'; CSV='/home/claude/geo/reverse_geocoder-1.5.1/reverse_geocoder/rg_cities1000.csv'
OUT=sys.argv[1] if len(sys.argv)>1 else '/home/claude/geo/lieux.bin.gz'
Q=10000
def zz(n): return (n<<1)^(n>>63)
def varint(n,b):
    while True:
        x=n&0x7F; n>>=7
        if n: b.append(x|0x80)
        else: b.append(x); break
# --- noms actuels
et=json.load(open(ET,encoding='utf-8'))
act={x['code']:x['nom'] for x in et if x['type']=='commune-actuelle'}
dele={}
for x in et:
    if x['type'] in('commune-deleguee','commune-associee') and x.get('chefLieu'): dele[x['code']]=x['chefLieu']
def nom_actuel(code,nom2018):
    if code in act: return act[code]
    c=dele.get(code)
    if c and c in act: return act[c]
    return nom2018
gj=json.load(open(GJ,encoding='utf-8'))
coms=[]; names=[]; nidx={}; geom=bytearray(); meta=[]; depc=[]
for f in gj['features']:
    g=f.get('geometry')
    if not g: continue
    code=f['properties']['code']; depc.append(code[:3] if code[:2] in ('97','98') else code[:2])   # département : deux premiers chiffres du code INSEE (trois pour l'outre-mer, 2A et 2B pour la Corse)
    nm=nom_actuel(code,f['properties']['nom'])
    if nm not in nidx: nidx[nm]=len(names); names.append(nm)
    polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
    rings=[r for p in polys for r in p]
    off=len(geom); varint(len(rings),geom)
    minx=miny=10**9; maxx=maxy=-10**9
    for r in rings:
        pts=[(round(x*Q),round(y*Q)) for x,y in r]
        if len(pts)>1 and pts[0]==pts[-1]: pts=pts[:-1]
        varint(len(pts),geom); px=py=0
        for k,(x,y) in enumerate(pts):
            varint(zz(x-px),geom); varint(zz(y-py),geom); px,py=x,y
            minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y)
    meta.append((minx,miny,maxx,maxy,nidx[nm],off))
nb='\n'.join(names).encode('utf-8')
out=bytearray(b'LIEU'+struct.pack('<BBH',1,0,0))
out+=struct.pack('<II',len(meta),len(nb)); out+=nb
while len(out)%4: out.append(0)
for m in meta: out+=struct.pack('<iiiiII',*m)
out+=struct.pack('<I',len(geom)); out+=geom
while len(out)%4: out.append(0)
# --- lieux du monde
rows=list(csv.DictReader(open(CSV,encoding='utf-8')))
lat=[round(float(r['lat'])*100) for r in rows]; lon=[round(float(r['lon'])*100) for r in rows]
cc=b''.join(r['cc'].encode('ascii').ljust(2,b' ')[:2] for r in rows)
pn='\n'.join(r['name'].replace('\n',' ') for r in rows).encode('utf-8')
out+=struct.pack('<I',len(rows))
out+=struct.pack('<%dh'%len(rows),*lat); out+=struct.pack('<%dh'%len(rows),*lon)
while len(out)%4: out.append(0)
out+=cc
while len(out)%4: out.append(0)
out+=struct.pack('<I',len(pn)); out+=pn
# --- départements (ajout : 0.89) : un octet par commune (rang du code dans la liste triée), puis la liste des codes ; lu après les noms des lieux, ignoré par les anciens lecteurs
dn=sorted(set(depc)); di={c:i for i,c in enumerate(dn)}
while len(out)%4: out.append(0)
out+=struct.pack('<I',len(depc)); out+=bytes(di[c] for c in depc)
while len(out)%4: out.append(0)
dnb='\n'.join(dn).encode('ascii'); out+=struct.pack('<I',len(dnb)); out+=dnb
data=bytes(out); gz=gzip.compress(data,9)
open(OUT,'wb').write(gz)
print('départements :',len(dn),'|',end=' '); print('communes :',len(meta),'| noms uniques :',len(names),'| géométrie : %.2f Mo | lieux du monde : %d | brut %.2f Mo | compressé %.2f Mo'%(len(geom)/1e6,len(rows),len(data)/1e6,len(gz)/1e6))
