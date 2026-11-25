# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
p='/home/claude/work.html'; s=open(p,encoding='utf-8').read()
def rep(o,n,c=1):
    global s; assert s.count(o)==c,(o[:110],s.count(o)); s=s.replace(o,n)
# ---------- 1) Telrad : cercle pointillé du champ du chercheur
rep("      $('eyeStars').textContent='★ '+n+' étoile'+(n>1?'s':'')+' visibles à l\\'œil nu dans le cadre de '",
"""      // Champ du chercheur (cercle pointillé au centre) : champ réel réglé dans le menu « Chercheur »
      const fcF=FC&&FC.fov>0?FC.fov:5.6, fcR=fcF/2*3600*s;
      starsSvg+='<circle r="'+f(fcR)+'" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="5 4"/><text x="0" y="'+f(-fcR-3)+'" text-anchor="middle" class="sname" fill="var(--accent)">Chercheur '+num(fcF)+'°</text>';
      $('eyeStars').textContent='★ '+n+' étoile'+(n>1?'s':'')+' visibles à l\\'œil nu dans le cadre de '""")
rep("cercles rouges de 0,5°, 2° et 4° au centre, vue comme à l\\'œil nu (zénith en haut). '","cercles rouges de 0,5°, 2° et 4° et cercle pointillé du champ du chercheur ('+num(FC&&FC.fov>0?FC.fov:5.6)+'°) au centre, vue comme à l\\'œil nu (zénith en haut). '")
rep("ou le Telrad (champ de 10° avec ses cercles rouges de 0,5°, 2° et 4°, comme à l’œil nu ;","ou le Telrad (champ de 10° avec ses cercles rouges de 0,5°, 2° et 4° et, en pointillé, le champ de ton chercheur, comme à l’œil nu ;")
# ---------- 2) ISS : un seul tableau, « Site actuel » en première ligne, transit le plus proche en doré
rep("let issTle=null, issRes=null, issBusy=false, issKey='';","let issTle=null, issRes=null, issBusy=false, issKey='', issObs=null;")
rep("try{ issEnsure(obs); issSitesEnsure();","try{ issObs=obs; issEnsure(obs); issSitesEnsure();")
rep("+issNextHtml()+issSitesHtml();","+issSitesHtml();")
a=s.index("  function issNextHtml(){"); b=s.index("  // Export vers le calendrier du téléphone")
s=s[:a]+s[b:]
# message du calendrier : toujours dans le tableau
rep("const msg=$(site?'issSitesMsg':'issMsg'), say=","const msg=$('issSitesMsg'), say=")
# clic sur le calendrier : « Site actuel » ou site enregistré
rep("""else if(e.target.closest('[data-iss-site]')){ const x=issSites.find(y=>y.id===e.target.closest('[data-iss-site]').dataset.issSite); if(x) issCalendar(x) }""","""else if(e.target.closest('[data-iss-site]')){ const sid=e.target.closest('[data-iss-site]').dataset.issSite; if(sid==='cur') issCalendar(); else { const x=issSites.find(y=>y.id===sid); if(x) issCalendar(x) } }""")
# nouveau corps du tableau
a=s.index("  function issSitesInner(){"); b=s.index("  function issSitesHtml(){")
NEW=r'''  function issSitesInner(){
    const goSites='<span class="eyelink" data-go="issSites">Paramètres ›</span>', goTle='<span class="eyelink" data-go="iss">Paramètres ›</span>';
    if(!issTle) return '<p class="nightq">Colle les éléments orbitaux (TLE) de l\'ISS dans '+goTle+' pour voir ici les transits devant la Lune et le Soleil.</p>';
    const cur={id:'cur',name:'Site actuel',kind:'cur'}, act=[cur].concat(issSites.filter(x=>x.on!==false));
    const pick=(x,b)=>x.id==='cur'?(issRes?issPick(b):null):issSitePick(x,b);
    const star=e=>(e.t-issTle.epoch)/864e5>3?'*':'';
    const subOf=x=>x.id==='cur'?((pos.src==='defaut'?'Lieu par défaut : précise ta position dans « Date et lieu »':pos.src==='gps'?'Position du téléphone':'Position saisie')+' · '+issLatLon(pos.lat,pos.lon)):issKindTxt(x.kind);
    // transit le plus proche en date (tous sites et astres) : mis en évidence, avec ceux qui en sont à moins de 5 minutes (même passage vu de plusieurs sites)
    const evs=[]; act.forEach(x=>['Moon','Sun'].forEach(b=>{ (pick(x,b)||[]).forEach(e=>evs.push(e)) }));
    const tmin=evs.length?Math.min.apply(null,evs.map(e=>e.t)):null, hl=e=>tmin!==null&&e.t-tmin<300000;
    const cal='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>';
    const nm=b=>b==='Sun'?'Soleil':'Lune';
    const row=(b,e)=>e?'<div class="issr'+(hl(e)?' next':'')+'"><span class="issa">'+nm(b)+'</span><span>'+issDay(e.t)+star(e)+'</span><span class="isst">'+fmtS(e.t)+'</span><span class="isso">'+num(e.dur,1)+' s</span><span class="isso issh2">'+Math.round(e.bodyAlt)+'°</span></div>'
      :'<div class="issr none"><span class="issa">'+nm(b)+'</span><span>Aucun transit dans les 400 prochains jours</span></div>';
    const cell=(b,e)=>e?'<span class="issxc'+(hl(e)?' next':'')+'"><b>'+issDay(e.t)+star(e)+'</b><i>'+fmtS(e.t)+'</i><small>durée '+num(e.dur,1)+' s · hauteur '+Math.round(e.bodyAlt)+'°</small></span>':'<span class="issxc none"><small>Aucun transit dans les 400 prochains jours</small></span>';
    let cards='', cross='<div class="issx"><div class="issxr issxh"><span>Site</span><span>Lune · 1er</span><span>Lune · 2e</span><span>Soleil · 1er</span><span>Soleil · 2e</span></div>', wait=false;
    act.forEach(x=>{
      const M=pick(x,'Moon'), S=pick(x,'Sun');
      const head='<b>'+issEsc(x.name)+'</b><span>'+issEsc(subOf(x))+'</span>';
      if(!M||!S){ wait=true; cards+='<div class="issc"><div class="isshead"><div>'+head+'</div></div><div class="issr none"><span>Calcul en attente…</span></div></div>'; cross+='<div class="issxr"><div class="isshead" style="padding:0"><div>'+head+'</div></div><span class="issxc none" style="grid-column:2 / span 4"><small>Calcul en attente…</small></span></div>'; return }
      const btn='<button class="ghost iconbtn" type="button" data-iss-site="'+x.id+'" aria-label="Ajouter les transits de '+issEsc(x.name)+' au calendrier">'+cal+'</button>';
      cards+='<div class="issc"><div class="isshead"><div>'+head+'</div>'+btn+'</div>'
        +'<div class="issr issh"><span>Astre</span><span>Date</span><span>Heure</span><span>Durée</span><span class="issh2">Haut.</span></div>'+row('Moon',M[0])+row('Moon',M[1])+row('Sun',S[0])+row('Sun',S[1])+'</div>';
      cross+='<div class="issxr"><div class="isshead" style="padding:0"><div>'+head+'</div>'+btn+'</div>'+cell('Moon',M[0])+cell('Moon',M[1])+cell('Sun',S[0])+cell('Sun',S[1])+'</div>';
    });
    cross+='</div>';
    const age=Math.max(0,(Date.now()-issTle.epoch)/864e5), old=age>14?' Le TLE a '+Math.round(age)+' jours : mets-le à jour dans '+goTle+'.':'';
    return '<p class="nightq" id="issSitesProg">'+issEsc(wait?(issBusy||issSitesBusy?issSitesProg||'Recherche des prochains transits…':'Calcul en attente…'):'')+'</p>'+cards+cross
      +'<p class="nightq eyehint">En doré : le transit le plus proche dans le temps. * Au-delà de 3 jours après l\'époque du TLE, les dates sont indicatives : l\'orbite de l\'ISS change. <b>Soleil : filtre solaire obligatoire.</b>'+old+(issSites.length?'':' Ajoute d\'autres sites dans '+goSites+'.')+' <span id="issSitesMsg"></span></p>';
  }
'''
s=s[:a]+NEW+s[b:]
rep("    if(typeof satellite==='undefined'||(!issSites.length&&!issTle)) return '';\n    return '<h3 class=\"evtitle\">Transits de l\\'ISS : mes sites</h3>","    if(typeof satellite==='undefined') return '';\n    return '<h3 class=\"evtitle\">Transits de l\\'ISS</h3>")
# styles : « Soleil » comme « Lune », transit le plus proche en doré
rep(".issr .issa{font-weight:700}.issr .issa.Sun{color:var(--accent)}",".issr .issa{font-weight:700}.issr.next span{color:var(--accent);font-weight:700}")
rep(".issxc.Sun i{color:var(--accent)}",".issxc.next b,.issxc.next i{color:var(--accent)}")
# menu des sites et Informations
rep("pour chacun de tes sites (six au plus). Les résultats s'affichent dans l'onglet « Système solaire ».</p>","pour ton lieu (« Site actuel », toujours en première ligne) et pour chacun de tes sites enregistrés (six au plus). Les résultats s'affichent dans un même tableau de l'onglet « Système solaire ».</p>")
rep("à ton lieu (heure à la seconde, durée d’environ une seconde, hauteur de l’astre ; filtre solaire obligatoire pour le Soleil), ou un passage rapproché de la Lune avec la distance à parcourir pour voir le transit ; sous la liste figurent les deux prochains transits devant la Lune et devant le Soleil, même lointains : au-delà de quelques jours, ces dates sont indicatives, l’orbite de l’ISS changeant. Le bouton « Ajouter au calendrier du téléphone » crée un fichier .ics avec ces transits et deux rappels (30 et 5 minutes avant) ; il fonctionne dans l’application installée.","à ton lieu (heure à la seconde, durée d’environ une seconde, hauteur de l’astre ; filtre solaire obligatoire pour le Soleil), ou un passage rapproché de la Lune avec la distance à parcourir pour voir le transit ; en dessous, le tableau « Transits de l’ISS » donne, pour ton lieu (« Site actuel », en première ligne) et pour chacun de tes sites enregistrés, les deux prochains transits devant la Lune et les deux prochains devant le Soleil, même lointains : le transit le plus proche dans le temps est en doré, et au-delà de quelques jours les dates sont indicatives, l’orbite de l’ISS changeant. Le bouton calendrier de chaque ligne crée un fichier .ics avec ces transits et deux rappels (30 et 5 minutes avant) ; il fonctionne dans l’application installée.")
rep("Pour chaque site coché, l’onglet « Système solaire » donne, dans un tableau, les deux prochains transits de l’ISS devant la Lune et les deux prochains devant le Soleil (date, heure à la seconde, durée, hauteur de l’astre), avec un bouton pour les ajouter au calendrier du téléphone.","Chaque site coché s’ajoute, sous « Site actuel », au tableau de l’onglet « Système solaire » (date, heure à la seconde, durée et hauteur de l’astre pour chaque transit).")
open(p,'w',encoding='utf-8').write(s); print('ok',round(len(s)/1e6,3),'Mo')
