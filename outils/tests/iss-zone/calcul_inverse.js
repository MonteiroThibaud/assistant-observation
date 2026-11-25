// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
const M=require('./harness.js'); const A=Astronomy;
const tle='ISS (ZARYA)\n1 25544U 98067A   26309.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537';
const sat=M.issParse(tle); console.log('TLE époque',new Date(sat.epoch).toISOString());
const ALT=+process.env.ALT||0, C={lat:46.0345,lon:4.072,alt:ALT}, R=+process.argv[3]||30, t0=sat.epoch, days=+process.argv[2]||30, t1=t0+days*864e5;
const out=[]; const t_a=Date.now();
for(const name of ['Moon','Sun']){ const g=M.iszGen(A,sat,C,R,t0,t1,name,out); let r; while(!(r=g.next()).done); }
out.sort((a,b)=>a.t-b.t); console.log('calcul inverse :',((Date.now()-t_a)/1000).toFixed(1),'s ;',out.length,'transits dans la zone de',R,'km sur',days,'jours');
out.slice(0,12).forEach((e,i)=>console.log((i+1)+'.',e.body,new Date(e.t).toISOString().replace('T',' ').slice(0,19),'UTC | d =',e.d.toFixed(1),'km cap',Math.round(e.bearing)+'° | largeur',(2*e.w).toFixed(1),'km | durée',e.dur.toFixed(2),'s | hauteur',e.el.toFixed(0)+'°','az',Math.round(e.az)+'° |',e.lat.toFixed(4),e.lon.toFixed(4),e.inside?'dans la zone':'en bordure'));
require('fs').writeFileSync('/tmp/isz_events.json',JSON.stringify(out));
