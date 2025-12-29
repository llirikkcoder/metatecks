#!/bin/bash
#
# Исправление Mixed Content через nginx sub_filter
# Замена абсолютных HTTP URL на относительные прямо в HTML
#

set -e

echo "=============================================================================="
echo "ИСПРАВЛЕНИЕ MIXED CONTENT ЧЕРЕЗ NGINX SUB_FILTER"
echo "=============================================================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите с sudo"
    exit 1
fi

NGINX_CONF="/usr/app/back/conf/mirror_nginx.conf"

echo "1. Создание бэкапа..."
cp "$NGINX_CONF" "${NGINX_CONF}.backup_subfilter_$(date +%Y%m%d_%H%M%S)"
echo "✓ Бэкап создан"
echo ""

echo "2. Обновление конфигурации nginx..."
cat > "$NGINX_CONF" << 'NGINX_EOF'
# -- redirects

server {
  listen 80;
  server_name metateks-admin.vinodesign.ru spb.metateks-admin.vinodesign.ru ekb.metateks-admin.vinodesign.ru nsk.metateks-admin.vinodesign.ru krasnodar.metateks-admin.vinodesign.ru yaroslavl.metateks-admin.vinodesign.ru murmansk.metateks-admin.vinodesign.ru;
  return 301 https://metateks-admin.vinodesign.ru$request_uri;
}

# -- main

server {
  listen 443 ssl http2;
  ssl_certificate /etc/letsencrypt/live/metateks-admin.vinodesign.ru/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/metateks-admin.vinodesign.ru/privkey.pem;

  server_name metateks-admin.vinodesign.ru spb.metateks-admin.vinodesign.ru ekb.metateks-admin.vinodesign.ru nsk.metateks-admin.vinodesign.ru krasnodar.metateks-admin.vinodesign.ru yaroslavl.metateks-admin.vinodesign.ru murmansk.metateks-admin.vinodesign.ru;

  charset utf-8;
  client_max_body_size 100M;
  client_body_buffer_size 50M;

  proxy_send_timeout 300;
  proxy_read_timeout 300;

  gzip on;
  gzip_types text/plain application/xml text/css application/javascript "application/javascript; charset=utf-8";
  gzip_min_length 1000;

  access_log /var/log/metateks/nginx/access.log;
  error_log /var/log/metateks/nginx/error.log;

  # ФИКС MIXED CONTENT: замена абсолютных HTTP URL на относительные
  sub_filter 'http://5.188.138.16/media/' '/media/';
  sub_filter 'http://5.188.138.16:8888/media/' '/media/';
  sub_filter 'http://5.188.138.16/static/' '/static/';
  sub_filter_once off;
  sub_filter_types text/html application/json;

  # Статика из Docker volume
  location /static/ {
    alias /var/lib/docker/volumes/metateks_static_volume/_data/;
    expires 30d;
    add_header Cache-Control "public, immutable";
  }

  # Media из проекта
  location /media/ {
    alias /opt/metatecks/media/;
    expires 7d;
    add_header Cache-Control "public";
  }

  # Проксирование в Docker nginx
  location / {
    proxy_pass http://127.0.0.1:8080;

    # ВАЖНО: Заголовки для правильной работы Django через HTTPS
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-Port $server_port;

    # Таймауты
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Буферизация (ВАЖНО для sub_filter!)
    proxy_buffering on;
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;
  }
}
NGINX_EOF

echo "✓ Конфигурация обновлена"
echo ""

echo "3. Что было добавлено:"
echo "----------------------"
echo "  sub_filter 'http://5.188.138.16/media/' '/media/';"
echo "  sub_filter 'http://5.188.138.16:8888/media/' '/media/';"
echo "  sub_filter 'http://5.188.138.16/static/' '/static/';"
echo "  sub_filter_once off;"
echo "  sub_filter_types text/html application/json;"
echo ""
echo "  + увеличены proxy_buffers для работы sub_filter"
echo ""

echo "4. Проверка синтаксиса nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✓ Синтаксис nginx корректен"
else
    echo "❌ Ошибка в конфигурации nginx:"
    nginx -t
    echo ""
    echo "Откат к предыдущей версии..."
    cp "${NGINX_CONF}.backup_subfilter_"* "$NGINX_CONF" 2>/dev/null || true
    exit 1
fi
echo ""

echo "5. Перезагрузка nginx..."
systemctl reload nginx
echo "✓ Nginx перезагружен"
echo ""

echo "6. Проверка результата..."
sleep 2
echo "----------------------------"
echo ""
echo "До (старые абсолютные URL):"
echo "  http://5.188.138.16/media/..."
echo ""
echo "После (относительные URL):"
curl -s https://metateks-admin.vinodesign.ru/ | grep -o 'src="[^"]*media[^"]*"' | head -5
echo ""
echo ""

echo "=============================================================================="
echo "✅ ГОТОВО!"
echo "=============================================================================="
echo ""
echo "Nginx теперь автоматически заменяет:"
echo "  http://5.188.138.16/media/xxx → /media/xxx"
echo ""
echo "Браузер будет загружать файлы через HTTPS и Mixed Content исчезнет!"
echo ""
echo "ПРОВЕРЬТЕ В БРАУЗЕРЕ:"
echo "  1. Очистите кэш (Ctrl+Shift+R)"
echo "  2. Откройте: https://metateks-admin.vinodesign.ru"
echo "  3. Проверьте консоль (F12) - ошибки blocked:mixed-content больше не должно быть"
echo "  4. Изображения должны загружаться!"
echo ""
echo "Это временное решение (workaround)."
echo "В будущем нужно будет обновить URL в базе данных."
echo ""
echo "=============================================================================="
