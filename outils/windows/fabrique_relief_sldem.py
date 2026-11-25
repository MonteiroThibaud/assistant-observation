#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
"""
Relief fin de l'Assistant d'observation a partir de SLDEM2015 (LOLA + camera SELENE de Kaguya, entre 60 degres N et 60 degres S)
et de la carte de deplacement LOLA a 64 points par degre (au-dela de 60 degres).

Entrees : SLDEM2015_128_60S_60N_000_360_FLOAT.IMG  (flottants 32 bits, 46 080 x 15 360 points, longitudes 0 a 360 degres vers l'est,
                                                  latitudes de 60 N a 60 S ; environ 2,8 Go)
          ldem_64_uint.tif                          (carte LOLA du CGI Moon Kit, deja utilisee par fabrique_relief_lune.py)
Sortie  : dossier relief-sldem (relief-fin.bin.gz au format LDE3, rapport.txt) et archive relief-sldem.zip.

Principe : SLDEM2015 est ramene de 128 a 32 points par degre par moyenne de 4 x 4 points, sur la face visible (-100 a +100 degres) ;
entre 58 et 60 degres de latitude (nord et sud) on se raccorde progressivement au relief LOLA, qui seul couvre les poles.
Le programme detecte tout seul l'ordre des octets et l'unite (metres, kilometres ou rayon en kilometres), mesure le decalage
avec le relief LOLA et le trait du Mare Nectaris, et ecrit tout cela dans rapport.txt.
"""
import argparse, math, os, sys, zipfile
import numpy as np
# Python portable (mode « embarque ») n'ajoute pas le dossier du programme au chemin des modules : on l'ajoute
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fabrique_relief_lune as L

BLEND = 64            # hauteur du raccord en lignes a 32 points par degre (2 degres)

