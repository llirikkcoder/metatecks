#!/bin/bash
set -e

echo "==> Waiting for database to be ready..."
python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db():
    db_url = "${DATABASE_URL:-postgresql://metateks:metateks_password@db:5432/metateks}"
    parsed = urlparse(db_url)

    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                dbname=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                host=parsed.hostname,
                port=parsed.port
            )
            conn.close()
            print("Database is ready!")
            return True
        except psycopg2.OperationalError:
            retry_count += 1
            print(f"Database not ready yet, retrying... ({retry_count}/{max_retries})")
            time.sleep(2)

    print("Could not connect to database after maximum retries")
    sys.exit(1)

wait_for_db()
END

echo "==> Running database migrations..."
python manage.py migrate --noinput --fake-initial || python manage.py migrate --noinput --fake

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

# Загрузка fixtures только при первом запуске
if [ ! -f /app/.fixtures_loaded ]; then
    echo "==> Loading initial fixtures..."

    # Проверка существования fixtures
    if [ -d "/app/fixtures" ] && [ "$(ls -A /app/fixtures/*.json 2>/dev/null)" ]; then
        python manage.py loaddata fixtures/20240722_addresses.json || true
        python manage.py loaddata fixtures/20240722_settings.json || true
        python manage.py loaddata fixtures/20240722_content.json || true
        python manage.py loaddata fixtures/20240901_categories_and_models.json || true
        python manage.py loaddata fixtures/20240902_brands.json || true
        python manage.py loaddata fixtures/20241105_attributes.json || true
        python manage.py loaddata fixtures/20241201_banners.json || true
        python manage.py loaddata fixtures/20241201_homepage.json || true
        python manage.py loaddata fixtures/20250607_delivery_companies.json || true
        python manage.py loaddata fixtures/20250820_cities.json || true

        touch /app/.fixtures_loaded
        echo "==> Fixtures loaded successfully!"
    else
        echo "==> No fixtures found, skipping..."
    fi
else
    echo "==> Fixtures already loaded, skipping..."
fi

# Построение поискового индекса Watson
echo "==> Building search index..."
python manage.py buildwatson || true

echo "==> Starting application..."
exec "$@"
