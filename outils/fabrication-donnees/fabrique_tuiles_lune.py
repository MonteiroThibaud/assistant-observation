#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""
Fabrication des tuiles de texture de la Lune pour l'Assistant d'observation (version installée).

Entrée  : la carte couleur LROC du CGI Moon Kit de la NASA, en 16 384 × 8 192 points :
          lroc_color_16bit_srgb_16k.tif
          (page https://svs.gsfc.nasa.gov/4720 , rubrique « Color » ; adresse directe :
           https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_16bit_srgb_16k.tif )
Sortie  : dossier « tuiles-lune » (tuiles JPEG de 512 × 512 points en niveaux de gris + manifest.json)
          et archive « tuiles-lune.zip » à envoyer à Claude.

Principe : on garde la face visible (longitudes −100,0176° à +100,0176°, comme la texture de base de l'application),
on convertit en niveaux de gris, on cale les tons sur la texture de base (moon-texture.jpg, fournie avec ce script)
par égalisation des histogrammes, puis on découpe en tuiles.

Usage   : python fabrique_tuiles_lune.py lroc_color_16bit_srgb_16k.tif
Options : --base moon-texture.jpg   (texture de base, par défaut celle qui est à côté du script)
          --qualite 72              (qualité JPEG, 60 à 85)
          --sortie tuiles-lune      (dossier de sortie)
          --essai                   (mode d'essai : fabrique de fausses tuiles à partir de la texture de base, sans carte NASA)
"""
import argparse, json, math, os, sys, zipfile
import numpy as np
from PIL import Image

TEX_LON0 = -100.0176          # longitude du bord gauche de la texture de base (degrés)
BASE_PPD = 8192 / 360         # points par degré de la texture de base
TILE = 512

def lire_carte(chemin):
    try:
        import tifffile
    except ImportError:
        sys.exit("Il manque le module tifffile : tapez  pip install numpy pillow tifffile imagecodecs  puis relancez.")
    print("Lecture de", chemin, "(patience, le fichier est volumineux)…")
    a = tifffile.imread(chemin)
    if a.ndim == 3 and a.shape[0] in (3, 4) and a.shape[2] > 4:
        a = np.moveaxis(a, 0, -1)
    if a.ndim == 2:
        a = a[:, :, None]
    return a[:, :, :3] if a.shape[2] >= 3 else np.repeat(a[:, :, :1], 3, axis=2)

def en_gris(rgb):
    """Luminance de la carte, ramenée à 0–255 (flottants)."""
    echelle = 255.0 / (65535.0 if rgb.dtype == np.uint16 else 255.0)
    y = np.zeros(rgb.shape[:2], np.float32)
    for k, c in enumerate((0.299, 0.587, 0.114)):
        y += c * rgb[:, :, k].astype(np.float32)
    return y * echelle

def caler_tons(gris, base_png):
    """Table de correspondance (256 valeurs) : même histogramme que la texture de base, une fois la carte réduite à sa taille."""
    base = np.asarray(Image.open(base_png).convert("L"))
    h, w = base.shape
    reduit = np.asarray(Image.fromarray(np.clip(gris, 0, 255).astype(np.uint8)).resize((w, h), Image.BOX))
    # on ignore les bords noirs éventuels
    m = (base > 0) | (reduit > 0)
    cb = np.cumsum(np.bincount(base[m], minlength=256)).astype(np.float64); cb /= cb[-1]
    cr = np.cumsum(np.bincount(reduit[m], minlength=256)).astype(np.float64); cr /= cr[-1]
    lut = np.interp(cr, cb, np.arange(256)).astype(np.float32)
    lut = np.maximum.accumulate(lut)               # monotone
    ecart = np.mean(np.abs(lut[reduit[m]] - base[m]))
    print("Calage des tons : écart moyen avec la texture de base après calage : %.2f niveaux (sur 255)" % ecart)
    return lut

def fausse_carte(base_png, facteur=2):
    """Mode d'essai : face visible « fine » fabriquée à partir de la texture de base (même détail, deux fois plus de points)."""
    base = Image.open(base_png).convert("L")
    w, h = base.size
    grand = base.resize((w * facteur, h * facteur), Image.BICUBIC)
    return np.asarray(grand, np.float32), BASE_PPD * facteur

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carte", nargs="?")
    ap.add_argument("--base", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "moon-texture.jpg"))
    ap.add_argument("--qualite", type=int, default=72)
    ap.add_argument("--sortie", default="tuiles-lune")
    ap.add_argument("--essai", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(a.base):
        sys.exit("Texture de base introuvable : " + a.base)
    if a.essai:
        gris, ppd = fausse_carte(a.base)
    else:
        if not a.carte:
            sys.exit("Indiquez la carte NASA : python fabrique_tuiles_lune.py lroc_color_16bit_srgb_16k.tif")
        rgb = lire_carte(a.carte)
        H, W = rgb.shape[:2]
        ppd = W / 360.0
        print("Carte : %d × %d points, %.2f points par degré (%.2f km par point)" % (W, H, ppd, 1737.4 * math.pi / 180 / ppd))
        if ppd < 40:
            print("Attention : cette carte est moins fine que prévu (il faut le fichier de 16 384 points de large).")
        x0 = int(round((TEX_LON0 + 180) * ppd))
        largeur = int(round(2 * -TEX_LON0 * ppd))
        rgb = rgb[:, x0:x0 + largeur, :]                         # face visible seulement : économie de mémoire
        gris = en_gris(rgb); del rgb
        x0 = 0
    h, w = gris.shape
    lut = caler_tons(gris, a.base)
    g8 = lut[np.clip(np.rint(gris), 0, 255).astype(np.uint8)].astype(np.uint8)
    cols = math.ceil(w / TILE); rows = math.ceil(h / TILE)
    os.makedirs(a.sortie, exist_ok=True)
    total = 0
    for r in range(rows):
        for c in range(cols):
            t = g8[r * TILE:(r + 1) * TILE, c * TILE:(c + 1) * TILE]
            f = os.path.join(a.sortie, "t_%d_%d.jpg" % (r, c))
            Image.fromarray(t, "L").save(f, "JPEG", quality=a.qualite, optimize=True)
            total += os.path.getsize(f)
        print("\rligne %d / %d" % (r + 1, rows), end="", flush=True)
    print()
    manifest = {"version": 1, "w": int(w), "h": int(h), "tile": TILE, "cols": cols, "rows": rows,
                "ppd": ppd, "lon0": TEX_LON0, "ext": "jpg", "qualite": a.qualite}
    json.dump(manifest, open(os.path.join(a.sortie, "manifest.json"), "w"), indent=1)
    zp = a.sortie.rstrip("/\\") + ".zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for f in sorted(os.listdir(a.sortie)):
            z.write(os.path.join(a.sortie, f), os.path.join(os.path.basename(a.sortie.rstrip("/\\")), f))
    print("%d tuiles, %.1f Mo au total. Archive à envoyer : %s" % (rows * cols, total / 1e6, zp))

if __name__ == "__main__":
    main()
