# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
INIT="""
window.__ev=[]; window.__act=false; window.__isfs=false;
['pointerup','click'].forEach(e=>document.addEventListener(e,()=>{window.__act=true},true));
Object.defineProperty(document,'fullscreenElement',{get:()=>window.__isfs?document.documentElement:null});
Element.prototype.requestFullscreen=function(){ window.__ev.push('plein écran demandé'); window.__isfs=true; setTimeout(()=>document.dispatchEvent(new Event('fullscreenchange')),30); return Promise.resolve() };
document.exitFullscreen=function(){ window.__isfs=false; document.dispatchEvent(new Event('fullscreenchange')); return Promise.resolve() };
Object.defineProperty(screen.orientation,'lock',{value:function(t){ const ok=window.__act&&window.__isfs; window.__ev.push('lock('+t+') '+(ok?'accepté':'refusé')); return ok?Promise.resolve():Promise.reject(new DOMException('x','NotAllowedError')) }});
Object.defineProperty(screen.orientation,'unlock',{value:function(){ window.__ev.push('unlock') }});
const mm=window.matchMedia.bind(window); window.matchMedia=q=>{ const r=mm(q); if(q==='(display-mode: standalone)') return {matches:%s,media:q,addEventListener(){},removeEventListener(){}}; if(q==='(display-mode: fullscreen)') return {matches:%s,media:q,addEventListener(){},removeEventListener(){}}; return r };
"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for nom,std,full in (('navigateur (onglet)','false','false'),('application autonome (manifeste non pris en compte)','true','false'),('application en plein écran (manifeste pris en compte)','false','true')):
        c=b.new_context(viewport={'width':360,'height':780},timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
        c.add_init_script(INIT%(std,full))
        pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(time=datetime.datetime(2026,10,30,22,0,tzinfo=tz)); pg.goto('http://localhost:8860/index.html'); pg.wait_for_timeout(8000)
        ev=lambda: pg.evaluate("window.__ev.splice(0)"); g=lambda i: pg.evaluate("(i)=>document.getElementById(i).textContent",i)
        e0=ev(); pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.evaluate("document.getElementById('scrBox').open=true"); pg.wait_for_timeout(700)
        e1=ev()
        print('==',nom); print('  au lancement :',e0,'| au premier geste :',e1); print('  boutons :',g('scrRot'),'|',g('scrFull')); print('  diagnostic :',g('scrDiag')); print('  erreurs JS :',errs[:2]); c.close()
    b.close()
