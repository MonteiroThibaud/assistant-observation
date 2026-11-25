# Mode « Explications allégées » : décisions du 20 novembre 2026 (version de travail 0.97)

Numéros : S = Système solaire, P = Détail planète, C = Ciel profond et petits corps, O = À l'oculaire, L = Lune (planches dans `diagnostic-allege/`). Paramètres n'est pas concerné. Les numéros non cités par l'utilisateur sont gardés. Les avertissements de sécurité (filtre solaire) et l'alerte sur l'âge du TLE sont toujours visibles.

## Décisions par texte

| N° | Début du texte | Nature | Décision |
|---|---|---|---|
| S1 | observable levée mais en plein jour ou trop basseTrait gris : l'heure actuelle ; noms dorés : observables en c… | explication (légende du tableau) | masqué |
| S2 | Soleil : coucher 17:07, lever le lendemain à 07:52. | donnée | gardé |
| S3 | Nuit noire de 18:55 à 06:04. Ciel noir sans Lune de 03:53 à 06:03 ; Lune (éclairée à 83 %) présente de 18:56 à… | donnée | gardé |
| S4 | Le TLE a 8 jours : la précision diminue, mets-le à jour dans Paramètres ›. | alerte (âge du TLE) | gardé (alerte : toujours visible) |
| S5 | En doré : le transit le plus proche dans le temps. * Au-delà de 3 jours après l'époque du TLE, les dates sont … | explication + avertissement | masqué en partie (l'avertissement « Soleil : filtre solaire obligatoire » reste) |
| S6 | Zone de 30 km autour de « Position GPS » (46,0345° N · 4,0720° E, altitude 400 m), du ven. 20 nov. au dim. 20 … | donnée (résumé de la zone) | gardé |
| S7 | Fais glisser la carte pour te déplacer, pince ou touche deux fois pour zoomer ; le zoom arrière va jusqu’à ×0,… | explication (aide de la carte) | masqué |
| S8 | Les heures sont celles du fuseau de ton téléphone. Sur la carte, les couloirs de la Lune sont rayés en blanc e… | explication + alerte | masqué en partie (l'alerte sur l'âge du TLE reste) |
| P1 | Gibbeuse croissante, éclairée à 80 %, diamètre apparent 31,5′. | donnée | gardé |
| P2 | Maintenant : hauteur 48°, direction SSO (199°). | donnée | gardé |
| P3 | Terminateur à 44,6° O au coucher du Soleil (17:07). Colongitude 44,6°. Près du terminateur : Aristarque, Gasse… | donnée + aide | gardé |
| P4 | Listes de formations affichées : À voir ce soir. Choisir les listes › | état des listes | gardé |
| C1 | Nuit noire de 18:55 à 06:04. Ciel noir sans Lune de 03:53 à 06:03 ; Lune (éclairée à 83 %) présente de 18:56 à… | donnée | gardé |
| C2 | Listes affichées : Messier. Choisir les listes › | état des listes | gardé |
| O1 | Maintenant : hauteur 48°, direction SSO (199°). | donnée | gardé |
| O2 | ★ 5 étoiles dans le champ, de magnitude 7,8 à 10,3. Limite du catalogue : magnitude 10,5. | donnée | gardé |
| O3 | Ethos 17 mm : grossissement ×88, champ réel 1,1°. Lune : 32′, vue comme un objet de 46,4° à l'œil nu (89,3 foi… | donnée + aide | masqué en partie (la fin « Fais glisser le ciel au doigt… ramène X au centre. ») |
| O4 | Le télescope (avec son sens de l'image par défaut), tes oculaires et barlows et le chercheur se règlent dans l… | aide (liens vers Matériel) | gardé |
| L1 | Plaine de 172 km au fond très sombre près du bord ouest : l'une des taches les plus sombres de la face visible… | contenu | gardé |
| L2 | Quatre axes : nord-sud (trait doré), nord-est–sud-ouest (trait clair), est-ouest (tirets), nord-ouest–sud-est … | explication (profil du relief) | gardé |
| L3 | Ouvrir la zone dans LROC QuickMap › (en ligne ; l'outil « Profil » y trace le relief complet de la NASA) | lien (LROC QuickMap) | gardé |
| L4 | Mesures faites sur le relief de la Lune embarqué, à environ 0,3 km près ; le rempart est mesuré par rapport au… | explication (méthode de mesure) | masqué |
| L5 | Gibbeuse croissante, éclairée à 80 %. Terminateur à 44,6° O au coucher du Soleil (17:07). Image orientée comme… | donnée | gardé |
| L6 | Fais glisser pour te déplacer, pince ou touche deux fois pour zoomer. Touche un nom pour lire sa description ;… | explication (aide des gestes) | masqué |

## Textes d'information réduits en mode allégé (hors numérotation)

- **Telrad** : « Telrad : cadre de 11° sur 11°, cercles rouges de 0,5°, 2° et 4° au centre, vue comme à l'œil nu (zénith en haut). Constellation au centre du champ : Poissons. Vue à 23:10. » (masqués : la phrase d'aide au doigt et « Z : direction du zénith »).
- **Chercheur** : « Chercheur 9×50 : champ réel de 5,6° sur le ciel. Constellation au centre du champ : Poissons. Vue à 23:10. » (masqués : l'optique, la consigne de pointage, l'aide au doigt, « Z : direction du zénith »).

## Carte de la Lune en mode allégé

La carte récupère la hauteur de l'aide masquée (rectangle vertical) et laisse au-dessus de la barre d'onglets la place d'une ligne vide et de trois lignes de texte (réglage `window.MAP_LIGHT_LIGNES`, 3 par défaut).
