# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Construction unique des livrables à partir du dépôt : python3 construire.py RACINE_DEPOT SORTIE_DIR [--zip]
# RACINE_DEPOT contient donnees/, donnees-hors-gpl/ (images DSS et listes de Stelvision, hors licence GPL), src/modele-page.html, site-statique/ et outils/construction/.
# 1) sommes de contrôle de donnees/  2) contrôle des données (schémas, doublons, références)  3) page web  4) site installé  5) (--zip) archive du site installé
import sys, os, subprocess, shutil, zipfile, json
racine,sortie=sys.argv[1:3]; zip_=('--zip' in sys.argv)
C=os.path.join(racine,'outils','construction'); don=os.path.join(racine,'donnees'); modele=os.path.join(racine,'src','modele-page.html'); stat=os.path.join(racine,'site-statique')
def run(*a): 
    r=subprocess.run([sys.executable]+list(a),capture_output=True,text=True); print(r.stdout.strip()[-600:]); 
    if r.returncode: print(r.stderr[-800:]); sys.exit('ÉCHEC : '+' '.join(os.path.basename(x) for x in a[:1]))
os.makedirs(sortie,exist_ok=True)
hg=os.path.join(racine,'donnees-hors-gpl')
print('1. sommes de contrôle'); run(os.path.join(C,'verifie_sommes.py'),don); run(os.path.join(C,'verifie_sommes.py'),hg)
print('2. contrôle des données'); run(os.path.join(C,'controle_donnees.py'),don)
print('3. page web'); web=os.path.join(sortie,'levers-planetes.html'); run(os.path.join(C,'assemble_page_web.py'),don,modele,web)
t=os.path.getsize(web); print('   %.3f Mo (limite 16 Mo : marge %.2f Mo)'%(t/1e6,(16e6-t)/1e6)); assert t<16e6,'page web trop grande'
print('4. site installé'); site=os.path.join(sortie,'site'); run(os.path.join(C,'assemble_site_installe.py'),don,modele,stat,site)
if zip_:
    zp=os.path.join(sortie,'assistant-observation-site.zip')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for r,_,fs in os.walk(site):
            for f in sorted(fs): z.write(os.path.join(r,f),os.path.relpath(os.path.join(r,f),site))
    print('5. archive : %.1f Mo'%(os.path.getsize(zp)/1e6))
print('TERMINÉ')
