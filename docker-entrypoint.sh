#!/bin/bash
set -e

# Проверяем нужно ли ждать PostgreSQL
# Пропускаем если USE_SQLITE=1 или DATABASE_URL не задан
if [ "${USE_SQLITE}" = "1" ] || [ "${USE_SQLITE}" = "true" ]; then
    echo "==> Using SQLite, skipping database wait..."
elif [ -z "${DATABASE_URL}" ]; then
    echo "==> No DATABASE_URL set, using SQLite fallback..."
else
    echo "==> Waiting for PostgreSQL database to be ready..."
    python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db():
    db_url = "${DATABASE_URL}"
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
            print("PostgreSQL database is ready!")
            return True
        except psycopg2.OperationalError:
            retry_count += 1
            print(f"Database not ready yet, retrying... ({retry_count}/{max_retries})")
            time.sleep(2)

    print("Could not connect to database after maximum retries")
    sys.exit(1)

wait_for_db()
END
fi

echo "==> Running database migrations..."
python manage.py migrate --noinput

# Создание суперпользователя если задана переменная
if [ "${CREATE_SUPERUSER}" = "1" ] || [ "${CREATE_SUPERUSER}" = "true" ]; then
    echo "==> Creating superuser..."
    python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from apps.users.models import User

email = os.getenv('SUPERUSER_EMAIL', 'admin@metateks.ru')
password = os.getenv('SUPERUSER_PASSWORD', 'MetaTeks2025Admin!')

if User.objects.filter(email=email).exists():
    print(f'✓ Superuser {email} already exists')
    user = User.objects.get(email=email)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'✓ Password updated')
else:
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name='Admin',
        last_name='Metateks'
    )
    print(f'✓ Superuser created: {email}')
END
fi

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

# Загрузка fixtures только при первом запуске
# Флаг хранится в /app/logs для сохранения между пересозданиями контейнера
if [ ! -f /app/logs/.fixtures_loaded ]; then
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

        touch /app/logs/.fixtures_loaded
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
