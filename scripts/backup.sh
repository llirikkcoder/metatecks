#!/bin/bash
# Скрипт для создания backup всех данных проекта

set -e

# Настройки
PROJECT_DIR="/opt/metatecks"
BACKUP_DIR="${PROJECT_DIR}/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="metateks_backup_${DATE}"

# Создать директорию для бекапов
mkdir -p "${BACKUP_DIR}"

echo "==> Создание backup: ${BACKUP_NAME}"

# 1. Backup базы данных PostgreSQL
echo "==> Backing up PostgreSQL database..."
docker-compose exec -T db pg_dump -U metateks metateks | gzip > "${BACKUP_DIR}/${BACKUP_NAME}_db.sql.gz"

# 2. Backup Redis (если нужны данные из очереди)
echo "==> Backing up Redis data..."
docker-compose exec -T redis redis-cli SAVE
docker cp metateks_redis:/data/dump.rdb "${BACKUP_DIR}/${BACKUP_NAME}_redis.rdb"

# 3. Backup media файлов
echo "==> Backing up media files..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}_media.tar.gz" -C "${PROJECT_DIR}" media/

# 4. Backup .env файлов
echo "==> Backing up environment files..."
cp "${PROJECT_DIR}/.env.docker" "${BACKUP_DIR}/${BACKUP_NAME}_env.docker"

# 5. Создать список Docker volumes
echo "==> Saving Docker volumes info..."
docker volume ls | grep metateks > "${BACKUP_DIR}/${BACKUP_NAME}_volumes.txt"

# Создать архив всех бекапов
echo "==> Creating final archive..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" \
    "${BACKUP_NAME}_db.sql.gz" \
    "${BACKUP_NAME}_redis.rdb" \
    "${BACKUP_NAME}_media.tar.gz" \
    "${BACKUP_NAME}_env.docker" \
    "${BACKUP_NAME}_volumes.txt"

# Удалить временные файлы
rm -f "${BACKUP_NAME}_db.sql.gz" \
      "${BACKUP_NAME}_redis.rdb" \
      "${BACKUP_NAME}_media.tar.gz" \
      "${BACKUP_NAME}_env.docker" \
      "${BACKUP_NAME}_volumes.txt"

echo ""
echo "✅ Backup completed successfully!"
echo "📦 Backup file: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo ""
echo "Size: $(du -h ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | cut -f1)"

# Удалить старые бекапы (старше 30 дней)
echo ""
echo "==> Cleaning up old backups (>30 days)..."
find "${BACKUP_DIR}" -name "metateks_backup_*.tar.gz" -mtime +30 -delete
echo "Done!"
