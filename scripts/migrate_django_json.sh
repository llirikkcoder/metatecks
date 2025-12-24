#!/bin/bash

# ============================================================================
# Скрипт миграции через Django dumpdata/loaddata (универсальный метод)
# Подходит для SQLite → PostgreSQL и PostgreSQL → PostgreSQL
# ============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VPS_USER="${VPS_USER:-your_user}"
VPS_HOST="${VPS_HOST:-your_vps_ip}"
VPS_PATH="${VPS_PATH:-/home/mt/metateks-dev}"

DUMP_FILE="production_dump_$(date +%Y%m%d_%H%M%S).json"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Миграция через Django JSON дамп${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

if [ "$VPS_USER" == "your_user" ] || [ "$VPS_HOST" == "your_vps_ip" ]; then
    echo -e "${RED}ОШИБКА: Настройте параметры подключения!${NC}"
    echo "export VPS_USER=\"ваш_пользователь\""
    echo "export VPS_HOST=\"ip_адрес_vps\""
    echo "export VPS_PATH=\"/путь/к/проекту\""
    exit 1
fi

echo "VPS: $VPS_USER@$VPS_HOST"
echo "Путь: $VPS_PATH"
echo "Файл: $DUMP_FILE"
echo ""

# ============================================================================
# Шаг 1: Создание JSON дампа на VPS
# ============================================================================

echo -e "${GREEN}[1/5] Создание JSON дампа на VPS...${NC}"

ssh $VPS_USER@$VPS_HOST << EOF
    cd $VPS_PATH

    # Активация виртуального окружения (если есть)
    if [ -f ~/.virtualenvs/metateks/bin/activate ]; then
        source ~/.virtualenvs/metateks/bin/activate
    fi

    echo "Создание дампа всех данных..."
    python manage.py dumpdata \
        --natural-foreign \
        --natural-primary \
        --exclude contenttypes \
        --exclude auth.permission \
        --exclude admin.logentry \
        --exclude sessions.session \
        --exclude easy_thumbnails \
        --indent 2 \
        -o $DUMP_FILE

    echo "Дамп создан: \$(du -h $DUMP_FILE | cut -f1)"
EOF

# ============================================================================
# Шаг 2: Скачивание дампа
# ============================================================================

echo ""
echo -e "${GREEN}[2/5] Скачивание дампа...${NC}"

scp $VPS_USER@$VPS_HOST:$VPS_PATH/$DUMP_FILE .

if [ ! -f "$DUMP_FILE" ]; then
    echo -e "${RED}ОШИБКА: Файл $DUMP_FILE не найден!${NC}"
    exit 1
fi

echo "Дамп скачан: $(du -h $DUMP_FILE | cut -f1)"

# ============================================================================
# Шаг 3: Пересоздание базы данных
# ============================================================================

echo ""
echo -e "${GREEN}[3/5] Пересоздание локальной базы данных...${NC}"

docker-compose down

read -p "Удалить существующую базу данных? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker volume rm metatecks_postgres_data 2>/dev/null || true
fi

docker-compose up -d db redis
echo "Ожидание запуска БД..."
sleep 10

# Запуск миграций
echo "Применение миграций..."
docker-compose run --rm web python manage.py migrate --noinput

# ============================================================================
# Шаг 4: Загрузка данных
# ============================================================================

echo ""
echo -e "${GREEN}[4/5] Загрузка данных из дампа...${NC}"

# Копируем дамп в контейнер
docker cp $DUMP_FILE metateks_web:/app/

# Загружаем данные
docker-compose run --rm web python manage.py loaddata $DUMP_FILE

echo "Данные загружены."

# ============================================================================
# Шаг 5: Запуск сервисов
# ============================================================================

echo ""
echo -e "${GREEN}[5/5] Запуск всех сервисов...${NC}"

docker-compose up -d

echo "Ожидание запуска..."
sleep 15

# ============================================================================
# Проверка
# ============================================================================

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Проверка результата${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

docker-compose ps

echo ""
echo -e "${YELLOW}Статистика базы данных:${NC}"
docker-compose exec -T web python manage.py shell << 'PYEOF'
from apps.catalog.models import Product, Category
from apps.orders.models import Order
from apps.users.models import User

print(f"Категорий: {Category.objects.count()}")
print(f"Товаров: {Product.objects.count()}")
print(f"Заказов: {Order.objects.count()}")
print(f"Пользователей: {User.objects.count()}")
PYEOF

# Пересоздание поискового индекса
echo ""
echo "Пересоздание поискового индекса..."
docker-compose exec -T web python manage.py buildwatson

echo ""
echo -e "${GREEN}Миграция завершена!${NC}"
echo ""
echo "Сайт: http://localhost"
echo "Админ: http://localhost/admin/"
echo ""

read -p "Удалить локальную копию дампа? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f $DUMP_FILE
    echo "Дамп удален."
fi