def ouvrir_sldem(chemin):
    taille = os.path.getsize(chemin)
    n = taille // 4
    ppd = int(round(math.sqrt(n / 43200.0)))
    W, H = 360 * ppd, 120 * ppd
    if W * H * 4 != taille:
        sys.exit("Taille inattendue de %s : %d octets (attendu : 46 080 x 15 360 x 4 = 2 831 155 200)." % (chemin, taille))
    meilleur = None
    for dt in ('<f4', '>f4'):
        a = np.memmap(chemin, dtype=dt, mode='r', shape=(H, W))
        ech = np.asarray(a[H // 2::max(H // 41, 1), ::101], dtype=np.float64).ravel()
        fin = np.isfinite(ech) & (np.abs(ech) < 1e5)
        score = fin.mean() * (1.0 if ech[fin].std() > 0.5 else 0.0) if fin.any() else 0.0
        if meilleur is None or score > meilleur[0]: meilleur = (score, dt, a, ech[fin])
    score, dt, a, ech = meilleur
    med = float(np.median(np.abs(ech)))
    sd = float(np.std(ech))
    if 1700 < med < 1780 and sd < 20: unite, f = "rayon en km", (lambda x: (x - 1737.4) * 1000.0)
    elif med < 25:        unite, f = "km",          (lambda x: x * 1000.0)
    else:                 unite, f = "m",           (lambda x: x)
    info = "ordre des octets %s, unite detectee : %s (valeur typique %.1f), %d x %d points (%d par degre)" % (dt, unite, med, W, H, ppd)
    print(info)
    return a, ppd, f, info

def reduire_sldem(a, ppd, conv):
    """Face visible (lon -100..100), latitudes 60 N..60 S, 4 x 4 -> 32 points par degre, en metres ; NaN la ou il manque des donnees."""
    f = ppd // 32
    H, W = a.shape
    gauche = int(round(260 * ppd)); droite = int(round(100 * ppd))
    hout = H // f; wout = (W - gauche + droite) // f
    out = np.full((hout, wout), np.nan, np.float32)
    pas = 256 * f
    for y in range(0, hout * f, pas):
        bloc = np.concatenate([np.asarray(a[y:y + pas, gauche:], dtype=np.float32), np.asarray(a[y:y + pas, :droite], dtype=np.float32)], axis=1)
        bloc = conv(bloc.astype(np.float64)).astype(np.float32)
        bloc[~np.isfinite(bloc) | (np.abs(bloc) > 2e4)] = np.nan
        h = bloc.shape[0] // f
        r = bloc[:h * f].reshape(h, f, wout, f)
        ok = np.isfinite(r); s = np.where(ok, r, 0).sum(axis=(1, 3)); n = ok.sum(axis=(1, 3))
        out[y // f:y // f + h] = np.where(n >= (f * f) // 2, s / np.maximum(n, 1), np.nan)
        print("\rSLDEM : lignes %d / %d" % (y // f + h, hout), end="", flush=True)
    print()
    return out

def decalage(S, B, y0):
    """Decalage moyen (en points a 32 par degre) entre SLDEM et le relief LOLA, par correlation des reliefs (passe-haut) sur quelques fenetres."""
    def hp(a):
        k = 6; c = np.cumsum(np.cumsum(np.pad(a, k, mode='edge'), 0), 1)
        m = (c[2*k:, 2*k:] - c[:-2*k, 2*k:] - c[2*k:, :-2*k] + c[:-2*k, :-2*k]) / (2*k) ** 2
        return a - m[:a.shape[0], :a.shape[1]]
    res = []
    rng = np.random.default_rng(5)
    for _ in range(40):
        yy = int(rng.integers(150, S.shape[0] - 250)); xx = int(rng.integers(100, S.shape[1] - 300)); w = 160
        s = S[yy:yy + w, xx:xx + w]; b = B[y0 + yy:y0 + yy + w, xx:xx + w]
        if not (np.isfinite(s).all() and b.std() > 20): continue
        s = hp(s); b = hp(b); best = (-2, 0, 0)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                A = s[6:-6, 6:-6]; Bb = b[6 + dy:b.shape[0] - 6 + dy, 6 + dx:b.shape[1] - 6 + dx]
                c = np.corrcoef(A.ravel(), Bb.ravel())[0, 1]
                if c > best[0]: best = (c, dy, dx)
        if best[0] > 0.6: res.append(best[1:])
    if not res: return None
    r = np.array(res, float); return float(np.median(r[:, 0])), float(np.median(r[:, 1])), len(res)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("sldem"); ap.add_argument("ldem64"); ap.add_argument("--sortie", default="relief-sldem")
    a = ap.parse_args()
    print("1/4 Relief LOLA a 64 points par degre"); B = L.reduire(L.lire_carte(a.ldem64))
    print("2/4 SLDEM2015"); s_mm, ppd, conv, info = ouvrir_sldem(a.sldem); S = reduire_sldem(s_mm, ppd, conv)
    y0 = int((90 - 60) * 32)                       # ligne de 60 N dans le relief complet
    print("3/4 Raccord et controles")
    dec = decalage(S, B, y0)
    out = B.copy(); hS = S.shape[0]
    w = np.ones(hS, np.float32); r = np.arange(BLEND, dtype=np.float32) / BLEND; w[:BLEND] = r; w[-BLEND:] = r[::-1]
    zone = out[y0:y0 + hS]; bon = np.isfinite(S)
    zone[:] = np.where(bon, w[:, None] * S + (1 - w[:, None]) * zone, zone)
    pris = bon.mean() * 100
    v = np.rint(out / L.UNITE).astype(np.int64) * L.UNITE
    os.makedirs(a.sortie, exist_ok=True); chemin = os.path.join(a.sortie, "relief-fin.bin.gz")
    print("4/4 Ecriture"); n = L.encoder(v, chemin)
    t, c, nb = L.mesurer_trait(v); taille = os.path.getsize(chemin) / 1e6
    texte = ("Relief fin SLDEM2015 + LOLA : %d x %d points (32 par degre), precision %d m, fichier %.1f Mo, %d valeurs speciales\nSLDEM2015 : %s ; points utilisables : %.1f %% ; raccord sur %d lignes\n"
             % (v.shape[1], v.shape[0], L.UNITE, taille, n, info, pris, BLEND))
    texte += ("Decalage SLDEM2015 - LOLA (mediane de %d fenetres) : vertical %+.1f, horizontal %+.1f point(s) de 0,95 km\n" % (dec[2], dec[0], dec[1])) if dec else "Decalage SLDEM2015 - LOLA : non mesure\n"
    texte += "Trait de reference (Mare Nectaris, 34,4 degres E) : ecart moyen aux colonnes voisines %.1f m, trace-temoin voisine %.1f m, sur %d lignes (relief LOLA a 64 points par degre : 29,3 m et 18,6 m)\n" % (t, c, nb)
    open(os.path.join(a.sortie, "rapport.txt"), "w", encoding="utf-8").write(texte); print(texte)
    zp = a.sortie.rstrip("/\\") + ".zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for f in ("relief-fin.bin.gz", "rapport.txt"): z.write(os.path.join(a.sortie, f), os.path.join(os.path.basename(a.sortie.rstrip("/\\")), f))
    print("Archive a envoyer :", zp)

if __name__ == "__main__":
    main()
