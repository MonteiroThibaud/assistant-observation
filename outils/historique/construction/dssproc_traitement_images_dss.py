# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Traitement des images DSS téléchargées de SkyView (reconstitué à partir des transcriptions de la version 0.72 ; JPEG de qualité 76 en sortie)
import numpy as np, cv2, json, re
def types():
    s=open('/home/claude/work.html').read()
    def grab(name):
        i=s.index('const '+name+'='); j=s.index(';\n',i); return json.loads(s[i+len('const '+name+'='):j])
    return {d[0]:(d[3],d[5],d[6]) for d in grab('MESSIER')+grab('DSO_EXTRA')}
T=types()
DIFFUSE={'snr','sfr','rn','bn','en'}
def deseam(a):
    # Raccords de plaques photographiques : marches horizontales ou verticales du fond de ciel, corrigées seulement si elles sont nettes
    from scipy.ndimage import median_filter
    out=a.copy()
    for axis in (1,0):
        prof=np.percentile(out,20,axis=axis)
        prof=median_filter(prof,size=9,mode='nearest')
        k=10; step=np.abs(prof[2*k:]-prof[:-2*k]).max()
        if step>0.035: out=out-(prof-np.median(prof))[(slice(None),None) if axis==1 else (None,slice(None))]
    return out
def process(path, ident):
    typ=T[ident][0]
    a=cv2.imread(path,cv2.IMREAD_GRAYSCALE).astype(np.float32)/255
    a=cv2.GaussianBlur(a,(0,0),0.7)
    if typ not in DIFFUSE: a=deseam(a)
    big=max(T[ident][1] or 0,T[ident][2] or 0)
    diffuse = typ in DIFFUSE or big>=25   # nébuleuses et grands objets : fond de ciel plus bas, contraste plus doux
    sky=np.percentile(a,6 if diffuse else 35)
    peak=np.percentile(a,99.8)
    if peak-sky<0.08: peak=sky+0.08
    b=np.clip((a-sky)/(peak-sky),0,1)
    bp=0.05 if diffuse else 0.10
    b=np.clip((b-bp)/(1-bp),0,1)**(1.15 if diffuse else 1.5)
    n=a.shape[0]; yy,xx=np.mgrid[0:n,0:n]; r=np.hypot((xx-n/2)/(n/2),(yy-n/2)/(n/2))
    b*=np.clip((1-r)/0.12,0,1)
    return (b*255).astype(np.uint8), typ
