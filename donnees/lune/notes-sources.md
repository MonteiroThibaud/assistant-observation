# Sources et méthodes des données lunaires

Ces notes sont les commentaires du code retiré à l'étape 3B (les corrections qu'il appliquait sont maintenant dans `formations.json`). Elles documentent l'origine de chaque correction.

- Corrections des notices lunaires (0.76) : positions et tailles du gazetier de nomenclature planétaire de l'UAI et de l'USGS (réseau de contrôle LOLA, téléchargement du 15 décembre 2012, fichier du projet LTVT), positions des modules lunaires Apollo (Davies et Colvin, 2000, mesures laser) et de Lunokhod 2 ;

- les mesures de rempart, de profondeur, de fond et de pic central ne sont refaites (relief LOLA de la NASA, calcul de l'outil) que pour les cratères dont le centre ou la taille ont changé, aucun tableau publié n'étant disponible ; les nombres cités dans les descriptions suivent ; noms corrigés (Walter devient Walther, Gruithuisen Gamma devient Mons Gruithuisen Gamma, Valentine devient Dôme Valentine) ; Rimae Liebig (nom abandonné par l'UAI) est retiré

- Altitude du sommet des montagnes, ajoutée à la description. Calcul étalonné sur des sommets mesurés par la NASA (LRO, LROC QuickMap : Mons Huygens, Mons Elbruz, Mons Mouton, Mons Cabeus, et des hauteurs publiées pour Pitón, Pico, Maraldi, Rümker, Gruithuisen Delta) :

- relief à 32 points par degré (et non 16), sommet = point le plus haut dans un disque de 0,4 fois la taille, plaine voisine = 10e centile de l'altitude dans l'anneau de 0,8 à 1,6 fois la taille (et non la médiane, trop haute au pied des Apennins) ; erreur moyenne de 0,08 km sur les hauteurs (0,41 km avant) et de 0,25 km sur l'altitude des sommets étroits (0,42 km avant ; les sommets plats de Mons Mouton et Mons Cabeus sont retrouvés à 0,03 km près) ;

- chaînes : maximum dans le disque de rayon moitié de la longueur, retenu seulement s'il dépasse de 150 m le terrain voisin ; les valeurs publiées par la NASA remplacent le calcul quand elles existent (NASA) ; altitudes comptées depuis la sphère de 1 737,4 km ; arrondi à 10 m

- Chaînes (0.77) : sommet dominant = point du disque de demi-longueur (hors remparts et éjectas des cratères de 15 km et plus) qui domine le plus la plaine locale (10e centile de l'altitude entre 30 et 50 km autour du point) ; hauteur = ce relief, altitude = celle du point, position = celle du point ; Apennins et Caucase : relevés de la NASA (Mons Huygens, Mons Elbruz) ; c'est la grandeur que donnent Rükl et les atlas (Montes Jura : 3 800 m sur la baie des Arcs-en-ciel)

- Classement des sources (0.77) : S1 NASA LROC QuickMap prime sur S2 relief LOLA calculé par l'application ; hauteurs relevées par Jim Singh (LROC QuickMap)

- Deux sommets de la région du pôle sud, nommés par l'UAI (valeurs LROC QuickMap) : visibles seulement quand la libration montre le pôle sud

- Formations ajoutées en 0.76 : cratères nommés de 3 à 30 km (positions et diamètres du gazetier de nomenclature planétaire de l'UAI et de l'USGS) et dômes de fiabilité A et B (Head et Gifford, 1980), repris des fichiers de points du projet LTVT ;

- [nom, longitude, latitude, diamètre en km (, fiabilité du dôme)] ; sans mesure de relief : la description dit où chercher (formation connue la plus proche)

- Mesures refaites en 0.77 sur le relief LOLA à 32 points par degré (et non 16), pour les cratères de 10 km et plus : rempart = moyenne de la crête moins l'altitude médiane du terrain à 1,4 à 2 rayons, profondeur = moyenne de la crête moins la médiane du fond, pic central = point le plus haut jusqu'à 0,2 rayon moins le fond (D ≥ 35 km, pic de 300 m et plus) ;

- contrôle sur 20 cratères aux valeurs sourcées (Pike 1976, Arthur 1974, LRO, Wood…) : écart médian de la profondeur −3 % ; ajout de 278 cratères nommés de l'UAI et de l'USGS visibles depuis la Terre (positions et diamètres officiels, mesures du même relief)

- Seconde profondeur (0.77) : depuis les crêtes les plus hautes du rempart = 90e centile des crêtes (une par tranche de 6° d'azimut) moins la médiane du fond ; plus proche des mesures anciennes faites avec les ombres (écart médian de +4 % sur onze références, contre −4 % pour la moyenne ; le maximum absolu surestime de 24 %, un seul pic voisin le gonfle : 3,06 km pour Platon à cause des Alpes)

- Mädler : pic central de 0,6 km (S12, Charles Wood, mesure des années 1970), faute de mesure de l'application (cratère de moins de 35 km)
