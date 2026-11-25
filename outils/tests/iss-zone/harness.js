// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Thibaud Monteiro
// Charge, depuis le modèle de page, le calcul direct des transits de l'ISS (issScan…) et le calcul inverse sur une zone (iszGen…), avec les mêmes bibliothèques que la page.
// Usage : cd outils/tests/iss-zone ; npm install satellite.js@5.0.0 astronomy-engine@2.1.19 ; MODELE=../../../src/modele-page.html node calcul_inverse.js 30 30
const fs=require('fs');
global.satellite=require('satellite.js'); const Astronomy=require('astronomy-engine'); global.Astronomy=Astronomy;
const t=fs.readFileSync(process.env.MODELE||'../../../src/modele-page.html','utf8');
const cut=(a,b)=>{ const i=t.indexOf(a), j=t.indexOf(b,i); if(i<0||j<0) throw new Error('repère introuvable : '+a); return t.slice(i,j) };
const direct=cut('  function issParse(text){','  const fmtS=d=>').replace('const issRD=Math.PI/180;','');
const inverse=cut("  // ---------- Transits de l'ISS sur une zone (calcul inverse) ----------",'  // ----- interface : formulaire');
const code='const issRD=Math.PI/180;'+direct+inverse+'\nreturn {issParse,issScan,issAzEl,issBody,issSep,iszGen,iszState,iszBodyKnots,iszGeo2Ecef,iszEcef2Geo,iszEnu,ISZ};';
module.exports=new Function('satellite','Astronomy',code)(satellite,Astronomy);
