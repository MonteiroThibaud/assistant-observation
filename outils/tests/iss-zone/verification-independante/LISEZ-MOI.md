# Vérification indépendante des transits de l'ISS sur une zone (10 novembre 2026)

But : contrôler le calcul de l'application avec un TLE RÉEL et un calcul qui ne partage rien avec elle (autre propagateur SGP4, autres éphémérides du Soleil et de la Lune).

- TLE : `tle_reel_2026-11-09.txt` (ISS, époque du 9 novembre 2026 à 20:27:37 UTC), relevé sur https://satellitemap.space/sat/25544 le 10 novembre 2026 (sommes de contrôle des deux lignes vérifiées).
- Application : `verif_app.js` charge le code de la page (satellite.js 5.0.0 et Astronomy Engine 2.1.19), comme les autres tests de ce dossier. `MODELE=../../../src/modele-page.html node verif_app.js 60 40` (60 jours, zone de 40 km autour de Roanne, altitude 400 m ; écrit `/tmp/isz_events_reel.json`).
- Calcul indépendant : `indep.py` (bibliothèque : `pip install sgp4 astropy`) ; `scan_ind.py 60` balaie 60 jours, repère les fenêtres où l'ISS et l'astre sont proches puis teste une grille de 197 lieux (pas de 5 km) dans la zone, à 0,1 s près (écrit `/tmp/ind_events.json`). Le contrôle point par point (transit central, durée, azimut et hauteur de l'astre, largeur du couloir) est fait par le script du journal 0.89, entrée 42.

Résultats du 10 novembre 2026 : voir le journal 0.89, entrée 42.
