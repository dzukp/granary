@echo off
chcp 65001 > nul
echo [1/3] Создание виртуального окружения...
python -m venv .venv
echo [2/3] Активация и обновление pip...
call .venv\Scripts\python.exe -m pip install --upgrade pip > nul
echo [3/3] Установка зависимостей...
call .venv\Scripts\python.exe -m pip install -r app\requirements.txt
echo Готово. Для запуска выполните start.bat
pause
