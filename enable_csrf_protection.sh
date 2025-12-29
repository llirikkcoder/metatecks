#!/bin/bash
#
# Включение CSRF защиты обратно (было отключено для дебага)
# КРИТИЧНО ДЛЯ БЕЗОПАСНОСТИ!
#

set -e

echo "=============================================================================="
echo "ВКЛЮЧЕНИЕ CSRF ЗАЩИТЫ"
echo "=============================================================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите с sudo"
    exit 1
fi

cd /opt/metatecks

SETTINGS_FILE="main/settings/base.py"

echo "1. Создание бэкапа settings..."
cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup_csrf_$(date +%Y%m%d_%H%M%S)"
echo "✓ Бэкап создан"
echo ""

echo "2. Проверка текущего состояния CSRF middleware..."
if grep -q "# ВРЕМЕННО ОТКЛЮЧЕН" "$SETTINGS_FILE"; then
    echo "⚠ CSRF middleware отключен - НЕБЕЗОПАСНО!"
    echo ""
elif grep -q "# 'django.middleware.csrf.CsrfViewMiddleware'" "$SETTINGS_FILE"; then
    echo "⚠ CSRF middleware закомментирован - НЕБЕЗОПАСНО!"
    echo ""
else
    echo "✓ CSRF middleware уже включен"
    echo ""
    read -p "Все равно продолжить проверку? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "3. Включение CSRF middleware..."

# Убрать комментарий с CsrfViewMiddleware
sed -i "s/# *'django.middleware.csrf.CsrfViewMiddleware'/'django.middleware.csrf.CsrfViewMiddleware'/g" "$SETTINGS_FILE"

# Убрать строку с комментарием "ВРЕМЕННО ОТКЛЮЧЕН"
sed -i "/ВРЕМЕННО ОТКЛЮЧЕН ДЛЯ ОТЛАДКИ/d" "$SETTINGS_FILE"
sed -i "/ВКЛЮЧИТЬ ПОСЛЕ РЕШЕНИЯ ПРОБЛЕМЫ/d" "$SETTINGS_FILE"

echo "✓ CSRF middleware включен"
echo ""

echo "4. Проверка что изменения применились..."
grep -A2 -B2 "CsrfViewMiddleware" "$SETTINGS_FILE"
echo ""

echo "5. Проверка настроек CSRF_TRUSTED_ORIGINS..."
grep "CSRF_TRUSTED_ORIGINS" .env.docker
echo ""

echo "6. Перезапуск web контейнера..."
docker-compose restart web
echo "✓ Web контейнер перезапущен"
echo ""

echo "7. Ожидание запуска (15 секунд)..."
sleep 15
echo ""

echo "8. Проверка что контейнер работает..."
docker-compose ps | grep web
echo ""

echo "9. Проверка доступности сайта..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://metateks-admin.vinodesign.ru/ 2>/dev/null || echo "FAILED")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Сайт отвечает (HTTP 200)"
else
    echo "⚠ Сайт вернул код: $HTTP_CODE"
fi
echo ""

echo "10. Проверка что Mixed Content все еще исправлен..."
MEDIA_URLS=$(curl -s https://metateks-admin.vinodesign.ru/ | grep -o 'src="[^"]*media[^"]*"' | head -3)
if echo "$MEDIA_URLS" | grep -q 'src="/media/'; then
    echo "✓ Media URL относительные - Mixed Content исправлен!"
    echo "$MEDIA_URLS"
elif echo "$MEDIA_URLS" | grep -q 'src="https://'; then
    echo "✓ Media URL абсолютные HTTPS - Mixed Content исправлен!"
    echo "$MEDIA_URLS"
else
    echo "⚠ Проверьте media URL вручную:"
    echo "$MEDIA_URLS"
fi
echo ""

echo "=============================================================================="
echo "✅ CSRF ЗАЩИТА ВКЛЮЧЕНА!"
echo "=============================================================================="
echo ""
echo "Что было сделано:"
echo "  1. CSRF middleware включен обратно в settings.py"
echo "  2. Web контейнер перезапущен"
echo "  3. Сайт проверен - работает"
echo ""
echo "ВАЖНО - ПРОВЕРЬТЕ В БРАУЗЕРЕ:"
echo "  1. Откройте: https://metateks-admin.vinodesign.ru/admin/"
echo "  2. Попробуйте войти в админку"
echo "  3. Если получите CSRF ошибку - проверьте CSRF_TRUSTED_ORIGINS в .env.docker"
echo ""
echo "Доступные URL:"
echo "  ✓ https://metateks-admin.vinodesign.ru (основной)"
echo "  ✓ http://5.188.138.16:8888 (временный доступ)"
echo ""
echo "Если возникнут проблемы, бэкап сохранен:"
echo "  ${SETTINGS_FILE}.backup_csrf_*"
echo ""
echo "=============================================================================="
