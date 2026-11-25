// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
const M=require('./harness.js'); const A=Astronomy; const rd=Math.PI/180;
const tle='ISS (ZARYA)\n1 25544U 98067A   26309.50000000 -.00002182  00000-0 -11606-4 0  2928\n2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537';
const sat=M.issParse(tle), C={lat:46.0345,lon:4.072}, inv=JSON.parse(require('fs').readFileSync('/tmp/isz_events.json','utf8'));
const kmLat=111.19, kmLon=111.19*Math.cos(C.lat*rd);
const fwd=(lat,lon,e)=>{ const o=new A.Observer(lat,lon,+process.env.ALT||0), g=M.issScan(A,sat,o,e.t-600000,e.t+600000,1.2).filter(x=>x.body===e.body); return g.length?g.reduce((a,b)=>a.sep<b.sep?a:b):null };
let n=0, bad=[], dts=[], ddur=[], inOK=0, inN=0, outOK=0, outN=0;
inv.forEach(e=>{
  const c=fwd(e.lat,e.lon,e); n++;
  if(!c||!c.transit||c.sep>0.02){ bad.push(['centre du couloir',e.body,new Date(e.t).toISOString().slice(0,19),c&&c.sep.toFixed(3)]); return }
  dts.push((c.t-e.t)/1000); ddur.push(e.dur-c.dur);
  // décalage perpendiculaire à la trajectoire (normale : (-dn, de) en est/nord)
  [-1,1].forEach(sg=>{
    [0.8,1.25].forEach(fct=>{
      const de=-e.dn*sg*e.w*fct, dn=e.de*sg*e.w*fct;                 // km vers l'est et vers le nord
      const lat=e.lat+dn/kmLat, lon=e.lon+de/(111.19*Math.cos(e.lat*rd));
      const f=fwd(lat,lon,e), tr=f&&f.transit;
      if(fct<1){ inN++; if(tr) inOK++; else bad.push(['0,8 w',e.body,new Date(e.t).toISOString().slice(0,19),f&&f.sep.toFixed(3)]) } else { outN++; if(!tr) outOK++; else bad.push(['1,25 w',e.body,new Date(e.t).toISOString().slice(0,19),f&&f.sep.toFixed(3)]) }
    });
  });
});
const st=a=>{ const m=a.reduce((x,y)=>x+y,0)/a.length, mx=Math.max.apply(null,a.map(Math.abs)); return 'moyenne '+m.toFixed(2)+', écart maximal '+mx.toFixed(2) };
console.log(n,'événements ; au centre du couloir : transit central confirmé pour',dts.length);
console.log('écart d’heure (direct − inverse) en s :',st(dts)); console.log('écart de durée (inverse − direct) en s :',st(ddur));
console.log('à 0,8 × la demi-largeur, de part et d’autre : transit confirmé',inOK,'sur',inN,'| à 1,25 × : pas de transit',outOK,'sur',outN);
console.log('cas en défaut :',bad.length,bad.slice(0,8));
