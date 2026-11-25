# Données de l'Assistant d'observation

**Éléments hors licence GPL** : les images du ciel profond (DSS) et les listes de Stelvision ne sont pas dans ce dossier mais dans `../donnees-hors-gpl/`, avec leurs avis de droits (voir `../donnees-hors-gpl/LISEZ-MOI.md`).

Ce dossier contient les **connaissances** de l'application, séparées du code. Le chantier est mené par étapes ; chaque étape prouve que l'application rend exactement la même chose qu'avant (voir `journal-0.88-en-cours.md`).

## État (5 novembre 2026)

| Étape | Contenu | État |
|---|---|---|
| 0. Socle | Version 0.87 figée comme référence (`_reference-0.87/` : 15 tables JSON et leurs empreintes SHA-256) ; script `outils/verification/instantane_donnees.py` qui re-extrait les tables d'une page et les compare à la référence | fait |
| 1. Sources | Registre `sources.json` (8 catégories, 49 liens) ; générateur `outils/construction/construit_liens.py` : menu « Liens des sources » régénéré identique octet pour octet. Textes des licences tierces dans `licences-tierces/` ; générateur `outils/construction/construit_licences.py` : `LICENCES-TIERCES.txt` et bloc d'Informations identiques octet pour octet | fait (les paragraphes de crédits, texte libre, passent à l'étape 5) |
| 2. Ciel profond | `ciel-profond/` : `messier.json` (110), `classiques.json` (167 en 0.89 : 70 d’origine et 97 ajoutés en 0.89), `doubles.json` (34, avec leurs informations astrophysiques), `types.json` (18), `asterismes.json` (6, avec la source de chaque tracé) en champs nommés ; `images-dss.json` (206 images dont 57 ajoutées en 0.89, application installée seulement : champ, position, fichiers) avec `../donnees-hors-gpl/dss/images-dss-512/` (application installée, 4,2 Mo) et `images-dss-256/` (page web, 96 images) ; générateurs `outils/construction/construit_ciel_profond.py` et `outils/construction/donnees_images_dss.py` : les deux tables DSO_IMG se régénèrent octet pour octet ; 8 vues identiques au pixel près. Les photos de l'auteur (18 photos, aux paramètres différents entre page web et installée) sont décrites par `ciel-profond/photos.json` (0.89 ; procédure : `ciel-profond/LISEZ-MOI-photos.md`) : `outils/construction/donnees_photos.py` génère les lignes de la table DSO_IMG des deux versions. **Listes d'objets (0.89)** : `ciel-profond/listes/*.json` (un fichier par ensemble de listes, avec source, licence et avis) ; `outils/construction/donnees_listes.py` génère les blocs `listes-saisonnieres` (protégées) et `listes-libres` ; procédure dans `ciel-profond/listes/LISEZ-MOI.md` ; **listes lunaires** : `lune/listes/*.json` (aujourd'hui `rayons.json`, 14 cratères) pour les listes choisies à la main, les autres (11) restent calculées par le code ; procédure dans `lune/listes/LISEZ-MOI.md` | fait |
| 3. Lune | **3A** (couches) puis **3B faite** : `lune/formations.json` contient une fiche finale par formation (1 161 : position, priorité, description, mesures) ; `lune/notes-sources.md` garde les sources et méthodes des corrections ; `lune/filtres.json` ; générateur `outils/construction/donnees_lune_final.py` : remplace FEATURES, DESC et FEAT_M par les valeurs finales et supprime de la page les 13 littéraux et 7 fonctions de correction (132 950 octets de code). Les couches d'origine sont conservées dans `lune/historique/` (non utilisées). Preuves : mêmes valeurs finales (13 tables), 12 vues identiques au pixel près, texte de 69 fiches échantillonnées identique | fait |
| 4. Ciel | `ciel/etoiles-reperes.json` (5 044 étoiles), `ciel/constellations.json` (88 : nom, centre, figure, limites), `ciel/noms-francais-constellations.json`, `lune/filtres.json` ; générateur `outils/construction/donnees_ciel.py` ; 12 vues identiques au pixel près. Les noms propres des étoiles et les informations stellaires binaires (STAR_INFO_C64) restent à décrire | fait |
| 5. Textes | `textes/fr/informations.json` : la section Informations (10 menus, 62 392 octets) en lignes HTML ; `version.json` ; les menus « Liens des sources » et « Licences des composants tiers » sont générés ; générateur `outils/construction/construit_textes.py` : section régénérée octet pour octet. Inventaire de l'interface dans `textes/fr/INVENTAIRE.md` (HTML statique : 115 textes ; JavaScript : environ 1 570 chaînes) : le catalogue d'interface sera fait avec l'anglais | Informations faites ; catalogue d'interface reporté |
| 6. Contrôles | `schemas/*.schema.json` (8 schémas) et `outils/construction/controle_donnees.py` : validation par schéma, identifiants uniques, types connus, bornes, ordre des clés, références (images, astérismes, tracés), fichiers présents, complétude des sources ; rapport `RAPPORT-CONTROLES.md` : 0 erreur, 3 avertissements | fait |
| 7. Construction et dépôt | **Faite.** `src/modele-page.html` (0,48 Mo : le code seul) + `donnees/` → page web ; + `site-statique/` (76 Mo de fichiers non générés : relief fin, tuiles, étoiles, texture, lieux, icônes, service worker) → site installé ; `outils/construction/construire.py RACINE SORTIE --zip` enchaîne : sommes de contrôle, contrôle des données, page web, site installé, archive. Résultat identique à la 0.87 aux données corrigées près : mêmes fichiers (474), mêmes octets pour tous sauf `index.html` ; les images ne portent plus les métadonnées C2PA (site 1,75 Mo plus léger) | fait |

## Construire

```
python3 outils/construction/construire.py . ../livrables --zip
```
Prérequis : Python 3 avec `jsonschema` (contrôles) ; Node et Playwright seulement pour les tests et la migration. La page web doit rester sous 16 Mo.

## Règles
- **Images JPEG et WebP : toujours lues avec `nettoie_binaires.py`** (la plateforme de travail y ajoute des métadonnées de provenance C2PA entre deux séances ; le manifeste est calculé sur les octets nettoyés).
- Format : JSON validé par schéma (UTF-8, points décimaux). Les gros tableaux plats pourront être édités en CSV plus tard (outil à créer sur demande).
- Identifiants stables : `dso:M13`, `lune:tycho`, `src:openngc`. Les fichiers se référencent par identifiant, jamais par nom affiché.
- Chaque jeu de données porte sa source et sa licence dans `sources.json` ; aucun jeu sans source. Chaque entrée du registre a une licence ou un statut : `verifiee` (licence vérifiée à la source), `audit` (relevée à l'audit des droits de la 0.87, non revérifiée), `citation` (référence citée, aucun contenu protégé repris), `non-incluse` (données téléchargées par l'utilisateur) ou `a-verifier` ; la note `verification` dit d'où vient l'information.
- Les données lourdes (relief, étoiles, tuiles, images) restent binaires mais seront décrites dans `manifeste.json`.
- Aucune donnée générée par une IA sans vérification.

## Tables de référence (page 0.87)
CONST 27 · FEATURES 1 161 formations lunaires · DESC 1 161 descriptions · FEAT_M 1 139 mesures · MESSIER 110 · DSO_EXTRA 70 · DSO_DOUBLE 34 · DOUBLE_INFO 34 · DSO_TYPE 18 · ASTERISMS 6 · SKY_CONS 88 · SKY_STARS 5 044 · MOON_FILTERS 10 (valeurs finales, après les corrections que le code applique ; CONS_P est un cache calculé à l'exécution, pas une donnée).
Autres tables à repérer aux étapes suivantes : paramètres des images (DSO_IMG), informations stellaires (STAR_INFO_C64), listes saisonnières (déjà dans un fichier à part), textes d'Informations et d'interface.
