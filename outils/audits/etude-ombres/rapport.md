# Étude du calcul des ombres de la Lune : borne régionale et saut de blocs

16 novembre 2026. Variantes comparées à la référence (calcul actuel) dans une copie de test ; l'application n'est pas modifiée. Critère : lumière de chaque point strictement identique (classe A : aucun point ne change de plus de 1 niveau).

## Preuves d'identité

| Série | Cas | Variantes évaluées | Points de lumière différents | Écart d'image maximal | Classes |
|---|---|---|---|---|---|
| Passage complet (matrice réduite) | 102 | 306 | 0 | 0 | A : 306 |
| Rendu de repos (1 079 points) | 23 | 69 | 0 | 0 | A : 69 |
| Orientations (37°, miroir, 213° + miroir) | 14 | 126 | 0 | 0 | A : 126 |
| Relief de base seul (16 points par degré) | 17 | 51 | 0 | 0 | A : 51 |
| Pôle nord (lat > 80°) | 24 | 72 | 0 | 0 | A : 72 |

Total : 180 cas, 624 évaluations de variantes, **0 point de lumière différent, 0 classe B ou C**.

Contrôle négatif (rayon supprimé au-dessus de 40° de hauteur du Soleil) : classé C dans 33 des 102 cas du passage complet (jusqu'à 56 niveaux d'écart, 10 095 points de lumière différents), donc le banc détecte bien un changement.

## Gain mesuré (relevés des rayons, indépendant de la machine), moyenne des 102 cas

| Variante | Gain moyen | Minimum | Maximum |
|---|---|---|---|
| Borne régionale | 43.1 % | 14 % | 72 % |
| + blocs de 32 km | 56.7 % | 38 % | 83 % |
| + blocs de 32 et 8 km | 72.1 % | 47 % | 93 % |

