# Étude du calcul des ombres de la Lune (16 au 20 novembre 2026)

Archive d'une expérience menée sur la version de travail de la 0.96, qui compare des variantes du calcul des ombres de la carte de la Lune au calcul de référence, dans une copie de test (l'application n'était pas modifiée).

## À retenir
- **Borne régionale** : exacte (aucun point de lumière différent sur environ 640 évaluations dans deux jeux de cas : passage complet, rendu de repos, orientations, pôles, relief de base), gain de temps de 11 % à 32 %, jamais négatif sur 31 cas. **Intégrée à la version 0.96** (carte des maxima construite dans les Workers du relief, réglage `window.RAY_REGIONAL`).
- **Saut de blocs** : exact aussi, mais gain de temps irrégulier, plus lent en moyenne dans les mesures finales : abandonné (voir `rapport.md` et `blocs-B1-B2.md`).

## Contenu
- `rapport.md` et `blocs-B1-B2.md` : méthode, tableaux, conclusions.
- `donnees/` : données d'entrée (dates, régions : `dates.json`, `dates2.json`, `pool2.json`, `dates_lune.js`, `cas-500.json`, `essai-banc.jsonl`) et résultats bruts (`resultats.json`, `resultats2.json`, `resultats_B1.json`, `resultats_B3.json`, `resultats_B4.json`, `resultats_B4b.json`). Les séries partielles citées dans `rapport.md` sous d'autres noms (`resultats_rest.json` et suivants) ne figurent pas dans ce dossier ; en cas de doute, les rapports font foi.
- `banc/` : les scripts du banc, de plusieurs générations d'essais (leur rôle est décrit en tête de chaque fichier) : `fabrique_banc.py`, `banc_run.py`, `patch_ombres_test.py`, `ombres_lib.py`, `run_ombres.py`.

## Limites : ces scripts ne sont pas relançables tels quels
Ils lisent des chemins de l'environnement d'origine (`/home/claude`, `/mnt/user-data`), dépendent d'une aide de test qui n'est pas dans le dépôt (lancer un serveur local) et surtout modifient une copie de la page en cherchant des morceaux de code précis de la 0.96 : depuis, ce code a changé. Ils sont conservés pour documenter la méthode et les résultats, pas pour être rejoués.
