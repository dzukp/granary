@echo off
chcp 65001 > nul

where python > nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден. Установите Python и добавьте его в PATH.
    pause
    exit /b 1
)

echo [1/3] Создание виртуального окружения...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось создать виртуальное окружение.
    pause
    exit /b 1
)
echo   + Виртуальное окружение создано

echo [2/3] Обновление pip...
call .venv\Scripts\python.exe -m pip install --upgrade pip > nul
if %errorlevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Не удалось обновить pip, продолжаем...
) else (
    echo   + pip обновлён
)

echo [3/3] Установка зависимостей...
call .venv\Scripts\python.exe -m pip install -r app\requirements.txt
if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось установить зависимости.
    pause
    exit /b 1
)
echo   + Зависимости установлены

echo.
echo ========================================
echo  Готово. Запустите start.bat
echo ========================================
pause
