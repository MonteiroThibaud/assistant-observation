@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Relief fin de la Lune avec SLDEM2015 - Assistant d'observation
set "PYVER=3.12.8"
set "PYDIR=%~dp0python-portable"
set "CARTE=ldem_64_uint.tif"
set "URLCARTE=https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/ldem_64_uint.tif"
set "SLDEM=SLDEM2015_128_60S_60N_000_360_FLOAT.IMG"
set "URLSLDEM=https://imbrium.mit.edu/DATA/SLDEM2015/GLOBAL/FLOAT_IMG/SLDEM2015_128_60S_60N_000_360_FLOAT.IMG"
set "URLLBL=https://imbrium.mit.edu/DATA/SLDEM2015/GLOBAL/FLOAT_IMG/SLDEM2015_128_60S_60N_000_360_FLOAT.LBL"

echo.
echo ==============================================================
echo   Relief fin de la Lune avec SLDEM2015
echo   Assistant d'observation
echo ==============================================================
echo.
echo Ce programme fait tout seul : il telecharge Python portable
echo (11 Mo, s'il n'est pas deja la), deux modules (30 Mo), la carte
echo SLDEM2015 de la NASA (2,8 Go) et, si elle n'est pas deja la, la
echo carte LOLA a 64 points par degre (506 Mo), puis il fabrique le
echo relief fin. Il n'installe rien sur Windows. Prevoyez 4 Go d'espace
echo libre, 3 Go de memoire libre et 30 a 90 minutes selon la connexion.
echo Ne fermez pas cette fenetre.
echo.
pause

rem ---------- 1. Python portable ----------
if exist "%PYDIR%\python.exe" goto python_ok
echo.
echo [1/5] Telechargement de Python portable...
curl.exe -L --fail --retry 3 -o "%~dp0python-embed.zip" "https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-embed-amd64.zip"
if errorlevel 1 goto erreur
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Force -LiteralPath '%~dp0python-embed.zip' -DestinationPath '%PYDIR%'"
if errorlevel 1 goto erreur
del "%~dp0python-embed.zip" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content -LiteralPath '%PYDIR%\python312._pth') -replace '#import site','import site' | Set-Content -LiteralPath '%PYDIR%\python312._pth'"
if errorlevel 1 goto erreur
:python_ok

rem ---------- 2. Modules ----------
if exist "%PYDIR%\modules-relief-ok.txt" goto modules_ok
echo.
echo [2/5] Installation des modules (numpy, tifffile)...
if exist "%PYDIR%\Scripts\pip.exe" goto pip_ok
curl.exe -L --fail --retry 3 -o "%~dp0get-pip.py" "https://bootstrap.pypa.io/get-pip.py"
if errorlevel 1 goto erreur
"%PYDIR%\python.exe" "%~dp0get-pip.py" --no-warn-script-location
if errorlevel 1 goto erreur
del "%~dp0get-pip.py" >nul 2>&1
:pip_ok
"%PYDIR%\python.exe" -m pip install --no-warn-script-location numpy tifffile
if errorlevel 1 goto erreur
echo ok> "%PYDIR%\modules-relief-ok.txt"
:modules_ok

rem ---------- 3. Carte LOLA a 64 points par degre (poles et raccord) ----------
echo.
echo [3/5] Carte LOLA a 64 points par degre (506 Mo, deja la si vous avez fait l'etape precedente)...
curl.exe -L --fail --retry 30 --retry-delay 10 --speed-limit 20000 --speed-time 60 -C - -o "%~dp0%CARTE%" "%URLCARTE%"
if errorlevel 1 goto erreur
for %%A in ("%~dp0%CARTE%") do if %%~zA LSS 400000000 goto carte_trop_petite

rem ---------- 4. SLDEM2015 ----------
echo.
echo [4/5] Carte SLDEM2015 (2,8 Go). Si le telechargement s'arrete plus d'une minute, il reprend tout seul.
echo      En cas de blocage prolonge : fermez cette fenetre et relancez le .bat (le telechargement reprend ou il en etait).
curl.exe -L --fail --retry 30 --retry-delay 10 --speed-limit 20000 --speed-time 60 -C - -o "%~dp0%SLDEM%" "%URLSLDEM%"
if errorlevel 1 goto erreur
curl.exe -L --fail -o "%~dp0SLDEM2015_128_60S_60N_000_360_FLOAT.LBL" "%URLLBL%" >nul 2>&1
for %%A in ("%~dp0%SLDEM%") do if %%~zA LSS 2800000000 goto sldem_trop_petite

rem ---------- 5. Fabrication ----------
echo.
echo [5/5] Fabrication du relief fin (10 a 30 minutes)...
"%PYDIR%\python.exe" "%~dp0fabrique_relief_sldem.py" "%~dp0%SLDEM%" "%~dp0%CARTE%" --sortie "%~dp0relief-sldem"
if errorlevel 1 goto erreur

echo.
echo ==============================================================
echo   TERMINE.
echo   Envoyez le fichier  relief-sldem.zip  (dossier : %~dp0)
echo   dans la conversation avec Claude.
echo ==============================================================
echo.
pause
exit /b 0

:carte_trop_petite
echo.
echo La carte LOLA telechargee est incomplete. Supprimez le fichier %CARTE% puis relancez ce programme.
goto erreur

:sldem_trop_petite
echo.
echo La carte SLDEM2015 telechargee est incomplete. Relancez ce programme (le telechargement reprend).
goto erreur

:erreur
echo.
echo ==============================================================
echo   UN PROBLEME EST SURVENU (voir les messages ci-dessus).
echo   Relancez simplement ce programme : les etapes deja faites
echo   ne sont pas refaites. Si le probleme persiste, envoyez une
echo   capture de cette fenetre a Claude.
echo ==============================================================
echo.
pause
exit /b 1
