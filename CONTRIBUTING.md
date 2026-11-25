# Contribuer

Merci de ton intérêt pour Assistant d’observation. Ce projet suit le [code de conduite](CODE_OF_CONDUCT.md).

## État du projet

Projet personnel, gratuit et non commercial, maintenu par une seule personne sans délai de réponse garanti. Les remarques, les signalements d’erreurs et les propositions sont les bienvenus ; toutes ne pourront pas être suivies.

## Signaler une erreur ou proposer une amélioration

Ouvre un ticket (« issue ») en précisant : la version affichée dans « Informations », l’appareil et le navigateur, ce que tu as fait, ce que tu attendais et ce qui s’est passé. Pour une erreur de données (position, magnitude, description), cite la source de référence. Pour une faille de sécurité, ne crée pas de ticket public : voir `SECURITY.md`.

## Proposer une modification

1. Fais une copie du dépôt (« fork »), crée une branche, puis propose ta modification par une demande de fusion (« pull request »).
2. Le code est dans `src/modele-page.html` et les connaissances dans `donnees/` ; la page web et le site installé s’en déduisent par `python3 outils/construction/construire.py . ../livrables` (voir `donnees/LISEZ-MOI.md`). On modifie toujours les sources, jamais la page assemblée. Les éléments hors licence GPL sont dans `donnees-hors-gpl/` : n’y ajoute rien sans accord écrit du titulaire des droits.
3. Vérifie ta modification dans un navigateur (les scripts `outils/tests/` utilisent Playwright pour Python) : écrans de 411 × 850, 360 × 780, 320 × 568, 891 × 411 et 1280 × 800, mode rouge compris. Une modification de données ou de construction doit laisser les empreintes des tables inchangées, sauf si c’est son objet (voir `outils/verification/`).
4. Toute donnée nouvelle doit être vérifiée sur une source fiable et sa licence indiquée dans `DONNEES-ET-LICENCES.md` et dans la rubrique « Informations » ; pas de données générées par une IA sans vérification.
5. Les textes de l’application s’adressent à l’utilisateur ; ils sont en français et décrivent l’état actuel de l’outil, sans parler d’évolution.

## Licence de tes contributions

En proposant une modification, tu acceptes qu’elle soit publiée sous la même licence que le code : GNU GPL version 3 ou ultérieure. N’ajoute ni code ni données dont tu ne peux pas garantir la licence.

## Contributions assistées par une IA

Elles sont acceptées à deux conditions : tu les as relues et testées toi-même, et tu l’indiques dans la description de ta demande (l’application elle-même a été écrite en très grande partie avec l’assistance d’une IA générative, sous la direction de son auteur). Aucun contenu protégé par des droits d’auteur, aucune donnée inventée.

## Respect de la vie privée

La position de l’utilisateur ne quitte jamais l’appareil : aucun appel à un service en ligne pour la traiter. Toute fonction qui utilise la position est facultative. N’ajoute aucune ressource chargée depuis un serveur tiers.
