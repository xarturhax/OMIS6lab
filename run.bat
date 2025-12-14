@echo off
REM Активация venv, если используешь виртуальное окружение
REM call venv\Scripts\activate

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
