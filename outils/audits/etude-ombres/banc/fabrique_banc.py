#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Fabrique la copie de test « banc » à partir d'un site construit : crochets de pilotage, enregistrement par point de la lumière (lit) et du nombre de relevés,
interrupteur de variante du lancer de rayon (window.__VAR : ref, ctl40, puis reg, blk1, blk2). Usage : fabrique_banc.py SITE_CONSTRUIT SORTIE"""
import sys, os
src, dst = sys.argv[1], sys.argv[2]
s = open(os.path.join(src,'index.html'),encoding='utf-8').read().replace("location.protocol==='https:'&&",'')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:90]); s=s.replace(a,b)
k = s.index("  $('featClose').onclick=")
s = s[:k]+"  window.__go=goMoonMap; window.__mvf=()=>mv; window.__applyf=()=>applyMap(); window.__moonJob=moonJob; window.__moonGeom=moonGeom; window.__hiEnsure=hiEnsure; window.__hiNeeded=hiNeeded; window.__curOrient=curOrient; window.__stf=()=>({F:mapF,or:mapOr,S:mapS}); window.__HCf=()=>HC;\n"+s[k:]
# enregistrement des passes (arguments de moonJob) lancées par l'application
rep("  function moonPaintAsync(slot,args,done){\n","  function moonPaintAsync(slot,args,done){\n    (window.__passes=window.__passes||[]).push({slot,args}); if(window.__passes.length>40) window.__passes.shift();\n")
# enregistrement par point et variantes
rep("    const row=j=>{for(let i=i0;i<i1;i++){\n","    const REC=(window.__REC&&window.__REC.n===n)?window.__REC:null, VAR=window.__VAR||'ref';\n    const row=j=>{for(let i=i0;i<i1;i++){\n")
rep("      let ci=d, lit=1;\n","      let ci=d, lit=1, stepsN=0;\n")
rep("          const xcap=Math.min(xmax,NCAP*STEP);       // portée de l'ombre (environ 300 km au plus)","          let xcap=Math.min(xmax,NCAP*STEP);       // portée de l'ombre (environ 300 km au plus)\n          if(VAR==='ctl40'&&Math.asin(Math.min(1,Math.max(-1,d)))*DEG>40) xcap=0;      // contrôle négatif du banc : rayon supprimé au-dessus de 40° de hauteur du Soleil")
rep("            x+=stp;\n            const lo2=lod+ux*x/(RM*cB)*DEG;","            x+=stp; stepsN++;\n            const lo2=lod+ux*x/(RM*cB)*DEG;")
rep("      const k=lit*Math.min(1,Math.max(0,(ci+0.02)/0.05));\n","      if(REC){ REC.lit[j*n+i]=lit; REC.st[j*n+i]=stepsN }\n      const k=lit*Math.min(1,Math.max(0,(ci+0.02)/0.05));\n")
os.makedirs(dst,exist_ok=True)
for n in os.listdir(src):
    if n!='index.html':
        p=os.path.join(dst,n)
        if not os.path.lexists(p): os.symlink(os.path.realpath(os.path.join(src,n)),p)
open(os.path.join(dst,'index.html'),'w',encoding='utf-8').write(s); print('banc prêt :',dst)
