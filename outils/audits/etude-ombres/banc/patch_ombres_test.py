# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys
SRC='/home/claude/livrables_p/site/index.html'; DST=sys.argv[1]
s=open(SRC,encoding='utf-8').read().replace("location.protocol==='https:'&&",'')
import re
if len(sys.argv)>2 and sys.argv[2]=='base': s=re.sub(r"window\.RELIEF_FINE_URL='[^']*';","window.RELIEF_FINE_URL='';",s,count=1)
def rep(a,b):
    global s; assert s.count(a)==1,(s.count(a),a[:90]); s=s.replace(a,b)
# 1. enveloppe de moonJob : capture des arguments des passages complet et de repos
rep("  function moonJob(n,c,rr,F,ox=0,oy=0,sc=1,or=curOrient(),hi=false){","  function moonJob(...a){ const n=a[0]; if(n>=500&&n<=700) window.__argsFull=a; else if(n>=1000) window.__argsRest=a; return moonJob0(...a) }\n  function moonJob0(n,c,rr,F,ox=0,oy=0,sc=1,or=curOrient(),hi=false){")
# 2. cartes de maxima (régionale et blocs de 8 et 32 km) et tableaux de sortie
rep("    const DW=useDem?dem.w:0, DH=useDem?dem.h:0, DA=useDem?dem.data:null;\n","""    const DW=useDem?dem.w:0, DH=useDem?dem.h:0, DA=useDem?dem.data:null;
    const VAR=window.__VAR||'ref', CNT=!!window.__COUNT, LITD=window.__WANTLIT?new Float32Array(n*n).fill(-1):null, RAYD=window.__WANTLIT?new Uint8Array(n*n):null;
    if(LITD){ window.__outLit=LITD; window.__outRay=RAYD }
    if(useDem&&!dem.mx){ const __tb=performance.now();
      const bmax=BSc=>{ const bw=Math.ceil(DW/BSc), bh=Math.ceil(DH/BSc), bm=new Int16Array(bw*bh).fill(-32768);
        for(let r=0;r<DH;r++){ const br=(r/BSc|0)*bw; for(let c=0;c<DW;c++){ const v=DA[r*DW+c], k=br+(c/BSc|0); if(v>bm[k]) bm[k]=v } } return {bw,bh,bs:BSc,bm} };
      const m3=o=>{ const {bw,bh,bm}=o, out=new Int16Array(bw*bh); for(let br=0;br<bh;br++) for(let bc=0;bc<bw;bc++){ let m=-32768; for(let y=Math.max(0,br-1);y<=Math.min(bh-1,br+1);y++) for(let x=Math.max(0,bc-1);x<=Math.min(bw-1,bc+1);x++){ const v=bm[y*bw+x]; if(v>m) m=v } out[br*bw+bc]=m } o.m3=out; return o };
      const reg=(()=>{ const o=bmax(Math.max(1,Math.round(32000/DSTEP))), {bw,bh,bm,bs}=o, hm=new Int16Array(bw*bh);
        for(let br=0;br<bh;br++){ const lat=(90-(br+0.5)*bs/PPD)*Math.PI/180, R=Math.min(bw,Math.ceil(11/Math.max(0.03,Math.cos(lat))));
          for(let bc=0;bc<bw;bc++){ let m=-32768; const a=Math.max(0,bc-R), b2=Math.min(bw-1,bc+R); for(let k=a;k<=b2;k++){ const v=bm[br*bw+k]; if(v>m) m=v } hm[br*bw+bc]=m } }
        const out=new Int16Array(bw*bh);
        for(let br=0;br<bh;br++){ const a=Math.max(0,br-11), b2=Math.min(bh-1,br+11); for(let bc=0;bc<bw;bc++){ let m=-32768; for(let k=a;k<=b2;k++){ const v=hm[k*bw+bc]; if(v>m) m=v } out[br*bw+bc]=m } }
        return {bw,bh,bs,m:out} })();
      dem.mx={reg,b8:m3(bmax(Math.max(1,Math.round(8000/DSTEP)))),b32:m3(bmax(Math.max(1,Math.round(32000/DSTEP)))),b128:m3(bmax(Math.max(1,Math.round(128000/DSTEP))))};
      window.__mxBuild={ms:Math.round(performance.now()-__tb),ppd:PPD,dem:DW+'x'+DH,octets:reg.m.byteLength+dem.mx.b8.bm.byteLength+dem.mx.b8.m3.byteLength+dem.mx.b32.bm.byteLength+dem.mx.b32.m3.byteLength};
    }
""")
# 3. bloc du rayon : variantes
a=s.index("          const h0=hAt(lod,lad), tE=d/sh, ux=se/sh, uy=sn/sh;"); b=s.index("          // Affinage local",a)
new="""          const h0=hAt(lod,lad), tE=d/sh, ux=se/sh, uy=sn/sh;
          let Hb=10700;
          if(VAR!=='ref'&&VAR!=='ref2'&&VAR!=='perturb'){ const R=dem.mx.reg, rc=Math.min(R.bw-1,Math.max(0,((lod-L0)*PPD/R.bs)|0)), rr2=Math.min(R.bh-1,Math.max(0,((90-lad)*PPD/R.bs)|0)); Hb=Math.min(10700,R.m[rr2*R.bw+rc]+250) }
          const xmax=RM*(-tE+Math.sqrt(tE*tE+2*Math.max(0,Hb-h0)/RM));
          const elv=Math.asin(Math.min(1,Math.max(-1,d)))*DEG;
          const xcap=(VAR==='perturb'&&elv>40)?0:Math.min(xmax,NCAP*STEP);
          let mm=1e9, x=0, stp=STEP, xm=0, sm=STEP, skipEnd=-1;
          const cosLmin=Math.max(0.05,Math.cos((Math.abs(lad)+3)*Math.PI/180));   // latitude du point + 3° : cosinus conservateur pour toute la portée du rayon
          let nt0=0,nt1=0,nt2=0,fl0=0,fl1=0,fl2=0,lc0=-1,lc1=-1,lc2=-1,lr0=-1,lr1=-1,lr2=-1,lk0=false,lk1=false,lk2=false;
          while(x<xcap){
            if(x>RAY_NEAR&&stp<STEPMAX) stp=Math.min(stp*RAY_G,STEPMAX);
            x+=stp;
            if(x<=skipEnd) continue;
            const lo2=lod+ux*x/(RM*cB)*DEG;
            if(lo2<L0||lo2>-L0) break;
            const la2=lad+uy*x/RM*DEG;
            if(useB&&x>=XMIN&&xcap>=XCM){          // rayons assez longs seulement (XCM : portée minimale du rayon)
              let ok=false;
              if(L128&&xcap-x>=100000){
                const o=o128, bc=Math.min(o.bw-1,Math.max(0,((lo2-L0)*PPD/o.bs)|0)), br=Math.min(o.bh-1,Math.max(0,((90-la2)*PPD/o.bs)|0));
                if(MODEB?((bc!==lc0||br!==lr0||lk0)&&x>=nt0):(x>=nt0)){
                  const Lb=o.bs*DSTEP*cosLmin, M=o.m3[br*o.bw+bc], f1=h0+x*tE+x*x/(2*RM), x2=x+Lb, f2=h0+x2*tE+x2*x2/(2*RM), sv=-tE*RM; let hm=f1<f2?f1:f2; if(sv>x&&sv<x2){ const fv=h0-tE*tE*RM/2; if(fv<hm) hm=fv }
                  if(CNT) window.__TESTS++;
                  lc0=bc; lr0=br;
                  if(hm-M>=600){ skipEnd=x2; ok=true; fl0=0; lk0=true; if(CNT) window.__TOK++ }
                  else { lk0=false; fl0++; nt0=x+Lb*(EXPB?Math.min(8,Math.pow(2,fl0-1)):0.5); if(CNT) window.__TFAIL++ }
                }
              }
              if(L32&&!ok){
                const o=o32, bc=Math.min(o.bw-1,Math.max(0,((lo2-L0)*PPD/o.bs)|0)), br=Math.min(o.bh-1,Math.max(0,((90-la2)*PPD/o.bs)|0));
                if(MODEB?((bc!==lc1||br!==lr1||lk1)&&x>=nt1):(x>=nt1)){
                  const Lb=o.bs*DSTEP*cosLmin, M=o.m3[br*o.bw+bc], f1=h0+x*tE+x*x/(2*RM), x2=x+Lb, f2=h0+x2*tE+x2*x2/(2*RM), sv=-tE*RM; let hm=f1<f2?f1:f2; if(sv>x&&sv<x2){ const fv=h0-tE*tE*RM/2; if(fv<hm) hm=fv }
                  if(CNT) window.__TESTS++;
                  lc1=bc; lr1=br;
                  if(hm-M>=600){ skipEnd=x2; ok=true; fl1=0; lk1=true; if(CNT) window.__TOK++ }
                  else { lk1=false; fl1++; nt1=x+Lb*(EXPB?Math.min(8,Math.pow(2,fl1-1)):0.25); if(CNT) window.__TFAIL++ }
                }
              }
              if(L8&&!ok){
                const o=o8, bc=Math.min(o.bw-1,Math.max(0,((lo2-L0)*PPD/o.bs)|0)), br=Math.min(o.bh-1,Math.max(0,((90-la2)*PPD/o.bs)|0));
                if(MODEB?((bc!==lc2||br!==lr2||lk2)&&x>=nt2):(x>=nt2)){
                  const Lb=o.bs*DSTEP*cosLmin, M=o.m3[br*o.bw+bc], f1=h0+x*tE+x*x/(2*RM), x2=x+Lb, f2=h0+x2*tE+x2*x2/(2*RM), sv=-tE*RM; let hm=f1<f2?f1:f2; if(sv>x&&sv<x2){ const fv=h0-tE*tE*RM/2; if(fv<hm) hm=fv }
                  if(CNT) window.__TESTS++;
                  lc2=bc; lr2=br;
                  if(hm-M>=600){ skipEnd=x2; ok=true; fl2=0; lk2=true; if(CNT) window.__TOK++ }
                  else { lk2=false; fl2++; nt2=x+Lb*(EXPB?Math.min(8,Math.pow(2,fl2-1)):0.5); if(CNT) window.__TFAIL++ }
                }
              }
              if(ok) continue;
            }
            if(CNT) window.__STEPS++;
            const m=h0+x*tE+x*x/(2*RM)-hAt(lo2, la2);
            if(m<mm){mm=m; xm=x; sm=stp; if(mm<-250) break;}
          }
"""
s=s[:a]+new+s[b:]
rep("      const k=lit*Math.min(1,Math.max(0,(ci+0.02)/0.05));","      if(LITD){ LITD[j*n+i]=lit; if(useDem&&d>-0.04&&ci>-0.02) RAYD[j*n+i]=1 }\n      const k=lit*Math.min(1,Math.max(0,(ci+0.02)/0.05));")

