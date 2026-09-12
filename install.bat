@echo off
setlocal EnableDelayedExpansion
chcp 65001 > nul

set "ROOT=%~dp0"
set "PY_INSTALLER=%ROOT%distribs\python-3.14.7-amd64.exe"
set "PY_DIR=%ROOT%distribs\python"
set "PACKAGES_DIR=%ROOT%distribs\packages"
set "VENV=%ROOT%.venv"

echo ========================================
echo  Установка Python и зависимостей
echo ========================================
echo.

rem ------------------------------------------------------------------
rem 1. Установка Python из дистрибутива (offline)
rem ------------------------------------------------------------------
if not exist "%PY_INSTALLER%" (
    echo [ОШИБКА] Не найден установщик Python: %PY_INSTALLER%
    pause
    exit /b 1
)

if exist "%PY_DIR%\python.exe" (
    echo [1/3] Python уже установлен: %PY_DIR%
) else (
    echo [1/3] Установка Python из дистрибутива...
    "%PY_INSTALLER%" /quiet InstallAllUsers=0 TargetDir="%PY_DIR%" \
        Include_launcher=1 Include_test=0 PrependPath=0 Shortcuts=0 \
        AssociateFiles=0 Include_doc=0 Include_dev=0 Include_tcltk=0 \
        Include_pip=1
    if %errorlevel% neq 0 (
        echo [ОШИБКА] Не удалось установить Python.
        pause
        exit /b 1
    )
    echo   + Python установлен в %PY_DIR%
)

if not exist "%PY_DIR%\python.exe" (
    echo [ОШИБКА] python.exe не найден в %PY_DIR%
    pause
    exit /b 1
)

echo.

rem ------------------------------------------------------------------
rem 2. Создание виртуального окружения
rem ------------------------------------------------------------------
if exist "%VENV%\Scripts\python.exe" (
    echo [2/3] Виртуальное окружение уже существует
) else (
    echo [2/3] Создание виртуального окружения...
    "%PY_DIR%\python.exe" -m venv "%VENV%"
    if %errorlevel% neq 0 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение.
        pause
        exit /b 1
    )
    echo   + Виртуальное окружение создано
)

echo.

rem ------------------------------------------------------------------
rem 3. Установка зависимостей из distribs\packages (offline)
rem ------------------------------------------------------------------
if not exist "%PACKAGES_DIR%" (
    echo [ОШИБКА] Не найдена папка с пакетами: %PACKAGES_DIR%
    pause
    exit /b 1
)

echo [3/3] Установка зависимостей из %PACKAGES_DIR% ...
"%VENV%\Scripts\python.exe" -m pip install --no-index --find-links="%PACKAGES_DIR%" -r "%ROOT%app\requirements.txt"
if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось установить зависимости.
    pause
    exit /b 1
)
echo   + Зависимости установлены

echo.
echo ========================================
echo  Установка завершена. Запустите start.bat
echo ========================================
pause
