# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 5 : textes d'Informations (français) -> donnees/textes/fr/informations.json ; les menus « Liens des sources » et
# « Licences des composants tiers » sont générés depuis le registre des sources et les textes de licences ; le numéro de version vient de donnees/version.json.
# Usage : python3 construit_textes.py migre PAGE.html DONNEES_DIR
#         python3 construit_textes.py verifie DONNEES_DIR PAGE.html          (régénère la section et la compare à la page)
#         python3 construit_textes.py construit DONNEES_DIR PAGE_IN PAGE_OUT
import sys, json, os, re, importlib.util
ICI=os.path.dirname(os.path.abspath(__file__))
def charge_mod(nom):
    sp=importlib.util.spec_from_file_location(nom,os.path.join(ICI,nom+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
DEB='<section class="about"'; FINSEC='</section>'
SEP='\n\n    <details>\n      <summary>'
def decoupe(seg):
    i=seg.index('\n\n    <details>'); entete=seg[:i]
    reste=seg[i:]; menus=[]
    for m in re.finditer(r'(\n\n?)    <details>(\n      )?<summary>(.*?)</summary>\n(.*?)\n    </details>',reste,re.S):
        menus.append((m.group(3),m.group(4),m.group(2) is None,m.group(1)))
    fin=reste[reste.rindex('</details>')+len('</details>'):]
    return entete,menus,fin
def migre(page,don):
    s=open(page,encoding='utf-8').read(); a=s.index(DEB); b=s.index(FINSEC,a)+len(FINSEC); seg=s[a:b]
    entete,menus,fin=decoupe(seg)
    m=re.search(r'Version ([\d.]+) du (.+?)(?: \((.+?)\))?<',entete); ver={'numero':m.group(1),'date':m.group(2)}
    entete=entete.replace(m.group(0)[:-1],'Version {{numero}} du {{date}}')
    out={'schema':'textes-informations-v1','langue':'fr','description':"Section Informations de l'application, en français. Chaque menu est une liste de lignes HTML. Les marques {{…}} sont remplacées à la construction : version (donnees/version.json), liens des sources (donnees/sources.json), licences des composants tiers (donnees/licences-tierces/).",'entete':entete.split('\n'),'menus':[],'fin':fin.split('\n')}
    for titre,corps,compact,sep in menus:
        mn={'titre':titre}
        if sep!='\n\n': mn['saut_de_ligne_unique_avant']=True
        if compact: mn['balise_sur_une_ligne']=True
        if titre=='Liens des sources': mn['genere']='liens'
        elif titre=='Licences des composants tiers':
            mn['genere']='licences'; mn['lignes']=re.sub(r'<pre class="lictxt">.*?</pre>','<pre class="lictxt">{{licences}}</pre>',corps,flags=re.S).split('\n')
        else: mn['lignes']=corps.split('\n')
        out['menus'].append(mn)
    os.makedirs(os.path.join(don,'textes','fr'),exist_ok=True)
    json.dump(out,open(os.path.join(don,'textes','fr','informations.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    json.dump({'numero':ver['numero'],'date':ver['date'],},open(os.path.join(don,'version.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(len(out['menus']),'menus ; version',ver)
def genere(don):
    T=json.load(open(os.path.join(don,'textes','fr','informations.json'),encoding='utf-8')); V=json.load(open(os.path.join(don,'version.json'),encoding='utf-8'))
    liens=charge_mod('construit_liens'); lic=charge_mod('construit_licences')
    reg=json.load(open(os.path.join(don,'sources.json'),encoding='utf-8')); bloc=lic.bloc_page(lic.charge(don))
    ent='\n'.join(T['entete']); 
    for k,v in V.items(): ent=ent.replace('{{'+k+'}}',v)
    out=ent
    for mn in T['menus']:
        sep='\n' if mn.get('saut_de_ligne_unique_avant') else '\n\n'
        out+=(sep+'    <details><summary>' if mn.get('balise_sur_une_ligne') else sep+'    <details>\n      <summary>')+mn['titre']+'</summary>\n'
        if mn.get('genere')=='liens': out+=liens.genere(reg)
        else:
            corps='\n'.join(mn['lignes'])
            if mn.get('genere')=='licences': corps=corps.replace('{{licences}}',bloc)
            out+=corps
        out+='\n    </details>'
    return out+'\n'.join(['']+T['fin'])[0:0]+'\n'.join(T['fin'])
def section(page):
    a=page.index(DEB); b=page.index(FINSEC,a)+len(FINSEC); return a,b
if __name__=='__main__':
    c=sys.argv[1]
    if c=='migre': migre(sys.argv[2],sys.argv[3])
    elif c=='verifie':
        p=open(sys.argv[3],encoding='utf-8').read(); a,b=section(p); n=genere(sys.argv[2]); print('section Informations :','IDENTIQUE octet pour octet' if p[a:b]==n else 'DIFFÉRENTE')
        if p[a:b]!=n:
            for i,(x,y) in enumerate(zip(p[a:b],n)):
                if x!=y: print(i,repr(p[a+i-80:a+i+80]),'\n',repr(n[i-80:i+80])); break
            print(len(p[a:b]),len(n))
    else:
        p=open(sys.argv[3],encoding='utf-8').read(); a,b=section(p); open(sys.argv[4],'w',encoding='utf-8').write(p[:a]+genere(sys.argv[2])+p[b:])
