#!/bin/bash

# Скрипт автоматического деплоя на VPS
# Использование: ./deploy.sh

set -e  # Остановить при ошибке

echo "🚀 Starting deployment process..."

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_DIR="/opt/metatecks"
BRANCH="main"

# Проверка директории проекта
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. Проверить текущую ветку
echo -e "${YELLOW}📌 Current branch:${NC}"
git branch --show-current

# 2. Сохранить изменения (если есть)
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  Uncommitted changes detected. Stashing...${NC}"
    git stash
fi

# 3. Подтянуть изменения из Git
echo -e "${YELLOW}⬇️  Pulling latest changes from $BRANCH...${NC}"
git pull origin $BRANCH

# 4. Показать последний коммит
echo -e "${GREEN}✅ Latest commit:${NC}"
git log -1 --oneline

# 5. Пересобрать Docker образы
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose build

# 6. Перезапустить контейнеры
echo -e "${YELLOW}🔄 Restarting containers...${NC}"
docker-compose up -d

# Ждем немного пока контейнеры запустятся
sleep 5

# 7. Выполнить миграции
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput || echo "⚠️  Migrations skipped"

# 8. Собрать статику
echo -e "${YELLOW}📦 Collecting static files...${NC}"
docker-compose exec -T web python manage.py collectstatic --noinput || echo "⚠️  Static collection skipped"

# 9. Проверить статус контейнеров
echo -e "${GREEN}📊 Container status:${NC}"
docker-compose ps

# 10. Проверить здоровье контейнеров
UNHEALTHY=$(docker-compose ps | grep -c "unhealthy" || true)
if [ "$UNHEALTHY" -gt 0 ]; then
    echo -e "${RED}❌ Some containers are unhealthy!${NC}"
    docker-compose ps
    exit 1
fi

# 11. Показать последние логи
echo -e "${GREEN}📝 Recent logs (last 20 lines):${NC}"
docker-compose logs --tail=20 web

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Application is running on: http://5.188.138.16:8888${NC}"
