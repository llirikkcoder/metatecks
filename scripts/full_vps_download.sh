#!/bin/bash
#
# Полная выгрузка данных с VPS
# Автоматически загружает ВСЕ данные: БД, медиа, статику, конфиги
#

set -e  # Выход при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции вывода
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Проверка переменных окружения
if [ -z "$VPS_USER" ] || [ -z "$VPS_HOST" ]; then
    error "Необходимо установить переменные окружения:"
    echo ""
    echo "export VPS_USER='ваш_пользователь'"
    echo "export VPS_HOST='IP_или_домен_VPS'"
    echo "export VPS_PATH='/home/mt/metateks-dev'  # опционально"
    echo ""
    exit 1
fi

VPS_PATH=${VPS_PATH:-"/home/mt/metateks-dev"}
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="vps_backup_${DATE}"

info "========================================="
info "  Полная выгрузка данных с VPS"
info "========================================="
echo ""
info "VPS: ${VPS_USER}@${VPS_HOST}"
info "Путь: ${VPS_PATH}"
info "Локальная папка: ./${BACKUP_DIR}"
echo ""

# Создаем локальную папку для бэкапов
mkdir -p "${BACKUP_DIR}"
cd "${BACKUP_DIR}"

# Функция для выполнения команд на VPS
vps_exec() {
    ssh "${VPS_USER}@${VPS_HOST}" "cd ${VPS_PATH} && $1"
}

# Шаг 1: Проверка доступа к VPS
info "Шаг 1/7: Проверка доступа к VPS..."
if vps_exec "pwd" > /dev/null 2>&1; then
    success "Подключение к VPS успешно"
else
    error "Не удается подключиться к VPS"
    error "Проверьте SSH доступ: ssh ${VPS_USER}@${VPS_HOST}"
    exit 1
fi

# Шаг 2: Проверка структуры проекта на VPS
info "Шаг 2/7: Проверка структуры проекта..."
echo ""

HAS_MANAGE_PY=$(vps_exec "test -f manage.py && echo 'yes' || echo 'no'")
HAS_MEDIA=$(vps_exec "test -d media && echo 'yes' || echo 'no'")
HAS_STATIC=$(vps_exec "test -d static && echo 'yes' || echo 'no'")
HAS_ASSETS=$(vps_exec "test -d assets && echo 'yes' || echo 'no'")
HAS_VENV=$(vps_exec "test -d ~/.virtualenvs/metateks && echo 'yes' || echo 'no'")

echo "  manage.py: ${HAS_MANAGE_PY}"
echo "  media/:    ${HAS_MEDIA}"
echo "  static/:   ${HAS_STATIC}"
echo "  assets/:   ${HAS_ASSETS}"
echo "  virtualenv: ${HAS_VENV}"
echo ""

if [ "$HAS_MANAGE_PY" != "yes" ]; then
    error "manage.py не найден! Проверьте путь VPS_PATH"
    exit 1
fi

# Шаг 3: Получение размеров
info "Шаг 3/7: Анализ размеров данных..."
echo ""

if [ "$HAS_MEDIA" = "yes" ]; then
    MEDIA_SIZE=$(vps_exec "du -sh media/ 2>/dev/null | cut -f1")
    MEDIA_COUNT=$(vps_exec "find media/ -type f 2>/dev/null | wc -l")
    info "  media/: ${MEDIA_SIZE} (файлов: ${MEDIA_COUNT})"
fi

if [ "$HAS_STATIC" = "yes" ]; then
    STATIC_SIZE=$(vps_exec "du -sh static/ 2>/dev/null | cut -f1")
    info "  static/: ${STATIC_SIZE}"
fi

# Определяем размер БД
DB_SIZE=$(vps_exec "python manage.py shell -c \"
from django.db import connection
cursor = connection.cursor()
try:
    cursor.execute('SELECT pg_size_pretty(pg_database_size(current_database()))')
    print(cursor.fetchone()[0])
except:
    print('unknown')
\" 2>/dev/null || echo 'unknown'")

info "  База данных: ${DB_SIZE}"
echo ""

# Шаг 4: Создание дампа БД на VPS
info "Шаг 4/7: Создание дампа базы данных на VPS..."

DUMP_FILE="metateks_dump_${DATE}.json"

if [ "$HAS_VENV" = "yes" ]; then
    PYTHON_CMD="source ~/.virtualenvs/metateks/bin/activate && python"
else
    warn "Virtualenv не найден, используется системный Python"
    PYTHON_CMD="python"
fi

