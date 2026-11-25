// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
const fs=require('fs'), vm=require('vm');
function charge(file){ const code=fs.readFileSync(file,'utf8'); const ctx={console,Math,Date,Number,Object,Array,JSON,Error,Map,Set,Symbol,isNaN,isFinite,parseFloat,parseInt,String,Boolean,TypeError,RangeError,Float64Array,Int32Array,Uint8Array,ArrayBuffer,WeakMap,Promise,RegExp,exports:{},module:{exports:{}}}; ctx.window=ctx; ctx.global=ctx; ctx.self=ctx; vm.createContext(ctx); vm.runInContext(code+'\n;globalThis.__A=(typeof Astronomy!=="undefined"?Astronomy:(module.exports&&module.exports.Equator?module.exports:null));',ctx,{filename:file}); return ctx.__A||ctx.Astronomy||ctx.window.Astronomy }
const A0=charge('package/astronomy.browser.min.js'), A1=charge(process.env.AE1||'ae-es2020.min.js');
if(!A0||!A1||!A0.Equator||!A1.Equator){ console.log('chargement impossible',!!A0,!!A1); process.exit(1) }
// générateur déterministe
let seed=123456789; const rnd=()=>{ seed=(seed*1664525+1013904223)>>>0; return seed/4294967296 };
const bodies=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto'];
const planetes=['Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune'];
const dateAlea=()=>new Date(Date.UTC(1990,0,1)+rnd()*(Date.UTC(2060,0,1)-Date.UTC(1990,0,1)));
const obsAlea=(A)=>{ const lat=(rnd()-0.5)*160, lon=(rnd()-0.5)*360, h=rnd()*3000; return [lat,lon,h] };
// comparaison profonde exacte
let maxd=0, diffs=0, total=0;
function cmp(a,b,path){
  if(typeof a==='number'||typeof b==='number'){ total++; if(a===b||(Number.isNaN(a)&&Number.isNaN(b))) return; diffs++; const d=Math.abs(a-b); if(d>maxd) maxd=d; if(diffs<=3) console.log('  différence en',path,a,b); return }
  if(a===null||b===null||typeof a!=='object'||typeof b!=='object'){ total++; if(a!==b){ diffs++; if(diffs<=3) console.log('  différence en',path,a,b) } return }
  if(a instanceof Date){ total++; if(a.getTime()!==b.getTime()){ diffs++; if(diffs<=3) console.log('  dates différentes',path) } return }
  const ka=Object.keys(a), kb=Object.keys(b); if(ka.length!==kb.length){ diffs++; console.log('  clés différentes en',path,ka.join(),kb.join()); return }
  for(const k of ka) cmp(a[k],b[k],path+'.'+k);
}
function essai(nom,n,f){ maxd=0; diffs=0; total=0; const t0=Date.now(); for(let i=0;i<n;i++){ const args=f.gen(); let r0,r1; try{ r0=f.run(A0,args) }catch(e){ r0='ERR:'+e.message } try{ r1=f.run(A1,args) }catch(e){ r1='ERR:'+e.message } cmp(r0,r1,nom) } console.log('%s : %d appels, %d valeurs comparées, %d différentes, écart maximal %s (%d ms)',nom.padEnd(26),n,total,diffs,maxd,Date.now()-t0); return diffs }
let bad=0;
const G=()=>({b:bodies[(rnd()*bodies.length)|0],t:dateAlea(),o:obsAlea()});
const mk=(A,x)=>new A.Observer(x.o[0],x.o[1],x.o[2]);
bad+=essai('Equator (date, aberr.)',3000,{gen:G,run:(A,x)=>A.Equator(x.b==='Moon'||x.b==='Sun'?x.b:x.b,x.t,mk(A,x),true,true)});
bad+=essai('Equator (J2000, sans aberr.)',2000,{gen:G,run:(A,x)=>A.Equator(x.b,x.t,mk(A,x),false,false)});
bad+=essai('Horizon',3000,{gen:()=>({t:dateAlea(),o:obsAlea(),ra:rnd()*24,dec:(rnd()-0.5)*180,r:rnd()<0.5?'normal':null}),run:(A,x)=>A.Horizon(x.t,mk(A,x),x.ra,x.dec,x.r)});
bad+=essai('GeoVector',3000,{gen:G,run:(A,x)=>A.GeoVector(x.b,x.t,true)});
bad+=essai('HelioVector',2000,{gen:G,run:(A,x)=>x.b==='Moon'?A.GeoMoon(x.t):A.HelioVector(x.b,x.t)});
bad+=essai('GeoMoon',2000,{gen:G,run:(A,x)=>A.GeoMoon(x.t)});
bad+=essai('Illumination',2000,{gen:G,run:(A,x)=>A.Illumination(x.b,x.t)});
bad+=essai('MoonPhase',3000,{gen:G,run:(A,x)=>A.MoonPhase(x.t)});
bad+=essai('Constellation',3000,{gen:()=>({ra:rnd()*24,dec:(rnd()-0.5)*180}),run:(A,x)=>A.Constellation(x.ra,x.dec)});
bad+=essai('SiderealTime',3000,{gen:G,run:(A,x)=>A.SiderealTime(x.t)});
bad+=essai('MakeTime',1000,{gen:G,run:(A,x)=>A.MakeTime(x.t)});
bad+=essai('ObserverVector',2000,{gen:()=>({t:dateAlea(),o:obsAlea(),e:rnd()<0.5}),run:(A,x)=>A.ObserverVector(x.t,mk(A,x),x.e)});
bad+=essai('RotationAxis',1500,{gen:()=>({b:planetes[(rnd()*planetes.length)|0],t:dateAlea()}),run:(A,x)=>A.RotationAxis(x.b,x.t)});
bad+=essai('Rotation_EQJ_EQD',1500,{gen:G,run:(A,x)=>A.Rotation_EQJ_EQD(x.t)});
bad+=essai('RotateVector',1500,{gen:()=>({t:dateAlea(),v:[rnd(),rnd(),rnd()]}),run:(A,x)=>{ const r=A.Rotation_EQJ_EQD(x.t); const v=new A.Vector(x.v[0],x.v[1],x.v[2],A.MakeTime(x.t)); return A.RotateVector(r,v) }});
bad+=essai('JupiterMoons',1500,{gen:G,run:(A,x)=>A.JupiterMoons(x.t)});
bad+=essai('SearchRiseSet',500,{gen:()=>({b:bodies[(rnd()*8)|0],t:dateAlea(),o:obsAlea(),d:rnd()<0.5?1:-1}),run:(A,x)=>A.SearchRiseSet(x.b,mk(A,x),x.d,x.t,1)});
bad+=essai('SearchHourAngle',400,{gen:G,run:(A,x)=>A.SearchHourAngle(x.b==='Pluto'?'Mars':x.b,mk(A,x),0,x.t)});
bad+=essai('SearchMaxElongation',200,{gen:()=>({b:rnd()<0.5?'Mercury':'Venus',t:dateAlea()}),run:(A,x)=>A.SearchMaxElongation(x.b,x.t)});
bad+=essai('SearchMoonQuarter',300,{gen:G,run:(A,x)=>A.SearchMoonQuarter(x.t)});
bad+=essai('PairLongitude',500,{gen:()=>({a:planetes[(rnd()*5)|0],lon:rnd()*360,t:dateAlea()}),run:(A,x)=>A.SearchRelativeLongitude?A.SearchRelativeLongitude(x.a,x.lon,x.t):A.PairLongitude(x.a,'Sun',x.lon)});
console.log(bad===0?'\nRÉSULTAT : toutes les valeurs sont strictement identiques (écart 0).':'\nRÉSULTAT : %d fonction(s) avec des différences.'.replace('%d',bad));
// vitesse : charge du démarrage
function work(A){ const obs=new A.Observer(46.0345,4.072,0); const t0=new Date('2026-11-15T16:00:00Z'); let s=0; for(let rep=0;rep<3;rep++) for(const b of bodies.slice(0,9)){ for(let i=0;i<=96;i++){ const t=new Date(t0.getTime()+i*900000); const e=A.Equator(b,t,obs,true,true); s+=A.Horizon(t,obs,e.ra,e.dec,'normal').altitude } } return s }
for(const [nom,A] of [['actuelle',A0],['boucles natives',A1]]){ work(A); let best=1e9; for(let k=0;k<7;k++){ const s=process.hrtime.bigint(); work(A); best=Math.min(best,Number(process.hrtime.bigint()-s)/1e6) } console.log('durée de la charge du démarrage (8 balayages de 97 instants ×3) :',nom,best.toFixed(1),'ms') }
