# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import re, json, base64, io, os
from PIL import Image
p='/home/claude/work.html'; w=open(p,encoding='utf-8').read()
L=w.split('\n'); i=[n for n,l in enumerate(L) if l.startswith('  const DSO_IMG=')][0]
line=L[i]; k=line.index('{'); depth=0; inq=False
for q in range(k,len(line)):
    c=line[q]
    if c=='"' and line[q-1]!='\\': inq=not inq
    if inq: continue
    if c=='{': depth+=1
    elif c=='}':
        depth-=1
        if depth==0: break
old=json.loads(line[k:q+1]); rest=line[q+1:]
print('anciennes entrées :',len(old),'| reste de la ligne :',repr(rest[:20]))
# table installée (images téléchargées de SkyView)
s=open('/home/claude/site086/index.html',encoding='utf-8').read(); i2=s.index('const DSO_IMG='); k2=s.index('{',i2); d=0
for q2 in range(k2,len(s)):
    if s[q2]=='{': d+=1
    elif s[q2]=='}':
        d-=1
        if d==0: break
inst=json.loads(s[k2:q2+1])
new={}; tot=0
for key in old:
    v=inst[key]; im=Image.open('/home/claude/site086/'+v[5]).convert('L'); assert im.size==(512,512),(key,im.size)
    r=im.resize((256,256),Image.LANCZOS); bio=io.BytesIO(); r.save(bio,'JPEG',quality=76,optimize=True)
    b=base64.b64encode(bio.getvalue()).decode(); tot+=len(b); new[key]=[v[0],v[1],v[2],256,256,b]
L[i]='  const DSO_IMG='+json.dumps(new,ensure_ascii=False,separators=(',',':'))+rest
w='\n'.join(L)
def rep(o,n,c=1):
    global w; assert w.count(o)==c,(o[:100],w.count(o)); w=w.replace(o,n)
rep("Elles proviennent du projet <i>messier-poster</i> de Y. Kim, qui les a extraites du DSS via WikiSky ; vingt-sept d’entre elles ont été retéléchargées depuis le service SkyView de la NASA (même relevé DSS, aux positions d’OpenNGC) et retraitées de la même façon.","Elles ont été téléchargées depuis SkyView, le service de la NASA qui diffuse le relevé DSS, pour la position et le champ de chaque objet (la position de 27 d’entre elles a été recalée d’après OpenNGC), puis retraitées de la même façon.")
rep('<li><a href="https://github.com/y-kim/messier-poster" target="_blank" rel="noopener">messier-poster (Y. Kim) : images des objets de Messier</a></li>','<li><a href="https://gsss.stsci.edu/Acknowledgements/DSSCopyrights.htm" target="_blank" rel="noopener">DSS : droits d’auteur et mentions (STScI)</a></li>')
rep("<p>Photos du ciel profond : « The Digitized Sky Survey was produced at the Space Telescope Science Institute under U.S. Government grant NAG W-2166. The images of these surveys are based on photographic data obtained using the Oschin Schmidt Telescope on Palomar Mountain and the UK Schmidt Telescope. » Leur utilisation est libre pour un usage non commercial, avec cette mention.</p>","<p>Images du ciel profond (Digitized Sky Survey, DSS) : « The Digitized Sky Survey was produced at the Space Telescope Science Institute under U.S. Government grant NAG W-2166. The images of these surveys are based on photographic data obtained using the Oschin Schmidt Telescope on Palomar Mountain and the UK Schmidt Telescope. The plates were processed into the present compressed digital form with the permission of these institutions. » Ces images restent protégées par le droit d’auteur de leurs détenteurs : © California Institute of Technology (relevés POSS-II du ciel nord), © Anglo-Australian Observatory Board (relevés UKST du ciel sud), © AURA / STScI (autres plaques). Leur utilisation est libre pour la recherche, l’enseignement et les activités sans but lucratif, avec mention de la source ; tout usage commercial exige l’autorisation des détenteurs. Images obtenues avec SkyView : « We acknowledge the use of NASA’s SkyView facility (skyview.gsfc.nasa.gov) located at NASA Goddard Space Flight Center. »</p>")
open(p,'w',encoding='utf-8').write(w); print('ok : %d entrées, %.2f Mo de base64, page %.3f Mo'%(len(new),tot/1e6,len(w.encode())/1e6))
