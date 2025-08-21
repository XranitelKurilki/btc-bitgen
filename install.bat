@echo off
echo =====================================
echo  BitGen Setup Script (Windows)
echo =====================================

REM Переход в папку проекта
cd /d %~dp0

REM Проверка наличия Python 3.8
where py >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python launcher (py) не найден. Установи Python 3.8 с https://www.python.org/downloads/release/python-3810/
    pause
    exit /b
)

echo [INFO] Создаём виртуальное окружение (venv) на Python 3.8...
py -3.8 -m venv venv

echo [INFO] Активируем окружение...
call venv\Scripts\activate

echo [INFO] Обновляем pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel

echo [INFO] Устанавливаем зависимости из requirements.txt...
pip install -r requirements.txt

echo =====================================
echo  Установка завершена!
echo  Для запуска используй run.bat
echo =====================================

pause
