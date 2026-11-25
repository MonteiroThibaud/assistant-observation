// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
const M=require('./harness.js'); const A=Astronomy; const rd=Math.PI/180;
const tle='ISS (ZARYA)\n1 25544U 98067A   26309.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537';
const sat=M.issParse(tle), C={lat:46.0345,lon:4.072};
const inv=JSON.parse(require('fs').readFileSync('/tmp/isz_events.json','utf8'));
const t=Date.UTC(2027,2,4,16,36,50);
const obs=new A.Observer(C.lat,C.lon,0);
const f=M.issScan(A,sat,obs,t-600000,t+600000,1.2); console.log('direct au centre :',f.map(x=>({body:x.body,t:new Date(x.t).toISOString().slice(11,19),sep:x.sep.toFixed(3),R:x.R.toFixed(3),transit:x.transit,dur:x.dur.toFixed(2),offsetKm:x.offsetKm.toFixed(1),el:x.bodyAlt.toFixed(1)})));
const e=inv.find(x=>Math.abs(x.t-t)<20000); console.log('inverse :',e&&{d:e.d,bearing:e.bearing,w:e.w,lat:e.lat,lon:e.lon,az:e.az,el:e.el});
// au point P de l'événement inverse
if(e){ const o2=new A.Observer(e.lat,e.lon,0); const g=M.issScan(A,sat,o2,e.t-600000,e.t+600000,1.2); console.log('direct au point P :',g.map(x=>({body:x.body,t:new Date(x.t).toISOString().slice(11,19),sep:x.sep.toFixed(3),R:x.R.toFixed(3),transit:x.transit,dur:x.dur.toFixed(2),el:x.bodyAlt.toFixed(1)}))); }
