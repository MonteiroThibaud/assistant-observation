# Fabrication de données

Scripts qui fabriquent des fichiers binaires de l'application à partir de sources externes (non incluses dans le dépôt). Ils ne font pas partie de la construction courante : les fichiers produits sont déjà dans `site-statique/img/`. Les chemins d'entrée écrits dans les scripts sont ceux de l'environnement d'origine : à adapter avant de les lancer.

- `fabrique_departements.py` : Fabrique « departements.bin.gz » : les limites des départements de France métropolitaine, pour le fond de la carte de zone de l'ISS au-delà du fond détaillé.
- `fabrique_lieux.py` : Fabrique le fichier « lieux.bin.gz » de l'application : contours des communes de France (IGN Admin Express 2018 via france-geojson,
- `fabrique_tuiles_lune.py` : !/usr/bin/env python3

Le relief de la Lune (`relief-fin.bin.gz`) se fabrique avec les scripts de `../windows/` (`fabrique_relief_lune.py`, `fabrique_relief_sldem.py`). Une autre copie de `fabrique_tuiles_lune.py` se trouve dans `../windows/tuiles/` : elle diffère de celle-ci (à réconcilier avant de s'en servir).
