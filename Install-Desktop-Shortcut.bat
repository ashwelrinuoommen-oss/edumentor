@echo off
title Install EduMentor Desktop Shortcut
cd /d "%~dp0"
echo Installing EduMentor desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Desktop-Shortcut.ps1"
echo.
pause
