@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions DisableDelayedExpansion
title Shogun - In-place Update Repair

set "REPO=AlphaHorizon-AI/Shogun"
set "BRANCH=main"
set "INSTALL_DIR=%USERPROFILE%\Shogun"
if exist "%~dp0version.json" set "INSTALL_DIR=%~dp0"
if "%INSTALL_DIR:~-1%"=="\" set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

set "WORK_DIR=%TEMP%\shogun-inplace-update"
set "ZIP_FILE=%WORK_DIR%\shogun-update.zip"
set "EXTRACT_DIR=%WORK_DIR%\extract"

echo.
echo  SHOGUN IN-PLACE UPDATE
echo  -----------------------
echo  Installation: %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%\version.json" (
    echo  ERROR: Shogun was not found at "%INSTALL_DIR%".
    echo  Place this file inside the Shogun folder and run it again.
    pause
    exit /b 1
)

if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
mkdir "%EXTRACT_DIR%" >nul 2>&1

echo  Downloading the latest update...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri 'https://github.com/%REPO%/archive/refs/heads/%BRANCH%.zip' -OutFile '%ZIP_FILE%'" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { Add-Type -AssemblyName System.IO.Compression.FileSystem; $z=[IO.Compression.ZipFile]::OpenRead('%ZIP_FILE%'); $z.Dispose() } catch { Remove-Item -LiteralPath '%ZIP_FILE%' -Force -ErrorAction SilentlyContinue; exit 1 }" >nul 2>&1

if not exist "%ZIP_FILE%" (
    echo.
    echo  GitHub requires access for this update source.
    echo  Enter a fine-grained GitHub token with read access to Shogun.
    echo  The token will be hidden and is not saved by this repair tool.
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$ProgressPreference='SilentlyContinue'; $s=Read-Host 'Token' -AsSecureString; $b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); try { $t=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($b); $h=@{Authorization=('Bearer '+$t);Accept='application/vnd.github+json';'User-Agent'='Shogun-Updater'}; Invoke-WebRequest -UseBasicParsing -Headers $h -Uri 'https://api.github.com/repos/%REPO%/zipball/%BRANCH%' -OutFile '%ZIP_FILE%'; Add-Type -AssemblyName System.IO.Compression.FileSystem; $z=[IO.Compression.ZipFile]::OpenRead('%ZIP_FILE%'); $z.Dispose() } catch { Remove-Item -LiteralPath '%ZIP_FILE%' -Force -ErrorAction SilentlyContinue; exit 1 } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b) }"
)

if not exist "%ZIP_FILE%" (
    echo  ERROR: The update could not be downloaded. Check the token and connection.
    pause
    exit /b 1
)

echo  Extracting update...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%ZIP_FILE%' -DestinationPath '%EXTRACT_DIR%' -Force"
for /d %%D in ("%EXTRACT_DIR%\*") do if not defined SOURCE_DIR set "SOURCE_DIR=%%~fD"

if not defined SOURCE_DIR (
    echo  ERROR: The downloaded update package was empty.
    pause
    exit /b 1
)

echo  Updating application files while preserving your data and settings...
robocopy "%SOURCE_DIR%" "%INSTALL_DIR%" /E /R:2 /W:1 ^
  /XD "%INSTALL_DIR%\data" "%INSTALL_DIR%\venv" "%INSTALL_DIR%\.venv" "%INSTALL_DIR%\node_modules" "%INSTALL_DIR%\frontend\node_modules" "%INSTALL_DIR%\configs" "%INSTALL_DIR%\vault" "%INSTALL_DIR%\logs" "%INSTALL_DIR%\scratch" "%INSTALL_DIR%\.states" "%INSTALL_DIR%\.git" __pycache__ ^
  /XF .env >nul
if errorlevel 8 (
    echo  ERROR: Some application files could not be updated.
    pause
    exit /b 1
)

echo  Refreshing dependencies in the existing environment...
if exist "%INSTALL_DIR%\.venv\Scripts\python.exe" (
    "%INSTALL_DIR%\.venv\Scripts\python.exe" -m pip install -e "%INSTALL_DIR%[office]" --disable-pip-version-check
) else if exist "%INSTALL_DIR%\venv\Scripts\python.exe" (
    "%INSTALL_DIR%\venv\Scripts\python.exe" -m pip install -e "%INSTALL_DIR%[office]" --disable-pip-version-check
)

if exist "%INSTALL_DIR%\frontend\package.json" (
    pushd "%INSTALL_DIR%\frontend"
    call npm install --silent
    call npm run build --silent
    popd
)

rmdir /s /q "%WORK_DIR%" >nul 2>&1

echo.
echo  Update complete. Your data, settings, vault, and existing environment were preserved.
echo  Restart Shogun now. Future updates can be installed from the Updates screen.
echo.
pause
