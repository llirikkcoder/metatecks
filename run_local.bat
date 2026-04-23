@echo off
chcp 65001 >nul
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
pip install -r requirements-conda.txt
pip install psycopg2-binary
pip install -r requirements-pip.txt

REM Load .env.local for local development
set ENV_LOCAL=.env.local
if exist %ENV_LOCAL% (
    echo Loading environment from %ENV_LOCAL%...
    for /f "usebackq tokens=* eol=#" %%a in ("%ENV_LOCAL%") do set %%a
)

REM Create logs directory if not exists
if not exist "logs" mkdir logs

REM Run migrations
echo.
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

REM Load fixtures if not already loaded
if exist ".fixtures_loaded" goto :SKIP_FIXTURES

echo.
echo Loading initial data (fixtures)...
python manage.py loaddata fixtures/20240722_addresses.json || echo SKIP: addresses
python manage.py loaddata fixtures/20240722_settings.json || echo SKIP: settings
python manage.py loaddata fixtures/20240722_content.json || echo SKIP: content (some models deprecated)
python manage.py loaddata fixtures/20240901_categories_and_models.json || echo SKIP: categories
python manage.py loaddata fixtures/20240902_brands.json || echo SKIP: brands
python manage.py loaddata fixtures/20241105_attributes.json || echo SKIP: attributes
python manage.py loaddata fixtures/20241201_banners.json || echo SKIP: banners
python manage.py loaddata fixtures/20241201_homepage.json || echo SKIP: homepage
python manage.py loaddata fixtures/20250607_delivery_companies.json || echo SKIP: delivery_companies
python manage.py loaddata fixtures/20250820_cities.json || echo SKIP: cities

echo Data loaded. Creating marker file .fixtures_loaded
echo %DATE% %TIME% > .fixtures_loaded

:SKIP_FIXTURES

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
