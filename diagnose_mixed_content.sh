#!/bin/bash
#
# Диагностика проблемы Mixed Content
#

echo "=============================================================================="
echo "ДИАГНОСТИКА MIXED CONTENT"
echo "=============================================================================="
echo ""

echo "1. Проверка что генерирует Django в HTML:"
echo "-------------------------------------------"
curl -s https://metateks-admin.vinodesign.ru/ | grep -o 'src="http[^"]*media[^"]*"' | head -3
echo ""

echo "2. Статус контейнеров:"
echo "----------------------"
docker-compose ps
echo ""

echo "3. Конфигурация Docker nginx (location /):"
echo "-------------------------------------------"
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf | grep -A10 "location / {" | head -15
echo ""

echo "4. .env.docker настройки:"
echo "-------------------------"
cat /opt/metatecks/.env.docker | grep -E "ALLOWED_HOSTS|CSRF_TRUSTED|DEFAULT_SCHEME"
echo ""

echo "5. Django settings USE_X_FORWARDED:"
echo "-----------------------------------"
grep -n "USE_X_FORWARDED" /opt/metatecks/main/settings/base.py
echo ""

echo "6. Django settings SECURE_PROXY_SSL_HEADER:"
echo "--------------------------------------------"
grep -n "SECURE_PROXY_SSL_HEADER" /opt/metatecks/main/settings/base.py
echo ""

echo "7. Системный nginx конфигурация (заголовки):"
echo "---------------------------------------------"
cat /usr/app/back/conf/mirror_nginx.conf | grep -A15 "location / {" | grep proxy_set_header
echo ""

echo "8. Логи Docker nginx (последние 10 строк):"
echo "-------------------------------------------"
docker-compose logs --tail=10 nginx
echo ""

echo "9. Логи web (последние 10 строк):"
echo "----------------------------------"
docker-compose logs --tail=10 web
echo ""

echo "=============================================================================="
echo "ДИАГНОСТИКА ЗАВЕРШЕНА"
echo "=============================================================================="