rep("    const row=j=>{for(let i=i0;i<i1;i++){","""    // Saut de blocs (variantes du banc) : paramètres fixés une fois par rendu, état du saut dans un tableau réutilisé (aucune allocation par point)
    const PM=(window.__VARS&&window.__VARS[VAR])||null, useB=!!PM&&useDem, L128=useB&&PM.lv.includes('b128'), L32=useB&&PM.lv.includes('b32'), L8=useB&&PM.lv.includes('b8'), MODEB=useB&&PM.mode==='block', EXPB=useB&&PM.exp, XMIN=useB?PM.xmin:0, XCM=useB?(PM.xc||0):0;
    const o128=useB&&dem.mx.b128, o32=useB&&dem.mx.b32, o8=useB&&dem.mx.b8;
    const row=j=>{for(let i=i0;i<i1;i++){""")
# 4. crochets et évaluation d'un cas
kk=s.index("  $('featClose').onclick=")
H=r"""  window.__go=goMoonMap; window.__moonJob0=moonJob0;
  const BK=(lv,mode,exp,xmin)=>({lv,mode,exp,xmin,back:[0.25,0.5,0.5]});
  window.__VARS={blk1:BK(['b32'],'sample',false,0),blk2:BK(['b32','b8'],'sample',false,0),v1a:BK(['b32','b8'],'sample',false,20000),v1b:BK(['b32','b8'],'sample',false,40000),v1c:BK(['b32','b8'],'sample',false,80000),v2:BK(['b32','b8'],'block',false,0),v3:BK(['b32','b8'],'sample',true,0),v4:BK(['b128','b32','b8'],'block',true,20000),v5:BK(['b32','b8'],'block',true,0),v6:{...BK(['b32','b8'],'sample',false,0),xc:60000},v7:{...BK(['b32','b8'],'sample',false,0),xc:100000},v8:{...BK(['b32'],'sample',false,0),xc:60000}};
  window.__timeCase=(variants,reps,which)=>{
    const a0=(which==='rest'?window.__argsRest:window.__argsFull); if(!a0) return {err:'aucun passage capturé'}; const T={}; variants.forEach(v=>T[v]=[]);
    window.__WANTLIT=false; window.__COUNT=false;
    for(let r=0;r<reps+1;r++) for(const v of variants){ window.__VAR=v; const t0=performance.now(), job=moonJob0(...a0); let g=0; while(!job.run(1e7)){ if(++g>1000) break } const ms=performance.now()-t0; if(r>0) T[v].push(Math.round(ms*10)/10) }
    window.__VAR=undefined; return T };
  window.__evalCase=(variants,which,orient)=>{
    let a=(which==='rest'?window.__argsRest:window.__argsFull); if(!a) return {err:'aucun passage capturé'};
    if(orient){ a=a.slice(); while(a.length<9) a.push(undefined); if(a[4]===undefined) a[4]=0; if(a[5]===undefined) a[5]=0; if(a[6]===undefined) a[6]=1; a[7]=orient; if(a[8]===undefined) a[8]=false }
    const out={}; let ref=null;
    for(const v of variants){
      window.__VAR=v; window.__WANTLIT=true; window.__COUNT=true; window.__STEPS=0; window.__TESTS=0; window.__TOK=0; window.__TFAIL=0;
      const t0=performance.now(), job=moonJob0(...a); let g=0; while(!job.run(1e7)){ if(++g>1000) break }
      const ms=performance.now()-t0, cv=job.cv, n=cv.width, img=new Uint8ClampedArray(cv.getContext('2d').getImageData(0,0,n,n).data);
      const res={img,lit:window.__outLit,ray:window.__outRay,steps:window.__STEPS,tests:window.__TESTS,tok:window.__TOK,tfail:window.__TFAIL,ms,n};
      if(v==='ref'){ ref=res; let disk=0,ray=0; for(let q=0;q<n*n;q++){ if(img[q*4+3]>0) disk++; if(res.ray[q]) ray++ } out.ref={n,disk,ray,steps:res.steps,ms:Math.round(ms)}; continue }
      let nd=0,nB=0,mx=0,diskc=0,litd=0,litmax=0; const mask=new Uint8Array(n*n);
      for(let q=0;q<n*n;q++){ if(ref.img[q*4+3]>0) diskc++;
        const d=Math.max(Math.abs(img[q*4]-ref.img[q*4]),Math.abs(img[q*4+1]-ref.img[q*4+1]),Math.abs(img[q*4+2]-ref.img[q*4+2]));
        if(d>mx) mx=d; if(d>=2){ nd++; mask[q]=1; if(d<=8) nB++ }
        if(res.lit[q]!==ref.lit[q]){ litd++; const e=Math.abs(res.lit[q]-ref.lit[q]); if(e>litmax) litmax=e } }
      let blob=0; if(nd){ const seen=new Uint8Array(n*n); for(let q0=0;q0<n*n;q0++){ if(!mask[q0]||seen[q0]) continue; let c=0; const st=[q0]; seen[q0]=1; while(st.length){ const q=st.pop(); c++; const x=q%n, y=(q/n)|0; if(x>0&&mask[q-1]&&!seen[q-1]){seen[q-1]=1;st.push(q-1)} if(x<n-1&&mask[q+1]&&!seen[q+1]){seen[q+1]=1;st.push(q+1)} if(y>0&&mask[q-n]&&!seen[q-n]){seen[q-n]=1;st.push(q-n)} if(y<n-1&&mask[q+n]&&!seen[q+n]){seen[q+n]=1;st.push(q+n)} } if(c>blob) blob=c } }
      let ss=0,sc=0; const C1=6.5025,C2=58.5225; for(let by=0;by+8<=n;by+=8) for(let bx=0;bx+8<=n;bx+=8){ let ok=true,ma=0,mb=0,saa=0,sbb=0,sab=0; for(let y=0;y<8&&ok;y++) for(let x=0;x<8;x++){ const q=(by+y)*n+bx+x; if(!(ref.img[q*4+3]>0)){ ok=false; break } const A=0.299*ref.img[q*4]+0.587*ref.img[q*4+1]+0.114*ref.img[q*4+2], B=0.299*img[q*4]+0.587*img[q*4+1]+0.114*img[q*4+2]; ma+=A; mb+=B; saa+=A*A; sbb+=B*B; sab+=A*B } if(!ok) continue; ma/=64; mb/=64; const va=saa/64-ma*ma, vb=sbb/64-mb*mb, cv2=sab/64-ma*mb; ss+=((2*ma*mb+C1)*(2*cv2+C2))/((ma*ma+mb*mb+C1)*(va+vb+C2)); sc++ }
      const frac=nd/Math.max(1,diskc), cls=(mx<=1)?'A':((nB/Math.max(1,diskc)<=0.0005&&mx<=8&&blob<=20&&nd===nB)?'B':'C');
      out[v]={cls,maxDiff:mx,nDiff2:nd,fracDiff2:frac,blobMax:blob,litDiff:litd,litMax:litmax,ssim:sc?+(ss/sc).toFixed(6):1,steps:res.steps,tests:res.tests,tok:res.tok,tfail:res.tfail,ms:Math.round(ms),gainSteps:+(1-res.steps/Math.max(1,ref.steps)).toFixed(4)};
    }
    window.__VAR=undefined; window.__WANTLIT=false; window.__COUNT=false; return out;
  };
"""
s=s[:kk]+H+s[kk:]
open(DST,'w',encoding='utf-8').write(s); print('copie de test des ombres écrite :',DST,len(s))
