# Inventaire des textes de l'application (5 novembre 2026)

| Ensemble | Taille | État |
|---|---|---|
| Section Informations (10 menus) | 62 392 octets | **dans `informations.json`**, régénérée octet pour octet ; les menus « Liens des sources » et « Licences des composants tiers » sont générés depuis `sources.json` et `licences-tierces/` ; la version vient de `version.json` |
| HTML statique de l'interface (hors Informations) | 21 009 octets : 115 textes visibles (3 695 caractères) et 70 attributs textuels (1 601 caractères) | dans la page ; à passer en catalogue avec l'anglais |
| Chaînes françaises du JavaScript | environ 1 570 chaînes de 12 caractères ou plus (151 000 caractères), dont une grande part de données (noms de formations, descriptions) déjà migrées à l'étape 3 | à repérer une par une ; le code doit appeler un catalogue (`T('clé')`) |

Pour la version anglaise (reportée jusqu'à ce que l'utilisateur ait trouvé un astronome anglophone) : créer `textes/en/informations.json` de même structure, un catalogue de l'interface, et traduire les données textuelles (descriptions des formations, noms français des constellations). Les phrases construites par le code (ex. « profond d'environ … km », « à … km au nord de … ») demandent un travail à part : ce sont des gabarits à traduire, pas des textes fixes.
