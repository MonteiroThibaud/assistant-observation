# Assistant d'observation — Audit de performance et de mémoire (version 0.95)

16 novembre 2026. Mesures faites dans un navigateur Chromium de test (machine d'essai, écran simulé 411 × 850, densité 2,625, sans ralentissement du processeur, profileur du navigateur actif : les durées sont gonflées par rapport à un usage normal). **Aucune mesure sur le S25** : les ordres de grandeur sont à confirmer sur le téléphone. Aucune modification de l'application n'a été faite : ce document propose, avec les gains mesurés ou estimés et le risque pour la qualité.

## 1. Ce qui a été mesuré

### Démarrage (page installée)
- Temps jusqu'à l'affichage des six onglets : 6,2 à 6,7 s ; tâche longue du fil principal d'environ 4,6 s dès le début, puis cinq tâches de 55 à 430 ms.
- Profil du fil principal (10,7 s échantillonnées, dont 37 % d'attente) : ramasse-miettes 12 % ; bibliothèque d'astronomie (fonctions `ma`, `Cb`, `Aa` et `$jscomp.makeIterator`) environ 14 % ; décodage des images de la carte et du relief (`im.onload`) 6,8 % ; formatage de l'heure `fmt` 2,7 % et des nombres `num` 1,1 %.
- Tas JavaScript : **4,7 Mo seulement**. Toute la mémoire est donc dans des tableaux typés, des images et des tampons du navigateur.
- Mémoire des processus de rendu : 80 Mo avant la page → **490 Mo à 6 s** (pic de 600 à 620 Mo pendant le décodage). Sans le relief fin : 412 Mo (pic 598 Mo) : **le relief fin ajoute 78 Mo**, ce qui correspond à ses 36,9 millions de points en 16 bits (74 Mo).
- Données décodées en mémoire (calcul) : carte de base 4 552 × 4 096 points en 8 bits = 18,6 Mo ; relief de base 3 200 × 2 880 en 16 bits = 18,4 Mo ; relief fin 6 400 × 5 760 en 16 bits = 73,7 Mo ; total 111 Mo. Le reste (environ 300 Mo) est le navigateur (images décodées, couches d'affichage à la densité 2,625) : non décomposé.

### Carte de la Lune à ×30 (un cycle : passage rapide, passage complet, rendu de repos)
- Mémoire : 458 → 520 Mo avec la vue à ×30 ; 513 Mo après un nouveau rendu.
- Fonctions du fil principal (hors attente), en ms sur le cycle : flou des ombres `blurL` 599 ; calcul par point `row` 432 ; interpolation bicubique des tuiles `hiSampleBic` 292 ; lecture du relief `hAt` 107 ; ramasse-miettes 75 ; pente `gradC` 28. **`blurL` est la première fonction (environ 40 % du calcul).**
- Part des points où le flou s'applique réellement (poids non nul) : 37 % à Al-Bakri (terminateur), 75 % à Rima Ariadaeus (longues ombres).
- Mémoire transitoire d'un passage à 1 079 points : neuf tableaux de 4,7 Mo (tableaux du flou et des ombres), soit environ 42 Mo recréés à chaque passage.

### Micro-mesures
- `toLocaleTimeString('fr-FR', {hour, minute})` : 55 µs par appel ; avec un `Intl.DateTimeFormat` créé une fois : 0,75 µs (**×73**), résultats identiques sur 20 000 dates. Même constat pour `toLocaleString` des nombres : 13 µs → 0,45 µs (**×30**), résultats identiques sur 20 000 nombres.
- Il y a 45 appels de `fmt(` et 26 `toLocale…String` dans le code.

## 2. Pistes classées (gain, risque pour la qualité, preuve)

| N° | Piste | Gain attendu | Risque pour la qualité | Preuve à faire |
|---|---|---|---|---|
| 1 | **Mettre en cache les formateurs d'heure et de nombres** (`fmt`, `num` et les `toLocale…String` répétés) | Démarrage : environ 0,4 s de fil principal gagnés dans le profil (à confirmer sur S25) ; toutes les listes de lever et coucher plus rapides | Nul pour les valeurs : sorties identiques mesurées ; seul cas limite : changement de fuseau horaire pendant que l'application est ouverte (créer le formateur à la première utilisation de chaque session) | 13 tables, 12 vues, tests existants |
| 2 | **Moon : ne flouter que les points à poids non nul** et réutiliser les tableaux du flou d'un passage à l'autre | `blurL` : de 1,3 fois (Rima) à 2,7 fois (Al-Bakri) plus rapide ; mémoire transitoire de 42 Mo à peu près supprimée, moins de ramasse-miettes | Nul : image identique pixel pour pixel (le poids est nul hors des zones concernées) | comparer les images avant et après sur les deux régions de référence ; temps de calcul |
| 3 | **Moon : chemin rapide de l'interpolation bicubique** quand les 16 points sont dans la même tuile (une recherche de tuile au lieu de 16) | `hiSampleBic` environ 2 fois plus rapide (environ 150 ms sur le cycle) | Nul : mêmes valeurs | images identiques |
| 4 | **Charger le relief fin plus tard** (au premier affichage de la Lune ou de l'oculaire, ou en temps libre quelques secondes après le démarrage) | Démarrage : environ 78 Mo et la boucle de décodage (environ 0,3 s de calcul) évités tant qu'on ne les utilise pas ; pic de mémoire plus bas | Nul si chargé avant le premier usage ; sinon un court état « chargement » à la première ouverture de la Lune | tests de la Lune ; état « Relief fin : activé » |
| 5 | **Bibliothèque d'astronomie : boucles natives** à la place des boucles transpilées avec `$jscomp.makeIterator` (version ES2015 de la bibliothèque, ou réécriture des 3 fonctions de séries) | environ 1 s de fil principal au démarrage dans le profil (14 %) ; à confirmer en cherchant d'abord quel appel au démarrage les sollicite | Faible mais réel : c'est du calcul de positions ; à prouver par les empreintes des tables et par la comparaison des positions de toutes les planètes à 1e-12 près | empreintes des tables, tests ISS et planètes, comparaison numérique |
| 6 | Calculs au démarrage à différer : repérer les appels de la bibliothèque (planètes, événements, rapport de nuit) que l'on peut faire quand l'onglet s'affiche | à chiffrer après repérage (ordre de 1 s) | Nul pour les valeurs ; changement de moment du calcul | tests des onglets |

## 3. Essai sans gain (résultat négatif)
- **Lecture par bandes de 64 lignes de la carte de base et du relief de base** (au lieu d'une copie complète de l'image en RVBA) : les tableaux obtenus sont **identiques** (empreintes égales), mais la mémoire n'a pas baissé : pic 608 à 664 Mo contre 604 à 618 Mo, état stable 562 à 565 Mo contre 489 à 492 Mo. Le navigateur décode l'image en entier de toute façon ; piste abandonnée.

## 4. Ce qui n'a pas été fait ou mesuré
- Aucune mesure sur le S25 (durées, mémoire Android, batterie).
- Pas de décomposition de la mémoire du navigateur (images décodées, couches d'affichage).
- Pas de profil du service worker, de l'onglet ciel profond ni des recherches de transits de l'ISS.
- Aucun changement appliqué à l'application ; la version reste 0.95.

## 5. Ordre de mise en œuvre conseillé
1 (simple, sans risque) puis 2 et 3 (rendu de la Lune, images identiques) puis 4 (mémoire au démarrage) ; 5 et 6 seulement après avoir repéré qui appelle la bibliothèque au démarrage, avec comparaison numérique complète.

## 6. Application des pistes (16 novembre 2026, non livrée : la version reste 0.95)

| Piste | Décision | Résultat mesuré |
|---|---|---|
| 1. Formateurs d'heure et de nombres en cache | **Gardée** | `fmt` et `num` disparaissent du profil de démarrage (environ 410 ms avant) ; première tâche longue de 4,59 s à 4,01 s (−13 %), temps de processeur échantillonné 10,7 s → 10,0 s ; sorties identiques |
| 2. Flou limité aux blocs concernés, sans les deux grands tableaux de la passe verticale | **Gardée (gain de vitesse non mesurable)** | image strictement identique (0 point différent sur 1 164 241, heure figée, Al-Bakri et Rima Ariadaeus) ; durée du passage complet +1 à +5 % (bruit de mesure) ; mémoire transitoire moindre (environ 9 Mo de tableaux en moins par passage à 1 079 points) |
| 3. Chemin rapide du bicubique | **Gardée (gain de vitesse non mesurable)** | image identique ; durées inchangées : le moteur de script optimisait déjà les appels |
| 4. Relief fin chargé plus tard | **Retirée** | démarrage plus court d'environ 0,8 s, mais mémoire stable plus haute de 94 Mo (583 Mo contre 489 Mo) : les tampons du décodage s'ajoutent à ceux déjà conservés par le navigateur au lieu de les réutiliser |

Notes de méthode :
- Les comparaisons d'images exigent une heure figée (`clock.set_fixed_time`) : avec l'horloge simulée qui avance, deux rendus de la même version diffèrent de 10 000 points (maximum 5 niveaux) à cause de la position de la Lune.
- La mémoire des processus de rendu varie de ±100 Mo d'une exécution à l'autre sur ce banc (ramasse-miettes et allocateur) : seuls les écarts répétés sont à retenir.
- Contrôles de la version finale : 13 tables identiques ; 12 vues identiques ; démarrage aux cinq formats ; `test_rendu_repos.py` 7/7 (cas « faible grossissement » corrigé : il passait par la carte à ×10 et dépendait de la vitesse de la machine).

## 7. Pistes 5 et 6 (16 novembre 2026, non livrées : la version reste 0.95 ; page en ligne republiée)

**Piste 6 : calculs du démarrage.** Arbre d'appels du profileur : la fonction `render` (tableau de la nuit) coûte 2,4 s cumulées ; `altOf` (altitude d'un astre à un instant : `Equator` puis `Horizon`) en représente 1,1 s ; la bibliothèque d'astronomie 1,3 s. Le rendu est exécuté **trois fois** au démarrage (1 896, 1 215 et 314 ms) avec les mêmes données : 8 670 appels d'altitude pour seulement 2 890 combinaisons (astre, instant, position) : deux tiers sont des répétitions. Mémorisation de `altOf` et `azOf` : résultat strictement identique par construction (la valeur mémorisée est celle du premier calcul) ; rendus du démarrage 3,4 à 3,6 s → 2,1 à 2,2 s en combinaison avec la piste 5 (avec la mémorisation seule, les 2e et 3e rendus passent de 1 215 et 314 ms à environ 400 et 200 ms).

**Piste 5 : bibliothèque d'astronomie.** La version minifiée du paquet (`astronomy.browser.min.js`, identique à celle embarquée) est transpilée en ES5 avec des itérateurs (`$jscomp.makeIterator`, 13 occurrences) dans les boucles des séries. Le même paquet contient le module ES : compilé en ES2020 avec esbuild (boucles natives), il pèse 107,6 Ko au lieu de 116,4 Ko et calcule **3,4 fois plus vite** (charge du démarrage : 440 ms → 130 ms, dans Node, même moteur que Chrome). Quatre variantes essayées (module ES minifié, minifié sans transformation de syntaxe, version navigateur minifiée, version navigateur non minifiée) : mêmes résultats, 126 à 131 ms (le non minifié, 422 Ko, est inutile). Comparaison valeur par valeur avec l'ancienne version (milliers d'entrées aléatoires de 1990 à 2060, observateurs dans le monde entier, 20 fonctions utilisées par l'application) : écart maximal **3,6e-15** (dernier chiffre binaire, sur 16 des 45 000 positions `Equator` et 6 des 42 000 valeurs de `Illumination`) ; 6,8e-21 sur le vecteur de l'observateur ; **0 écart** sur tous les temps de lever, coucher, passage, quartiers de Lune, élongations et longitudes appariées. Le critère de 1e-12 est respecté avec trois ordres de grandeur de marge. Dans l'application : texte de cinq onglets comparé pour six dates et six lieux (hémisphère sud et haute latitude compris) : 30 onglets, **0 différence** ; 12 vues identiques au pixel ; tests des lieux et de l'ISS 13/13, de la carte de zone 10/10, de l'organisation des listes 49/49 ; démarrage aux cinq formats.

**Résultat mesuré** (profileur, démarrage de la page installée) : temps de processeur échantillonné 13,1 s → 9,3 s (−29 %). **Non mesuré** : le gain sur le S25 ; la mémoire (la bibliothèque est plus petite de 9 Ko ; la mémoire des processus varie de ±100 Mo d'un essai à l'autre sur ce banc). Reste lourd au démarrage : décodage de la carte et du relief (`im.onload`, 1,3 s sous le profileur).

## 8. Décodage de la carte et du relief au démarrage (16 novembre 2026, non livré : la version reste 0.95 ; page en ligne republiée)

**Constat (profil)** : décodage de la carte de base (JPEG 4 552 × 4 096) environ 1,2 à 1,4 s sur le fil principal (dessin de l'image 120 à 275 ms, `getImageData` 660 à 1 090 ms, conversion en niveaux de gris 70 à 300 ms) ; relief de base (WebP 3 200 × 2 880) environ 0,3 s ; relief fin : boucle de décodage de 160 ms plus lecture et décompression de 31 Mo (tampon de 37 Mo, tableau final de 74 Mo).

**Essais**
1. Canvas de la carte en mémoire centrale (`willReadFrequently`) et boucles sur mots de 32 bits : valeurs identiques, gain faible (carte 1,17 s → 1,01 s sous le profileur).
2. `HTMLImageElement.decode()` avant lecture : −0,5 s sur le fil principal, **mais mémoire plus haute** (l'image décodée reste en cache : 595 à 600 Mo au lieu de 486 Mo) : abandonné.
3. **Décodage dans des Workers** (carte et relief de base : `createImageBitmap`, `OffscreenCanvas`, extraction des points ; relief fin : lecture, gunzip et décodage ; les tableaux reviennent par transfert sans copie ; le Worker est arrêté ensuite) : **retenu**.

**Résultats du Worker** (3 essais de chaque version en alternance, page installée, écran simulé de 411 points) : six onglets affichés en **2,94 à 2,98 s contre 5,2 à 5,9 s** (−2,2 à −2,9 s, −45 %) ; mémoire des processus de rendu après 6 s **327 à 329 Mo contre 446 à 488 Mo** (−120 à −160 Mo) ; **pic transitoire plus haut : 689 à 704 Mo contre 604 à 614 Mo** (+85 à +90 Mo, pendant 2 à 3 s, quand le Worker et le fil principal travaillent ensemble). Valeurs décodées **strictement identiques** (empreintes FNV-1a des trois tableaux : carte 903946043, relief de base 3871169845, relief fin 3031205647) dans les trois modes : Workers, sans Worker, sans OffscreenCanvas.

**Robustesse** : repli automatique sur la lecture du fil principal si les Workers ou OffscreenCanvas ne sont pas disponibles, si le Worker ne peut pas lire le fichier (hors ligne : le test hors ligne de bout en bout passe 11/11, relief fin actif) ou en cas d'échec ; la page en ligne (images intégrées en base 64) décode aussi dans un Worker dans mon navigateur de test (empreintes identiques) ; son comportement dans le cadre de claude.ai n'est pas vérifié (si le cadre interdit les Workers, le repli s'applique). Contrôles : tables identiques ; 12 vues identiques ; démarrage aux cinq formats ; test du rendu de repos 7/7 ; `test_decodage_worker.py` 16/16.

**Non mesuré** : le gain sur le S25 ; l'effet du pic de mémoire plus haut sur un téléphone à mémoire limitée (le S25 a 12 Go).
