#!/bin/bash

# ============================================================================
# Скрипт переноса Docker приложения на новый сервер
# ============================================================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
BACKUP_DIR="./migrate_$(date +%Y%m%d_%H%M%S)"
SOURCE_SERVER="${1:-}"  # опционально: user@host для rsync
DEST_SERVER="${2:-}"    # опционально: user@host для деплоя

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Перенос Docker приложения${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# ============================================================================
# Функция: Показать прогресс
# ============================================================================

show_progress() {
    local message=$1
    echo -e "${BLUE}▶ $message${NC}"
}

# ============================================================================
# Функция: Создать бэкап БД
# ============================================================================

backup_database() {
    show_progress "Создание бэкапа базы данных..."

    docker exec metateks_db pg_isready -U metateks > /dev/null 2>&1 || {
        echo -e "${RED}База данных не запущена!${NC}"
        return 1
    }

    docker exec metateks_db pg_dump \
        -U metateks \
        -d metateks \
        -F c \
        -f /tmp/db_backup.backup

    docker cp metateks_db:/tmp/db_backup.backup "$BACKUP_DIR/db_backup.backup"

    echo -e "${GREEN}✓ База данных сохранена: $(du -h "$BACKUP_DIR/db_backup.backup" | cut -f1)${NC}"
}

# ============================================================================
# Функция: Сохранить Docker образы
# ============================================================================

backup_docker_images() {
    show_progress "Сохранение Docker образов..."

    docker images | grep metateks > /dev/null 2>&1 || {
        echo -e "${YELLOW}⚠ Docker образы не найдены, пропускаем...${NC}"
        return 0
    }

    docker save metatecks-web metateks-celery | gzip > "$BACKUP_DIR/metateks_images.tar.gz"

    echo -e "${GREEN}✓ Docker образы сохранены: $(du -h "$BACKUP_DIR/metateks_images.tar.gz" | cut -f1)${NC}"
}

# ============================================================================
# Функция: Бэкап статических файлов
# ============================================================================

backup_static() {
    show_progress "Бэкап статических файлов..."

    docker run --rm \
        -v metateks_static_volume:/data \
        -v "$(pwd)/$BACKUP_DIR:/backup" \
        alpine tar czf /backup/static_backup.tar.gz -C /data . 2>/dev/null || {
        echo -e "${YELLOW}⚠ Статика не найдена, пропускаем...${NC}"
        return 0
    }

    echo -e "${GREEN}✓ Статика сохранена: $(du -h "$BACKUP_DIR/static_backup.tar.gz" | cut -f1)${NC}"
}

# ============================================================================
# Функция: Бэкап медиа
# ============================================================================

backup_media() {
    show_progress "Бэкап медиа-файлов..."

    if [ -d "media" ] && [ "$(ls -A media)" ]; then
        tar czf "$BACKUP_DIR/media_backup.tar.gz" media/
        echo -e "${GREEN}✓ Медиа сохранены: $(du -h "$BACKUP_DIR/media_backup.tar.gz" | cut -f1)${NC}"
    else
        echo -e "${YELLOW}⚠ Папка media пуста или не существует${NC}"
    fi
}

# ============================================================================
# Функция: Бэкап конфигурации
# ============================================================================

backup_config() {
    show_progress "Бэкап конфигурации..."

    tar czf "$BACKUP_DIR/config_backup.tar.gz" \
        docker-compose.yml \
        .env.docker \
        docker/ 2>/dev/null || {
        echo -e "${YELLOW}⚠ Некоторые файлы конфигурации не найдены${NC}"
    }

    echo -e "${GREEN}✓ Конфигурация сохранена${NC}"
}

# ============================================================================
# Функция: rsync на удаленный сервер
# ============================================================================

rsync_to_server() {
    local server=$1
    show_progress "Отправка бэкапа на сервер $server..."

    rsync -avz --progress "$BACKUP_DIR/" "$server:/tmp/metateks_backup/"

    echo -e "${GREEN}✓ Бэкап отправлен на сервер${NC}"
}

# ============================================================================
# Функция: Восстановление на новом сервере
# ============================================================================

restore_on_server() {
    local server=$1
    local backup_dir="/tmp/metateks_backup"

    show_progress "Инструкции по восстановлению на сервере $server:"

    echo ""
    echo -e "${YELLOW}Выполните на сервере $server:${NC}"
    echo ""
    echo "  # 1. Создайте директорию проекта"
    echo "  mkdir -p /opt/metateks && cd /opt/metateks"
    echo ""
    echo "  # 2. Распакуйте конфигурацию"
    echo "  tar xzf $backup_dir/config_backup.tar.gz"
    echo ""
    echo "  # 3. Создайте папки"
    echo "  mkdir -p media logs static"
    echo "  chmod 755 media logs static"
    echo ""
    echo "  # 4. Загрузите Docker образы"
    echo "  docker load < $backup_dir/metateks_images.tar.gz"
    echo ""
    echo "  # 5. Создайте volumes"
    echo "  docker volume create metateks_postgres_data"
    echo "  docker volume create metateks_redis_data"
    echo "  docker volume create metateks_static_volume"
    echo ""
    echo "  # 6. Восстановите статику"
    echo "  docker run --rm \\"
    echo "    -v metateks_static_volume:/data \\"
    echo "    -v $backup_dir:/backup \\"
    echo "    alpine sh -c 'cd /data && tar xzf /backup/static_backup.tar.gz'"
    echo ""
    echo "  # 7. Восстановите медиа"
    echo "  tar xzf $backup_dir/media_backup.tar.gz"
    echo ""
    echo "  # 8. Запустите БД"
    echo "  docker-compose up -d db redis"
    echo "  sleep 10"
    echo ""
    echo "  # 9. Восстановите БД"
    echo "  docker cp $backup_dir/db_backup.backup metateks_db:/tmp/"
    echo "  docker exec metateks_db pg_restore \\"
    echo "    -U metateks \\"
    echo "    -d metateks \\"
    echo "    --clean --if-exists \\"
    echo "    /tmp/db_backup.backup"
    echo ""
    echo "  # 10. Запустите все сервисы"
    echo "  docker-compose up -d"
    echo ""
    echo "  # 11. Проверьте"
    echo "  docker-compose ps"
    echo "  curl http://localhost/"
    echo ""
}

# ============================================================================
# Главная программа
# ============================================================================

main() {
    # Создаем папку для бэкапа
    mkdir -p "$BACKUP_DIR"

    echo -e "${YELLOW}Папка для бэкапа: $BACKUP_DIR${NC}"
    echo ""

    # Проверяем Docker контейнеры
    if ! docker ps | grep -q metateks; then
        echo -e "${RED}⚠ Контейнеры metateks не запущены!${NC}"
        echo -e "${YELLOW}Будет создан только бэкап файлов.${NC}"
    fi

    # Создаем бэкапы
    backup_database
    backup_docker_images
    backup_static
    backup_media
    backup_config

    # Итоговая статистика
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  Бэкап завершен!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${YELLOW}Содержимое бэкапа:${NC}"
    ls -lh "$BACKUP_DIR"
    echo ""
    echo -e "${YELLOW}Общий размер:${NC} $(du -sh "$BACKUP_DIR" | cut -f1)"
    echo ""

    # rsync на удаленный сервер (если указан)
    if [ -n "$DEST_SERVER" ]; then
        rsync_to_server "$DEST_SERVER"
    fi

    # Восстановление (если указан сервер)
    if [ -n "$DEST_SERVER" ]; then
        restore_on_server "$DEST_SERVER"
    else
        echo -e "${BLUE}Для восстановления на новом сервере:${NC}"
        echo ""
        echo "  1. Скопируйте папку $BACKUP_DIR на новый сервер"
        echo "  2. Распакуйте и восстановите по инструкциям в docs/DOCKER_DEPLOYMENT.md"
        echo ""
    fi
}

# Запуск
main
