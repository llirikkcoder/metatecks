#!/bin/bash
#
# Скрипт для настройки Nginx на порту 8888 для Docker приложения
# Безопасно - не трогает существующие конфигурации
#
# Использование:
#   chmod +x setup_nginx_port8888.sh
#   sudo ./setup_nginx_port8888.sh
#

set -e

echo "=============================================================================="
echo "НАСТРОЙКА NGINX ДЛЯ DOCKER ПРИЛОЖЕНИЯ (ПОРТ 8888)"
echo "=============================================================================="
echo ""

# Проверка что запущен от root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: запустите скрипт с sudo"
    echo "   Используйте: sudo bash setup_nginx_port8888.sh"
    exit 1
fi

echo "✓ Права root подтверждены"
echo ""

# Проверка что Docker приложение запущено
echo "Проверка Docker контейнеров..."
if docker ps | grep -q metateks_nginx; then
    echo "✓ Docker nginx контейнер запущен"
else
    echo "⚠ Предупреждение: Docker nginx контейнер не найден"
    echo "  Убедитесь что вы запустили: docker-compose up -d"
    read -p "Продолжить? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# Проверка что порт 8888 свободен
echo "Проверка доступности порта 8888..."
if netstat -tlnp | grep -q ":8888 "; then
    echo "❌ Ошибка: порт 8888 уже занят"
    netstat -tlnp | grep ":8888 "
    echo "  Измените порт в скрипте или освободите 8888"
    exit 1
else
    echo "✓ Порт 8888 свободен"
fi
echo ""

# Создание конфигурации Nginx
echo "Создание конфигурации Nginx..."

CONFIG_FILE="/etc/nginx/sites-available/metateks-ip"

cat > "$CONFIG_FILE" << 'EOF'
# Временная конфигурация для доступа к Docker приложению по IP
# Создано автоматически скриптом setup_nginx_port8888.sh

server {
    listen 8888;
    server_name _;

    # Логи
    access_log /var/log/nginx/metateks-docker-ip_access.log;
    error_log /var/log/nginx/metateks-docker-ip_error.log;

    # Максимальный размер загружаемых файлов
    client_max_body_size 100M;
    client_body_buffer_size 50M;

    # Статические файлы из Docker volume
    location /static/ {
        alias /var/lib/docker/volumes/metateks_static_volume/_data/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media файлы из /opt/metatecks
    location /media/ {
        alias /opt/metatecks/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Проксирование в Docker nginx
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

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
EOF

echo "✓ Конфигурация создана: $CONFIG_FILE"
echo ""

# Создание симлинка
echo "Активация конфигурации..."

SYMLINK="/etc/nginx/sites-enabled/metateks-ip"

if [ -L "$SYMLINK" ]; then
    echo "⚠ Симлинк уже существует, пересоздаю..."
    rm "$SYMLINK"
fi

ln -s "$CONFIG_FILE" "$SYMLINK"
echo "✓ Симлинк создан: $SYMLINK"
echo ""

# Проверка конфигурации Nginx
echo "Проверка конфигурации Nginx..."
if nginx -t 2>&1 | tee /tmp/nginx_test.log; then
    echo "✓ Конфигурация Nginx корректна"
else
    echo "❌ Ошибка в конфигурации Nginx:"
    cat /tmp/nginx_test.log
    echo ""
    echo "Откат изменений..."
    rm "$SYMLINK"
    rm "$CONFIG_FILE"
    echo "Конфигурация удалена"
    exit 1
fi
echo ""

# Перезагрузка Nginx
echo "Перезагрузка Nginx..."
if systemctl reload nginx; then
    echo "✓ Nginx успешно перезагружен"
else
    echo "❌ Ошибка при перезагрузке Nginx"
    systemctl status nginx
    exit 1
fi
echo ""

# Проверка что порт слушается
sleep 2
echo "Проверка что порт 8888 активен..."
if netstat -tlnp | grep -q ":8888 "; then
    echo "✓ Nginx слушает на порту 8888"
    netstat -tlnp | grep ":8888 "
else
    echo "⚠ Nginx не слушает на порту 8888"
    echo "  Проверьте логи: tail -f /var/log/nginx/error.log"
fi
echo ""

# Определение IP адреса
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "5.188.138.16")
echo ""

echo "=============================================================================="
echo "✅ НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!"
echo "=============================================================================="
echo ""
echo "Приложение доступно по адресу:"
echo "  → http://$PUBLIC_IP:8888"
echo ""
echo "Также можно открыть:"
echo "  → http://5.188.138.16:8888"
echo ""
echo "Админка:"
echo "  → http://$PUBLIC_IP:8888/admin/"
echo ""
echo "Проверка работы:"
echo "  curl http://127.0.0.1:8888"
echo "  curl http://$PUBLIC_IP:8888"
echo ""
echo "Логи Nginx:"
echo "  tail -f /var/log/nginx/metateks-docker-ip_access.log"
echo "  tail -f /var/log/nginx/metateks-docker-ip_error.log"
echo ""
echo "Логи Docker:"
echo "  docker-compose -f /opt/metatecks/docker-compose.yml logs -f"
echo ""
echo "Старые приложения продолжают работать:"
echo "  ✓ https://metateks.vlch.dev"
echo "  ✓ https://metateks-admin.vinodesign.ru"
echo ""
echo "Для отключения этого конфига:"
echo "  sudo rm /etc/nginx/sites-enabled/metateks-ip"
echo "  sudo systemctl reload nginx"
echo ""
echo "=============================================================================="
