#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""
Fabrication du relief fin de l'Assistant d'observation (version installee) a partir de la carte de deplacement LOLA a 64 points par degre
du CGI Moon Kit de la NASA : ldem_64_uint.tif (23 040 x 11 520 points, entiers 16 bits non signes, unite = demi-metre,
altitude en metres = (valeur - 20 000) / 2, par rapport a la sphere de 1 737,4 km).

Principe : on garde la face visible (longitudes -100 a +100 degres), on ramene les 64 points par degre a 32 par moyenne de 2 x 2 points
(ce qui reduit le bruit et les traces du satellite), on conserve une precision de 1 m (au lieu de 5 m), et on ecrit le fichier
relief-fin.bin.gz (format LDE3 : comme LDE2, avec un compteur de valeurs speciales sur 32 bits). Le programme mesure aussi le trait de
relief signale pres du Mare Nectaris (34,4 degres E, de 13,1 a 19,9 degres S) pour dire s'il subsiste.

Usage : python fabrique_relief_lune.py ldem_64_uint.tif
        python fabrique_relief_lune.py --essai          (essai sans carte NASA : relief fabrique de toutes pieces)
"""
import argparse, gzip, os, struct, sys, zipfile
import numpy as np

LON0 = -100          # longitude du bord gauche du relief fin (degres)
PPD_OUT = 32         # points par degre du relief fin
UNITE = 1            # precision de l'altitude (metres)
TRAIT = dict(lon=34.44, lat0=-13.12, lat1=-19.88)   # trait de reference (trace de LRO) : longitude, latitudes de debut et de fin

def lire_carte(chemin):
    try:
        import tifffile
    except ImportError:
        sys.exit("Il manque le module tifffile : pip install numpy tifffile")
    print("Ouverture de", chemin)
    try:
        a = tifffile.memmap(chemin)       # fichier non compresse : lecture par morceaux, peu de memoire
    except Exception:
        print("Lecture complete du fichier (une demi-minute, 1 Go de memoire)")
        a = tifffile.imread(chemin)
    if a.ndim != 2 or a.dtype != np.uint16:
        sys.exit("Fichier inattendu : il faut ldem_64_uint.tif (entiers 16 bits non signes, une seule bande). Forme %s, type %s" % (a.shape, a.dtype))
    return a

def reduire(a):
    """Face visible, 64 -> 32 points par degre (moyenne de 2 x 2), en metres (flottants)."""
    H, W = a.shape
    ppd = W / 360.0
    if abs(ppd - 64) > 0.5:
        print("Attention : %.1f points par degre au lieu de 64 ; le programme continue." % ppd)
    f = ppd / PPD_OUT
    if abs(f - round(f)) > 1e-6 or f < 1:
        sys.exit("Le rapport entre la resolution de la carte et 32 points par degre doit etre un entier (carte a 64 : 2).")
    f = int(round(f))
    x0 = int(round((LON0 + 180) * ppd)); x1 = x0 + int(round(200 * ppd))
    hout = (H // f); wout = (x1 - x0) // f
    out = np.empty((hout, wout), np.float32)
    pas = 512 * f
    for y in range(0, hout * f, pas):
        bloc = np.asarray(a[y:y + pas, x0:x1], dtype=np.float32)
        bloc = (bloc - 20000.0) * 0.5                        # metres
        h = bloc.shape[0] // f
        bloc = bloc[:h * f].reshape(h, f, wout, f).mean(axis=(1, 3))
        out[y // f:y // f + h] = bloc
        print("\rlignes %d / %d" % (y // f + h, hout), end="", flush=True)
    print()
    return out

def essai():
    """Relief de toutes pieces : mer lisse, cratere, trait incline de 2,8 degres (comme celui du Mare Nectaris)."""
    H, W = 5760, 6400
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    h = 40 * np.sin(xx / 900.0) + 30 * np.cos(yy / 700.0)
    r = np.hypot(xx - 3200, yy - 2900); h += np.where(r < 120, -800 * (1 - (r / 120) ** 2) + 600 * np.exp(-((r - 120) / 12) ** 2), 0)
    return h.astype(np.float32)

def encoder(v, chemin):
    """Format LDE3 : en-tete de 18 octets, un octet par point (ecart a la valeur predite gauche + haut - haut-gauche, en pas d'altitude ; 127 annonce une valeur lue dans la liste de 16 bits qui suit)."""
    h, w = v.shape
    p = np.zeros((h + 1, w + 1), np.int64); p[1:, 1:] = v
    r2 = p[1:, 1:] - p[1:, :-1] - p[:-1, 1:] + p[:-1, :-1]
    r = (r2 // UNITE).ravel()
    gros = np.abs(r) >= 127
    main = np.where(gros, 127, r).astype(np.int8); esc = r[gros].astype(np.int16)
    en_tete = b'LDE3' + struct.pack('<HHHhHI', w, h, PPD_OUT, LON0, UNITE * 10, len(esc))
    with gzip.GzipFile(chemin, 'wb', compresslevel=9) as f:
        f.write(en_tete + main.tobytes() + esc.tobytes())
    return len(esc)

def mesurer_trait(v):
    """Ecart moyen (en metres) du trait de reference aux colonnes voisines, le long de sa trace inclinee de 2,8 degres, et meme mesure sur une trace-temoin
    decalee de 40 points vers l'ouest : si la premiere est nettement plus grande que la seconde, le trait subsiste."""
    y0 = int((90 - TRAIT['lat0']) * PPD_OUT); y1 = int((90 - TRAIT['lat1']) * PPD_OUT)
    def mesure(decal):
        ec = []
        for y in range(y0, y1):
            x = int(round(4297 + 0.0493 * (y - 3300))) + decal   # trace relevee dans l'ancien relief (colonnes 4297 a 4307, lignes 3300 a 3516)
            if x < 6 or x > v.shape[1] - 7: continue
            voisines = np.concatenate([v[y, x - 6:x - 3], v[y, x + 4:x + 7]]).mean()
            ec.append(np.abs(v[y, x - 1:x + 2] - voisines).max())
        return float(np.mean(ec)), len(ec)
    (t, n), (c, _) = mesure(0), mesure(-40)
    return t, c, n

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("carte", nargs="?"); ap.add_argument("--essai", action="store_true"); ap.add_argument("--sortie", default="relief-lune")
    a = ap.parse_args()
    if a.essai: v = essai()
    else:
        if not a.carte: sys.exit("Indiquez la carte : python fabrique_relief_lune.py ldem_64_uint.tif")
        v = reduire(lire_carte(a.carte))
    v = np.rint(v / UNITE).astype(np.int64) * UNITE
    os.makedirs(a.sortie, exist_ok=True)
    chemin = os.path.join(a.sortie, "relief-fin.bin.gz")
    n = encoder(v, chemin)
    ecart, temoin, nb = mesurer_trait(v) if not a.essai else (0.0, 0.0, 0)
    taille = os.path.getsize(chemin) / 1e6
    texte = ("Relief fin : %d x %d points (32 par degre, face visible), precision %d m\nValeurs speciales : %d ; fichier : %.1f Mo\nAltitude : minimum %d m, maximum %d m\n"
             % (v.shape[1], v.shape[0], UNITE, n, taille, v.min(), v.max()))
    if not a.essai: texte += "Trait de reference (Mare Nectaris, 34,4 degres E) : ecart moyen aux colonnes voisines %.1f m, trace-temoin voisine %.1f m, sur %d lignes (un trait present donne un ecart nettement plus grand que le temoin)\n" % (ecart, temoin, nb)
    open(os.path.join(a.sortie, "rapport.txt"), "w", encoding="utf-8").write(texte); print(texte)
    zp = a.sortie.rstrip("/\\") + ".zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for f in ("relief-fin.bin.gz", "rapport.txt"): z.write(os.path.join(a.sortie, f), os.path.join(os.path.basename(a.sortie.rstrip("/\\")), f))
    print("Archive a envoyer :", zp)

if __name__ == "__main__":
    main()
