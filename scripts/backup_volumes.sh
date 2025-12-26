#!/bin/bash
#
# Скрипт для создания бэкапа Docker Volumes и важных данных
#

set -e

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
PROJECT_NAME="728bf29e23a24cd8736c56d3f16c545434f9270f593c7b8d26edc7fb423ab445"

echo "==> Создание папки для бэкапа: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 1. Бэкап PostgreSQL (через pg_dump - рекомендуется)
echo ""
echo "==> 1. Бэкап базы данных PostgreSQL..."
docker exec metateks_db pg_dump -U metateks metateks > "$BACKUP_DIR/database.sql"
echo "✓ Сохранено: $BACKUP_DIR/database.sql ($(du -h $BACKUP_DIR/database.sql | cut -f1))"

# 2. Бэкап PostgreSQL Volume (альтернативный метод)
echo ""
echo "==> 2. Бэкап PostgreSQL volume (файлы БД)..."
docker run --rm \
  -v ${PROJECT_NAME}_postgres_data:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/postgres_volume.tar.gz -C /data .
echo "✓ Сохранено: $BACKUP_DIR/postgres_volume.tar.gz ($(du -h $BACKUP_DIR/postgres_volume.tar.gz | cut -f1))"

# 3. Бэкап Redis Volume
echo ""
echo "==> 3. Бэкап Redis volume..."
docker run --rm \
  -v ${PROJECT_NAME}_redis_data:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/redis_volume.tar.gz -C /data .
echo "✓ Сохранено: $BACKUP_DIR/redis_volume.tar.gz ($(du -h $BACKUP_DIR/redis_volume.tar.gz | cut -f1))"

# 4. Бэкап Static Volume
echo ""
echo "==> 4. Бэкап static volume..."
docker run --rm \
  -v ${PROJECT_NAME}_static_volume:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/static_volume.tar.gz -C /data . 2>/dev/null || echo "  (Static volume пустой или не требует бэкапа)"

# 5. Бэкап Media (bind mount - просто копируем)
echo ""
echo "==> 5. Бэкап media файлов..."
if [ -d "media" ] && [ "$(ls -A media)" ]; then
  tar czf "$BACKUP_DIR/media.tar.gz" media/
  echo "✓ Сохранено: $BACKUP_DIR/media.tar.gz ($(du -h $BACKUP_DIR/media.tar.gz | cut -f1))"
else
  echo "  (Media папка пустая)"
fi

# 6. Бэкап Logs (опционально)
echo ""
echo "==> 6. Бэкап логов (опционально)..."
if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
  tar czf "$BACKUP_DIR/logs.tar.gz" logs/
  echo "✓ Сохранено: $BACKUP_DIR/logs.tar.gz ($(du -h $BACKUP_DIR/logs.tar.gz | cut -f1))"
else
  echo "  (Logs папка пустая)"
fi

# 7. Сохранение .env файла (важно!)
echo ""
echo "==> 7. Сохранение конфигурации..."
if [ -f ".env.docker" ]; then
  cp .env.docker "$BACKUP_DIR/env.docker.backup"
  echo "✓ Сохранено: $BACKUP_DIR/env.docker.backup"
  echo "  ⚠️  ВНИМАНИЕ: Файл содержит пароли - храните безопасно!"
fi

# Итоговая информация
echo ""
echo "=========================================="
echo "✅ Бэкап завершен!"
echo "=========================================="
echo "Папка: $BACKUP_DIR"
echo "Содержимое:"
ls -lh "$BACKUP_DIR/"
echo ""
echo "Общий размер бэкапа:"
du -sh "$BACKUP_DIR"
echo ""
echo "📦 Для восстановления используйте: scripts/restore_volumes.sh"
