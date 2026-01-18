@echo off
chcp 65001 >nul

echo Loading fixtures...

.venv\Scripts\python.exe manage.py loaddata fixtures/20240722_addresses.json 2>nul || echo SKIP: addresses
.venv\Scripts\python.exe manage.py loaddata fixtures/20240722_settings.json 2>nul || echo SKIP: settings  
.venv\Scripts\python.exe manage.py loaddata fixtures/20240722_content.json 2>nul || echo SKIP: content (some models may be deprecated)
.venv\Scripts\python.exe manage.py loaddata fixtures/20240901_categories_and_models.json 2>nul || echo SKIP: categories_and_models
.venv\Scripts\python.exe manage.py loaddata fixtures/20240902_brands.json 2>nul || echo SKIP: brands
.venv\Scripts\python.exe manage.py loaddata fixtures/20241105_attributes.json 2>nul || echo SKIP: attributes
.venv\Scripts\python.exe manage.py loaddata fixtures/20241201_banners.json 2>nul || echo SKIP: banners
.venv\Scripts\python.exe manage.py loaddata fixtures/20241201_homepage.json 2>nul || echo SKIP: homepage
.venv\Scripts\python.exe manage.py loaddata fixtures/20250607_delivery_companies.json 2>nul || echo SKIP: delivery_companies
.venv\Scripts\python.exe manage.py loaddata fixtures/20250820_cities.json 2>nul || echo SKIP: cities

echo.
echo Done! Checking categories count...
.venv\Scripts\python.exe manage.py shell -c "from apps.catalog.models import Category; print('Categories in database:', Category.objects.count())"
