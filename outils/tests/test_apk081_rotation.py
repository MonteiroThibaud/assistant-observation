# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
# navigateur simulé : le verrou n'est accepté qu'après un geste de l'utilisateur et, pour les orientations précises, qu'en plein écran
INIT="""
window.__ev=[]; window.__act=false; window.__isfs=false;
['pointerup','click'].forEach(e=>document.addEventListener(e,()=>{window.__act=true},true));
Object.defineProperty(document,'fullscreenElement',{get:()=>window.__isfs?document.documentElement:null});
Element.prototype.requestFullscreen=function(){ window.__ev.push('plein écran demandé'); window.__isfs=true; document.dispatchEvent(new Event('fullscreenchange')); return Promise.resolve() };
document.exitFullscreen=function(){ window.__isfs=false; document.dispatchEvent(new Event('fullscreenchange')); return Promise.resolve() };
Object.defineProperty(screen.orientation,'lock',{value:function(t){ const ok=window.__act&&(t==='any'||window.__isfs); window.__ev.push('lock('+t+') '+(ok?'accepté':'refusé')); return ok?Promise.resolve():Promise.reject(new DOMException('x','NotAllowedError')) }});
Object.defineProperty(screen.orientation,'unlock',{value:function(){ window.__ev.push('unlock') }});
"""
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':360,'height':780},timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    c.add_init_script(INIT)
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.clock.install(time=datetime.datetime(2026,10,29,22,0,tzinfo=tz)); pg.goto('http://localhost:8810/index.html'); pg.wait_for_timeout(8000)
    ev=lambda: pg.evaluate("window.__ev.splice(0)"); g=lambda i: pg.evaluate("(i)=>document.getElementById(i).textContent",i)
    print('1. au lancement (sans geste) :',ev())
    pg.evaluate("document.querySelector('.tabbar [data-tab=loc]').click()"); pg.wait_for_timeout(300)
    print('2. au premier geste :',ev())
    pg.evaluate("document.getElementById('scrBox').open=true")
    pg.click('#scrRot'); pg.wait_for_timeout(400); print('3. « bloquée » avec plein écran bloqué :',g('scrRot'),'|',g('scrFull'),'|',ev(),'| message :',repr(g('scrMsg')))
    pg.click('#scrFull'); pg.wait_for_timeout(300); ev()
    pg.click('#scrRot'); pg.wait_for_timeout(400); print('4. plein écran autorisé puis « bloquée » :',g('scrRot'),'|',g('scrFull'),'|',ev(),'| message :',repr(g('scrMsg')))
    pg.click('#scrRot'); pg.wait_for_timeout(400); print('5. retour à « autorisée » :',g('scrRot'),'|',ev())
    print('erreurs JS :',errs[:2]); b.close()
