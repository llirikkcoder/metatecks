#!/bin/bash
#
# Пересоздание SQLite базы для git (с миграциями, без данных)
#

set -e

echo "=============================================================================="
echo "ПЕРЕСОЗДАНИЕ SQLITE БАЗЫ ДЛЯ GIT"
echo "=============================================================================="
echo ""

# 1. Удалить старую базу
echo "1. Удаление старой базы..."
rm -f db.sqlite3
echo "✓ Старая база удалена"
echo ""

# 2. Установить USE_SQLITE=1 временно
echo "2. Создание новой базы с миграциями..."
export USE_SQLITE=1
export DEBUG=1
export SECRET_KEY=local-dev-secret-key
export ALLOWED_HOSTS=localhost,127.0.0.1

# 3. Применить миграции
echo "Запуск миграций..."
python manage.py migrate --noinput

echo "✓ Миграции применены"
echo ""

# 4. Создать суперпользователя
echo "3. Создание суперпользователя..."
python manage.py shell << 'PYEOF'
from apps.users.models import User

email = 'admin@test.ru'
password = 'admin'

if not User.objects.filter(email=email).exists():
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name='Admin',
        last_name='User'
    )
    user.is_admin = True
    user.save()
    print(f"✓ Суперпользователь создан: {email} / {password}")
else:
    print("✓ Суперпользователь уже существует")
PYEOF
echo ""

# 5. Проверить размер базы
DB_SIZE=$(ls -lh db.sqlite3 | awk '{print $5}')
echo "4. Информация о базе:"
echo "   Файл: db.sqlite3"
echo "   Размер: $DB_SIZE"
echo ""

# 6. Проверить таблицы
echo "5. Проверка таблиц в базе..."
python manage.py dbshell << 'EOF'
.tables
.quit
EOF
echo ""

echo "=============================================================================="
echo "✅ БАЗА ГОТОВА!"
echo "=============================================================================="
echo ""
echo "Что создано:"
echo "  ✓ db.sqlite3 с актуальными миграциями"
echo "  ✓ Суперпользователь: admin@test.ru / admin"
echo "  ✓ Размер базы: $DB_SIZE"
echo ""
echo "Следующие шаги:"
echo "  1. git add db.sqlite3 .gitignore"
echo "  2. git commit -m 'Add SQLite database for Railway deployment'"
echo "  3. git push origin feature/seo-improve"
echo ""
echo "После пуша:"
echo "  - Railway задеплоит с этой базой"
echo "  - Админка: https://metatecks-production.up.railway.app/admin/"
echo "  - Логин: admin@test.ru / admin"
echo ""
echo "Для добавления тестовых данных локально:"
echo "  - Запусти Django локально: python manage.py runserver"
echo "  - Зайди в админку: http://localhost:8000/admin/"
echo "  - Добавь категории/товары"
echo "  - Закоммить обновлённую db.sqlite3"
echo ""
echo "=============================================================================="
