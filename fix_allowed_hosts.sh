#!/bin/bash
#
# Исправление ALLOWED_HOSTS и CSRF_TRUSTED_ORIGINS для правильной работы HTTPS
#

set -e

echo "=============================================================================="
echo "ИСПРАВЛЕНИЕ ALLOWED_HOSTS И CSRF_TRUSTED_ORIGINS"
echo "=============================================================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите с sudo"
    exit 1
fi

cd /opt/metatecks

echo "1. Текущие настройки в .env.docker:"
echo "------------------------------------"
grep -E "ALLOWED_HOSTS|CSRF_TRUSTED|DEFAULT_SCHEME" .env.docker || echo "Не найдено"
echo ""

echo "2. Создание бэкапа .env.docker..."
cp .env.docker .env.docker.backup_$(date +%Y%m%d_%H%M%S)
echo "✓ Бэкап создан"
echo ""

echo "3. Обновление настроек..."

# Удаляем старые настройки если есть
sed -i '/^ALLOWED_HOSTS=/d' .env.docker
sed -i '/^CSRF_TRUSTED_ORIGINS=/d' .env.docker
sed -i '/^DEFAULT_SCHEME=/d' .env.docker

# Добавляем новые настройки
cat >> .env.docker << 'EOF'

# HTTPS настройки для правильной работы домена
ALLOWED_HOSTS=metateks-admin.vinodesign.ru spb.metateks-admin.vinodesign.ru ekb.metateks-admin.vinodesign.ru nsk.metateks-admin.vinodesign.ru krasnodar.metateks-admin.vinodesign.ru yaroslavl.metateks-admin.vinodesign.ru murmansk.metateks-admin.vinodesign.ru 5.188.138.16 localhost 127.0.0.1
CSRF_TRUSTED_ORIGINS=https://metateks-admin.vinodesign.ru,https://spb.metateks-admin.vinodesign.ru,https://ekb.metateks-admin.vinodesign.ru,https://nsk.metateks-admin.vinodesign.ru,https://krasnodar.metateks-admin.vinodesign.ru,https://yaroslavl.metateks-admin.vinodesign.ru,https://murmansk.metateks-admin.vinodesign.ru,http://5.188.138.16:8888,http://127.0.0.1:8888
EOF

echo "✓ Настройки добавлены"
echo ""

echo "4. Новые настройки:"
echo "-------------------"
grep -E "ALLOWED_HOSTS|CSRF_TRUSTED" .env.docker
echo ""

echo "5. Перезапуск контейнеров..."
docker-compose restart web
echo "✓ Web контейнер перезапущен"
echo ""

echo "6. Ожидание запуска (15 секунд)..."
sleep 15
echo ""

echo "7. Проверка статуса..."
docker-compose ps
echo ""

echo "8. Проверка что генерирует Django в HTML:"
echo "------------------------------------------"
curl -s https://metateks-admin.vinodesign.ru/ | grep -o 'src="http[^"]*media[^"]*"' | head -3
echo ""

echo "=============================================================================="
echo "✅ ГОТОВО!"
echo "=============================================================================="
echo ""
echo "Если все еще видите src=\"http://5.188.138.16/media/...\" то проблема в другом."
echo "Если видите src=\"https://metateks-admin.vinodesign.ru/media/...\" - проблема решена!"
echo ""
echo "Очистите кэш браузера (Ctrl+Shift+R) и проверьте:"
echo "  https://metateks-admin.vinodesign.ru"
echo ""
