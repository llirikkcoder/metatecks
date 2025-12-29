#!/bin/bash
#
# Полный бэкап перед апгрейдом сервера
# Для безопасного увеличения RAM/диска на Selectel
#

set -e

echo "=============================================================================="
echo "СОЗДАНИЕ ПОЛНОГО БЭКАПА ПЕРЕД АПГРЕЙДОМ СЕРВЕРА"
echo "=============================================================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите с sudo"
    exit 1
fi

BACKUP_DIR="/root/backups_before_upgrade_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Директория бэкапов: $BACKUP_DIR"
echo ""

# 1. Информация о сервере
echo "1. Сохранение информации о сервере..."
echo "====================================="
cat > "$BACKUP_DIR/server_info.txt" << EOF
Дата создания бэкапа: $(date)
Hostname: $(hostname)
IP адрес: $(hostname -I)
OS: $(cat /etc/os-release | grep PRETTY_NAME)
Kernel: $(uname -r)
RAM: $(free -h | grep Mem)
Disk: $(df -h /)
EOF
cat "$BACKUP_DIR/server_info.txt"
echo "✓ Сохранено в server_info.txt"
echo ""

# 2. Бэкап базы данных PostgreSQL
echo "2. Бэкап базы данных PostgreSQL..."
echo "===================================="
cd /opt/metatecks
if docker-compose ps | grep -q metateks_db; then
    echo "Создание дампа БД..."
    docker-compose exec -T db pg_dump -U metateks metateks > "$BACKUP_DIR/postgresql_dump.sql"

    # Сжать для экономии места
    gzip "$BACKUP_DIR/postgresql_dump.sql"

    DUMP_SIZE=$(ls -lh "$BACKUP_DIR/postgresql_dump.sql.gz" | awk '{print $5}')
    echo "✓ БД сохранена: postgresql_dump.sql.gz ($DUMP_SIZE)"
else
    echo "⚠ Docker БД не запущена, пропускаем"
fi
echo ""

# 3. Бэкап конфигураций
echo "3. Бэкап конфигураций..."
echo "========================"
echo "Создание архива конфигураций..."
tar -czf "$BACKUP_DIR/configs.tar.gz" \
    /opt/metatecks/.env.docker \
    /opt/metatecks/docker-compose.yml \
    /opt/metatecks/main/settings/ \
    /usr/app/back/conf/ \
    /etc/nginx/sites-enabled/ \
    /etc/nginx/sites-available/ \
    2>/dev/null || true

CONF_SIZE=$(ls -lh "$BACKUP_DIR/configs.tar.gz" 2>/dev/null | awk '{print $5}')
echo "✓ Конфигурации: configs.tar.gz ($CONF_SIZE)"
echo ""

# 4. Список Docker контейнеров и volumes
echo "4. Docker информация..."
echo "======================="
docker-compose ps > "$BACKUP_DIR/docker_containers.txt"
docker volume ls > "$BACKUP_DIR/docker_volumes.txt"
docker images > "$BACKUP_DIR/docker_images.txt"
echo "✓ Docker информация сохранена"
echo ""

# 5. Список установленных пакетов
echo "5. Список установленных пакетов..."
echo "==================================="
dpkg -l > "$BACKUP_DIR/installed_packages.txt"
echo "✓ Список пакетов сохранён"
echo ""

# 6. Nginx конфигурации
echo "6. Копирование nginx конфигураций..."
echo "======================================"
mkdir -p "$BACKUP_DIR/nginx"
cp -r /etc/nginx/sites-enabled/* "$BACKUP_DIR/nginx/" 2>/dev/null || true
cp /usr/app/back/conf/mirror_nginx.conf "$BACKUP_DIR/nginx/" 2>/dev/null || true
echo "✓ Nginx конфигурации скопированы"
echo ""

# 7. Список cron задач
echo "7. Cron задачи..."
echo "================="
crontab -l > "$BACKUP_DIR/crontab.txt" 2>/dev/null || echo "Нет cron задач"
echo "✓ Cron задачи сохранены"
echo ""

# 8. Создание итогового архива
echo "8. Создание финального архива..."
echo "================================="
cd /root
FINAL_ARCHIVE="backup_full_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$FINAL_ARCHIVE" "$(basename $BACKUP_DIR)"

FINAL_SIZE=$(ls -lh "$FINAL_ARCHIVE" | awk '{print $5}')
echo "✓ Финальный архив: $FINAL_ARCHIVE ($FINAL_SIZE)"
echo ""

# 9. Итоговая информация
echo "=============================================================================="
echo "✅ БЭКАП СОЗДАН УСПЕШНО!"
echo "=============================================================================="
echo ""
echo "Созданные файлы:"
echo "----------------"
echo "Директория бэкапов: $BACKUP_DIR"
echo "  - postgresql_dump.sql.gz (база данных)"
echo "  - configs.tar.gz (все конфигурации)"
echo "  - docker_containers.txt (список контейнеров)"
echo "  - docker_volumes.txt (список volumes)"
echo "  - server_info.txt (информация о сервере)"
echo ""
echo "Финальный архив:"
echo "  /root/$FINAL_ARCHIVE ($FINAL_SIZE)"
echo ""
echo "=============================================================================="
echo "ЧТО ДЕЛАТЬ ДАЛЬШЕ:"
echo "=============================================================================="
echo ""
echo "1. СКАЧАТЬ БЭКАП К СЕБЕ НА КОМПЬЮТЕР:"
echo "   На своём компьютере выполните:"
echo "   scp root@5.188.138.16:/root/$FINAL_ARCHIVE ./"
echo ""
echo "2. АПГРЕЙД СЕРВЕРА В SELECTEL:"
echo "   Личный кабинет → Облачная платформа → Ваш сервер → Изменить конфигурацию"
echo ""
echo "   Рекомендации для параллельной работы двух проектов:"
echo "   - RAM: 8GB (минимум) или 16GB (комфортно)"
echo "   - Диск: 40GB (минимум) или 60GB (с запасом)"
echo "   - CPU: 4 ядра (рекомендуется)"
echo ""
echo "3. ПОСЛЕ АПГРЕЙДА:"
echo "   - Сервер перезагрузится (это нормально)"
echo "   - Проверьте что Docker контейнеры запустились:"
echo "     cd /opt/metatecks && docker-compose ps"
echo "   - Проверьте сайт: https://metateks-admin.vinodesign.ru"
echo ""
echo "4. ЕСЛИ ЧТО-ТО ПОЙДЁТ НЕ ТАК:"
echo "   - У вас есть полный бэкап: $FINAL_ARCHIVE"
echo "   - Можно восстановить БД из postgresql_dump.sql.gz"
echo "   - Можно восстановить конфигурации из configs.tar.gz"
echo ""
echo "=============================================================================="
echo ""
echo "Бэкап занимает: $(du -sh $BACKUP_DIR | awk '{print $1}')"
echo "Финальный архив: $FINAL_SIZE"
echo ""
echo "ВАЖНО: Скачайте бэкап к себе ПЕРЕД апгрейдом!"
echo ""
echo "=============================================================================="
