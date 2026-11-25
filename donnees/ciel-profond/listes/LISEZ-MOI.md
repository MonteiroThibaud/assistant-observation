# Listes d'objets du ciel profond

Un fichier JSON = un ensemble de listes de même origine (un livre, un club, une liste personnelle exportée). **Les listes libres sont dans ce dossier ; les listes protégées (`libre: false`, par exemple celle de Stelvision) sont dans `../../../donnees-hors-gpl/stelvision/`, avec leur avis de droits** (le contrôle des données refuse une liste rangée au mauvais endroit). Les listes apparaissent dans Paramètres, section « Listes d'objets », avec une case à cocher ; la fiche de chaque objet indique les listes dont il fait partie.

## Ajouter une liste
1. Vérifier que chaque objet existe dans `../messier.json`, `../classiques.json` ou `../doubles.json` (sinon l'ajouter d'abord, avec une source fiable). La désignation de la liste doit être celle du catalogue (par exemple `M13`, `NGC 6543`, `β Cyg`).
2. Copier un fichier existant (par exemple `../../../donnees-hors-gpl/stelvision/ciel-au-telescope.json`, en retirant `avis` et en mettant `libre` à true pour une liste libre) sous un nouveau nom dans ce dossier et remplir : `ensemble` (titre, auteurs, éditeur, adresse), `libre` (true si la liste est libre de droits ou sous licence libre ; false si elle est protégée), `licence`, et pour une liste protégée `avis` (le texte de l'accord et de la mention, une ligne par entrée), puis `listes` : un `id` court (1 à 6 caractères minuscules ou chiffres, différent de m, x, xg, xa, xp, xn, d, c, a et des autres listes), un `nom`, un `nom_complet` éventuel, `pages` (false si la liste n'a pas de numéros de page) et les `objets` : `{"objet":"M13","page":122}`.
3. Ajouter la source dans `../../sources.json` (et la citer dans Informations si elle demande une mention).
4. Lancer `python3 outils/construction/controle_donnees.py donnees` : il refuse un objet inconnu, un identifiant déjà pris, une liste protégée sans avis.
5. Lancer `python3 outils/construction/construire.py . ../livrables --zip` puis regarder la liste dans l'application.

## Boutons de filtre (onglet Ciel profond)
Les boutons Galaxies, Amas, Nébuleuses, Doubles, Comètes et Petites planètes ne s'affichent que si une liste cochée peut fournir ce type d'objets. Une liste ajoutée sans rien d'autre est une liste du ciel profond : elle fait apparaître Galaxies, Amas et Nébuleuses. Pour une liste d'un autre genre, ajouter dans sa définition le champ facultatif `filtres`, par exemple `"filtres": ["dbl"]` pour une liste d'étoiles doubles (valeurs permises : `gal`, `amas`, `neb`, `dbl`, `com`, `ast`). Un nouveau type de bouton demande en plus d'ajouter le bouton dans le code de l'onglet (une ligne) et d'associer ses objets à ce type (`DSO_GROUP`).

## Listes libres et listes protégées
- `libre: true` : la liste est écrite dans la page (bloc `listes-libres`).
- `libre: false` : le fichier va dans `donnees-hors-gpl/stelvision/` (avec son avis) ; la liste est écrite dans un bloc séparé (`listes-saisonnieres`), qui devient le fichier `listes-saisonnieres.js` de l'application installée, avec son avis ; ce fichier n'est pas couvert par la licence GPL et peut être retiré sans que l'application cesse de fonctionner.

## Listes calculées par le code et sélection personnelle
- **Autres objets classiques** : quatre listes selon la magnitude (très lumineux, 8,0 et moins ; lumineux, 8,1 à 9,5 ; moyens, 9,6 à 10,5 ; faibles, plus de 10,5 ou inconnue), calculées sur `../classiques.json` : aucun fichier à écrire ; les seuils sont dans `src/modele-page.html` (`clSub`).
- **Sélection personnelle** : liste dynamique, remplie par l'utilisateur avec l'étoile des fiches (ciel profond et oculaire) et enregistrée sur son appareil (clé `mySel`) ; elle n'a pas de fichier de données. `_archives/selection-300mm.json` garde, pour mémoire, la sélection de 97 objets de la 0.89 (hors construction).

## Listes lunaires
Elles sont encore définies dans le code (`LUNAR_LISTS`, calculées sur `lune/formations.json`) ; même démarche à prévoir pour elles.

## Ordre des objets dans une liste
L'ordre prévu est celui du fichier de la liste. L'utilisateur peut le changer sur son téléphone (Paramètres, « Listes d'objets », partie « Organisation des listes ») : l'ordre choisi est mémorisé sur l'appareil, jamais dans ces fichiers, et ne vaut que pour le mode « Par liste (numéro, page) » de l'onglet Ciel profond.
