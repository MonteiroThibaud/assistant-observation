// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
// Calcul de l'application (code de la page) avec un TLE réel : transits dont le couloir traverse une zone autour de Roanne
const M=require('../harness.js'); const A=Astronomy;
const fs=require('fs'); const tle=fs.readFileSync('./tle_reel_2026-11-09.txt','utf8').trim();
const sat=M.issParse(tle); console.log('TLE époque',new Date(sat.epoch).toISOString());
const ALT=+process.env.ALT||400, C={lat:46.0345,lon:4.072,alt:ALT}, R=+process.argv[3]||40, t0=sat.epoch, days=+process.argv[2]||60, t1=t0+days*864e5;
const out=[]; const ta=Date.now();
for(const name of ['Moon','Sun']){ const g=M.iszGen(A,sat,C,R,t0,t1,name,out); let r; while(!(r=g.next()).done); }
out.sort((a,b)=>a.t-b.t);
console.log('calcul inverse :',((Date.now()-ta)/1000).toFixed(1),'s ;',out.length,'transits dans la zone de',R,'km sur',days,'jours');
out.forEach((e,i)=>console.log((i+1)+'.',e.body,new Date(e.t).toISOString().replace('T',' ').slice(0,19),'UTC | écart au centre',e.d.toFixed(1),'km cap',Math.round(e.bearing)+'° | largeur',(2*e.w).toFixed(1),'km | durée',(e.dur!==undefined?e.dur.toFixed(2):'?'),'s | élévation',e.el!==undefined?e.el.toFixed(1):'?'));
fs.writeFileSync('/tmp/isz_events_reel.json',JSON.stringify(out));
