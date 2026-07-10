@echo off
REM ═══════════════════════════════════════════════════════════════
REM  SHOGUN AFM — Docker Installer (Windows)
REM
REM  Thin shim: runs installer\install.mjs inside an ephemeral
REM  node:20-alpine container, so the host only ever needs Docker —
REM  no Node.js install required. See installer\install.mjs for the
REM  actual logic (all the real logic lives there, not duplicated
REM  between .sh and .bat).
REM
REM  This script never runs "docker compose" — it only prepares
REM  config and prints the exact command for you to review and run.
REM
REM  Usage:
REM    Shogun-AFM-Docker-Install.bat [--clean | --image[=TAG]] [--profile server]
REM    Shogun-AFM-Docker-Install.bat --help
REM ═══════════════════════════════════════════════════════════════

setlocal

set "SCRIPT_DIR=%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. See: https://docs.docker.com/get-docker/
    exit /b 1
)

docker run --rm -i ^
    -v "%SCRIPT_DIR%:/repo" ^
    -w /repo/installer ^
    node:20-alpine ^
    sh -c "npm ci --silent --no-progress && node install.mjs %*"

endlocal
