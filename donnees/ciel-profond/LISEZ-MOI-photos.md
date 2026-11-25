# Photos de l'auteur

`photos.json` décrit les photos de Thibaud Monteiro montrées à l'oculaire à la place de l'image du Digitized Sky Survey. Une photo sert à un ou plusieurs objets (ex. Orion : M42, M43 et NGC 1977).

## Ajouter ou corriger une photo
1. Mettre le fichier de 1 500 points dans `../binaires/web/` (`photo-NOM.jpg`) et celui de 3 000 points dans `../binaires/installee/photos/` (`ph_NOM.jpg`). Les images du dossier de sortie se lisent avec `nettoie_binaires.py`.
2. Ajouter une entrée dans `photos.json` : `id` (lettres et chiffres), `legende` (« photo de … (mois année) »), `objets` (désignations des catalogues : `M13`, `NGC 6888`…), `web` et `installee` avec `fichier`, `champ` (largeur du champ en degrés), `ra` et `dec` (centre de la photo, degrés J2000), `largeur` et `hauteur` (dimensions de l'image en points). Un `commentaire` facultatif est écrit dans le code avant la photo.
3. `python3 outils/construction/controle_donnees.py donnees` refuse un objet inconnu, un objet déjà dans une autre photo, un fichier absent et des dimensions différentes de l'image.
4. `python3 outils/construction/construire.py . ../livrables --zip`, puis regarder l'objet à l'oculaire.

La page web garde la limite de 16 Mo : chaque photo de 1 500 points y pèse environ 0,1 Mo.
