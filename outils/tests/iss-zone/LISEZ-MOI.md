# Tests du calcul des transits de l'ISS sur une zone

Ils chargent le calcul direct (`issScan`) et le calcul inverse (`iszGen`) depuis `src/modele-page.html`, avec satellite.js 5.0.0 et Astronomy Engine 2.1.19 (les versions de la page).

Variable facultative `ALT` : altitude du lieu en mètres (0 par défaut ; 400 m dans l'application), prise en compte à la fois par le calcul inverse et par le calcul direct (`ALT=400 node calcul_inverse.js 365 25`, puis les autres tests avec la même valeur).

```
npm install satellite.js@5.0.0 astronomy-engine@2.1.19
MODELE=../../../src/modele-page.html node calcul_inverse.js 365 25      # événements ; écrit /tmp/isz_events.json
MODELE=... node completude_grille.js 365 25 5                            # compare à un calcul direct sur une grille de sites (pas de 5 km)
MODELE=... node aller_retour_et_largeur.js                               # transit central au point du couloir, durée, largeur à 0,8 et 1,25 fois la demi-largeur
MODELE=... node un_passage.js                                            # un cas : calcul direct au centre et au point du couloir
MODELE=... node liste_pour_navigateur.js 90 100                          # liste (astre, instant) à comparer à l'affichage de la page
```
Résultats du 6 novembre 2026 (TLE de démonstration, centre de Roanne) : 37 passages avec l'astre à 5° ou plus sur 365 jours dans 25 km : tous retrouvés par la grille de 81 sites, aucun en trop ; 37 transits centraux confirmés au point du couloir (écart d'heure 0,00 s, de durée au plus 0,01 s) ; à 0,8 fois la demi-largeur : transit dans 74 cas sur 74 ; à 1,25 fois : aucun transit dans 74 cas sur 74.

Avec une altitude de 400 m (et de 1 000 m pour l'aller-retour et la largeur) : mêmes résultats : 37 transits retrouvés par la grille et aucun manquant à 400 m ; transits centraux confirmés 37 sur 37 (38 sur 38 à 1 000 m) ; largeur du couloir confirmée (74 sur 74 et 74 sur 74 à 400 m ; 76 sur 76 et 76 sur 76 à 1 000 m).
