#!/bin/bash
# Скрипт для восстановления из backup

set -e

# Проверка аргументов
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /opt/metatecks/backups/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
PROJECT_DIR="/opt/metatecks"
TEMP_DIR="${PROJECT_DIR}/backups/restore_temp"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "⚠️  WARNING: This will restore data from backup!"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Создать временную директорию
mkdir -p "${TEMP_DIR}"
cd "${TEMP_DIR}"

echo "==> Extracting backup archive..."
tar -xzf "${BACKUP_FILE}"

# Найти файлы бекапа
DB_BACKUP=$(ls *_db.sql.gz 2>/dev/null | head -1)
REDIS_BACKUP=$(ls *_redis.rdb 2>/dev/null | head -1)
MEDIA_BACKUP=$(ls *_media.tar.gz 2>/dev/null | head -1)
ENV_BACKUP=$(ls *_env.docker 2>/dev/null | head -1)

# 1. Восстановить базу данных
if [ -n "${DB_BACKUP}" ]; then
    echo "==> Restoring PostgreSQL database..."
    gunzip -c "${DB_BACKUP}" | docker-compose exec -T db psql -U metateks metateks
    echo "✅ Database restored"
else
    echo "⚠️  Database backup not found"
fi

# 2. Восстановить Redis
if [ -n "${REDIS_BACKUP}" ]; then
    echo "==> Restoring Redis data..."
    docker-compose stop redis
    docker cp "${REDIS_BACKUP}" metateks_redis:/data/dump.rdb
    docker-compose start redis
    echo "✅ Redis restored"
else
    echo "⚠️  Redis backup not found"
fi

# 3. Восстановить media файлы
if [ -n "${MEDIA_BACKUP}" ]; then
    echo "==> Restoring media files..."
    tar -xzf "${MEDIA_BACKUP}" -C "${PROJECT_DIR}/"
    echo "✅ Media files restored"
else
    echo "⚠️  Media backup not found"
fi

# 4. Восстановить .env файл
if [ -n "${ENV_BACKUP}" ]; then
    echo "==> Restoring environment file..."
    cp "${ENV_BACKUP}" "${PROJECT_DIR}/.env.docker"
    echo "✅ Environment file restored"
else
    echo "⚠️  Environment file backup not found"
fi

# Очистка
echo "==> Cleaning up..."
cd "${PROJECT_DIR}"
rm -rf "${TEMP_DIR}"

echo ""
echo "✅ Restore completed successfully!"
echo ""
echo "Next steps:"
echo "1. Restart containers: docker-compose restart"
echo "2. Check logs: docker-compose logs -f"
echo "3. Test application: curl http://127.0.0.1:8080"
