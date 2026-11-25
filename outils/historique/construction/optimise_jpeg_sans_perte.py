# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""Recompression JPEG sans perte (mozjpeg : coefficients identiques, tables de Huffman optimisées, mode progressif) des images JPEG de donnees/binaires/web.
Usage : python3 optimise_jpeg_sans_perte.py DONNEES_DIR [--ecrit]   (sans --ecrit : mesure seulement)
Contrôle : les pixels décodés sont identiques (comparaison complète) ; les octets lus sont ceux de nettoie_binaires (sans les métadonnées C2PA)."""
import sys, os, glob, importlib.util, io
import numpy as np
from PIL import Image
import mozjpeg_lossless_optimization as mz
ICI=os.path.dirname(os.path.abspath(__file__)); spec=importlib.util.spec_from_file_location('nb',os.path.join(ICI,'nettoie_binaires.py')); nb=importlib.util.module_from_spec(spec); spec.loader.exec_module(nb)
don=sys.argv[1]; ecrit='--ecrit' in sys.argv; tot0=tot1=0; ok=True
for f in sorted(glob.glob(os.path.join(don,'binaires','web','*.jpg'))):
    b=nb.lit(f); o=mz.optimize(b,copy=mz.COPY_MARKERS.ALL)
    a0=np.asarray(Image.open(io.BytesIO(b)).convert('RGB')); a1=np.asarray(Image.open(io.BytesIO(o)).convert('RGB'))
    same=a0.shape==a1.shape and bool((a0==a1).all())
    gain=len(b)-len(o)
    print('%-22s %9d -> %9d octets (%+.1f %%) | pixels identiques : %s'%(os.path.basename(f),len(b),len(o),-100*gain/len(b),same))
    if not same: ok=False; continue
    if gain>0:
        tot0+=len(b); tot1+=len(o)
        if ecrit: open(f,'wb').write(o)
print('total retenu : %d -> %d octets, gain %d octets (%.0f Ko ; en base64 : %.0f Ko)'%(tot0,tot1,tot0-tot1,(tot0-tot1)/1e3,(tot0-tot1)*4/3/1e3)); sys.exit(0 if ok else 1)
