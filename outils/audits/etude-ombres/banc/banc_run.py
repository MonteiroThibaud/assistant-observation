#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Banc d'identité du calcul des ombres de la Lune (étude du 16 novembre 2026).
Pour chaque cas (date, région, zoom) : rendu de référence (calcul actuel) et rendu de chaque variante avec les mêmes arguments ; comparaison point par point de l'image et de la lumière.
Usage : banc_run.py --cas cas-500.json --variantes ctl40,reg --sortie resultats-xxx.jsonl [--budget 240] [--ids c001,c002 | --date CLE | --max N] [--passe full|rest]
Reprise automatique : les cas déjà présents dans le fichier de sortie pour ces variantes sont sautés (mémoire des cas testés)."""
import sys, os, json, time, argparse, datetime
sys.path.insert(0,'/home/claude/p2/outils')
import cap_lib as C
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser(); ap.add_argument('--cas',default='/mnt/user-data/outputs/etude-ombres/cas-500.json'); ap.add_argument('--variantes',default='ref'); ap.add_argument('--sortie',required=True)
ap.add_argument('--budget',type=int,default=240); ap.add_argument('--ids'); ap.add_argument('--date'); ap.add_argument('--max',type=int,default=10**9); ap.add_argument('--passe',default='full'); ap.add_argument('--banc',default='/home/claude/ng/banc'); ap.add_argument('--port',type=int,default=9100)
a=ap.parse_args(); VARS=a.variantes.split(','); T0=time.time()
data=json.load(open(a.cas,encoding='utf-8')); cas=data['cas']
if a.ids: cas=[c for c in cas if c['id'] in a.ids.split(',')]
if a.date: cas=[c for c in cas if c['date_cle']==a.date]
cle='+'.join(VARS)+'|'+a.passe
faits=set()
if os.path.exists(a.sortie):
    for l in open(a.sortie,encoding='utf-8'):
        try: r=json.loads(l); faits.add(r['id']+'|'+r['cle'])
        except Exception: pass
cas=[c for c in cas if c['id']+'|'+cle not in faits][:a.max]
if not cas: print('rien à faire : tous les cas demandés sont déjà dans',a.sortie); sys.exit(0)
JS_INIT=r"""(()=>{
window.__zoomTo=(s,tx0,ty0)=>{ const mv=window.__mvf(), b=document.getElementById('mapBox'), W=b.clientWidth, Hb=b.clientHeight, p={x:W/2,y:Hb/2};
  if(s<=1.0001){ mv.s=1; mv.tx=0; mv.ty=0; return } const cx=(p.x-mv.tx)/mv.s, cy=(p.y-mv.ty)/mv.s; mv.s=s; mv.tx=p.x-cx*s; mv.ty=p.y-cy*s };
window.__argsFor=(passe)=>{ const st=window.__stf(), mv=window.__mvf(), W=document.getElementById('mapBox').clientWidth, S=st.S||W, N=1000, R=N/2-2, s=mv.s;
  if(s<=1.0001) return [N,N/2,R,st.F,0,0,1,st.or,false];
  const kmCss=3474.8/(S*s), dpr=Math.min(window.devicePixelRatio||1,3,Math.max(1.5,kmCss/0.33)), n=Math.round(W*dpr), sc=N/(S*dpr*s), ox=-mv.tx*N/(S*s), oy=-mv.ty*N/(S*s);
  const nR=Math.round(W*Math.min(window.devicePixelRatio||1,3));
  return passe==='rest'?[nR,N/2,R,st.F,ox,oy,N/(S*(nR/W)*s),st.or,true]:[n,N/2,R,st.F,ox,oy,sc,st.or,true] };
window.__fnv=(u8)=>{ let h=2166136261>>>0; for(let i=0;i<u8.length;i++){ h=Math.imul(h^u8[i],16777619)>>>0 } return h };
window.__run=(args,v)=>{ const n=args[0]; window.__REC={n,lit:new Float32Array(n*n),st:new Int32Array(n*n)}; window.__VAR=v; const j=window.__moonJob(...args); const t0=performance.now(); j.run(1e9); const ms=performance.now()-t0;
  const img=j.cv.getContext('2d').getImageData(0,0,n,n).data; const R=window.__REC; window.__REC=null; return {img,lit:R.lit,st:R.st,ms,n} };
window.__cmpCase=(args,vars)=>{ const A=window.__run(args,'ref'); const n=A.n; const out={n,ref_ms:Math.round(A.ms),img_hash:window.__fnv(new Uint8Array(A.img.buffer)),lit_hash:window.__fnv(new Uint8Array(A.lit.buffer)),
    pts_rayon:0,pts_disque:0,etapes_ref:0,var:{}}; for(let q=0;q<n*n;q++){ if(A.img[q*4+3]>0) out.pts_disque++; if(A.st[q]>0) out.pts_rayon++; out.etapes_ref+=A.st[q] }
  for(const v of vars){ const B=window.__run(args,v); const r={ms:Math.round(B.ms),etapes:0,nd0:0,nd1:0,nd8:0,dmax:0,moy:0,lit_diff:0,lit_dmax:0,blob_max:0,blob_nb:0};
    const mask=new Uint8Array(n*n); let somme=0;
    for(let q=0;q<n*n;q++){ r.etapes+=B.st[q]; const o=q*4; const d=Math.max(Math.abs(A.img[o]-B.img[o]),Math.abs(A.img[o+1]-B.img[o+1]),Math.abs(A.img[o+2]-B.img[o+2])); if(d>0){ r.nd0++; somme+=d; if(d>r.dmax) r.dmax=d } if(d>1){ r.nd1++; mask[q]=1 } if(d>8) r.nd8++;
      const dl=Math.abs(A.lit[q]-B.lit[q]); if(dl>0){ r.lit_diff++; if(dl>r.lit_dmax) r.lit_dmax=dl } }
    r.moy=r.nd0?somme/r.nd0:0;
    if(r.nd1){ const seen=new Uint8Array(n*n), pile=new Int32Array(n*n); for(let q=0;q<n*n;q++){ if(!mask[q]||seen[q]) continue; let sp=0, taille=0; pile[sp++]=q; seen[q]=1; while(sp){ const c=pile[--sp]; taille++; const x=c%n, y=(c/n)|0;
        if(x>0&&mask[c-1]&&!seen[c-1]){seen[c-1]=1; pile[sp++]=c-1} if(x<n-1&&mask[c+1]&&!seen[c+1]){seen[c+1]=1; pile[sp++]=c+1} if(y>0&&mask[c-n]&&!seen[c-n]){seen[c-n]=1; pile[sp++]=c-n} if(y<n-1&&mask[c+n]&&!seen[c+n]){seen[c+n]=1; pile[sp++]=c+n} }
        r.blob_nb++; if(taille>r.blob_max) r.blob_max=taille } }
    out.var[v]=r }
  return out };
})()
"""
srv=C.serve(a.banc,a.port); tz=datetime.timezone.utc; nf=0
try:
  with sync_playwright() as p:
    par_date={}
    for c in cas: par_date.setdefault(c['date'],[]).append(c)
    for date,lst in par_date.items():
        if time.time()-T0>a.budget-40: break
        dt=datetime.datetime.fromisoformat(date.replace('Z','+00:00'))
        b=p.chromium.launch(); ctx=b.new_context(viewport={'width':411,'height':850},device_scale_factor=2.625,is_mobile=True,has_touch=True,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=dt); pg.clock.set_fixed_time(dt); pg.goto('http://localhost:%d/index.html'%a.port); pg.wait_for_timeout(7500)
        pg.evaluate(JS_INIT); pg.evaluate("document.querySelector('.tabbar [data-tab=moon]').click()"); pg.wait_for_timeout(2500); pg.click('#mapNow'); pg.wait_for_timeout(2500)
        for _ in range(30):
            if pg.evaluate("(document.getElementById('fineText')||{}).textContent||''").startswith('Relief à 32'): break
            pg.wait_for_timeout(500)
        for c in lst:
            if time.time()-T0>a.budget: break
            try:
                if c['region']: pg.evaluate("(n)=>window.__go(n)",c['region']); pg.wait_for_timeout(700)
                pg.evaluate("(s)=>window.__zoomTo(s)",c['zoom'])
                args_ok=pg.evaluate("(p)=>{ const a=window.__argsFor(p); return a?true:false }",a.passe)
                keys=pg.evaluate("(p)=>{ const a=window.__argsFor(p); const HC=window.__HCf(); if(!HC.ready||!a[8]) return 0; const k=window.__hiNeeded(...a); return Promise.race([window.__hiEnsure(k).then(()=>k.length),new Promise(r=>setTimeout(()=>r(-1),12000))]) }",a.passe)
                res=pg.evaluate("([p,v])=>window.__cmpCase(window.__argsFor(p),v)",[a.passe,VARS])
                rec={'id':c['id'],'cle':cle,'date_cle':c['date_cle'],'region':c['region'],'zoom':c['zoom'],'strate':c['strate'],'passe':a.passe,'tuiles':keys,'res':res,'erreurs':errs[:1]}
                open(a.sortie,'a',encoding='utf-8').write(json.dumps(rec)+'\n'); nf+=1
            except Exception as e:
                open(a.sortie,'a',encoding='utf-8').write(json.dumps({'id':c['id'],'cle':cle+'|erreur','erreur':str(e)[:200]})+'\n')
        b.close()
finally: srv.terminate()
print('cas traités dans ce lot : %d ; durée %.0f s ; restant : %d'%(nf,time.time()-T0,len(cas)-nf))
