# Saut de blocs : phases B1 (diagnostic) et B2 (variantes), 16 novembre 2026

Référence : la borne régionale (déjà intégrée). Critère : lumière de chaque point strictement identique ; gain de temps d'au moins 8 % en moyenne sans cas plus lent de plus de 2 % (phase B4).

## B1, diagnostic
- Sur neuf cas représentatifs, 53 à 85 % des tests de saut échouent (pôles : 72 à 85 %) : la plupart des tests sont perdus.
- Les variantes écrites avec une fonction de test appelée à chaque point étaient plus lentes que la borne régionale seule (de −4 % à +116 %) bien qu'elles évitent jusqu'à 80 % des relevés : le coût venait de l'appel de fonction (les nombres décimaux passés en paramètres sont recréés à chaque appel) et, dans la première généralisation, de tableaux alloués pour chaque point. Une régression sur ces mesures n'est pas exploitable (surcoût par point dominant).
- Correction : tests écrits en ligne, avec des variables locales, sans appel de fonction ni tableau par point.

## B2, variantes (toutes exactes : classe A et 0 point de lumière différent sur les vues testées)
| Variante | Principe |
|---|---|
| blk1 | un niveau de blocs de 32 km, retest espacé d'un quart de bloc après un échec |
| blk2 | blocs de 32 km puis de 8 km |
| v1a, v1b, v1c | blk2 seulement au-delà de 20, 40 ou 80 km de portée |
| v2 | blk2, un test à l'entrée de chaque bloc |
| v3 | blk2, retrait exponentiel après échecs répétés |
| v4 | niveau de 128 km pour les rayons de plus de 100 km, mode bloc, retrait exponentiel, à partir de 20 km |
| v5 | blk2 en mode bloc avec retrait exponentiel |

## Premières mesures (version en ligne, 2 vues, médiane de 4 répétitions alternées, borne régionale = 100)
| Vue | blk1 | blk2 | v2 | v3 | v5 | v4 |
|---|---|---|---|---|---|---|
| Mare Imbrium ×10 | 89 | 82 | 96 | 93 | 120 | 113 |
| Mons Mouton ×30 (pôle sud) | 84 | 77 | 93 | 93 | 111 | 98 |

Meilleure variante provisoire : blk2 (−18 à −23 % par rapport à la borne régionale), exacte. À confirmer en B3 (identité sur 60 cas) et B4 (temps sur 43 cas).

## B3, B4 et conclusion (16 novembre 2026)

**B3, identité** : 55 cas mémorisés (32 régions, 30 dates, tous les zooms), 322 évaluations (161 par variante : passage complet, orientation variée, rendu de repos) : blk1 et blk2 en classe A partout, 0 point de lumière différent, écart d'image maximal 0. Les variantes sont donc exactes, comme prévu par construction.

**B4, temps (médiane de 4 répétitions alternées, par rapport à la borne régionale seule)** :

| Série | Variante | Passage complet : moyenne [meilleur ; pire] | Cas plus lents de plus de 2 % |
|---|---|---|---|
| 9 cas (arrêt anticipé) | blk1 | +6 % [-15 ; +19] | 6 sur 9 |
| 9 cas (arrêt anticipé) | blk2 | +3 % [-26 ; +31] | 6 sur 9 |
| 11 cas du premier jeu | blk2 | +6 % [-18 ; +27] | 8 sur 11 |
| 11 cas du premier jeu | v6 | +8 % [-3 ; +23] | 9 sur 11 |
| 11 cas du premier jeu | v7 | +5 % [-2 ; +16] | 6 sur 11 |
| 11 cas du premier jeu | v8 | +4 % [-2 ; +11] | 7 sur 11 |

Au rendu de repos (9 cas) : blk1 +1 % en moyenne, blk2 +1 %.

Les variantes limitées aux rayons longs (v6, v7, v8 : saut de blocs seulement si la portée de la borne régionale dépasse 60 ou 100 km) perdent les gains de blk2 (Mare Imbrium ×10 : de −17 % à +4 / +11 %) sans en créer ailleurs.

**Conclusion** : critère fixé (gain moyen d'au moins 8 % et aucun cas plus lent de plus de 2 %) non atteint par aucune variante : blk2 gagne dans trois cas (Clavius −9 à −18 %, Mare Imbrium ×10 −17 à −26 %, Mare Fecunditatis ×10 −14 %) mais perd de 2 à 31 % dans la plupart des autres, en particulier aux pôles, près du terminateur et sur les vues larges. Les tests de saut échouent dans 53 à 85 % des cas : le travail évité (relevés de relief, peu coûteux) est trop proche du coût des tests. **Arrêt anticipé : la borne régionale seule est conservée** ; le saut de blocs n'est pas intégré. Résultats et banc conservés dans `etude-ombres/` si une nouvelle idée de test moins coûteux apparaît.