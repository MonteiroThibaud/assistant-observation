@echo off
chcp 65001 >nul
echo Telechargement de 57 photos du ciel profond (environ 5 minutes)...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Telecharger-DSS.ps1"
echo.
echo Appuie sur une touche pour fermer cette fenetre.
pause >nul
