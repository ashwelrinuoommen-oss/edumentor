@echo off
setlocal enabledelayedexpansion
title EduMentor — Launcher

:: Set current directory to project root
cd /d "%~dp0"

echo =======================================================
echo           EduMentor — AI Study Companion
echo =======================================================
echo.

set "PORT=8501"
set "HEALTH_URL=http://127.0.0.1:%PORT%/_stcore/health"
set "APP_URL=http://localhost:%PORT%"

:: 1. Detect Python Environment
set "PYTHON_CMD="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
    echo [INFO] Using virtual environment: .venv
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
    echo [INFO] Using virtual environment: venv
) else (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=python"
        echo [INFO] Using system Python
    ) else (
        echo [ERROR] Python was not found on your system or in PATH.
        echo Please install Python 3.10+ from https://www.python.org/
        echo and ensure "Add python.exe to PATH" is checked during setup.
        pause
        exit /b 1
    )
)

:: Verify Streamlit is installed
"%PYTHON_CMD%" -c "import streamlit" >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Streamlit is not installed in the selected Python environment.
    echo Please install dependencies by running:
    echo     "%PYTHON_CMD%" -m pip install -r requirements.txt
    pause
    exit /b 1
)

:: 2. Check if EduMentor is already running
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -Uri '%HEALTH_URL%' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if !errorlevel! equ 0 (
    echo [INFO] EduMentor is already running on %APP_URL%.
    echo Opening browser window...
    goto :OPEN_BROWSER
)

:: 3. Launch EduMentor Streamlit Server in a separate window
echo [INFO] Starting EduMentor server on port %PORT%...
start "EduMentor Server" /min "%PYTHON_CMD%" -m streamlit run app.py --server.headless=true --server.port=%PORT%

:: 4. Wait for server to become healthy
echo [INFO] Waiting for EduMentor to initialize...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ready = $false; for ($i=0; $i -lt 35; $i++) { try { $r = Invoke-WebRequest -Uri '%HEALTH_URL%' -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop; if ($r.StatusCode -eq 200) { $ready = $true; break } } catch {}; Start-Sleep -Milliseconds 800; Write-Host '.' -NoNewline }; if ($ready) { Write-Host ' [READY]'; exit 0 } else { Write-Host ' [TIMEOUT]'; exit 1 }"
if !errorlevel! neq 0 (
    echo.
    echo [WARNING] Server took longer than expected to report ready status.
    echo Opening browser anyway...
)

:OPEN_BROWSER
:: 5. Launch browser (Prefer clean app-window mode if Edge or Chrome is installed)
set "BROWSER_EXE="
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_EXE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_EXE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
) else if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_EXE=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_EXE=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
)

if defined BROWSER_EXE (
    start "" "%BROWSER_EXE%" --app="%APP_URL%"
) else (
    start "" "%APP_URL%"
)

echo.
echo =======================================================
echo   EduMentor is running successfully!
echo   Application URL: %APP_URL%
echo =======================================================
echo.
echo   * Keep the "EduMentor Server" minimized window open
echo     while you are studying.
echo.
echo   * To stop EduMentor when finished:
echo     Close the "EduMentor Server" window, or close
echo     your browser session.
echo.
echo =======================================================
ping 127.0.0.1 -n 4 >nul 2>&1
exit /b 0
