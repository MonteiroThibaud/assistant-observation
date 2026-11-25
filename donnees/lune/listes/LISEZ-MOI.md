# Listes de formations lunaires

Elles se cochent dans Paramètres, section « Listes d'objets », partie « Formations lunaires », et alimentent la liste de l'onglet Lune.

## Deux sortes de listes
- **Calculées par le code** (elles ne sont pas dans ce dossier, car elles suivent les mesures et la position de la Lune) : Toutes les formations, À voir ce soir (près du terminateur), Libration favorable, Incontournables (priorité 1 de `../formations.json`), Grands cratères (≥ 100 km), Cratères à pic central, Les plus profonds (30 par profondeur moyenne et 30 par profondeur maximale), Remparts les plus hauts (30), Œil nu et jumelles (≥ 100 km), Petit télescope (30 à 100 km), Télescope moyen (10 à 30 km), Grand télescope (< 10 km et dômes). Pour les modifier, il faut modifier le code (seuils, nombre de formations).
- **Choisies à la main** (ce dossier) : une liste de noms de formations. Aujourd'hui : `rayons.json` (cratères à rayons, 14 formations).

## Ajouter une liste choisie à la main
1. Copier `rayons.json` sous un nouveau nom.
2. Remplir `ensemble` (titre), `libre` (true si la liste est libre ou sous licence libre, false si elle est protégée : dans ce cas ajouter aussi `avis`, le texte de l'accord et de la mention), `licence`, puis `listes` : un `id` court (minuscules et chiffres, 8 caractères au plus, différent des listes calculées : all, tonight, libr, must, big, pic, deep, high, i1 à i4), un `groupe` (un groupe existant : Base et dynamiques, Sélections, Par instrument ; ou un nouveau, qui apparaît à la fin), un `nom`, un `sous_titre` éventuel et les `formations` (noms exacts de `../formations.json`).
3. Ajouter la source dans `../../sources.json` si la liste vient d'un tiers.
4. `python3 outils/construction/controle_donnees.py donnees` refuse une formation inconnue ou un identifiant déjà pris.
5. `python3 outils/construction/construire.py . ../livrables --zip`.

Les listes d'un même groupe se classent par `ordre` croissant (entier facultatif, à écrire dans la liste : `"ordre": 1`), puis par nom de fichier.
