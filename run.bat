@echo off
REM Переход в папку проекта
cd /d %~dp0

REM Активация виртуального окружения
call venv\Scripts\activate

REM Запуск BitGen (передаются все аргументы, которые ты пишешь после run.bat)
python main.py --savedry %*

REM Деактивация окружения (по желанию)
deactivate
