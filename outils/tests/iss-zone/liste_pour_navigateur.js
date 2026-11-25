// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
const M=require('./harness.js'); const A=Astronomy;
const tle='ISS (ZARYA)\n1 25544U 98067A   26309.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537';
const sat=M.issParse(tle), C={lat:46.0345,lon:4.072}, R=+process.argv[3], t0=Date.UTC(2026,10,6,21,0,0), t1=t0+(+process.argv[2])*864e5;
const out=[]; for(const name of ['Moon','Sun']){ const g=M.iszGen(A,sat,C,R,t0,t1,name,out); let r; while(!(r=g.next()).done); }
out.sort((a,b)=>a.t-b.t); console.log(JSON.stringify(out.map(e=>[e.body,e.t])));
