# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Construction du site installé 0.87 à partir du site 0.86 (script de la 0.86 adapté)
# (ancien en-tête : construction du site installé 0.79 à partir du site 0.78 (données, photos, images, relief fin, étoiles inchangés) et de la page en ligne actuelle,
# avec la texture fine (289 fichiers), le fichier d'informations stellaires, le manifeste (autonome, rotation libre) et le service worker 078.)
import re, os, shutil, zipfile, json
PAGE='/home/claude/work.html'; OLDZIP='/mnt/user-data/outputs/assistant-observation-site-0.86.zip'; AS='/mnt/user-data/outputs/build083-assets/'
OUT='/home/claude/site087'; shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
z=zipfile.ZipFile(OLDZIP); page=open(PAGE,encoding='utf-8').read(); old=z.read('index.html').decode('utf-8')
def bounds(txt):
    L=txt.split('\n'); i=[n for n,l in enumerate(L) if l.startswith('  const DSO_IMG=')][0]; last=max(n for n,l in enumerate(L) if re.match(r"  DSO_IMG\[",l)); return L,i,last
LP,ip,lp=bounds(page); LS,is_,ls=bounds(old)
LP[ip:lp+1]=LS[is_:ls+1]; w='\n'.join(LP)                      # table des images du ciel : fichiers du site installé
w,n1=re.subn(r"const MOON_MAP='data:image/jpeg;base64,[A-Za-z0-9+/=]+'","const MOON_MAP=''",w,count=1)
w,n2=re.subn(r"const DEM_MAP='data:image/webp;base64,[A-Za-z0-9+/=]+'","const DEM_MAP=''",w,count=1)
assert n1==1 and n2==1
o="window.FIELD_URL='img/etoiles.bin.gz';"; assert w.count(o)==1
w=w.replace(o,o+" window.STARINFO_URL='img/etoiles-info.bin.gz'; window.PLACES_URL='img/lieux.bin.gz'; window.TEX_TILES_URL='img/tuiles/manifest.json'; window.MOON_MAP_URL='img/moon-texture.jpg'; window.DEM_MAP_URL='img/relief.webp';")
k=w.index('<script id="listes-saisonnieres">'); e=w.index('</script>',k)
open(OUT+'/listes-saisonnieres.js','w',encoding='utf-8').write(w[k+len('<script id="listes-saisonnieres">'):e].strip()+'\n')
w=w[:k]+'<script src="listes-saisonnieres.js"></script>'+w[e+len('</script>'):]
open(OUT+'/index.html','w',encoding='utf-8').write(w)
for n in z.namelist():
    if n in('index.html','sw.js','manifest.webmanifest') or n.endswith('/'): continue
    d=OUT+'/'+n; os.makedirs(os.path.dirname(d),exist_ok=True); open(d,'wb').write(z.read(n))
shutil.copy('/mnt/user-data/outputs/build086-assets/lieux.bin.gz',OUT+'/img/lieux.bin.gz'); shutil.copy(AS+'manifest.webmanifest',OUT+'/manifest.webmanifest'); shutil.copy(AS+'moon-texture.jpg',OUT+'/img/moon-texture.jpg'); shutil.rmtree(OUT+'/img/tuiles'); shutil.copytree(AS+'tuiles',OUT+'/img/tuiles'); shutil.copy(AS+'relief-fin.bin.gz',OUT+'/img/relief-fin.bin.gz'); shutil.copy(AS+'relief.webp',OUT+'/img/relief.webp'); shutil.copy(AS+'LICENSE',OUT+'/LICENSE'); shutil.copy(AS+'LICENCE-LISTES-SAISONNIERES.txt',OUT+'/LICENCE-LISTES-SAISONNIERES.txt'); shutil.copy('/mnt/user-data/outputs/build086-assets/LICENCES-TIERCES.txt',OUT+'/LICENCES-TIERCES.txt')
sw=z.read('sw.js').decode('utf-8').replace('assistant-observation-086','assistant-observation-087')
m=re.search(r"\n(\s*)'\./img/NGC_4631\.jpg',?",sw); assert m
ajout=[]
for root,_,fs in os.walk(OUT+'/img'):
    for f in sorted(fs):
        rel='./'+os.path.relpath(os.path.join(root,f),OUT).replace(os.sep,'/')
        if "'"+rel+"'" not in sw: ajout.append(rel)
sw=sw[:m.end()]+''.join("\n"+m.group(1)+"'"+r+"'," for r in ajout)+sw[m.end():]
if "'./listes-saisonnieres.js'" not in sw:
    assert "'./manifest.webmanifest'," in sw; sw=sw.replace("'./manifest.webmanifest',","'./manifest.webmanifest', './listes-saisonnieres.js',",1); ajout.append('./listes-saisonnieres.js')
if "'./LICENCES-TIERCES.txt'" not in sw:
    sw=sw.replace("'./manifest.webmanifest',","'./manifest.webmanifest', './LICENCES-TIERCES.txt',",1); ajout.append('./LICENCES-TIERCES.txt')
print(len(ajout),'fichiers ajoutés au service worker')
open(OUT+'/sw.js','w',encoding='utf-8').write(sw)
zp='/mnt/user-data/outputs/assistant-observation-site-0.87.zip'
if os.path.exists(zp): os.remove(zp)
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as zz:
    for root,_,fs in os.walk(OUT):
        for f in sorted(fs):
            full=os.path.join(root,f); zz.write(full,os.path.relpath(full,OUT))
nf=sum(len(f) for _,_,f in os.walk(OUT)); tot=sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(OUT) for f in fs)
print(json.dumps({'index_Mo':round(len(w)/1e6,2),'fichiers':nf,'dossier_Mo':round(tot/1e6,1),'zip_Mo':round(os.path.getsize(zp)/1e6,1)},ensure_ascii=False))