info "Создается дамп: ${DUMP_FILE}"
vps_exec "${PYTHON_CMD} manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions.session \
  --exclude admin.logentry \
  --indent 2 \
  > ${DUMP_FILE}" || {
    error "Не удалось создать дамп БД"
    exit 1
}

DUMP_SIZE=$(vps_exec "ls -lh ${DUMP_FILE} | awk '{print \$5}'")
success "Дамп создан: ${DUMP_SIZE}"

# Шаг 5: Скачивание дампа БД
info "Шаг 5/7: Скачивание дампа БД..."
rsync -avz --progress \
  "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/${DUMP_FILE}" \
  ./
success "Дамп БД скачан: ${DUMP_FILE}"

# Шаг 6: Скачивание медиа-файлов
if [ "$HAS_MEDIA" = "yes" ]; then
    info "Шаг 6/7: Синхронизация медиа-файлов (${MEDIA_SIZE})..."
    
    mkdir -p media
    rsync -avz --progress \
      "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/media/" \
      ./media/ || {
        warn "Частичная ошибка при синхронизации медиа"
    }
    
    LOCAL_MEDIA_COUNT=$(find media/ -type f 2>/dev/null | wc -l || echo "0")
    success "Медиа синхронизированы: ${LOCAL_MEDIA_COUNT} файлов"
else
    warn "Шаг 6/7: Папка media/ не найдена на VPS"
fi

# Шаг 7: Скачивание дополнительных данных
info "Шаг 7/7: Скачивание дополнительных данных..."

# Статика (опционально - можно пересобрать локально)
if [ "$HAS_STATIC" = "yes" ]; then
    read -p "Скачать static/? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p static
        rsync -avz --progress \
          "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/static/" \
          ./static/
        success "Статика скачана"
    fi
fi

# Assets
if [ "$HAS_ASSETS" = "yes" ]; then
    read -p "Скачать assets/? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p assets
        rsync -avz --progress \
          "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/assets/" \
          ./assets/
        success "Assets скачаны"
    fi
fi

# Конфигурация
read -p "Скачать конфигурационные файлы (.env, conf/)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p config
    rsync -avz --progress \
      --include='.env*' \
      --include='conf/' \
      --include='conf/**' \
      --include='requirements*.txt' \
      --include='docker-compose.yml' \
      --exclude='*' \
      "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/" \
      ./config/ 2>/dev/null || true
    success "Конфиги скачаны в ./config/"
fi

# Логи
read -p "Скачать логи? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p logs_vps
    rsync -avz --progress \
      "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/logs/" \
      ./logs_vps/ 2>/dev/null || true
    success "Логи скачаны в ./logs_vps/"
fi

# Очистка дампа на VPS (опционально)
echo ""
read -p "Удалить дамп ${DUMP_FILE} на VPS? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    vps_exec "rm -f ${DUMP_FILE}"
    success "Дамп удален на VPS"
fi

# Итоговая статистика
echo ""
success "========================================="
success "  Выгрузка завершена успешно!"
success "========================================="
echo ""
info "Скачано в: $(pwd)"
echo ""
info "Содержимое:"
ls -lh | grep -v "^total" | awk '{print "  " $9 " (" $5 ")"}'
echo ""
info "Следующие шаги:"
echo "  1. Проверьте содержимое: ls -la"
echo "  2. Переместите данные в проект:"
echo "     cd .."
echo "     cp -r ${BACKUP_DIR}/media/* ./media/"
echo "     cp ${BACKUP_DIR}/${DUMP_FILE} ./"
echo ""
echo "  3. Загрузите в Docker:"
echo "     docker-compose up -d"
echo "     docker-compose exec -T web python manage.py loaddata < ${DUMP_FILE}"
echo ""
echo "  4. Проверьте данные:"
echo "     docker-compose exec web python manage.py shell"
echo ""

# Создаем README в папке бэкапа
cat > README.txt << EOF
Бэкап с VPS создан: $(date)

VPS: ${VPS_USER}@${VPS_HOST}
Путь: ${VPS_PATH}

Содержимое:
- ${DUMP_FILE} - Дамп базы данных (Django dumpdata)
- media/ - Медиа-файлы
- static/ - Статические файлы (если скачаны)
- assets/ - Assets (если скачаны)
- config/ - Конфигурационные файлы (если скачаны)
- logs_vps/ - Логи с VPS (если скачаны)

Для загрузки в Docker:
1. docker-compose up -d
2. docker-compose exec -T web python manage.py loaddata < ${DUMP_FILE}
3. Скопируйте медиа: cp -r media/* ../media/

Проверка:
docker-compose exec web python manage.py shell
>>> from apps.users.models import User
>>> User.objects.count()
EOF

success "README.txt создан в папке бэкапа"
echo ""
