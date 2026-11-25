# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys, numpy as np, json
from PIL import Image
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2))
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3]); S=4
ROWS=[('sys','#tab-sys .nightbar',''),
 ('det','#tab-det .nightbar',''),('det','#tab-det .phead',''),('det','#tab-det .phead .rise',''),
 ('deep','#tab-deep .nightbar',''),('deep','#deepList [data-dso="M1"] .findhead',"document.querySelector('#deepFilter [data-f=\"all\"]').click(); const e=document.querySelector('#deepList [data-dso=\"M1\"]'); if(e&&!e.classList.contains('open')) e.querySelector('.dhead').click()"),
 ('deep','#deepList [data-dso="M1"] .dhead',''),
 ('eye','#tab-eye .nightbar',''),('eye','#tab-eye .objrow',''),
 ('moon','#tab-moon .nightbar:not(.timebar)',''),('moon','#tab-moon .timebar',''),
 ('loc','#tab-loc details.setdet > summary',"document.querySelectorAll('#tab-loc details').forEach(d=>d.open=false)")]
def run(pg,tab,sel,setup):
    run.n+=1
    pg.evaluate("t=>document.querySelector('.tabbar [data-tab='+t+']').click()",tab); pg.wait_for_timeout(700)
    if setup: pg.evaluate("()=>{"+setup+"}"); pg.wait_for_timeout(900)
    info=pg.evaluate("""(sel)=>{const hd=document.querySelector(sel); if(!hd) return null; hd.scrollIntoView({block:'center'}); const r=hd.getBoundingClientRect(); const kids=[...hd.children].filter(k=>{const q=k.getBoundingClientRect(); return q.width>1&&q.height>1}); return {r:[r.left,r.top,r.width,r.height],kids:kids.map(k=>{const q=k.getBoundingClientRect(); return [q.left-r.left,q.right-r.left,k.tagName+(k.className&&typeof k.className==='string'?'.'+k.className.split(' ')[0]:''),(k.textContent||'').trim().slice(0,16)]})}}""",sel)
    if not info: return None
    r=info['r']; pad=8
    pg.screenshot(path='/tmp/_row%d.png'%run.n,clip={'x':max(0,r[0]-4),'y':max(0,r[1]-pad),'width':min(W,r[2]+8),'height':r[3]+2*pad})
    im=np.asarray(Image.open('/tmp/_row%d.png'%run.n).convert('RGB')).astype(float)
    bg=np.median(im.reshape(-1,3),axis=0); mask=np.abs(im-bg).sum(axis=2)>70
    out=[]
    for (a,b,tag,txt) in info['kids']:
        shrink=16 if tag.startswith('BUTTON') else 0
        x0=max(0,int((a+4)*S)+shrink); x1=min(mask.shape[1],int((b+4)*S)-shrink)
        m=mask[int(pad*S):int((pad+r[3])*S),x0:x1]; rows=np.nonzero(m.sum(axis=1)>0)[0]
        if not len(rows): continue
        dens=m.sum(axis=1); cum=np.cumsum(dens)/dens.sum(); med=np.searchsorted(cum,0.5)/S
        out.append((tag,txt,(rows.min()+rows.max())/2/S,med))
    return out
run.n=0
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=S,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    import os
    if len(sys.argv)>4 and os.path.exists(sys.argv[4]): pg.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const st=document.createElement('style'); st.textContent=%s; document.head.appendChild(st)})"%json.dumps(open(sys.argv[4],encoding='utf-8').read()))
    pg.clock.install(time=datetime.datetime(2026,10,30,13,0,tzinfo=tz)); pg.goto(f'http://localhost:{PORT}/index.html'); pg.wait_for_timeout(8000)
    for tab,sel,setup in ROWS:
        o=run(pg,tab,sel,setup)
        if not o: print('%-52s : introuvable'%sel); continue
        cs=[x[2] for x in o]; dev=max(cs)-min(cs); ms=[x[3] for x in o]; devm=max(ms)-min(ms)
        print('%-44s : étendue %.2f | masse %.2f px %s | %s'%(sel[-44:],dev,devm,'<<<' if max(dev,devm)>1.0 else '',[ (x[1][:9],round(x[2]-min(cs),2),round(x[3]-min(ms),2)) for x in o]))
    print('erreurs JS :',errs[:1]); b.close()
