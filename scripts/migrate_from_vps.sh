#!/bin/bash

# ============================================================================
# Скрипт автоматической миграции базы данных с VPS на локальный Docker
# ============================================================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация (ИЗМЕНИТЕ НА СВОИ ЗНАЧЕНИЯ!)
VPS_USER="${VPS_USER:-your_user}"
VPS_HOST="${VPS_HOST:-your_vps_ip}"
VPS_PATH="${VPS_PATH:-/home/mt/metateks-dev}"
DB_NAME="${DB_NAME:-metateks}"
DB_USER="${DB_USER:-metateks}"

# Имя файла дампа с временной меткой
DUMP_FILE="metateks_dump_$(date +%Y%m%d_%H%M%S).backup"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Миграция БД с VPS на локальный Docker${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Проверка параметров
if [ "$VPS_USER" == "your_user" ] || [ "$VPS_HOST" == "your_vps_ip" ]; then
    echo -e "${RED}ОШИБКА: Необходимо настроить параметры подключения!${NC}"
    echo ""
    echo "Отредактируйте скрипт или используйте переменные окружения:"
    echo "  export VPS_USER=\"ваш_пользователь\""
    echo "  export VPS_HOST=\"ip_адрес_vps\""
    echo "  export VPS_PATH=\"/путь/к/проекту\""
    echo ""
    exit 1
fi

echo -e "${YELLOW}Конфигурация:${NC}"
echo "  VPS: $VPS_USER@$VPS_HOST"
echo "  Путь: $VPS_PATH"
echo "  База данных: $DB_NAME"
echo "  Файл дампа: $DUMP_FILE"
echo ""

read -p "Продолжить? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отменено."
    exit 0
fi

# ============================================================================
# Шаг 1: Создание дампа на VPS
# ============================================================================

echo ""
echo -e "${GREEN}[1/7] Создание дампа базы данных на VPS...${NC}"

ssh $VPS_USER@$VPS_HOST << EOF
    cd $VPS_PATH
    echo "Создание дампа $DUMP_FILE..."

    # Проверяем, какая БД используется (PostgreSQL или SQLite)
    if command -v pg_dump &> /dev/null; then
        # PostgreSQL
        pg_dump -U $DB_USER -d $DB_NAME -F c -b -v -f $DUMP_FILE 2>&1
    else
        echo "ОШИБКА: pg_dump не найден. Используйте Django dumpdata или скопируйте db.sqlite3"
        exit 1
    fi

    echo "Дамп создан: \$(du -h $DUMP_FILE | cut -f1)"
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}ОШИБКА при создании дампа!${NC}"
    exit 1
fi

# ============================================================================
# Шаг 2: Скачивание дампа
# ============================================================================

echo ""
echo -e "${GREEN}[2/7] Скачивание дампа с VPS...${NC}"

scp $VPS_USER@$VPS_HOST:$VPS_PATH/$DUMP_FILE .

if [ ! -f "$DUMP_FILE" ]; then
    echo -e "${RED}ОШИБКА: Файл $DUMP_FILE не найден!${NC}"
    exit 1
fi

echo "Дамп скачан: $(du -h $DUMP_FILE | cut -f1)"

# ============================================================================
# Шаг 3: Скачивание медиа-файлов (опционально)
# ============================================================================

echo ""
read -p "Скачать медиа-файлы (изображения, документы)? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}[3/7] Синхронизация медиа-файлов...${NC}"

    mkdir -p media
    rsync -avz --progress $VPS_USER@$VPS_HOST:$VPS_PATH/media/ ./media/ || true

    echo "Медиа-файлы синхронизированы."
else
    echo -e "${YELLOW}[3/7] Пропуск медиа-файлов.${NC}"
fi

# ============================================================================
# Шаг 4: Остановка контейнеров
# ============================================================================

echo ""
echo -e "${GREEN}[4/7] Остановка Docker контейнеров...${NC}"

docker-compose down

echo ""
read -p "Удалить существующую базу данных? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Удаление volume с базой данных..."
    docker volume rm metatecks_postgres_data 2>/dev/null || true
else
    echo -e "${YELLOW}ВНИМАНИЕ: Существующая база данных будет перезаписана!${NC}"
fi

# ============================================================================
# Шаг 5: Запуск базы данных
# ============================================================================

echo ""
echo -e "${GREEN}[5/7] Запуск PostgreSQL и Redis...${NC}"

docker-compose up -d db redis

echo "Ожидание готовности базы данных..."
sleep 10

# Проверка, что БД запустилась
if ! docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${RED}ОШИБКА: База данных не запустилась!${NC}"
    docker-compose logs db
    exit 1
fi

echo "База данных готова."

# ============================================================================
# Шаг 6: Копирование и восстановление дампа
# ============================================================================

echo ""
echo -e "${GREEN}[6/7] Восстановление дампа в PostgreSQL...${NC}"

# Копируем дамп в контейнер
docker cp $DUMP_FILE metateks_db:/tmp/

# Восстанавливаем дамп
echo "Восстановление данных..."
docker-compose exec -T db pg_restore \
    -U $DB_USER \
    -d $DB_NAME \
    -v \
    -c \
    --no-owner \
    --no-acl \
    /tmp/$DUMP_FILE 2>&1 || {
        echo -e "${YELLOW}Предупреждение: Некоторые ошибки при восстановлении (обычно это нормально)${NC}"
    }

echo "Дамп восстановлен."

# ============================================================================
# Шаг 7: Запуск всех сервисов
# ============================================================================

echo ""
echo -e "${GREEN}[7/7] Запуск всех сервисов...${NC}"

docker-compose up -d

echo "Ожидание запуска сервисов..."
sleep 15

# ============================================================================
# Проверка результата
# ============================================================================

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Проверка результата${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Статус контейнеров
echo -e "${YELLOW}Статус контейнеров:${NC}"
docker-compose ps

echo ""
echo -e "${YELLOW}Проверка подключения к сайту:${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "FAIL")

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ Сайт доступен (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Сайт недоступен (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo -e "${YELLOW}Проверка данных в базе:${NC}"
docker-compose exec -T web python manage.py shell << 'PYEOF'
from apps.catalog.models import Product, Category
from apps.orders.models import Order
from apps.users.models import User

print(f"✓ Категорий: {Category.objects.count()}")
print(f"✓ Товаров: {Product.objects.count()}")
print(f"✓ Заказов: {Order.objects.count()}")
print(f"✓ Пользователей: {User.objects.count()}")
PYEOF

# ============================================================================
# Очистка
# ============================================================================

echo ""
read -p "Удалить локальную копию дампа? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f $DUMP_FILE
    echo "Дамп удален."
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Миграция завершена успешно!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Доступ к приложению:"
echo "  - Сайт: http://localhost"
echo "  - Админ: http://localhost/admin/"
echo ""
echo "Полезные команды:"
echo "  docker-compose logs -f web      # Просмотр логов"
echo "  docker-compose ps               # Статус контейнеров"
echo "  docker-compose down             # Остановка"
echo ""
echo -e "${YELLOW}Не забудьте удалить дамп с VPS, если он больше не нужен!${NC}"
