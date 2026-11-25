# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys, json
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3])
JS="""
(()=>{
  const out=[];
  const vis=e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'};
  const tcenter=e=>{ // centre vertical du texte (sinon de la boîte)
    const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.textContent.trim()?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT}); let n=w.nextNode(); if(!n){const r=e.getBoundingClientRect(); return [r.top+r.height/2,r.height,false]}
    const rg=document.createRange(); rg.selectNodeContents(n); const rs=[...rg.getClientRects()]; if(!rs.length){const r=e.getBoundingClientRect(); return [r.top+r.height/2,r.height,false]}
    const f=rs[0]; return [f.top+f.height/2,f.height,rs.length>1];
  };
  document.querySelectorAll('body *').forEach(c=>{
    if(!vis(c)) return; const cs=getComputedStyle(c);
    if(!(cs.display==='flex'||cs.display==='inline-flex')) return; if(cs.flexDirection!=='row'&&cs.flexDirection!=='row-reverse') return;
    const kids=[...c.children].filter(vis); if(kids.length<2) return;
    const info=kids.map(k=>{const t=tcenter(k); return {tag:k.tagName.toLowerCase()+(k.className&&typeof k.className==='string'?'.'+k.className.split(' ')[0]:''),centre:t[0],multi:t[2],texte:(k.textContent||'').trim().slice(0,22)}});
    if(info.some(i=>i.multi)) return;        // texte sur plusieurs lignes : l'alignement vertical n'a pas de sens
    const cs_=info.map(i=>i.centre); const dev=Math.max(...cs_)-Math.min(...cs_);
    const tops=kids.map(k=>k.getBoundingClientRect().top), hh=Math.max(...kids.map(k=>k.getBoundingClientRect().height)); if(Math.max(...tops)-Math.min(...tops)>0.7*hh+4 && cs.flexWrap!=='nowrap') return;   // rangée repliée sur plusieurs lignes
    if(dev>0.8){ const r=c.getBoundingClientRect(); out.push({conteneur:c.tagName.toLowerCase()+'.'+String(c.className).split(' ').join('.')+(c.id?'#'+c.id:''),ecart:+dev.toFixed(1),alignItems:cs.alignItems,enfants:info.map(i=>[i.tag,i.texte,+(i.centre-Math.min(...cs_)).toFixed(1)])}) }
  });
  return out;
})()
"""
res={}
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto(f'http://localhost:{PORT}/index.html'); pg.wait_for_timeout(9000)
    def audit(nom):
        r=pg.evaluate(JS); res[nom]=r; print('==',nom,':',len(r),'rangées mal centrées')
        for x in r[:12]: print('   ',x['conteneur'],'| écart',x['ecart'],'px | align-items',x['alignItems'],'|',x['enfants'])
    for tab in ('sys','det','deep','eye','moon','loc'):
        pg.evaluate("t=>document.querySelector('.tabbar [data-tab='+t+']').click()",tab); pg.wait_for_timeout(1200)
        if tab=='loc': pg.evaluate("document.querySelectorAll('#tab-loc details').forEach(d=>d.open=true)"); pg.wait_for_timeout(500)
        if tab=='deep':
            for f in ('all','gal','amas','neb','dbl','com','ast'):
                pg.evaluate("f=>{const b=document.querySelector('#deepFilter [data-f=\"'+f+'\"]'); if(b) b.click()}",f); pg.wait_for_timeout(400)
                pg.evaluate("document.querySelectorAll('#deepList [data-dso], #deepList [data-sb], #deepList li').forEach((e,i)=>{ if(i<6){ const h=e.querySelector('.dhead'); if(h&&!e.classList.contains('open')) h.click() } })"); pg.wait_for_timeout(900)
                audit('deep/'+f)
        if tab=='moon':
            pg.evaluate("window.__show&&window.__show('Tycho')"); pg.wait_for_timeout(1200)
        audit(tab)
    print('erreurs JS :',errs[:2]); b.close()
json.dump(res,open('/tmp/audit_align_%d.json'%W,'w'),ensure_ascii=False)
