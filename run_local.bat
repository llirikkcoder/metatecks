@echo off
REM Local Django development startup script for Windows

echo ===================================
echo Metateks - Local Django Development
echo ===================================
echo.

REM Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created.
)

REM Activate venv
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements-pip.txt

REM Load .env.local for local development
set ENV_LOCAL=.env.local
if exist %ENV_LOCAL% (
    echo Loading environment from %ENV_LOCAL%...
    for /f "tokens=*" %%a in ('type %ENV_LOCAL%') do set %%a
)

REM Create logs directory if not exists
if not exist "logs" mkdir logs

REM Run migrations
echo.
echo Running migrations...
python manage.py migrate

REM Collect static files
echo.
echo Collecting static files...
python manage.py collectstatic --noinput

REM Start development server
echo.
echo ===================================
echo Starting Django development server
echo URL: http://localhost:8000
echo ===================================
python manage.py runserver
