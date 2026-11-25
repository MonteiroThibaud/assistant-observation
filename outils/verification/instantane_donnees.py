# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Instantané des tables de connaissances de la page : extrait les tables (JSON compact) depuis une page HTML de l'application,
# calcule leurs empreintes SHA-256 et, si on donne un dossier de référence, vérifie qu'elles sont identiques.
# Usage : python3 instantane_donnees.py PAGE.html DOSSIER_SORTIE [DOSSIER_REFERENCE]
# La page est servie dans une copie de test où un crochet window.__K() expose les tables (jamais dans la page livrée).
import sys, json, hashlib, os, shutil, subprocess, time
from playwright.sync_api import sync_playwright
NOMS=['CONST','FEATURES','MESSIER','DSO_EXTRA','DSO_DOUBLE','SKY_STARS','SKY_CONS','DSO_TYPE','DOUBLE_INFO','ASTERISMS','MOON_FILTERS','DESC','FEAT_M']
def instantane(page, sortie, port=8839):
    s=open(page,encoding='utf-8').read(); k=s.index("  $('featClose').onclick=")
    tmp='/tmp/instantane_site'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    open(tmp+'/index.html','w',encoding='utf-8').write(s[:k]+"  window.__K=()=>({"+",".join(NOMS)+"});\n"+s[k:])
    srv=subprocess.Popen([sys.executable,'-m','http.server',str(port)],cwd=tmp,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(2)
    try:
        with sync_playwright() as p:
            b=p.chromium.launch(); pg=b.new_page(); pg.goto(f'http://localhost:{port}/index.html'); pg.wait_for_timeout(7000)
            txt=pg.evaluate("(()=>{const K=window.__K(); const o={}; for(const k in K){ o[k]=JSON.stringify(K[k]) } return o})()"); b.close()
    finally: srv.terminate()
    os.makedirs(sortie,exist_ok=True); man={}
    for k,v in txt.items():
        open(os.path.join(sortie,k+'.json'),'w',encoding='utf-8').write(v); d=json.loads(v)
        man[k]={'octets':len(v.encode()),'elements':len(d),'type':type(d).__name__,'sha256':hashlib.sha256(v.encode()).hexdigest()}
    json.dump(man,open(os.path.join(sortie,'MANIFESTE.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1); return man
def compare(man, ref):
    r=json.load(open(os.path.join(ref,'MANIFESTE.json'),encoding='utf-8')); bad=[k for k in r if man.get(k,{}).get('sha256')!=r[k]['sha256']]
    return bad
if __name__=='__main__':
    man=instantane(sys.argv[1],sys.argv[2]); print(len(man),'tables extraites')
    if len(sys.argv)>3:
        bad=compare(man,sys.argv[3]); print('identiques à la référence' if not bad else 'DIFFÉRENCES : '+', '.join(bad)); sys.exit(1 if bad else 0)
