@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ===================================
echo Metateks - Local Django (FAST)
echo ===================================

:: Load environment variables from .env.local
if exist .env.local (
    echo Loading environment from .env.local...
    for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env.local") do (
        set "%%a=%%b"
    )
)

:: Activate virtual environment
if exist .venv\Scripts\activate (
    echo Activating virtual environment...
    call .venv\Scripts\activate
) else (
    echo Virtual environment NOT FOUND in .venv. Run run_local.bat first.
    pause
    exit /b
)

:: Only migrations and runserver
echo Running migrations...
python manage.py migrate

echo Starting Django development server...
python manage.py runserver 0.0.0.0:8000

pause
