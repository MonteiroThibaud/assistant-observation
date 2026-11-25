# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 1 de la migration : registre des sources (donnees/sources.json) et générateur du menu « Liens des sources » d'Informations.
# Usage : python3 construit_liens.py extrait PAGE.html donnees/sources.json     (crée le registre à partir de la page)
#         python3 construit_liens.py verifie PAGE.html donnees/sources.json     (régénère le menu et le compare à la page)
import sys, re, json, html, unicodedata
DEBUT='<summary>Liens des sources</summary>'
def segment(page):
    a=page.index(DEBUT); a=page.index('\n',a)+1; b=page.index('\n    </details>',a); return a,b
def slug(t):
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower(); t=re.sub(r'[^a-z0-9]+','-',t).strip('-'); return t[:48]
LICENCES={'astronomy-engine-don-cross':'MIT','astronomia-commenthol-d-apres-jean-meeus':'MIT','satellite-js-shashwat-kandadai':'MIT','d3-celestial-olaf-frohn-constellations-et-catalogues':'BSD-3-Clause','openngc-mattia-verga-positions-du-ciel-profond':'CC-BY-SA-4.0','at-hyg-david-nash-types-spectraux-et-distances':'CC-BY-SA-4.0'}
def extrait(page):
    a,b=segment(page); seg=page[a:b]; lines=seg.split('\n')
    intro=re.match(r'\s*<p>(.*)</p>$',lines[0]).group(1)
    reg={'version_registre':1,'intro':html.unescape(intro),'categories':[]}; used=set()
    corps='\n'.join(lines[1:])
    for m in re.finditer(r'<p><b>([^<]+)</b></p><ul>(.*?)</ul>',corps,re.S):
        cat={'id':slug(html.unescape(m.group(1))),'titre':html.unescape(m.group(1)),'liens':[]}
        for l in re.finditer(r'<li><a href="([^"]+)" target="_blank" rel="noopener">(.*?)</a></li>',m.group(2),re.S):
            t=html.unescape(l.group(2)); i=slug(t); k=2
            while i in used: i=slug(t)+'-'+str(k); k+=1
            used.add(i); cat['liens'].append({'id':i,'titre':t,'url':html.unescape(l.group(1)),'licence':LICENCES.get(i)})
        reg['categories'].append(cat)
    return reg
def genere(reg):
    e=lambda t: html.escape(t,quote=False)
    out=['      <p>'+e(reg['intro'])+'</p>']
    out.append('      '+''.join('<p><b>'+e(c['titre'])+'</b></p><ul>'+''.join('<li><a href="'+e(l['url'])+'" target="_blank" rel="noopener">'+e(l['titre'])+'</a></li>' for l in c['liens'])+'</ul>' for c in reg['categories']))
    return '\n'.join(out)
if __name__=='__main__':
    cmd,pagef,regf=sys.argv[1:4]; page=open(pagef,encoding='utf-8').read()
    if cmd=='extrait':
        reg=extrait(page); json.dump(reg,open(regf,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        print(len(reg['categories']),'catégories,',sum(len(c['liens']) for c in reg['categories']),'liens')
    else:
        reg=json.load(open(regf,encoding='utf-8')); a,b=segment(page); cur=page[a:b]; new=genere(reg)
        print('IDENTIQUE octet pour octet' if cur==new else 'DIFFÉRENT'); 
        if cur!=new:
            import difflib; 
            for i,(x,y) in enumerate(zip(cur,new)):
                if x!=y: print(i,repr(cur[max(0,i-60):i+80]),'\n',repr(new[max(0,i-60):i+80])); break
        sys.exit(0 if cur==new else 1)
