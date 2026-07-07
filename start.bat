@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

title Shogun - The Tenshu

:: Navigate to script directory (handles shortcut launches)
cd /d "%~dp0"

echo.
echo   SHOGUN - Starting the Tenshu...
echo.

:: Check if venv exists (support both "venv" and ".venv" names)
set "VENV_DIR="
if exist "venv\Scripts\activate.bat" (
    set "VENV_DIR=venv"
)
if exist ".venv\Scripts\activate.bat" (
    set "VENV_DIR=.venv"
)

if "%VENV_DIR%"=="" (
    echo   ERROR: Virtual environment not found.
    echo   Looked for: venv\ and .venv\
    echo   Please run install.bat first.
    echo.
    echo   Press any key to close...
    pause >nul
    exit /b 1
)

:: Activate venv
echo   Using virtual environment: %VENV_DIR%
call %VENV_DIR%\Scripts\activate.bat

:: Build frontend on every launch so the served UI always matches this codebase.
:: This prevents stale laptop builds from hiding newly-added tabs or panels.
echo   Building frontend assets...
cd frontend
call npm run build --silent
if errorlevel 1 (
    cd ..
    echo.
    echo   ERROR: Frontend build failed.
    echo   Please run Shogun-Repair-Update.bat, then start Shogun again.
    echo.
    echo   Press any key to close...
    pause >nul
    exit /b 1
)
cd ..
echo   Frontend assets ready.

echo   Shogun is starting at http://localhost:8000
echo   Your browser will open automatically.
echo.
echo   Press Ctrl+C to stop the server.
echo.

:: Wait for backend to be ready, then open browser (background).
start "" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\open_shogun_when_ready.ps1" -Url "http://localhost:8000" -HealthUrl "http://localhost:8000/api/v1/health" -TimeoutSeconds 180 -LogPath "%CD%\logs\launcher-browser.log"

:: Start the server (blocking; keeps the window open)
python -m shogun

:: If the server exits, keep the window open so the user can see errors
echo.
echo   Shogun has stopped.
echo   Press any key to close this window.
pause >nul
