# Assistant d’observation

Application gratuite et libre d’aide à l’observation de la Lune, des planètes et du ciel profond au télescope. Pour une date et un lieu, elle indique quand observer chaque objet, où le trouver dans le ciel et à quoi il ressemble dans le télescope. Elle fonctionne sans réseau.

**Version 1.0** · [Application en ligne](https://assistant-observation-thibaud.netlify.app/) · [Journal des changements](CHANGELOG.md) · [Licence GPL v3](LICENSE)

*English: a free, offline-first web app (installable on Android) that helps amateur astronomers plan telescope sessions: Moon atlas with relief and shadows, planets, deep-sky objects, double stars, asterisms, observing log. GPL-3.0-or-later, French interface.*

## Ce que fait l’application

- **Système solaire** : le tableau de la nuit (Lune, planètes), qualité de la nuit, phénomènes (satellites de Jupiter, occultations, rapprochements, X lunaire, transits de l’ISS).
- **Détail planète** et **Lune** : carte de la Lune avec relief et ombres calculés, plus de 1 100 formations avec fiche (hauteur de rempart, profondeur, éclairage, grossissement conseillé), listes d’observation.
- **Ciel profond et petits corps** : 110 objets de Messier, 70 objets classiques, 34 étoiles doubles, comètes et petites planètes (éléments d’orbite importés), plans de recherche.
- **À l’oculaire** : vue à l’échelle exacte du champ pour ton instrument, avec les étoiles jusqu’à la magnitude 10,5, des astérismes tracés étoile par étoile, et le mode Dobson (orientation de l’image).
- **Carnet d’observation** gardé sur l’appareil, avec, au choix, la commune et le pays de ta position (calcul sur le téléphone, rien n’est envoyé).
- **Mode rouge** pour préserver la vision nocturne.

## Installer

- **Navigateur** : ouvrir l’[application en ligne](https://assistant-observation-thibaud.netlify.app/), puis ajouter l’application à l’écran d’accueil depuis le menu du navigateur (« Ajouter à l’écran d’accueil » ou « Installer l’application »). Après une première ouverture avec une connexion (environ 80 Mo), tout fonctionne hors ligne.
- **Application Android (APK)** : elle se fabrique à partir du site publié avec PWABuilder (voir « Publier le site ») ; le fichier de signature et ses mots de passe ne sont jamais publiés.

## Contenu du dépôt

| Dossier | Contenu |
|---|---|
| `src/` | `modele-page.html` : le code de l’application (page unique), avec des marques à la place des données |
| `donnees/` | Les connaissances de l’application (JSON validés par schémas) et leurs binaires ; documentation : `donnees/LISEZ-MOI.md` |
| `donnees-hors-gpl/` | Les éléments **non couverts par la licence GPL** (images du ciel profond du Digitized Sky Survey, listes de Stelvision), chacun avec son avis de droits : `donnees-hors-gpl/LISEZ-MOI.md` |
| `site-statique/` | Les fichiers de l’application installée qui ne sont pas générés (relief fin, tuiles de la Lune, étoiles, lieux, icônes, service worker) |
| `outils/` | Construction (`construction/`), vérification, tests, audits, fabrication de données, scripts historiques : voir `outils/LISEZ-MOI.md` |

Fichiers importants à la racine : `LICENSE` (GPL v3), `LICENCES-TIERCES.txt` (textes des licences des bibliothèques et des polices), `DONNEES-ET-LICENCES.md` (sources, licences et fichiers concernés), `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `CITATION.cff` et `codemeta.json` (pour citer le logiciel).

## Construire

```
python3 outils/construction/construire.py . ../livrables --zip
```

La commande vérifie les sommes de contrôle de `donnees/` et de `donnees-hors-gpl/`, contrôle les données (schémas, doublons, références, avis de droits), assemble la page web (moins de 16 Mo) et le site installé, puis l’archive. Prérequis : Python 3 avec `jsonschema` ; Node et Playwright seulement pour les tests.

## Publier le site

Le site installé produit dans `../livrables/site/` est un site statique : il suffit de le publier tel quel sur un hébergeur de fichiers statiques servi en HTTPS. L’application installée charge ses fichiers au premier lancement (environ 80 Mo) puis fonctionne hors ligne grâce à un service worker ; ensuite, le navigateur ne vérifie que la présence d’une nouvelle version (une requête légère).

Pour obtenir une APK Android à partir d’un site publié, utiliser [PWABuilder](https://www.pwabuilder.com/) (Android : mode d’affichage plein écran, orientation par défaut, signature avec **sa propre clé** : ne jamais publier le fichier de clé ni ses mots de passe).

## Données, sources et licences

L’application s’appuie sur des données publiques (NASA, ESA, IGN, GeoNames…) et sur des bibliothèques libres. Le détail des sources, licences et crédits est dans `DONNEES-ET-LICENCES.md` et dans la rubrique « Informations » de l’application.

## Contribuer

Les remarques, signalements d’erreurs et propositions sont les bienvenus : voir `CONTRIBUTING.md`. Ce projet suit le code de conduite du fichier `CODE_OF_CONDUCT.md`. Pour signaler une faille de sécurité, voir `SECURITY.md`.

## Licence

Code : © 2026 Thibaud Monteiro, [GNU GPL version 3](LICENSE) ou ultérieure. **Sont exclus de cette licence** : le contenu du dossier `donnees-hors-gpl/` (images du Digitized Sky Survey : © leurs détenteurs, usage non lucratif avec mention de la source ; listes de Stelvision : © éditions Stelvision et ses auteurs, reprises avec leur autorisation) et les données et images qui gardent leurs licences propres (cartes, catalogues, photos, polices : voir `DONNEES-ET-LICENCES.md`, qui liste aussi les fichiers sous CC BY-SA 4.0 et sous CC BY-NC 3.0 IGO).

## Auteur et transparence sur l’IA

Thibaud Monteiro, Club Astro Jupiter du Roannais : contact.assistantobservation@laposte.net.

Le code a été écrit **en très grande partie avec l’assistance d’une IA générative** (Claude, d’Anthropic), sous la direction de l’auteur : c’est lui qui a défini les fonctions, relu, testé sur son télescope et validé chaque version. Les résultats sont contrôlés par comparaison avec des données de référence (positions du Soleil aux sites Apollo, relief et images de la Lune de la NASA, catalogues astronomiques) et par des tests automatiques dans un navigateur (`outils/tests/`). Aucune donnée n’est générée par une IA sans vérification sur une source fiable.

## Remerciements

Merci aux bêta-testeurs du [Club Astro Jupiter du Roannais](https://www.astrojupiter.fr/gs/) pour leurs retours, et aux auteurs des données et des bibliothèques libres listées dans `DONNEES-ET-LICENCES.md` et `LICENCES-TIERCES.txt`.

## Citer ce logiciel

Voir `CITATION.cff` (le bouton « Cite this repository » de GitHub l’utilise).
