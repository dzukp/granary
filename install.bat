@echo off
setlocal EnableDelayedExpansion
chcp 65001 > nul

set "ROOT=%~dp0"
set "PACKAGES_DIR=%ROOT%distribs\packages"
set "VENV=%ROOT%.venv"

echo ========================================
echo  Installing Python dependencies
echo ========================================
echo.

where python > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python and add it to PATH.
    pause
    exit /b 1
)

if exist "%VENV%\Scripts\python.exe" (
    echo [1/2] Virtual environment already exists
) else (
    echo [1/2] Creating virtual environment...
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   + Virtual environment created
)

echo.

if not exist "%PACKAGES_DIR%" (
    echo [ERROR] Packages folder not found: %PACKAGES_DIR%
    pause
    exit /b 1
)

echo [2/2] Installing dependencies from %PACKAGES_DIR% ...
"%VENV%\Scripts\python.exe" -m pip install --no-index --find-links="%PACKAGES_DIR%" -r "%ROOT%app\deploy-requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo   + Dependencies installed

echo.
echo ========================================
echo  Install complete. Run start.bat
echo ========================================
pause
