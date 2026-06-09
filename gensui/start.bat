@echo off
chcp 65001 >nul 2>&1
title Gensui - Fleet Command

:: -- Resolve paths relative to this script --
set "GENSUI_DIR=%~dp0"
for %%I in ("%GENSUI_DIR%..") do set "SHOGUN_ROOT=%%~fI"
set "VENV=%GENSUI_DIR%.venv"
set "VENV_PYTHON=%VENV%\Scripts\python.exe"

:: -- Check venv exists --
if not exist "%VENV_PYTHON%" (
    echo ERROR: No virtual environment found at %VENV%
    echo Run: python -m venv gensui\.venv
    pause
    exit /b 1
)

:: -- Set PYTHONPATH so 'gensui' package resolves --
set "PYTHONPATH=%SHOGUN_ROOT%"

:: -- Change to gensui dir for data/ paths --
cd /d "%GENSUI_DIR%"

:: -- Open browser after 3 seconds --
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8787"

echo.
echo  ==========================================
echo    GENSUI - Fleet Command Server
echo    http://localhost:8787
echo  ==========================================
echo.

:: -- Use venv python directly (no activate needed) --
"%VENV_PYTHON%" -m gensui
pause
