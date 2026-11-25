// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
const M=require('./harness.js'); const A=Astronomy;
const tle='ISS (ZARYA)\n1 25544U 98067A   26309.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537';
const sat=M.issParse(tle), C={lat:46.0345,lon:4.072}, R=+process.argv[3]||30, t0=sat.epoch, days=+process.argv[2]||30, t1=t0+days*864e5, rd=Math.PI/180;
const inv=JSON.parse(require('fs').readFileSync('/tmp/isz_events.json','utf8'));
// grille de sites dans la zone : pas de 5 km
const step=+process.argv[4]||5, kmLat=111.19, kmLon=111.19*Math.cos(C.lat*rd), pts=[];
for(let n=-R;n<=R;n+=step) for(let e=-R;e<=R;e+=step) if(Math.hypot(e,n)<=R+0.01) pts.push({lat:C.lat+n/kmLat,lon:C.lon+e/kmLon,e,n});
console.log(pts.length,'sites de la grille (pas de',step,'km)');
const fwd=[]; const ta=Date.now();
pts.forEach((p,k)=>{ const obs=new A.Observer(p.lat,p.lon,+process.env.ALT||0); const evs=[];
  for(let t=t0;t<t1;t+=3*864e5){ M.issScan(A,sat,obs,t,Math.min(t+3*864e5,t1),1.2).forEach(x=>{ if(!evs.some(y=>y.body===x.body&&Math.abs(y.t-x.t)<5000)) evs.push(x) }) }
  evs.filter(x=>x.transit).forEach(x=>fwd.push({site:k,e:p.e,n:p.n,body:x.body,t:x.t,dur:x.dur,el:x.bodyAlt})) });
console.log('calcul direct sur la grille :',((Date.now()-ta)/1000).toFixed(0),'s ;',fwd.length,'transits site par site');
// regroupement par passage (même astre, à moins de 20 s)
const groups=[]; fwd.sort((a,b)=>a.t-b.t).forEach(x=>{ const g=groups.find(g=>g.body===x.body&&Math.abs(g.t-x.t)<20000); if(g) g.sites.push(x); else groups.push({body:x.body,t:x.t,sites:[x]}) });
console.log(groups.length,'passages distincts vus par la grille ;',inv.length,'passages trouvés par le calcul inverse');
let manq=0,bas=0,ok=0; groups.forEach(g=>{ const m=inv.find(e=>e.body===g.body&&Math.abs(e.t-g.t)<20000); const el=Math.max.apply(null,g.sites.map(x=>x.el)); if(m) ok++; else if(el<5) bas++; else { manq++; console.log(' MANQUANT à hauteur >= 5° :',g.body,new Date(g.t).toISOString().slice(0,19),'sites',g.sites.length,'hauteur',el.toFixed(1)) } });
console.log('passages de la grille retrouvés :',ok,'| non retenus car astre sous 5° :',bas,'| MANQUANTS à hauteur >= 5° :',manq);
inv.forEach(e=>{ const g=groups.find(g=>g.body===e.body&&Math.abs(e.t-g.t)<20000); if(!g) console.log(' inverse sans équivalent dans la grille :',e.body,new Date(e.t).toISOString().slice(0,19),'d=',e.d.toFixed(1),'w=',e.w.toFixed(1)) });
