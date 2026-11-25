# Bibliothèque d'astronomie intégrée (Astronomy Engine 2.1.19)

Depuis le 16 novembre 2026, la page embarque la version « boucles natives » de la bibliothèque, compilée en ES2020 à partir du **module ES du même paquet** (la version minifiée du paquet est transpilée en ES5 avec des itérateurs lents).

## Refaire la compilation
```
npm pack astronomy-engine@2.1.19 && tar xzf astronomy-engine-2.1.19.tgz
npm install esbuild@0.25
./node_modules/.bin/esbuild package/esm/astronomy.js --bundle --minify --format=iife --global-name=Astronomy --target=es2020 --outfile=ae-es2020.min.js
```
Le bloc de la page (`src/modele-page.html`, après le commentaire « Astronomy Engine 2.1.19 ») est l'en-tête de licence MIT d'origine suivi du contenu de `ae-es2020.min.js`.

## Preuve avant toute mise à jour de la bibliothèque
- `outils/audits/compare_astronomy.js` : compare, valeur par valeur, l'ancienne version (fichier `astronomy.browser.min.js` du paquet) et la nouvelle sur toutes les fonctions utilisées par l'application (Equator, Horizon, GeoVector, HelioVector, GeoMoon, Illumination, MoonPhase, Constellation, SiderealTime, MakeTime, ObserverVector, RotationAxis, Rotation_EQJ_EQD, RotateVector, JupiterMoons, SearchRiseSet, SearchHourAngle, SearchMaxElongation, SearchMoonQuarter, PairLongitude) avec des milliers d'entrées aléatoires. Résultat du 16 novembre 2026 : écart maximal de 3,6e-15 sur 17 valeurs de position ou de magnitude (dernier chiffre binaire), 6,8e-21 sur les vecteurs de l'observateur, 0 écart sur tous les temps de lever, coucher, passage, quartiers et élongations. Critère : écart inférieur à 1e-12.
- `outils/audits/cmp_textes_calculs.py` : compare le texte de cinq onglets (Système solaire, Détail planète, Ciel profond, Lune, À l'oculaire) entre deux constructions, pour six dates et six lieux du monde (hémisphère sud et haute latitude compris) : 30 onglets, 0 différence.
