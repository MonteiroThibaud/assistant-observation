# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Listes d'objets du ciel profond : donnees/ciel-profond/listes/*.json -> blocs de la page.
# Un fichier = un ensemble de listes (un livre, un club, une liste perso exportée…) avec sa source et sa licence.
#   libre:false -> bloc « listes-saisonnieres » (fichier séparé dans la version installée, hors licence GPL, avec l'avis du titulaire)
#   libre:true  -> bloc « listes-libres » (dans la page)
# Usage : python3 donnees_listes.py migre PAGE_OU_MODELE.html DONNEES_DIR    (écrit listes/ciel-au-telescope.json depuis le bloc existant)
import sys, os, json, re, subprocess
def charge(don):
    # listes libres : donnees/ciel-profond/listes/ ; listes protégées (Stelvision) : donnees-hors-gpl/stelvision/ ; ordre : nom de fichier
    out=[]
    for d in (os.path.join(don,'ciel-profond','listes'),os.path.join(os.path.dirname(os.path.abspath(don)),'donnees-hors-gpl','stelvision')):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith('.json'): out.append((f,json.load(open(os.path.join(d,f),encoding='utf-8'))))
    return sorted(out,key=lambda x:x[0])
def q(s): return "'"+s.replace('\\','\\\\').replace("'","\\'")+"'"
def liste_js(l):
    nom=l['nom_complet'] if 'nom_complet' in l else l['nom']
    pages=l.get('pages',True)
    items=','.join('['+q(o['objet'])+(','+str(o['page']) if pages else ',0')+']' for o in l['objets'])
    kinds=(',kinds:['+','.join(q(k) for k in l['filtres'])+']') if l.get('filtres') else ''   # types d'objets fournis (boutons de filtre du ciel profond) ; absent : galaxies, amas, nébuleuses
    return "    {id:%s,name:%s,long:%s,pages:%s%s,items:[%s]}"%(q(l['id']),q(l['nom']),q(nom),'1' if pages else '0',kinds,items)
def charge_lune(don):
    d=os.path.join(don,'lune','listes'); out=[]
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith('.json'): out.append((f,json.load(open(os.path.join(d,f),encoding='utf-8'))))
    return out
def liste_lune_js(l):
    sub=(',sub:'+q(l['sous_titre'])) if l.get('sous_titre') else ''
    return "    {id:%s,group:%s,short:%s%s,noms:[%s]}"%(q(l['id']),q(l['groupe']),q(l['nom']),sub,','.join(q(n) for n in l['formations']))
def genere(don):
    # Les listes d'un même groupe se classent par `ordre` croissant (entier facultatif), puis par nom de fichier, puis par position dans le fichier
    nl=[];lib=[]; avis=[]; lnl=[]; llib=[]
    for f,j in charge(don):
        for k,l in enumerate(j['listes']): (lib if j.get('libre') else nl).append((l.get('ordre',1000),f,k,liste_js(l)))
        if not j.get('libre') and j.get('avis'): avis.append('/* '+'\n   '.join(j['avis'])+' */')
    for f,j in charge_lune(don):
        for k,l in enumerate(j['listes']): (llib if j.get('libre') else lnl).append((l.get('ordre',1000),f,k,liste_lune_js(l)))
        if not j.get('libre') and j.get('avis'): avis.append('/* '+'\n   '.join(j['avis'])+' */')
    tri=lambda L:[x[3] for x in sorted(L,key=lambda x:x[:3])]
    arr=lambda nom,L: 'window.'+nom+'=['+('\n'+',\n'.join(tri(L))+'\n  ' if L else '')+'];\n'
    t_nl=('\n'.join(avis)+'\n' if avis else '')+arr('BOOK_LISTS_DATA',nl)+(arr('LUN_LISTS_DATA',lnl) if lnl else '')
    t_lib=arr('LISTS_LIBRES',lib)+(arr('LUN_LISTS_LIBRES',llib) if llib else '')
    return t_nl,t_lib
def migre(page,don):
    s=open(page,encoding='utf-8').read(); i=s.index('<script id="listes-saisonnieres">')+len('<script id="listes-saisonnieres">'); j=s.index('</script>',i); blk=s[i:j]
    com=re.search(r'/\*(.*?)\*/',blk,re.S).group(1).strip('\n'); avis=[l.strip() if n else l.strip() for n,l in enumerate(com.split('\n'))]
    js="process.stdout.write(JSON.stringify((function(){var window={};"+blk+";return window.BOOK_LISTS_DATA})()))"
    data=json.loads(subprocess.run(['node','-e',js],capture_output=True,text=True,check=True).stdout)
    fix={'sp':'Printemps','se':'Été','sa':'Automne','sh':'Hiver'}
    listes=[{'id':l['id'],'nom':l['name'],'nom_complet':l['name']+' (Le Ciel au télescope)','pages':True,'objets':[{'objet':o,'page':p} for o,p in l['items']]} for l in data]
    out={'schema':'listes-v1','description':"Listes d'objets du ciel profond à cocher dans Paramètres : un fichier = un ensemble de listes de même origine. Chaque objet est cité par sa désignation (celle des catalogues : messier.json, classiques.json, doubles.json) ; `page` = numéro de page dans la source (0 ou absent si la liste n'en a pas ; `pages:false` pour une liste sans pages).",
         'ensemble':{'id':'ciel-au-telescope','titre':"Le Ciel au télescope – 110 observations essentielles à faire avec votre instrument",'auteurs':"Carine Souplet et Bertrand d'Armagnac",'editeur':'éditions Stelvision','annee':2021,'isbn':'978-2-9563417-4-1','url':'https://www.stelvision.com/astro/boutique/le-ciel-au-telescope/'},
         'libre':False,'licence':"© éditions Stelvision et ses auteurs ; reprise des noms d'objets et des numéros de page avec leur accord écrit du 29 octobre 2026 ; hors licence GPL v3",'avis':avis,'listes':listes}
    json.dump(out,open(os.path.join(don,'ciel-profond','listes','ciel-au-telescope.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(len(listes),'listes,',sum(len(l['objets']) for l in listes),'objets ;',len(avis),"lignes d'avis")
if __name__=='__main__':
    if sys.argv[1]=='migre': migre(sys.argv[2],sys.argv[3])
