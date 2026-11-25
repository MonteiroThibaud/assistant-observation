# Éléments hors licence GPL

Le code de l'application est sous licence GNU GPL version 3 ou ultérieure (fichier `LICENSE` à la racine). **Ce dossier contient les éléments du dépôt qui ne sont pas couverts par cette licence**, chacun avec son avis de droits. À conserver séparés du reste, avec leur avis, si tu redistribues le dépôt.

| Dossier | Contenu | Titulaire des droits | Conditions | Avis |
|---|---|---|---|---|
| `dss/images-dss-512/` | 206 images du ciel profond (Digitized Sky Survey, 512 × 512 points, niveaux de gris, retraitées) | California Institute of Technology (POSS-II), Anglo-Australian Observatory Board (UKST), AURA / STScI | Libre pour la recherche, l'enseignement et les usages sans but lucratif, avec mention de la source ; usage commercial interdit sans autorisation | `dss/LICENCE-DSS.txt` |
| `stelvision/ciel-au-telescope.json` | Listes saisonnières (Printemps, Été, Automne, Hiver) : sélection, ordre et numéros de page du livre « Le Ciel au télescope » (noms d'objets et numéros de page seulement) | éditions Stelvision et ses auteurs (Carine Souplet, Bertrand d'Armagnac) | Reprise avec leur accord écrit du 29 octobre 2026, à condition de citer l'ouvrage dans « Informations » (fait) | `stelvision/LICENCE-LISTES-SAISONNIERES.txt` |

## Comment ces éléments sont utilisés
- Les paramètres des images (champ, position du centre) sont dans `donnees/ciel-profond/images-dss.json` (sous GPL) ; les fichiers JPEG sont ici.
- Les listes de Stelvision sont lues comme les autres listes (`donnees/ciel-profond/listes/`), avec le repère `libre: false` et leur avis. À la construction du site installé, elles deviennent le fichier `listes-saisonnieres.js` (avec `LICENCE-LISTES-SAISONNIERES.txt`), qui peut être retiré sans que l'application cesse de fonctionner.
- `manifeste.json` donne l'empreinte (SHA-256) de chaque fichier ; la construction (`outils/construction/construire.py`) la vérifie avant de commencer.

## Autres éléments qui ne sont pas sous GPL
D'autres données gardent leurs licences propres (cartes de la NASA, catalogues de l'ESA, OpenNGC et AT-HYG en CC BY-SA 4.0, photos de l'auteur en CC BY 4.0, polices SIL OFL, etc.) : voir `DONNEES-ET-LICENCES.md` à la racine.
