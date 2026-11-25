# Vérification

Preuves de non-régression utilisées à chaque modification de données ou de construction (trois preuves : empreintes des tables, aucune déclaration disparue, comparaison d'images sans erreur JavaScript).

- `instantane_donnees.py` : instantané des tables de connaissances d'une page (empreintes SHA-256) et comparaison à une référence. Usage : `python3 instantane_donnees.py PAGE.html DOSSIER_SORTIE [DOSSIER_REFERENCE]` (références dans `donnees/_reference-*/`).
- `cmp_vues_avant_apres.py` : compare des vues de l'application avant et après une modification (images au pixel près, erreurs JavaScript) ; il attend deux copies de la page servies localement (voir l'en-tête du fichier).
