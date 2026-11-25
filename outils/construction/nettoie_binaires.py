# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Retire les métadonnées de provenance (C2PA / JUMBF) que la plateforme ajoute aux images JPEG, WebP et PNG du dossier de sortie
# entre deux tours de travail (JPEG : segments APP11 de 5 771 octets ; WebP : bloc « C2PA »). Le retrait redonne exactement les octets d'origine.
import struct, hashlib
def nettoie_jpeg(b):
    if b[:2]!=b'\xff\xd8': return b
    out=bytearray(b[:2]); i=2
    while i<len(b):
        if b[i]!=0xff: out+=b[i:]; break
        m=b[i+1]
        if m==0xda: out+=b[i:]; break
        L=struct.unpack('>H',b[i+2:i+4])[0]; seg=b[i:i+2+L]
        if not (m==0xeb and (b'jumb' in seg[:40] or b'c2pa' in seg[:60].lower() or b'JP' in seg[4:6])): out+=seg
        i+=2+L
    return bytes(out)
def nettoie_webp(b):
    if b[:4]!=b'RIFF' or b[8:12]!=b'WEBP': return b
    out=bytearray(b[:12]); i=12
    while i+8<=len(b):
        cc=b[i:i+4]; n=struct.unpack('<I',b[i+4:i+8])[0]; ch=b[i:i+8+n+(n&1)]
        if cc!=b'C2PA': out+=ch
        i+=8+n+(n&1)
    out[4:8]=struct.pack('<I',len(out)-8); return bytes(out)
def nettoie_png(b):
    # PNG : bloc « caBX » (manifeste C2PA / JUMBF) ajouté par la plateforme
    if b[:8]!=b'\x89PNG\r\n\x1a\n': return b
    out=bytearray(b[:8]); i=8
    while i+12<=len(b):
        n=struct.unpack('>I',b[i:i+4])[0]; ch=b[i:i+12+n]
        if b[i+4:i+8]!=b'caBX': out+=ch
        i+=12+n
    return bytes(out)
def nettoie(b,nom):
    n=nom.lower()
    if n.endswith(('.jpg','.jpeg')): return nettoie_jpeg(b)
    if n.endswith('.webp'): return nettoie_webp(b)
    if n.endswith('.png'): return nettoie_png(b)
    return b
def lit(chemin):
    return nettoie(open(chemin,'rb').read(),chemin)
