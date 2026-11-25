# Outils

| Dossier | Contenu |
|---|---|
| `construction/` | La chaîne de construction : `construire.py` (commande unique) et les scripts qu'il utilise (sommes de contrôle, contrôle des données, assemblage de la page web et du site installé, service worker) |
| `verification/` | Preuves de non-régression : empreintes des tables de données (`instantane_donnees.py`) et comparaison d'images avant et après (`cmp_vues_avant_apres.py`) |
| `tests/` | Tests de l'application (Playwright pour Python) ; usage de chaque test en tête du fichier ; les captures d'écran sont écrites dans `/tmp` |
| `audits/` | Audits ponctuels : outils réutilisables (`cmp_textes_calculs.py` : compare les textes et calculs de deux copies de l'application, dossiers donnés en arguments ; `audit_alignement_*.py`), inventaire des textes d'explication, vérifications avant publication, et l'archive de l'étude des ombres de la Lune (`etude-ombres/` : rapport, données et résultats ; scripts non relançables sur les versions suivantes, voir son `LISEZ-MOI.md`) |
| `fabrication-donnees/` | Scripts qui fabriquent des fichiers binaires à partir de sources externes (lieux, départements, tuiles de la Lune) ; chemins d'entrée d'origine à adapter (voir `LISEZ-MOI.md` du dossier) |
| `windows/` | Scripts et fichiers `.bat` pour fabriquer le relief de la Lune, les tuiles et télécharger les images DSS sous Windows (un `LISEZ-MOI` dans chaque dossier) |
| `historique/` | Scripts ponctuels de migration et de correction, anciens essais ; non maintenus ; à ne pas rejouer (voir `LISEZ-MOI.md` du dossier) |

Construire : `python3 outils/construction/construire.py . ../livrables --zip`.
