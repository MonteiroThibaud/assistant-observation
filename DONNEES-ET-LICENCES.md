# Données, sources et licences

Le code de l’application est sous licence GPL v3 ou ultérieure (fichier `LICENSE`). Les données, images et bibliothèques ci-dessous gardent leurs propres licences. La rubrique « Informations » de l’application en donne la version détaillée pour l’utilisateur.

| Élément | Source | Licence ou conditions |
|---|---|---|
| Carte de la Lune | NASA Scientific Visualization Studio, CGI Moon Kit (caméra LROC de la sonde LRO) | Domaine public aux États-Unis ; citer « NASA’s Scientific Visualization Studio », LROC et LOLA |
| Relief de la Lune | SLDEM2015 (Barker et al., Icarus 273, 2016 ; LOLA et SELENE/Kaguya, NASA PDS) ; carte de déplacement LOLA (NASA SVS) | Indiqués comme domaine public ; conserver les citations |
| Étoiles | Hipparcos et Tycho-2 (Agence spatiale européenne) | CC BY-NC 3.0 IGO (ESA) : usage non commercial ; crédit « ESA » ; citer les catalogues |
| Types spectraux et distances | AT-HYG (David Nash : Hipparcos, Tycho-2, Gaia DR3) | CC BY-SA 4.0 |
| Objets du ciel profond | OpenNGC (Mattia Verga ; SIMBAD, NED) ; d3-celestial (Olaf Frohn) | CC BY-SA 4.0 ; licence BSD à 3 clauses |
| Objets NGC et IC ajoutés en 0.89 (97 objets) | OpenNGC (Mattia Verga ; NGC/IC d'après Dreyer, SIMBAD, NED) : positions, magnitudes, tailles ; noms français : dictionnaire de l’Observatoire de Paris, Société astronomique de France, Wikipédia en français, ESA/Hubble (traductions de surnoms anglais faites par l’application) | CC BY-SA 4.0 (OpenNGC) ; noms : voir `sources.json` |
| Étoiles doubles | Washington Double Star Catalog (US Naval Observatory), valeurs arrondies | À citer |
| Formations lunaires | Gazetier de l’UAI et de l’USGS ; LROC QuickMap ; Head et Gifford (1980) via le projet LTVT de Jim Mosher ; autres sources citées dans l’application | Voir l’application |
| Bibliothèques | Astronomy Engine (Don Cross), astronomia (commenthol), satellite.js ; d3-celestial (Olaf Frohn) | MIT ; BSD à 3 clauses : textes complets dans `LICENCES-TIERCES.txt` |
| Polices | Alegreya et Alegreya Sans (Huerta Tipográfica), intégrées à l’application : plus aucun appel aux serveurs de Google | SIL Open Font License 1.1 : texte dans `LICENCES-TIERCES.txt` |
| Images du ciel profond | Digitized Sky Survey (STScI, subvention NAG W-2166), téléchargées depuis SkyView (NASA) pour chaque objet puis retraitées (niveaux de gris, fond assombri) ; la page web n’en contient aucune (limite de 16 Mo) ; l’application installée utilise les images de 512 points | Droits d’auteur de leurs détenteurs : Caltech (POSS-II, ciel nord), Anglo-Australian Observatory Board (UKST, ciel sud), AURA / STScI (autres plaques). Libre pour la recherche, l’enseignement et les usages non lucratifs avec mention de la source ; usage commercial interdit sans autorisation. Mentions : formule du STScI et remerciement à SkyView, reprises dans Informations ; fichiers dans `donnees-hors-gpl/dss/` avec leur avis `LICENCE-DSS.txt` (dossier non couvert par la GPL) |
| Lieux du carnet (et fond de carte de la zone des transits de l’ISS : limites de communes et de départements, noms) | IGN Admin Express 2018 via france-geojson (Grégoire David) ; découpage administratif d’Etalab ; GeoNames ; le département est déduit du code INSEE de la commune | Licence Ouverte Etalab 2.0 ; CC BY 4.0 |
| Astérismes | Deep Sky Corner (Picot 1) ; Houston Astronomical Society (Kemble 2) ; SIMBAD (M73) ; photo de Chuck Ayoub (NGC 2169) ; silhouette de hibou de NGC 457 (dessin de Thibaud Monteiro, calé sur le catalogue d’étoiles de l’application) | CC BY 4.0 ; article cité ; CDS ; CC0 1.0 ; CC BY 4.0 |
| Photos de l’auteur (grande nébuleuse d’Orion, M13, M27, M31, M33, M45, M52, M81, M101, Rosette, NGC 7000, IC 5070, NGC 7023, NGC 6888, NGC 6960, NGC 6992, NGC 7635, IC 1396, Flamme et Tête de Cheval) | © Thibaud Monteiro, prises entre 2020 et 2026, traitées avec Siril, calées avec Astrometry.net | CC BY 4.0 |
| Listes saisonnières (Printemps, Été, Automne, Hiver) | Sélection, ordre et numéros de page du livre « Le Ciel au télescope » (C. Souplet et B. d’Armagnac, Stelvision, 2021) ; seuls les noms d’objets et les numéros de page sont repris | © Stelvision et ses auteurs pour la sélection ; reprise avec leur accord écrit du 29 octobre 2026 ; fichier hors GPL : `donnees-hors-gpl/stelvision/` (avis : `LICENCE-LISTES-SAISONNIERES.txt`) |
| Icônes de l’application | Dessin original créé pour l’application (généré par programme : planète à anneau, croissant de Lune, étoiles), sans élément tiers | Mêmes conditions que le code (GPL v3) |
| Éléments d’orbite et TLE | Minor Planet Center ; CelesTrak | Importés ou téléchargés par l’utilisateur, non inclus |

## Éléments à traiter avant de rendre le dépôt public

| Élément | Point à régler |
|---|---|
| Images du ciel profond (DSS) | **Fait le 22 novembre 2026** : les 206 images sont dans `donnees-hors-gpl/dss/images-dss-512/` avec leur avis `LICENCE-DSS.txt` (titulaires des droits, conditions, mentions à conserver) ; leurs paramètres restent dans `donnees/ciel-profond/images-dss.json` (sous GPL) ; la construction produit exactement les mêmes 534 fichiers qu'avant (empreintes identiques). Dans le formulaire du plan Open Source de Netlify : signaler que le dépôt contient ce dossier non GPL |
| Listes saisonnières (Stelvision) | Accord écrit du 29 octobre 2026 (condition : citer le livre dans Informations avec titre, auteurs, éditeur et lien vers la boutique : fait). **Dossier préparé le 22 novembre 2026** : `donnees-hors-gpl/stelvision/` (`ciel-au-telescope.json` et `LICENCE-LISTES-SAISONNIERES.txt`) ; le fichier `listes-saisonnieres.js` du site installé reste isolé avec son avis. **À la publication : informer Stelvision** (ils l'ont demandé) en mentionnant le dépôt public |
| Photos de l’auteur (`donnees/binaires/` et `site-statique/img/ph_*.jpg`) | Réglé le 4 novembre 2026 : licence CC BY 4.0 (usage libre, y compris commercial, avec mention « Thibaud Monteiro » et indication des modifications) ; écrite dans Informations |
| Étoiles Hipparcos et Tycho-2 (ESA) | Catalogues sous CC BY-NC 3.0 IGO (usage non commercial), vérifié le 6 novembre 2026. Fichiers concernés : voir « Fichiers sous licence de données » ci-dessous. Le projet reste non commercial (condition déjà posée par le plan Open Source de Netlify) ; la GPL v3 ne couvre que le code |
| Données CC BY-SA 4.0 (OpenNGC, AT-HYG) | Le partage dans les mêmes conditions s’applique à ces données et à leurs dérivés : voir « Fichiers sous licence de données » ci-dessous |
| Code de conduite | `CODE_OF_CONDUCT.md` à la racine : adaptation du Contributor Covenant 2.1 (CC BY 4.0, attribution incluse) |

## Fichiers sous licence de données (non couverts par la GPL)

La licence GNU GPL v3 ne couvre que le code. Les fichiers de données ci-dessous gardent la licence de leur source ; si tu les réutilises ou les redistribues, respecte-la.

| Source et licence | Fichiers du dépôt concernés |
|---|---|
| Hipparcos et Tycho-2 (ESA) : CC BY-NC 3.0 IGO, usage non commercial, crédit ESA | `donnees/ciel/etoiles-reperes.json`, `donnees/binaires/web/etoiles-champ.bin`, `site-statique/img/etoiles.bin.gz` |
| AT-HYG (David Nash ; Hipparcos, Tycho-2, Gaia DR3) : CC BY-SA 4.0, partage dans les mêmes conditions | `donnees/binaires/web/etoiles-info.bin.gz`, `site-statique/img/etoiles-info.bin.gz` (types spectraux et distances) |
| OpenNGC (Mattia Verga ; SIMBAD, NED) : CC BY-SA 4.0, partage dans les mêmes conditions | `donnees/ciel-profond/messier.json`, `donnees/ciel-profond/classiques.json` (positions, types, tailles) |
| Digitized Sky Survey (STScI, SkyView) : usage non lucratif avec mention de la source | `donnees-hors-gpl/dss/images-dss-512/` |
| Listes de Stelvision : accord écrit du 29 octobre 2026 | `donnees-hors-gpl/stelvision/ciel-au-telescope.json` |
| Photos de l’auteur : CC BY 4.0 | `donnees/binaires/web/photo-*.jpg`, `donnees/binaires/installee/photos/` |
| Polices Alegreya : SIL Open Font License 1.1 | `donnees/binaires/web/police-*.woff2` (texte de la licence : `LICENCES-TIERCES.txt`) |

Cette liste de fichiers a été dressée d’après le registre des sources (`donnees/sources.json`) et le rôle de chaque fichier ; en cas de doute, le registre fait foi.

## Registre des sources : statuts (6 novembre 2026)

Chaque entrée de `donnees/sources.json` porte une licence ou un statut, avec une note de vérification. État : 31 licences vérifiées à la source (dont les 10 relevées à l'audit de la 0.87, revérifiées le 6 novembre 2026), 18 références citées dont seules des valeurs numériques ou des noms (des faits) sont repris, le cas échéant, sans aucun texte, 1 licence retenue par l'auteur (Gaia : CC BY-SA 4.0, via AT-HYG), 3 jeux de données téléchargés par l'utilisateur et non inclus. Aucune source n'est à vérifier.

Point d'attention : les catalogues Hipparcos et Tycho de l'ESA sont sous CC BY-NC 3.0 IGO (usage non commercial). Les données d'étoiles de l'application en dérivent ; l'application doit donc rester non commerciale.
