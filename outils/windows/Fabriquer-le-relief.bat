@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Relief fin de la Lune - Assistant d'observation
set "PYVER=3.12.8"
set "PYDIR=%~dp0python-portable"
set "CARTE=ldem_64_uint.tif"
set "URLCARTE=https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/ldem_64_uint.tif"

echo.
echo ==============================================================
echo   Relief fin de la Lune - Assistant d'observation
echo ==============================================================
echo.
echo Ce programme fait tout seul : il telecharge un Python portable
echo (11 Mo, s'il n'est pas deja la), deux modules (30 Mo) et la carte
de deplacement LOLA de la NASA a 64 points par degre (506 Mo), puis il
fabrique le relief fin. Il n'installe rien sur Windows. Compte 10 a 30
minutes selon la connexion et 3 Go de memoire libre. Ne fermez pas
cette fenetre.
echo.
pause

rem ---------- 1. Python portable ----------
if exist "%PYDIR%\python.exe" goto python_ok
echo.
echo [1/4] Telechargement de Python portable...
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
echo [2/4] Installation des modules (numpy, tifffile)...
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

rem ---------- 3. Carte de deplacement LOLA ----------
echo.
echo [3/4] Carte de deplacement LOLA de la NASA (506 Mo, reprise possible si la connexion s'interrompt)...
curl.exe -L --fail --retry 5 -C - -o "%~dp0%CARTE%" "%URLCARTE%"
if errorlevel 1 goto erreur
for %%A in ("%~dp0%CARTE%") do if %%~zA LSS 400000000 goto carte_trop_petite

rem ---------- 4. Fabrication ----------
echo.
echo [4/4] Fabrication du relief fin (10 a 20 minutes)...
"%PYDIR%\python.exe" "%~dp0fabrique_relief_lune.py" "%~dp0%CARTE%" --sortie "%~dp0relief-lune"
if errorlevel 1 goto erreur

echo.
echo ==============================================================
echo   TERMINE.
echo   Envoyez le fichier  relief-lune.zip  (dossier : %~dp0)
echo   dans la conversation avec Claude.
echo ==============================================================
echo.
pause
exit /b 0

:carte_trop_petite
echo.
echo La carte telechargee est incomplete. Supprimez le fichier %CARTE% puis relancez ce programme.
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
