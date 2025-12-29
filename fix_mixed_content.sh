#!/bin/bash
#
# Скрипт для исправления Mixed Content Error
# Проблема: Django генерирует HTTP ссылки на медиафайлы на HTTPS странице
# Решение: Настроить nginx для передачи X-Forwarded-Proto заголовка
#
# Использование:
#   chmod +x fix_mixed_content.sh
#   sudo ./fix_mixed_content.sh
#

set -e

echo "=============================================================================="
echo "ИСПРАВЛЕНИЕ MIXED CONTENT ERROR (HTTP медиа на HTTPS странице)"
echo "=============================================================================="
echo ""

# Проверка что запущен от root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: запустите скрипт с sudo"
    echo "   Используйте: sudo bash fix_mixed_content.sh"
    exit 1
fi

echo "✓ Права root подтверждены"
echo ""

# Путь к конфигурации
NGINX_CONF="/usr/app/back/conf/mirror_nginx.conf"
BACKUP_SUFFIX="_before_mixed_content_fix_$(date +%Y%m%d_%H%M%S)"

# 1. Проверка существования конфигурации
echo "1. Проверка nginx конфигурации..."
if [ ! -f "$NGINX_CONF" ]; then
    echo "❌ Файл не найден: $NGINX_CONF"
    echo "   Ищу альтернативные конфигурации..."
    find /etc/nginx /usr -name "*vinodesign*" -o -name "*mirror*" 2>/dev/null || echo "   Не найдено"
    exit 1
fi
echo "✓ Найдена конфигурация: $NGINX_CONF"
echo ""

# 2. Создание бэкапа
echo "2. Создание бэкапа конфигурации..."
cp "$NGINX_CONF" "${NGINX_CONF}${BACKUP_SUFFIX}"
echo "✓ Бэкап создан: ${NGINX_CONF}${BACKUP_SUFFIX}"
echo ""

# 3. Проверка текущей конфигурации
echo "3. Проверка текущих proxy заголовков..."
if grep -q "X-Forwarded-Proto" "$NGINX_CONF"; then
    echo "✓ X-Forwarded-Proto уже настроен:"
    grep "X-Forwarded-Proto" "$NGINX_CONF"
    echo ""
    echo "Если проблема все еще есть, проверьте значение заголовка."
    echo "Должно быть: proxy_set_header X-Forwarded-Proto \$scheme;"
    echo ""
    read -p "Продолжить и обновить конфигурацию? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo "⚠ X-Forwarded-Proto НЕ настроен - это причина mixed content!"
fi
echo ""

# 4. Обновление конфигурации
echo "4. Обновление nginx конфигурации..."

# Создаем новую конфигурацию с правильными заголовками
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
    proxy_set_header X-Forwarded-Proto $scheme;  # ← ЭТО ИСПРАВЛЯЕТ MIXED CONTENT!
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-Port $server_port;

    # Таймауты
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Буферизация
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
  }
}
NGINX_EOF

echo "✓ Конфигурация обновлена"
echo ""

# 5. Показываем изменения
echo "5. Добавленные заголовки для исправления mixed content:"
echo "   proxy_set_header X-Forwarded-Proto \$scheme;"
echo "   proxy_set_header X-Forwarded-Host \$http_host;"
echo "   proxy_set_header X-Forwarded-Port \$server_port;"
echo ""

# 6. Проверка синтаксиса nginx
echo "6. Проверка синтаксиса nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✓ Синтаксис nginx корректен"
else
    echo "❌ Ошибка в конфигурации nginx:"
    nginx -t
    echo ""
    echo "Откат к предыдущей версии..."
    cp "${NGINX_CONF}${BACKUP_SUFFIX}" "$NGINX_CONF"
    echo "Конфигурация восстановлена из бэкапа"
    exit 1
fi
echo ""

# 7. Перезагрузка nginx
echo "7. Перезагрузка nginx..."
systemctl reload nginx
echo "✓ Nginx перезагружен"
echo ""

# 8. Проверка Django settings
echo "8. Проверка настроек Django..."
SETTINGS_FILE="/opt/metatecks/main/settings/base.py"
if [ -f "$SETTINGS_FILE" ]; then
    echo "   Проверяю наличие SECURE_PROXY_SSL_HEADER..."
    if grep -q "SECURE_PROXY_SSL_HEADER" "$SETTINGS_FILE"; then
        echo "   ✓ SECURE_PROXY_SSL_HEADER настроен в Django"
        grep "SECURE_PROXY_SSL_HEADER" "$SETTINGS_FILE" | head -1
    else
        echo "   ⚠ SECURE_PROXY_SSL_HEADER не найден в settings.py"
        echo "   Это может потребовать дополнительной настройки Django"
    fi
else
    echo "   ⚠ Файл настроек Django не найден: $SETTINGS_FILE"
fi
echo ""

# 9. Тест
echo "9. Тестирование..."
echo "   Проверяю заголовки которые получает Django..."
echo ""
echo "   Делаю запрос через домен и проверяю заголовки:"
curl -s -I -k "https://metateks-admin.vinodesign.ru/" | head -10
echo ""

echo "=============================================================================="
echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "=============================================================================="
echo ""
echo "Что было исправлено:"
echo "  1. Добавлен заголовок X-Forwarded-Proto в nginx"
echo "  2. Nginx теперь передает Django информацию о HTTPS"
echo "  3. Django будет генерировать HTTPS ссылки на медиафайлы"
echo ""
echo "Следующие шаги:"
echo "  1. Очистите кэш браузера (Ctrl+Shift+R)"
echo "  2. Откройте: https://metateks-admin.vinodesign.ru"
echo "  3. Проверьте загрузку изображений (F12 → Console)"
echo "  4. Ошибка 'blocked:mixed-content' должна исчезнуть"
echo ""
echo "Если проблема сохраняется:"
echo "  - Проверьте в Django settings что SECURE_PROXY_SSL_HEADER настроен:"
echo "    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')"
echo "  - Перезапустите Docker контейнеры:"
echo "    cd /opt/metatecks && docker-compose restart web"
echo ""
echo "Бэкап конфигурации сохранен:"
echo "  ${NGINX_CONF}${BACKUP_SUFFIX}"
echo ""
echo "=============================================================================="
