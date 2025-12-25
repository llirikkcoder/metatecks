#!/bin/bash
#
# Интеграция данных с VPS в Docker проект
# Специально для случая когда код уже есть, нужны только данные
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Проверка переменных
if [ -z "$VPS_USER" ] || [ -z "$VPS_HOST" ]; then
    error "Установите переменные окружения:"
    echo "export VPS_USER='ваш_пользователь'"
    echo "export VPS_HOST='IP_VPS'"
    echo "export VPS_PATH='/usr/app/back'"
    exit 1
fi

VPS_PATH=${VPS_PATH:-"/usr/app/back"}
DATE=$(date +%Y%m%d_%H%M%S)

info "========================================="
info "  Интеграция данных VPS → Docker"
info "========================================="
echo ""
info "VPS: ${VPS_USER}@${VPS_HOST}"
info "Путь: ${VPS_PATH}"
echo ""

# Функция выполнения на VPS
vps_exec() {
    ssh "${VPS_USER}@${VPS_HOST}" "cd ${VPS_PATH} && $1"
}

# Шаг 1: Проверка подключения
info "Шаг 1/5: Проверка VPS..."
if ! vps_exec "pwd" > /dev/null 2>&1; then
    error "Не удается подключиться к VPS"
    exit 1
fi
success "Подключение успешно"

# Шаг 2: Создание дампа на VPS
info "Шаг 2/5: Создание дампа БД на VPS..."

DUMP_FILE="metateks_dump_${DATE}.json"
VENV_CMD="source ~/.virtualenvs/metateks/bin/activate"

info "Создается: ${DUMP_FILE}"
vps_exec "${VENV_CMD} && python manage.py dumpdata \
  --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.permission \
  --exclude sessions.session --exclude admin.logentry \
  --indent 2 > ${DUMP_FILE}" || {
    error "Не удалось создать дамп"
    exit 1
}

DUMP_SIZE=$(vps_exec "ls -lh ${DUMP_FILE} | awk '{print \$5}'")
success "Дамп создан: ${DUMP_SIZE}"

# Шаг 3: Скачивание дампа
info "Шаг 3/5: Скачивание дампа..."
rsync -avz --progress \
  "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/${DUMP_FILE}" \
  ./
success "Дамп скачан"

# Шаг 4: Синхронизация медиа
info "Шаг 4/5: Синхронизация медиа..."

# Создаем папку media если нет
mkdir -p media

MEDIA_COUNT_BEFORE=$(find media/ -type f 2>/dev/null | wc -l || echo "0")
info "Локально медиа: ${MEDIA_COUNT_BEFORE} файлов"

rsync -avz --progress \
  "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/media/" \
  ./media/ || warn "Частичная ошибка синхронизации"

MEDIA_COUNT_AFTER=$(find media/ -type f 2>/dev/null | wc -l || echo "0")
success "Медиа синхронизированы: ${MEDIA_COUNT_AFTER} файлов"

# Шаг 5: Загрузка в Docker
info "Шаг 5/5: Загрузка в Docker..."

# Проверка Docker
if ! docker-compose ps > /dev/null 2>&1; then
    warn "Docker не запущен, запускаю..."
    docker-compose up -d
    sleep 10
fi

# Ждем БД
info "Ожидание готовности PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U metateks > /dev/null 2>&1; then
        success "PostgreSQL готов"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Загрузка дампа
info "Загрузка дампа в БД..."
docker-compose exec -T web python manage.py loaddata < ${DUMP_FILE} || {
    error "Ошибка загрузки дампа"
    warn "Попробуйте очистить БД и повторить:"
    echo "docker-compose exec web python manage.py flush --noinput"
    echo "docker-compose exec web python manage.py migrate"
    echo "docker-compose exec -T web python manage.py loaddata < ${DUMP_FILE}"
    exit 1
}

success "Дамп загружен успешно"

# Проверка данных
info "Проверка данных..."
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order

users = User.objects.count()
orders = Order.objects.count()

print(f"\n✓ Пользователей: {users}")
print(f"✓ Заказов: {orders}")

if users == 0:
    print("\n⚠ ВНИМАНИЕ: Пользователей нет! Проверьте дамп.")
PYEOF

# Итоги
echo ""
success "========================================="
success "  Интеграция завершена!"
success "========================================="
echo ""
info "Что сделано:"
echo "  ✓ Дамп БД создан и загружен: ${DUMP_FILE}"
echo "  ✓ Медиа синхронизированы: ${MEDIA_COUNT_AFTER} файлов"
echo "  ✓ Docker запущен и работает"
echo ""
info "Проверьте:"
echo "  1. Сайт:    http://localhost/"
echo "  2. Админка: http://localhost/admin/"
echo "  3. Медиа:   http://localhost/media/"
echo ""
info "Войдите в админку используя данные с VPS"
echo ""

# Очистка дампа на VPS
read -p "Удалить дамп ${DUMP_FILE} на VPS? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    vps_exec "rm -f ${DUMP_FILE}"
    success "Дамп удален на VPS"
fi

echo ""
info "Локальный дамп сохранен: ${DUMP_FILE}"
warn "Не удаляйте его до полной проверки!"