Au pôle nord (Soleil à moins de 5° d'élévation) : borne régionale de 0 à 36 %, blocs de 3 à 46 %.

## Gain de temps réel (médiane de 4 répétitions alternées au passage complet, 3 au rendu de repos), 11 cas

| Cas | Réf. complet (ms) | Borne | Blocs 1 | Blocs 2 | Réf. repos (ms) | Borne | Blocs 1 | Blocs 2 |
|---|---|---|---|---|---|---|---|---|
| disque entier x1 x1 (phase 160°) | 318 | -30 % | -27 % | -31 % | | | | |
| Cabeus x10 x10 (phase 160°) | 292 | -11 % | -11 % | -4 % | 1161 | -12 % | -11 % | -4 % |
| Mare Imbrium x30 x20 (phase 180°) | 379 | -29 % | -25 % | -22 % | 1231 | -27 % | -30 % | -29 % |
| Mons Mouton x30 x20 (phase 180°) | 474 | -14 % | -4 % | +7 % | 1346 | -5 % | -3 % | +6 % |
| Clavius x30 x20 (phase 200°) | 514 | -19 % | -26 % | -36 % | 1631 | -19 % | -27 % | -35 % |
| Grimaldi xmax x20 (phase 235°) | 250 | -15 % | -4 % | -1 % | 772 | -9 % | -5 % | -5 % |
| Mare Imbrium x10 x10 (phase 270°) | 454 | -32 % | -44 % | -49 % | 1885 | -30 % | -40 % | -44 % |
| Sylvester x10 x10 (phase 305°) | 142 | -15 % | -7 % | +11 % | 638 | -12 % | -3 % | +5 % |
| Langrenus x3 x3 (phase 90°) | 180 | -27 % | -20 % | -27 % | 598 | -19 % | -10 % | -10 % |
| Tycho x30 x20 (libration est maximale) | 842 | -25 % | -18 % | -22 % | 2616 | -26 % | -29 % | -29 % |
| Mare Fecunditatis x10 x10 (phase 55°) | 442 | -31 % | -38 % | -48 % | 2052 | -34 % | -37 % | -44 % |

Moyenne [meilleur, pire] : passage complet : borne -23 % [-32 ; -11], blocs 1 -21 % [-44 ; -4], blocs 2 -20 % [-49 ; 11] ; rendu de repos : borne -19 % [-34 ; -5], blocs 1 -20 % [-40 ; -3], blocs 2 -19 % [-44 ; 6].

## Coût des cartes de maxima (une fois par relief)

Relief de base (3 200 × 2 880) : environ 170 ms ; relief fin (6 400 × 5 760) : environ 400 à 480 ms ; 2,5 Mo de tableaux (carte régionale et deux niveaux de blocs). Dans l'application, la construction irait dans le Worker du relief : aucun coût sur le fil principal.

## Conclusion

- La borne régionale est exacte (0 écart dans toute la matrice), robuste (gain de temps de 11 % à 32 %, jamais négatif) et simple.
- Le saut de blocs est exact aussi, mais le gain de temps supplémentaire est irrégulier : meilleur en moyenne latitude (Mare Imbrium ×10 : 44 à 49 % contre 32 %), nul ou négatif aux pôles et près du terminateur (jusqu'à +11 % de temps), car les tests de saut coûtent autant que les relevés évités. À optimiser avant de l'intégrer, ou à écarter.
- Recommandation : intégrer la borne régionale seule ; garder le saut de blocs comme piste d'optimisation séparée.

Fichiers : `dates.json`, `resultats.json` (102 cas), `resultats_rest.json`, `resultats_orient.json`, `resultats_base.json`, `resultats_nord.json`, `resultats_temps.json`, code du banc dans `banc/`.

## Second jeu de tests et intégration de la borne régionale (16 novembre 2026)

**Second jeu** (dates de la lunaison suivante, 41 régions jamais utilisées, tous les zooms, trois évaluations par cas : passage complet, orientation variée, rendu de repos, thème jour) : 148 cas, 432 évaluations de la borne régionale, **0 point de lumière différent, 0 classe B ou C**, écart d'image maximal 0, SSIM minimal 1. Contrôle négatif détecté dans 17 des 37 cas où il a été essayé. Gain de relevés : 47 % en moyenne (14 à 68 %) ; pôles 23 %, bords 55 %, mers 52 %, plateaux 44 %.

**Cumul des deux jeux** : environ 640 évaluations de la borne régionale, aucun écart.

**Temps réels (variantes alternées, médiane)** : second jeu, 20 cas : passage complet -25 % en moyenne (-36 à -5 %), rendu de repos -24 % (-38 à -2 %) ; premier jeu : -23 % et -19 %. Sur les 31 cas des deux jeux, aucun gain négatif ; les plus faibles sont au pôle sud et dans les hauts plateaux du sud (−2 à −7 %).

**Intégration** (modèle de page) : la carte du relief maximal (blocs de 32 km, maximum à moins de 320 km, fenêtre élargie en longitude selon la latitude, 189 × 170 blocs pour le relief fin) est construite dans les Workers du relief de base et du relief fin (`regMaxMap`) ; le lancer de rayon utilise cette borne plus 250 m de marge à la place du relief maximal global de 10,7 km ; sans carte (repli sans Worker), la borne globale actuelle s'applique : même résultat. Réglage : `window.RAY_REGIONAL = 0` désactive la borne. Dans l'application intégrée : Mare Imbrium ×10 : −28 % (complet) et −32 % (repos) ; Clavius ×20 : −12 % et −17 %. Tests : `test_borne_regionale.py` 24/24 (8 cas : image identique avec la borne régionale et avec la borne globale, point par point ; carte construite par le Worker) ; `test_decodage_worker.py` 16/16 ; `test_rendu_repos.py` 7/7 ; test hors ligne de bout en bout 11/11 ; démarrage aux cinq formats ; tables et 12 vues identiques ; page en ligne : carte construite pour le relief de base, aucune erreur.

**Saut de blocs** : mis de côté pour un second temps (gain de temps irrégulier, voir ci-dessus).
