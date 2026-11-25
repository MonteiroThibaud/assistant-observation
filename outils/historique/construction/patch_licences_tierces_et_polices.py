# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import html, re
L='/home/claude/lic/'
def rd(f): return open(L+f,encoding='utf-8').read().replace('\r\n','\n').strip()
sat=open(L+'sat-LICENSE.md',encoding='utf-8').read().strip()
blocs=[
 ("Astronomy Engine 2.1.19 (Don Cross) — licence MIT — https://github.com/cosinekitty/astronomy",rd('astronomy-engine.txt')),
 ("satellite.js 5.0.0 (Shashwat Kandadai et UCSC) — licence MIT — https://github.com/shashwatak/satellite-js",sat),
 ("astronomia (Sonia Keys, Commenthol), d'après Jean Meeus — licence MIT — https://github.com/commenthol/astronomia",rd('astronomia.txt')),
 ("d3-celestial (Olaf Frohn) : données des constellations — licence BSD à 3 clauses — https://github.com/ofrohn/d3-celestial",rd('d3-celestial.txt')),
 ("Police Alegreya (Huerta Tipográfica) — SIL Open Font License 1.1 — https://github.com/huertatipografica/Alegreya",rd('alegreya-ofl.txt')),
 ("Police Alegreya Sans (Huerta Tipográfica) — SIL Open Font License 1.1 — https://github.com/huertatipografica/Alegreya-Sans",rd('alegreya-sans-ofl.txt')),
]
intro=("LICENCES DES COMPOSANTS TIERS — Assistant d'observation\n"
"=====================================================\n\n"
"Le code de l'application est sous licence GNU GPL version 3 ou ultérieure (fichier LICENSE). Les composants ci-dessous gardent leurs propres licences, reproduites ici comme elles l'exigent. "
"Les données et images (OpenNGC et AT-HYG : CC BY-SA 4.0 ; GeoNames, photos de l'auteur : CC BY 4.0 ; photo de NGC 2169 : CC0 1.0 ; IGN, Etalab : Licence Ouverte 2.0 ; DSS, NASA, ESA et autres) sont décrites dans la rubrique « Informations » de l'application et dans le fichier DONNEES-ET-LICENCES.md du dépôt.\n")
txt=intro+'\n'
for t,b in blocs: txt+='\n'+('-'*78)+'\n'+t+'\n'+('-'*78)+'\n\n'+b+'\n'
open('/home/claude/LICENCES-TIERCES.txt','w',encoding='utf-8').write(txt)
print('fichier : %.1f Ko'%(len(txt.encode())/1e3))
# --- page
p='/home/claude/work.html'; w=open(p,encoding='utf-8').read()
def rep(o,n,c=1):
    global w; assert w.count(o)==c,(o[:90],w.count(o)); w=w.replace(o,n)
# 1) polices Google retirées
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Alegreya:wght@500;700&family=Alegreya+Sans:wght@400;500;700&display=swap" rel="stylesheet">\n','')
rep("si une connexion est disponible, les polices de caractères peuvent être chargées depuis Google Fonts, et les mises à jour facultatives","les polices de caractères sont intégrées à l’application, et seules les mises à jour facultatives")
# 2) remerciements et marques, après le paragraphe sur les images DSS
o="Images obtenues avec SkyView : « We acknowledge the use of NASA’s SkyView facility (skyview.gsfc.nasa.gov) located at NASA Goddard Space Flight Center. »</p>"
n=o+"\n      <p>Remerciements : « This research has made use of the SIMBAD database, operated at CDS, Strasbourg, France. » « This research has made use of the NASA/IPAC Extragalactic Database (NED), which is funded by the National Aeronautics and Space Administration and operated by the California Institute of Technology. » « This work has made use of data from the European Space Agency (ESA) mission Gaia (https://www.cosmos.esa.int/gaia), processed by the Gaia Data Processing and Analysis Consortium (DPAC, https://www.cosmos.esa.int/web/gaia/dpac/consortium). » « This research has made use of the Washington Double Star Catalog maintained at the U.S. Naval Observatory. » Catalogues Hipparcos et Tycho : ESA, 1997 (The Hipparcos and Tycho Catalogues, ESA SP-1200) ; Høg et al., 2000 (Astronomy &amp; Astrophysics 355, L27).</p>\n      <p>Les noms de produits et de marques cités (Telrad, Tele Vue Ethos, Sky-Watcher, Android…) appartiennent à leurs propriétaires et sont employés à titre descriptif ; l’application n’est affiliée à aucun d’eux.</p>\n      <p>Les textes complets des licences des composants tiers (Astronomy Engine, satellite.js, astronomia, d3-celestial, polices Alegreya) figurent dans le menu « Licences des composants tiers » ci-dessous et dans le fichier LICENCES-TIERCES.txt fourni avec l’application installée et le dépôt.</p>"
rep(o,n)
# 3) nouveau menu d'Informations avec les textes
i=w.index('<summary>Confidentialité</summary>'); k=w.rindex('<details',0,i)
tag=re.match(r'<details[^>]*>',w[k:]).group(0); print('balise de menu :',tag)
menu=tag+'<summary>Licences des composants tiers</summary>\n      <div class="setbody"><p>Ces licences sont reproduites comme elles l’exigent. Le code de l’application est sous GNU GPL version 3 ou ultérieure.</p><pre class="lictxt">'+html.escape(txt.split('\n',8)[-1] if False else '\n'.join(txt.split('\n')[8:]),quote=False)+'</pre></div>\n    </details>\n    '
w=w[:k]+menu+w[k:]
# 4) style
rep(".carnet{margin-top:1.8rem;padding-top:1.2rem;border-top:1px solid var(--line)}",".carnet{margin-top:1.8rem;padding-top:1.2rem;border-top:1px solid var(--line)}\n.lictxt{white-space:pre-wrap;overflow-wrap:anywhere;font-family:inherit;font-size:.74rem;line-height:1.4;color:var(--muted);margin:.4rem 0 0}")
open(p,'w',encoding='utf-8').write(w); print('page : %.3f Mo'%(len(w.encode())/1e6))
