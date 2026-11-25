# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
p='/home/claude/work.html'; s=open(p,encoding='utf-8').read()
def rep(o,n,c=1):
    global s; assert s.count(o)==c,(o[:100],s.count(o)); s=s.replace(o,n)
# ---------- 1) menu « Transits de l'ISS » dans Paramètres (avant « Paramètres écran »)
HTML='''  <details class="setdet" id="issSitesBox">
    <summary>Transits de l'ISS</summary>
    <div class="setbody">
      <p class="eyehint">L'application calcule les prochains transits de l'ISS devant la Lune et devant le Soleil pour chacun de tes sites (six au plus). Les résultats s'affichent dans l'onglet « Système solaire ».</p>
      <p id="issSitesTle" class="eyehint issinfo"></p>
      <h3 class="subset">Mes sites <span id="issSitesCount" class="eyehint"></span></h3>
      <ul id="issSitesList" class="sitelist"></ul>
      <h3 class="subset">Ajouter un site</h3>
      <p class="sitesub">Par commune ou lieu</p>
      <label class="sitefld">Nom de la commune ou du lieu
        <input id="issSiteQ" type="text" autocomplete="off" spellcheck="false" placeholder="Par exemple : Charlieu">
      </label>
      <ul id="issSiteSug" class="sitesug"></ul>
      <p id="issSiteQHint" class="eyehint issinfo"></p>
      <p class="sitesub">Par coordonnées GPS</p>
      <label class="sitefld">Nom du site <input id="issSiteName" type="text" autocomplete="off" placeholder="Par exemple : Terrain du club"></label>
      <div class="siterow2">
        <label class="sitefld">Latitude (° N) <input id="issSiteLat" inputmode="decimal" autocomplete="off" placeholder="46,0345"></label>
        <label class="sitefld">Longitude (° E) <input id="issSiteLon" inputmode="decimal" autocomplete="off" placeholder="4,0720"></label>
      </div>
      <div class="sbbtns"><button id="issSitePos" class="ghost" type="button">Ma position</button><button id="issSiteAdd" class="ghost" type="button">Ajouter le site</button></div>
      <p id="issSiteMsg" class="eyehint" role="status"></p>
      <div class="sbbtns"><button id="issSitesForget" class="ghost" type="button">Oublier tous les sites</button></div>
    </div>
  </details>
'''
marker='  <details class="setdet" id="scrBox">'
rep(marker,HTML+marker)
# ---------- 2) styles
CSS='''
/* Transits de l'ISS : sites (Paramètres) et tableau (Système solaire) */
.sitelist{list-style:none;margin:.2rem 0 .4rem;padding:0}
.siterow{display:grid;grid-template-columns:2.75rem 1fr 2.75rem;align-items:center;min-height:3.75rem;border-top:1px solid var(--line)}
.sitechk{display:flex;align-items:center;justify-content:center;min-height:2.75rem}
.sitechk input{width:1.4rem;height:1.4rem;accent-color:var(--accent)}
.sitetxt{display:flex;flex-direction:column;padding:.3rem 0;min-width:0}
.sitetxt b{font-size:1rem;overflow-wrap:anywhere}.sitetxt span{font-size:.86rem;color:var(--muted)}.sitetxt em{font-style:normal;font-size:.78rem;color:var(--accent)}
.iconbtn{min-width:2.75rem;min-height:2.75rem;padding:0;font-size:1.3rem;line-height:1;display:inline-flex;align-items:center;justify-content:center}
.siteempty{padding:.6rem 0;color:var(--muted);font-size:.9rem;border-top:1px solid var(--line)}
.sitesub{margin:.8rem 0 .3rem;font-weight:700;color:var(--accent);font-size:.95rem}
.sitefld{display:flex;flex-direction:column;gap:.25rem;flex:1;min-width:0;font-size:.84rem;color:var(--muted);margin-bottom:.5rem}
.sitefld input{min-height:2.75rem;box-sizing:border-box;width:100%;padding:0 .75rem;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:.6rem;font:inherit;font-size:1rem}
.sitefld input:disabled{opacity:.55}
.siterow2{display:flex;gap:.6rem}
.sitesug{list-style:none;margin:0 0 .4rem;padding:0;border:1px solid var(--line);border-radius:.6rem;overflow:hidden}
.sitesug:empty{display:none}
.sitesug li+li{border-top:1px solid var(--line)}
.sitesug button{display:flex;flex-direction:column;align-items:flex-start;width:100%;min-height:3rem;padding:.35rem .75rem;border:0;background:transparent;color:var(--ink);text-align:left;font:inherit}
.sitesug b{font-size:1rem}.sitesug span{font-size:.8rem;color:var(--muted)}
.issinfo{padding:.5rem .7rem;border:1px solid var(--line);border-radius:.6rem;background:var(--bg)}
.isswrap{container-type:inline-size;margin-top:.3rem}
.issc{margin:.5rem 0;border:1px solid var(--line);border-radius:.7rem;overflow:hidden;background:var(--surface)}
.isshead{display:flex;align-items:center;justify-content:space-between;gap:.5rem;padding:.5rem .7rem}
.isshead b{font-family:var(--serif);font-size:1.1rem;overflow-wrap:anywhere}.isshead span{display:block;font-size:.78rem;color:var(--muted)}
.issr{display:grid;grid-template-columns:4.6rem 1fr 4.4rem 2.9rem 2.2rem;align-items:center;gap:.2rem;min-height:2.3rem;padding:0 .7rem;border-top:1px solid var(--line);font-size:.86rem}
.issr.issh{min-height:1.7rem;font-size:.74rem;color:var(--muted);border-top:0}
.issr .issa{font-weight:700}.issr .issa.Sun{color:var(--accent)}
.issr .isst{font-variant-numeric:tabular-nums}.issr .isso{color:var(--muted)}.issr .issh2{color:var(--muted);text-align:right}
.issr.none{color:var(--muted)}
.issx{display:none;margin:.5rem 0;border:1px solid var(--line);border-radius:.7rem;overflow:hidden;background:var(--surface)}
.issxr{display:grid;grid-template-columns:11rem repeat(4,1fr);border-top:1px solid var(--line)}
.issxr.issxh{border-top:0;background:var(--card,#1b2547);font-size:.8rem;color:var(--muted);font-weight:700}
.issxr>*{padding:.5rem .7rem;border-left:1px solid var(--line)}.issxr>:first-child{border-left:0}
.issxc{display:flex;flex-direction:column}.issxc b{font-size:.92rem}.issxc i{font-style:normal;font-family:var(--serif);font-weight:700;font-size:1.15rem;font-variant-numeric:tabular-nums}.issxc small{font-size:.78rem;color:var(--muted)}
.issxc.Sun i{color:var(--accent)}
@container (min-width:640px){.issc{display:none}.issx{display:block}}
'''
o=".carnet{margin-top:1.8rem;padding-top:1.2rem;border-top:1px solid var(--line)}"
rep(o,o+CSS)
# ---------- 3) JavaScript : sites, calcul, tableau, calendrier
JS=r'''  // ---------- Transits de l'ISS pour plusieurs sites (Paramètres › Transits de l'ISS ; tableau dans Système solaire) ----------
  // Les sites (nom, latitude, longitude) restent sur l'appareil. Pour chaque site coché, le calcul est celui du lieu de l'utilisateur (issScan sur 400 jours), un site après l'autre, par tranches de trois jours.
  const ISS_MAX_SITES=6;
  let issSites=(store.get('issSites')||[]).filter(x=>x&&x.id&&isFinite(x.lat)&&isFinite(x.lon)).slice(0,ISS_MAX_SITES);
  const issSiteRes={}; let issSitesBusy=false, issSitesProg='', issSugs=[], issSugT=0, issForgetT=0;
  const issSitesSave=()=>store.set('issSites',issSites);
  const issKindTxt=k=>k==='pos'?'Position du téléphone':k==='commune'?'Centre de la commune : à affiner':k==='lieu'?'Lieu habité le plus proche : à affiner':'Coordonnées saisies';
  const issLatLon=(la,lo)=>num(Math.abs(la),4)+'° '+(la>=0?'N':'S')+' · '+num(Math.abs(lo),4)+'° '+(lo>=0?'E':'O');
  const issSiteKey=x=>(issTle?issTle.l1+issTle.l2:'')+'|'+x.lat.toFixed(3)+'|'+x.lon.toFixed(3)+'|'+new Date().toISOString().slice(0,10);
  const issSitePick=(x,b)=>{ const r=issSiteRes[x.id]; return r&&r.key===issSiteKey(x)?r.events.filter(e=>e.body===b&&e.transit&&e.t>Date.now()).sort((a,c)=>a.t-c.t).slice(0,2):null };
  const issDay=ms=>{ const d=new Date(ms); return d.toLocaleDateString('fr-FR',{weekday:'short',day:'numeric',month:'short'})+(d.getFullYear()!==new Date().getFullYear()?' '+d.getFullYear():'') };
  function issSitesEnsure(){
    if(!issTle||typeof satellite==='undefined'||issSitesBusy) return;
    const act=issSites.filter(x=>x.on!==false), todo=act.filter(x=>!(issSiteRes[x.id]&&issSiteRes[x.id].key===issSiteKey(x)));
    if(!todo.length){ issSitesProg=''; return }
    const x=todo[0], key=issSiteKey(x), n=act.length, k=n-todo.length+1;
    issSitesBusy=true;
    const obs=new Astronomy.Observer(x.lat,x.lon,0), sat=issTle, t0=Date.now(), t1=t0+400*864e5, seg=3*864e5, all=[]; let t=t0;
    const step=()=>{
      if(!issSites.some(y=>y.id===x.id&&y.on!==false)||issSiteKey(x)!==key){ issSitesBusy=false; issSitesEnsure(); return }   // site retiré, décoché ou TLE changé en cours de calcul
      const e=Math.min(t+seg,t1);
      try{ issScan(Astronomy,sat,obs,t,e,1.2).forEach(v=>{ if(!all.some(y=>y.body===v.body&&Math.abs(y.t-v.t)<5000)) all.push(v) }) }catch(err){}
      t=e; issSitesProg='Calcul en cours : site '+k+' sur '+n+' ('+Math.round((t-t0)/(t1-t0)*100)+' %)…';
      const pe=$('issSitesProg'); if(pe) pe.textContent=issSitesProg;
      if(t<t1) setTimeout(step,0);
      else { issSiteRes[x.id]={key,events:all.sort((a,b)=>a.t-b.t)}; issSitesBusy=false; issSitesRefresh(); issSitesEnsure() }
    };
    setTimeout(step,200);
  }
  function issSitesInner(){
    const link='<span class="eyelink" data-go="issSites">Paramètres ›</span>', act=issSites.filter(x=>x.on!==false);
    if(!issSites.length) return '<p class="nightq">Ajoute des sites dans '+link+' pour voir ici leurs prochains transits de l\'ISS devant la Lune et le Soleil.</p>';
    if(!act.length) return '<p class="nightq">Aucun site coché dans '+link+'.</p>';
    if(!issTle) return '<p class="nightq">Colle d\'abord les éléments orbitaux de l\'ISS dans '+link+'.</p>';
    const star=e=>(e.t-issTle.epoch)/864e5>3?'*':'';
    const cal='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>';
    const row=(b,e)=>e?'<div class="issr"><span class="issa '+b+'">'+(b==='Sun'?'Soleil':'Lune')+'</span><span>'+issDay(e.t)+star(e)+'</span><span class="isst">'+fmtS(e.t)+'</span><span class="isso">'+num(e.dur,1)+' s</span><span class="isso issh2">'+Math.round(e.bodyAlt)+'°</span></div>'
      :'<div class="issr none"><span class="issa '+b+'">'+(b==='Sun'?'Soleil':'Lune')+'</span><span>Aucun transit dans les 400 prochains jours</span></div>';
    const cell=(b,e)=>e?'<span class="issxc '+b+'"><b>'+issDay(e.t)+star(e)+'</b><i>'+fmtS(e.t)+'</i><small>durée '+num(e.dur,1)+' s · hauteur '+Math.round(e.bodyAlt)+'°</small></span>':'<span class="issxc none"><small>Aucun transit dans les 400 prochains jours</small></span>';
    let cards='', cross='<div class="issx"><div class="issxr issxh"><span>Site</span><span>Lune · 1er</span><span>Lune · 2e</span><span>Soleil · 1er</span><span>Soleil · 2e</span></div>', wait=false;
    act.forEach(x=>{
      const M=issSitePick(x,'Moon'), S=issSitePick(x,'Sun');
      const head='<b>'+esc(x.name)+'</b><span>'+issKindTxt(x.kind)+'</span>';
      if(!M||!S){ wait=true; cards+='<div class="issc"><div class="isshead"><div>'+head+'</div></div><div class="issr none"><span>Calcul en attente…</span></div></div>'; cross+='<div class="issxr"><div class="isshead" style="padding:0"><div>'+head+'</div></div><span class="issxc none" style="grid-column:2 / span 4"><small>Calcul en attente…</small></span></div>'; return }
      cards+='<div class="issc"><div class="isshead"><div>'+head+'</div><button class="ghost iconbtn" type="button" data-iss-site="'+x.id+'" aria-label="Ajouter les transits de '+esc(x.name)+' au calendrier">'+cal+'</button></div>'
        +'<div class="issr issh"><span>Astre</span><span>Date</span><span>Heure</span><span>Durée</span><span class="issh2">Haut.</span></div>'+row('Moon',M[0])+row('Moon',M[1])+row('Sun',S[0])+row('Sun',S[1])+'</div>';
      cross+='<div class="issxr"><div class="isshead" style="padding:0"><div>'+head+'</div><button class="ghost iconbtn" type="button" data-iss-site="'+x.id+'" aria-label="Ajouter les transits de '+esc(x.name)+' au calendrier">'+cal+'</button></div>'+cell('Moon',M[0])+cell('Moon',M[1])+cell('Sun',S[0])+cell('Sun',S[1])+'</div>';
    });
    cross+='</div>';
    return '<p class="nightq" id="issSitesProg">'+esc(wait?issSitesProg||'Calcul en attente…':'')+'</p>'+cards+cross
      +'<p class="nightq eyehint">* Au-delà de 3 jours après l\'époque du TLE, les dates sont indicatives : l\'orbite de l\'ISS change. <b>Soleil : filtre solaire obligatoire.</b> <span id="issSitesMsg"></span></p>';
  }
  function issSitesHtml(){
    if(typeof satellite==='undefined') return '';
    return '<h3 class="evtitle">Transits de l\'ISS : mes sites</h3><div id="issSitesTable" class="isswrap">'+issSitesInner()+'</div>';
  }
  function issSitesRefresh(){ const e=$('issSitesTable'); if(e) e.innerHTML=issSitesInner() }
  function issSiteMsg(t){ const e=$('issSiteMsg'); if(e) e.textContent=t||'' }
  function issSitesUi(){
    const L=$('issSitesList'); if(!L) return;
    $('issSitesCount').textContent='· '+issSites.length+' sur '+ISS_MAX_SITES;
    L.innerHTML=issSites.length?issSites.map(x=>'<li class="siterow"><label class="sitechk"><input type="checkbox" data-site="'+x.id+'"'+(x.on!==false?' checked':'')+' aria-label="Calculer les transits pour '+esc(x.name)+'"></label><div class="sitetxt"><b>'+esc(x.name)+'</b><span>'+issLatLon(x.lat,x.lon)+'</span><em>'+issKindTxt(x.kind)+'</em></div><button class="ghost iconbtn" type="button" data-sitedel="'+x.id+'" aria-label="Supprimer le site '+esc(x.name)+'">×</button></li>').join(''):'<li class="siteempty">Aucun site pour le moment.</li>';
    const te=$('issSitesTle');
    if(!issTle) te.textContent='Aucun élément orbital (TLE) : colle-le dans « Imports », partie « Station spatiale (ISS) ».';
    else { const age=(Date.now()-issTle.epoch)/864e5; te.textContent='Éléments orbitaux du '+fmtD(issTle.epoch)+' à '+fmtS(issTle.epoch)+(age>3?' : plus de 3 jours, les dates sont indicatives. ':' : fiables pendant 2 à 3 jours. ')+'Mise à jour dans « Imports ».' }
    const q=$('issSiteQ'); q.disabled=!window.PLACES_URL;
    $('issSiteQHint').textContent=window.PLACES_URL?'Pour une commune, l\'application prend son centre. La zone de transit ne fait qu\'environ 8 km de large : précise ensuite le lieu d\'observation par ses coordonnées ou par « Ma position ».':'La recherche par nom de commune fonctionne dans l\'application installée : ici, saisis les coordonnées.';
  }
  function issSiteAdd(site){
    if(issSites.length>=ISS_MAX_SITES){ issSiteMsg('Six sites au plus : supprime-en un avant d\'en ajouter.'); return false }
    if(issSites.some(x=>Math.abs(x.lat-site.lat)<5e-4&&Math.abs(x.lon-site.lon)<5e-4)){ issSiteMsg('Ce lieu figure déjà dans la liste.'); return false }
    issSites.push(Object.assign({id:'s'+Date.now().toString(36)+Math.random().toString(36).slice(2,5),on:true},site));
    issSitesSave(); issSitesUi(); issSitesRefresh(); issSitesEnsure(); issSiteMsg('Site ajouté : « '+site.name+' ».'); return true;
  }
  function issSiteQuery(){
    const q=$('issSiteQ').value, ul=$('issSiteSug');
    if(!window.PLACES_URL||q.trim().length<2){ issSugs=[]; ul.innerHTML=''; return }
    loadPlaces().then(db=>{
      if(q!==$('issSiteQ').value) return;
      if(!db){ issSiteMsg('Le fichier des lieux n\'a pas pu être lu.'); return }
      issSugs=placeSearch(db,q,pos&&pos.src!=='defaut'?pos:null);
      ul.innerHTML=issSugs.length?issSugs.map((r,i)=>'<li><button type="button" data-sug="'+i+'"><b>'+esc(r.label)+'</b><span>'+esc(r.sub)+'</span></button></li>').join(''):'<li><span style="padding:.6rem .75rem;display:block">Aucun résultat.</span></li>';
    });
  }
  issSitesUi();
  $('issSiteQ').addEventListener('input',()=>{ clearTimeout(issSugT); issSugT=setTimeout(issSiteQuery,180) });
  $('issSiteSug').addEventListener('click',async e=>{
    const b=e.target.closest('[data-sug]'); if(!b) return;
    const r=issSugs[+b.dataset.sug]; if(!r) return;
    const db=await loadPlaces(); let la=r.lat, lo=r.lon;
    if(db&&r.k!=null){ const c=placeCenter(db,r.k); la=c[0]; lo=c[1] }
    if(issSiteAdd({name:r.label,lat:+la.toFixed(4),lon:+lo.toFixed(4),kind:r.kind})){ $('issSiteQ').value=''; $('issSiteSug').innerHTML=''; issSugs=[] }
  });
  $('issSitesList').addEventListener('change',e=>{
    const c=e.target.closest('[data-site]'); if(!c) return;
    const x=issSites.find(y=>y.id===c.dataset.site); if(!x) return;
    x.on=c.checked; issSitesSave(); issSitesRefresh(); issSitesEnsure();
  });
  $('issSitesList').addEventListener('click',e=>{
    const b=e.target.closest('[data-sitedel]'); if(!b) return;
    issSites=issSites.filter(y=>y.id!==b.dataset.sitedel); delete issSiteRes[b.dataset.sitedel]; issSitesSave(); issSitesUi(); issSitesRefresh(); issSiteMsg('Site supprimé.');
  });
  $('issSitePos').onclick=()=>{
    if(!pos||pos.src==='defaut'){ issSiteMsg('Position non disponible : autorise la localisation ou saisis un lieu dans « Date et lieu ».'); return }
    $('issSiteLat').value=num(pos.lat,4); $('issSiteLon').value=num(pos.lon,4); if(!$('issSiteName').value.trim()) $('issSiteName').value='Ma position';
    issSiteMsg('Position du téléphone reprise : appuie sur « Ajouter le site ».');
  };
  $('issSiteAdd').onclick=()=>{
    const pf=v=>parseFloat(String(v).replace(',','.').replace(/\s/g,'')), la=pf($('issSiteLat').value), lo=pf($('issSiteLon').value);
    if(!isFinite(la)||!isFinite(lo)||Math.abs(la)>90||Math.abs(lo)>180){ issSiteMsg('Coordonnées non valides : latitude de −90 à 90, longitude de −180 à 180 (en degrés décimaux, nord et est positifs).'); return }
    const nm=$('issSiteName').value.trim()||'Site '+(issSites.length+1), kind=(pos&&pos.src!=='defaut'&&Math.abs(pos.lat-la)<5e-4&&Math.abs(pos.lon-lo)<5e-4)?'pos':'coord';
    if(issSiteAdd({name:nm,lat:+la.toFixed(4),lon:+lo.toFixed(4),kind})){ $('issSiteName').value=''; $('issSiteLat').value=''; $('issSiteLon').value='' }
  };
  $('issSitesForget').onclick=()=>{
    const b=$('issSitesForget'), now=Date.now();
    if(now-issForgetT>4000){ issForgetT=now; b.textContent='Confirmer : tout oublier ?'; setTimeout(()=>{ b.textContent='Oublier tous les sites' },4200); return }
    issForgetT=0; issSites=[]; Object.keys(issSiteRes).forEach(k=>delete issSiteRes[k]); issSitesSave(); issSitesUi(); issSitesRefresh(); b.textContent='Oublier tous les sites'; issSiteMsg('Tous les sites sont oubliés.');
  };
'''
rep("  async function issFetch(){",JS+"  async function issFetch(){")
# ---------- 4) le tableau dans Système solaire, calcul lancé avec celui du lieu de l'utilisateur
rep("try{ issEnsure(obs); issNightEvents(times[0].getTime(),times[N].getTime()).forEach(x=>ev.push(x)) }catch(e){}","try{ issEnsure(obs); issSitesEnsure(); issNightEvents(times[0].getTime(),times[N].getTime()).forEach(x=>ev.push(x)) }catch(e){}")
rep("+issNextHtml();\n  }\n  let nightQ=''","+issNextHtml()+issSitesHtml();\n  }\n  let nightQ=''")
# ---------- 5) calendrier : par site
rep("function issIcsText(){\n    const ev=issPick('Moon').concat(issPick('Sun')).sort((a,b)=>a.t-b.t); if(!ev.length) return '';","function issIcsText(evs,site){\n    const ev=(evs||issPick('Moon').concat(issPick('Sun'))).slice().sort((a,b)=>a.t-b.t); if(!ev.length) return '';")
rep("const desc=issEventText(e)+'\\n'+(sun?","const desc=(site?'Site : '+site.name+'\\n':'')+issEventText(e)+'\\n'+(sun?")
rep("'UID:iss-'+e.body+'-'+Math.round(e.t/1000)+'@assistant-observation'","'UID:iss-'+(site?site.id+'-':'')+e.body+'-'+Math.round(e.t/1000)+'@assistant-observation'")
rep("""function issCalendar(){
    const msg=$('issMsg'), say=t=>{ if(msg) msg.textContent=t }, txt=issIcsText();""","""function issCalendar(site){
    const msg=$(site?'issSitesMsg':'issMsg'), say=t=>{ if(msg) msg.textContent=t }, txt=issIcsText(site?(issSitePick(site,'Moon')||[]).concat(issSitePick(site,'Sun')||[]):null,site);""")
