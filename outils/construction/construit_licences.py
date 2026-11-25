# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Étape 1 : génère LICENCES-TIERCES.txt et le bloc « Licences des composants tiers » d'Informations depuis donnees/licences-tierces/.
# Usage : python3 construit_licences.py DONNEES_DIR SORTIE_TXT [PAGE.html]   (avec PAGE : vérifie que le bloc de la page est identique)
import sys, json, re, html, os
def charge(d):
    c=json.load(open(os.path.join(d,'licences-tierces','composants.json'),encoding='utf-8'))
    for x in c['composants']: x['texte']=open(os.path.join(d,'licences-tierces',x['fichier']),encoding='utf-8').read().strip()
    return c
def fichier_txt(c):
    t="LICENCES DES COMPOSANTS TIERS — Assistant d'observation\n=====================================================\n\n"+c['intro']+"\n\n"
    for x in c['composants']: t+='\n'+('-'*78)+'\n'+x['titre']+'\n'+('-'*78)+'\n\n'+x['texte']+'\n'
    return t
def bloc_page(c):
    out=[]
    for x in c['composants']:
        out.append(x['titre'])
        for para in re.split(r'\n\s*\n',x['texte']): out.append(re.sub(r'\s*\n\s*',' ',para.strip()))
        out.append(''); out.append('· · ·'); out.append('')
    body='\n\n'.join(y for y in out if y!='')
    return html.escape(body[:-len('· · ·')].strip()+'\n',quote=False)
if __name__=='__main__':
    c=charge(sys.argv[1]); t=fichier_txt(c); open(sys.argv[2],'w',encoding='utf-8').write(t); print('fichier :',len(t.encode()),'octets')
    if len(sys.argv)>3:
        p=open(sys.argv[3],encoding='utf-8').read(); i=p.index('<pre class="lictxt">')+len('<pre class="lictxt">'); j=p.index('</pre>',i)
        print('bloc de la page : IDENTIQUE' if p[i:j]==bloc_page(c) else 'bloc de la page : DIFFÉRENT')
