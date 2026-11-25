# Politique de sécurité

## Versions prises en charge

Seule la dernière version publiée (1.0 au 25 novembre 2026) reçoit des corrections.

## Signaler une vulnérabilité

Ne crée pas de ticket public pour une faille de sécurité. Utilise l’une de ces voies :

- le signalement privé de GitHub : onglet « Security » du dépôt, « Report a vulnerability » ;
- ou un courriel à **contact.assistantobservation@laposte.net**, avec « Sécurité » dans l’objet.

Indique la version affichée dans « Informations », l’appareil et le navigateur, les étapes pour reproduire le problème et son effet. Le projet est maintenu par une seule personne : les réponses se font au mieux, sans délai garanti.

## Périmètre

L’application est une page statique sans serveur ni compte : tous les calculs et toutes les données de l’utilisateur (position, réglages, carnet) restent sur l’appareil. Sont dans le périmètre : une fuite de données personnelles (position comprise), l’exécution de code par un fichier importé (éléments d’orbite du Minor Planet Center, TLE), un défaut du service worker qui servirait un contenu altéré, ou l’ajout d’une ressource chargée depuis un serveur tiers. Les requêtes sortantes de l’application se limitent aux mises à jour facultatives (Minor Planet Center, CelesTrak) et à celles de l’application elle-même auprès de son hébergeur.