rep("a.download='transits-iss.ics'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(a.href),4000);\n      say('Fichier « transits-iss.ics » créé : ouvre-le pour l\\'ajouter à ton calendrier.');",
    "const fn='transits-iss'+(site?'-'+(normQ(site.name).replace(/ /g,'-')||'site'):'')+'.ics'; a.download=fn; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(a.href),4000);\n      say('Fichier « '+fn+' » créé : ouvre-le pour l\\'ajouter à ton calendrier.');")
rep("""    if(e.target.closest('[data-go="iss"]')){ showTab('loc'); goSet('issBox') }
    else if(e.target.closest('[data-iss="ics"]')) issCalendar();""","""    if(e.target.closest('[data-go="iss"]')){ showTab('loc'); goSet('issBox') }
    else if(e.target.closest('[data-go="issSites"]')){ showTab('loc'); goSet('issSitesBox') }
    else if(e.target.closest('[data-iss-site]')){ const x=issSites.find(y=>y.id===e.target.closest('[data-iss-site]').dataset.issSite); if(x) issCalendar(x) }
    else if(e.target.closest('[data-iss="ics"]')) issCalendar();""")
# état du TLE : la ligne du menu se met à jour avec le statut
rep("  function issStatus(msg){\n    const el=$('issStatus'); if(msg){ el.textContent=msg; return }","  function issStatus(msg){\n    if(typeof issSitesUi==='function'&&$('issSitesList')) issSitesUi();\n    const el=$('issStatus'); if(msg){ el.textContent=msg; return }")
# ---------- 6) recherche de lieux (communes et lieux habités)
PLACES=r'''  // Recherche d'un lieu par son nom (fichier de lieux, application installée) : communes de France d'abord, puis lieux habités du monde ; sans accent ni majuscule
  const normQ=t=>String(t).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
  function placeIndex(db){
    if(db.nn) return;
    db.nn=db.names.map(normQ); db.pnn=db.pn.map(normQ); db.byName=new Map();
    for(let k=0;k<db.nCom;k++){ const ni=db.meta[k*6+4], a=db.byName.get(ni); if(a) a.push(k); else db.byName.set(ni,[k]) }
  }
  // Centre d'une commune : centre de gravité de son plus grand contour s'il est dans la commune, sinon centre de son cadre
  function placeCenter(db,k){
    const mt=db.meta, o=k*6; let cx=(mt[o]+mt[o+2])/2, cy=(mt[o+1]+mt[o+3])/2;
    try{
      const b=db.u8; let i=db.g0+mt[o+5];
      const rv=()=>{let v=0,sh=0,c; do{c=b[i++]; v|=(c&127)<<sh; sh+=7}while(c>=128); return v}, zz=a=>(a>>>1)^-(a&1);
      const nr=rv(); let best=null;
      for(let r=0;r<nr;r++){
        const m=rv(); let px=0,py=0; const pts=[];
        for(let q=0;q<m;q++){ px+=zz(rv()); py+=zz(rv()); pts.push([px,py]) }
        let A=0,GX=0,GY=0;
        for(let q=0;q<m;q++){ const [x1,y1]=pts[q], [x2,y2]=pts[(q+1)%m], cr=x1*y2-x2*y1; A+=cr; GX+=(x1+x2)*cr; GY+=(y1+y2)*cr }
        if(!best||Math.abs(A)>Math.abs(best.A)) best={A,GX,GY};
      }
      if(best&&best.A){ const gx=best.GX/(3*best.A), gy=best.GY/(3*best.A); if(placeInRings(db,mt[o+5],Math.round(gx),Math.round(gy))){ cx=gx; cy=gy } }
    }catch(e){}
    return [cy/1e4,cx/1e4];
  }
  function placeSearch(db,q,here){
    const n=normQ(q); if(n.length<2) return [];
    placeIndex(db);
    const cd=(la,lo)=>here?Math.hypot((la-here.lat)*111.2,(lo-here.lon)*111.2*Math.cos(here.lat*Math.PI/180)):0;
    const country=cc=>{ try{ return new Intl.DisplayNames(['fr'],{type:'region'}).of(cc)||cc }catch(e){ return cc } };
    const fmtSub=(c,la,lo,d)=>c+' · '+num(Math.abs(la),2)+'° '+(la>=0?'N':'S')+', '+num(Math.abs(lo),2)+'° '+(lo>=0?'E':'O')+(here?' · à '+Math.round(d)+' km de ta position':'');
    const com=[];
    db.nn.forEach((nm,i)=>{ const rk=nm.startsWith(n)?0:nm.indexOf(' '+n)>=0?1:-1; if(rk<0) return; (db.byName.get(i)||[]).forEach(k=>{ const o=k*6, la=(db.meta[o+1]+db.meta[o+3])/2e4, lo=(db.meta[o]+db.meta[o+2])/2e4; com.push({rk,k,la,lo,d:cd(la,lo),nm:db.names[i]}) }) });
    com.sort((a,b)=>a.rk-b.rk||(here?a.d-b.d:a.nm.localeCompare(b.nm,'fr')));
    const out=com.slice(0,6).map(r=>({label:r.nm,sub:fmtSub('France',r.la,r.lo,r.d),lat:r.la,lon:r.lo,k:r.k,kind:'commune'}));
    const pl=[];
    db.pnn.forEach((nm,i)=>{ const rk=nm.startsWith(n)?0:nm.indexOf(' '+n)>=0?1:-1; if(rk<0) return; const la=db.lat[i]/100, lo=db.lon[i]/100; pl.push({rk,i,la,lo,d:cd(la,lo)}) });
    pl.sort((a,b)=>a.rk-b.rk||(here?a.d-b.d:db.pn[a.i].localeCompare(db.pn[b.i])));
    for(const r of pl){
      if(out.length>=9) break;
      if(out.some(o=>Math.hypot((o.lat-r.la)*111.2,(o.lon-r.lo)*111.2*Math.cos(r.la*Math.PI/180))<8)) continue;     // même lieu qu'une commune déjà proposée
      const cc=String.fromCharCode(db.cc[2*r.i],db.cc[2*r.i+1]);
      out.push({label:db.pn[r.i],sub:fmtSub(country(cc),r.la,r.lo,r.d),lat:r.la,lon:r.lo,k:null,kind:'lieu'});
    }
    return out;
  }
'''
rep("  let carnetPlace=store.get('carnetPlace')===true;",PLACES+"  let carnetPlace=store.get('carnetPlace')===true;")
open(p,'w',encoding='utf-8').write(s); print('ok',round(len(s)/1e6,3),'Mo')
