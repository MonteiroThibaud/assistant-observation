# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
import sys, numpy as np, json
from PIL import Image
from playwright.sync_api import sync_playwright
import datetime
tz=datetime.timezone(datetime.timedelta(hours=2)); S=4
PORT=int(sys.argv[1]); css=open(sys.argv[2]).read() if len(sys.argv)>2 else ''
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':411,'height':850},device_scale_factor=S,timezone_id='Europe/Paris',locale='fr-FR',geolocation={'latitude':46.0345,'longitude':4.072},permissions=['geolocation'])
    pg=c.new_page()
    if css: pg.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const st=document.createElement('style'); st.textContent=%s; document.head.appendChild(st)})"%json.dumps(css))
    pg.clock.install(time=datetime.datetime(2026,10,30,13,0,tzinfo=tz)); pg.goto(f'http://localhost:{PORT}/index.html'); pg.wait_for_timeout(8000)
    pg.evaluate("document.querySelector('.tabbar [data-tab=det]').click()"); pg.wait_for_timeout(800)
    info=pg.evaluate("""()=>{const ph=document.querySelector('#tab-det .phead'); ph.scrollIntoView({block:'center'}); const r=ph.getBoundingClientRect();
      const h3=ph.querySelector('h3'); let tn=[...h3.childNodes].find(n=>n.nodeType===3&&n.textContent.trim()); const g=document.createRange(); g.selectNodeContents(tn); const q=g.getBoundingClientRect();
      const j=h3.querySelector('.jday').getBoundingClientRect(); const rise=ph.querySelector('.rise .t').getBoundingClientRect();
      return {r:[r.left,r.top,r.width,r.height],lune:[q.left,q.right],j:[j.left,j.right],t:[rise.left,rise.right]}}""")
    r=info['r']; pad=8
    pg.screenshot(path='/tmp/_jd.png',clip={'x':0,'y':r[1]-pad,'width':411,'height':r[3]+2*pad}); b.close()
im=np.asarray(Image.open('/tmp/_jd.png').convert('RGB')).astype(float); bg=np.median(im.reshape(-1,3),axis=0); mask=np.abs(im-bg).sum(axis=2)>70
def ink(x0,x1):
    m=mask[int(pad*S):int((pad+r[3])*S),int(x0*S):int(x1*S)]; rows=np.nonzero(m.sum(axis=1)>0)[0]; d=m.sum(axis=1); cum=np.cumsum(d)/d.sum()
    # ligne de base : bas de l'encre de la majorité des lettres (percentile 90 du bas)
    return rows.min()/S, rows.max()/S, (rows.min()+rows.max())/2/S, np.searchsorted(cum,.5)/S
for nom,key in (('« Lune »','lune'),('« J+20 »','j'),('« 20:50 »','t')):
    a,b_,e,mm=ink(*info[key]); print('%-10s encre de %.2f à %.2f ; centre de l’étendue %.2f ; centre de masse %.2f'%(nom,a,b_,e,mm))
