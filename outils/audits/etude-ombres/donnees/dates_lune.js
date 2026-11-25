// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
const A=require('/tmp/aebench/package/astronomy.browser.min.js');
const out={phases:[],libr:[]};
let t=new A.MakeTime(new Date('2026-11-20T21:00:00Z'));
for(const deg of [0,45,90,135,180,225,270,315]){ const r=A.SearchMoonPhase(deg,t.date,40); out.phases.push({deg,date:r.date.toISOString()}) }
// extrêmes de libration entre le 20 nov. 2026 et le 1er déc. 2027, phase éclairée entre 70° et 290° (face bien éclairée)
let best={latN:null,latS:null,lonE:null,lonW:null};
for(let h=0;h<24*376;h+=3){ const d=new Date(Date.UTC(2026,10,20,21)+h*3600e3); const ph=A.MoonPhase(d); if(ph<70||ph>290) continue; const L=A.Libration(d);
  if(!best.latN||L.elat>best.latN.v) best.latN={v:L.elat,d}; if(!best.latS||L.elat<best.latS.v) best.latS={v:L.elat,d};
  if(!best.lonE||L.elon>best.lonE.v) best.lonE={v:L.elon,d}; if(!best.lonW||L.elon<best.lonW.v) best.lonW={v:L.elon,d} }
for(const k of Object.keys(best)) out.libr.push({nom:k,valeur:Math.round(best[k].v*100)/100,date:best[k].d.toISOString(),phase:Math.round(A.MoonPhase(best[k].d))});
console.log(JSON.stringify(out));
