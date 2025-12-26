#!/bin/bash
#
# Скрипт для восстановления Docker Volumes из бэкапа
#

set -e

if [ -z "$1" ]; then
  echo "Использование: $0 <путь_к_папке_бэкапа>"
  echo ""
  echo "Пример: $0 backups/20251226_173000"
  echo ""
  echo "Доступные бэкапы:"
  ls -d backups/*/ 2>/dev/null || echo "  (Нет бэкапов)"
  exit 1
fi

BACKUP_DIR="$1"
PROJECT_NAME="728bf29e23a24cd8736c56d3f16c545434f9270f593c7b8d26edc7fb423ab445"

if [ ! -d "$BACKUP_DIR" ]; then
  echo "❌ Ошибка: Папка $BACKUP_DIR не найдена"
  exit 1
fi

echo "⚠️  ВНИМАНИЕ: Это восстановит данные из бэкапа"
echo "Текущие данные будут ПЕРЕЗАПИСАНЫ!"
echo ""
echo "Восстановление из: $BACKUP_DIR"
echo ""
read -p "Продолжить? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
  echo "Отменено"
  exit 0
fi

# Остановка контейнеров
echo ""
echo "==> Остановка контейнеров..."
docker compose down

# 1. Восстановление PostgreSQL из SQL дампа
echo ""
echo "==> 1. Восстановление базы данных..."
if [ -f "$BACKUP_DIR/database.sql" ]; then
  # Запуск только БД
  docker compose up -d db
  echo "Ожидание запуска PostgreSQL..."
  sleep 10

  # Очистка старой БД и восстановление
  docker exec -i metateks_db psql -U metateks -c "DROP DATABASE IF EXISTS metateks;"
  docker exec -i metateks_db psql -U metateks -c "CREATE DATABASE metateks;"
  docker exec -i metateks_db psql -U metateks metateks < "$BACKUP_DIR/database.sql"
  echo "✓ База данных восстановлена"
else
  echo "  ⚠️  database.sql не найден, пропускаем"
fi

# 2. Восстановление PostgreSQL Volume (если нужно полное восстановление)
echo ""
echo "==> 2. Восстановление PostgreSQL volume (опционально)..."
if [ -f "$BACKUP_DIR/postgres_volume.tar.gz" ]; then
  read -p "Восстановить PostgreSQL volume? (yes/no): " restore_pg
  if [ "$restore_pg" = "yes" ]; then
    docker compose down
    docker volume rm ${PROJECT_NAME}_postgres_data || true
    docker volume create ${PROJECT_NAME}_postgres_data
    docker run --rm \
      -v ${PROJECT_NAME}_postgres_data:/data \
      -v $(pwd)/$BACKUP_DIR:/backup \
      alpine sh -c "cd /data && tar xzf /backup/postgres_volume.tar.gz"
    echo "✓ PostgreSQL volume восстановлен"
  fi
fi

# 3. Восстановление Redis Volume
echo ""
echo "==> 3. Восстановление Redis volume..."
if [ -f "$BACKUP_DIR/redis_volume.tar.gz" ]; then
  docker volume rm ${PROJECT_NAME}_redis_data || true
  docker volume create ${PROJECT_NAME}_redis_data
  docker run --rm \
    -v ${PROJECT_NAME}_redis_data:/data \
    -v $(pwd)/$BACKUP_DIR:/backup \
    alpine sh -c "cd /data && tar xzf /backup/redis_volume.tar.gz"
  echo "✓ Redis volume восстановлен"
fi

# 4. Восстановление Static Volume
echo ""
echo "==> 4. Восстановление static volume..."
if [ -f "$BACKUP_DIR/static_volume.tar.gz" ]; then
  docker volume rm ${PROJECT_NAME}_static_volume || true
  docker volume create ${PROJECT_NAME}_static_volume
  docker run --rm \
    -v ${PROJECT_NAME}_static_volume:/data \
    -v $(pwd)/$BACKUP_DIR:/backup \
    alpine sh -c "cd /data && tar xzf /backup/static_volume.tar.gz"
  echo "✓ Static volume восстановлен"
fi

# 5. Восстановление Media
echo ""
echo "==> 5. Восстановление media файлов..."
if [ -f "$BACKUP_DIR/media.tar.gz" ]; then
  rm -rf media/
  tar xzf "$BACKUP_DIR/media.tar.gz"
  echo "✓ Media файлы восстановлены"
fi

# 6. Восстановление конфигурации
echo ""
echo "==> 6. Восстановление конфигурации..."
if [ -f "$BACKUP_DIR/env.docker.backup" ]; then
  echo "  ⚠️  Найден .env файл в бэкапе"
  read -p "Восстановить .env.docker? (yes/no): " restore_env
  if [ "$restore_env" = "yes" ]; then
    cp "$BACKUP_DIR/env.docker.backup" .env.docker
    echo "✓ .env.docker восстановлен"
  fi
fi

# Запуск всех контейнеров
echo ""
echo "==> Запуск контейнеров..."
docker compose up -d

echo ""
echo "=========================================="
echo "✅ Восстановление завершено!"
echo "=========================================="
echo ""
echo "Проверьте работу приложения: http://localhost:8000"
