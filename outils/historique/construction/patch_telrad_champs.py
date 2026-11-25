# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
p='/home/claude/work.html'; s=open(p,encoding='utf-8').read()
def rep(o,n,c=1):
    global s; assert s.count(o)==c,(o[:110],s.count(o)); s=s.replace(o,n)
# constantes
rep("  const TELRAD_S=140/18000;","  // Telrad : champ de 10° au départ ; chaque nouvel appui sur le bouton l'élargit (20° puis 40°) avant de revenir au champ de départ ; noms d'étoiles limités en champ large\n  const TEL_Z=[1,2,4], TEL_NAMEMAG=[99,3.5,2.6], telZ=()=>Math.min(TEL_Z.length-1,Math.max(0,eyeCfg.telZ|0));\n  const TELRAD_S=140/18000;")
# champ
rep("tf=telrad?36000:finder?FC.fov*3600:eyeCfg.afov/M*3600","tf=telrad?36000*TEL_Z[telZ()]:finder?FC.fov*3600:eyeCfg.afov/M*3600")
rep("Champ : oculaire (focales et champ apparent) ou Telrad (champ de 10°, sans grossissement)","Champ : oculaire (focales et champ apparent) ou Telrad (champ de 10°, 20° ou 40°, sans grossissement)")
# noms d'étoiles
rep("if(st[3]&&st[3].length>1){labels+=","if(st[3]&&st[3].length>1&&m<=TEL_NAMEMAG[telZ()]){labels+=")
# bouton : libellé et titre
o=r"""+'<button class="ghost chip telrad" data-ep="telrad" aria-pressed="'+(eyeCfg.ep==='telrad')+'" title="Vue au Telrad (un nouvel appui recentre l’objet)">Telrad</button>';"""
n=r"""+'<button class="ghost chip telrad" data-ep="telrad" aria-pressed="'+(eyeCfg.ep==='telrad')+'" title="Vue au Telrad : champ de 10°. Un nouvel appui élargit le champ à 20° puis à 40°, puis revient à 10°.">Telrad'+(eyeCfg.ep==='telrad'&&telZ()?' · '+(10*TEL_Z[telZ()])+'°':'')+'</button>';"""
rep(o,n)
# clic
rep("""    if(eyeCfg.ep===id){eyePan={x:0,y:0,key:String(eyeSel)}; drawEye(); return}   // vue déjà active : un nouvel appui recentre l'objet""","""    if(eyeCfg.ep===id){
      // Telrad déjà actif : chaque appui élargit le champ (10° → 20° → 40°) puis revient au champ de départ, ce qui recentre l'objet
      if(id==='telrad'){ eyeCfg.telZ=(telZ()+1)%TEL_Z.length; if(!eyeCfg.telZ) eyePan={x:0,y:0,key:String(eyeSel)}; store.set('eyeCfg4',eyeCfg); buildEpChips(); drawEye(); return }
      eyePan={x:0,y:0,key:String(eyeSel)}; drawEye(); return }   // autre vue déjà active : un nouvel appui recentre l'objet""")
rep("    eyeCfg.ep=id;\n    if(ep){eyeCfg.fOc=ep.f;","    eyeCfg.ep=id; if(id==='telrad') eyeCfg.telZ=0;\n    if(ep){eyeCfg.fOc=ep.f;")
# texte de la vue
rep("un nouvel appui sur « Telrad » ramène '+o.name+' au centre des cercles, avant de passer à l\\'oculaire de plus faible grossissement.'","un nouvel appui sur « Telrad » élargit le champ (20° puis 40°) ; revenir au champ de 10° recentre '+o.name+' au centre des cercles.'")
# Informations
rep("ou le Telrad (champ de 10° avec ses cercles rouges de 0,5°, 2° et 4°, comme à l’œil nu).","ou le Telrad (champ de 10° avec ses cercles rouges de 0,5°, 2° et 4°, comme à l’œil nu ; chaque nouvel appui sur « Telrad » élargit le champ à 20° puis à 40°, et le suivant revient au champ de départ en recentrant l’objet).")
rep("et un nouvel appui sur la puce choisie le ramène au centre.","et un nouvel appui sur la puce choisie le ramène au centre (au Telrad, il élargit le champ).")
open(p,'w',encoding='utf-8').write(s); print('ok')
