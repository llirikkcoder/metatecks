#!/bin/bash
#
# Скрипт для исправления доступа к медиафайлам
# Проблема: изображения не загружаются на https://metateks-admin.vinodesign.ru
#          но работают на http://5.188.138.16:8888
#
# Использование:
#   chmod +x fix_media_permissions.sh
#   sudo ./fix_media_permissions.sh
#

set -e

echo "=============================================================================="
echo "ДИАГНОСТИКА И ИСПРАВЛЕНИЕ ДОСТУПА К MEDIA ФАЙЛАМ"
echo "=============================================================================="
echo ""

# Проверка что запущен от root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: запустите скрипт с sudo"
    echo "   Используйте: sudo bash fix_media_permissions.sh"
    exit 1
fi

echo "✓ Права root подтверждены"
echo ""

# 1. Проверка существования директории media
echo "1. Проверка директории media..."
if [ -d "/opt/metatecks/media" ]; then
    echo "✓ Директория /opt/metatecks/media существует"
    ls -la /opt/metatecks/media | head -5
else
    echo "❌ ОШИБКА: Директория /opt/metatecks/media НЕ СУЩЕСТВУЕТ!"
    echo ""
    echo "Проверяю альтернативные пути:"
    find /opt -maxdepth 3 -name media -type d 2>/dev/null || echo "  Не найдено"
    echo ""
    echo "Возможно медиафайлы не были скопированы на VPS."
    echo "Где находятся медиафайлы?"
    exit 1
fi
echo ""

# 2. Проверка прав доступа
echo "2. Проверка прав доступа к media..."
MEDIA_PERMS=$(stat -c "%a" /opt/metatecks/media 2>/dev/null)
echo "  Текущие права на /opt/metatecks/media: $MEDIA_PERMS"
echo ""

# 3. Проверка доступа для nginx (пользователь www-data)
echo "3. Проверка доступа для nginx (пользователь www-data)..."
if sudo -u www-data test -r /opt/metatecks/media; then
    echo "✓ www-data может читать /opt/metatecks/media"
else
    echo "❌ www-data НЕ МОЖЕТ читать /opt/metatecks/media"
fi

if sudo -u www-data ls /opt/metatecks/media >/dev/null 2>&1; then
    echo "✓ www-data может получить список файлов"
else
    echo "❌ www-data НЕ МОЖЕТ получить список файлов"
fi
echo ""

# 4. Проверка родительских директорий
echo "4. Проверка прав на родительские директории..."
for dir in /opt /opt/metatecks /opt/metatecks/media; do
    if [ -e "$dir" ]; then
        perms=$(stat -c "%a" "$dir")
        owner=$(stat -c "%U:%G" "$dir")
        echo "  $dir: $perms ($owner)"
    fi
done
echo ""

# 5. Тестовая проверка конкретного файла
echo "5. Поиск тестового изображения..."
TEST_IMAGE=$(find /opt/metatecks/media -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.svg" \) | head -1)
if [ -n "$TEST_IMAGE" ]; then
    echo "  Найден: $TEST_IMAGE"
    TEST_PERMS=$(stat -c "%a" "$TEST_IMAGE" 2>/dev/null)
    TEST_OWNER=$(stat -c "%U:%G" "$TEST_IMAGE" 2>/dev/null)
    echo "  Права: $TEST_PERMS, Владелец: $TEST_OWNER"

    if sudo -u www-data test -r "$TEST_IMAGE"; then
        echo "✓ www-data может читать этот файл"
    else
        echo "❌ www-data НЕ МОЖЕТ читать этот файл"
    fi
else
    echo "⚠ Тестовое изображение не найдено"
fi
echo ""

# 6. Исправление прав доступа
echo "6. Исправление прав доступа..."
echo "  Устанавливаю права доступа для nginx..."

# Даем execute права на родительские директории
chmod +x /opt 2>/dev/null || true
chmod +x /opt/metatecks 2>/dev/null || true
chmod +x /opt/metatecks/media 2>/dev/null || true

# Даем права на чтение всех файлов и обход всех директорий
chmod -R +rX /opt/metatecks/media

echo "✓ Права установлены"
echo ""

# 7. Проверка после исправления
echo "7. Проверка после исправления..."
if sudo -u www-data ls /opt/metatecks/media >/dev/null 2>&1; then
    echo "✓ www-data теперь может получить список файлов"
else
    echo "❌ www-data все еще НЕ МОЖЕТ получить список файлов"
    echo "  Требуется дополнительная диагностика"
fi

if [ -n "$TEST_IMAGE" ]; then
    if sudo -u www-data test -r "$TEST_IMAGE"; then
        echo "✓ www-data теперь может читать тестовый файл"
    else
        echo "❌ www-data все еще НЕ МОЖЕТ читать тестовый файл"
    fi
fi
echo ""

# 8. Проверка nginx конфигурации
echo "8. Проверка nginx конфигурации для домена..."
if [ -f "/usr/app/back/conf/mirror_nginx.conf" ]; then
    echo "  Конфигурация найдена: /usr/app/back/conf/mirror_nginx.conf"
    echo "  Путь к media в конфигурации:"
    grep -A2 "location /media" /usr/app/back/conf/mirror_nginx.conf || echo "  Не найдено"
else
    echo "⚠ Файл /usr/app/back/conf/mirror_nginx.conf не найден"
    echo "  Ищу конфигурации nginx с metateks..."
    find /etc/nginx -name "*metateks*" -o -name "*vinodesign*" 2>/dev/null
fi
echo ""

# 9. Тест доступности через curl
echo "9. Тест доступности медиафайлов через nginx..."
if [ -n "$TEST_IMAGE" ]; then
    # Получаем относительный путь от media/
    REL_PATH=${TEST_IMAGE#/opt/metatecks/media/}
    echo "  Тестовый URL: /media/$REL_PATH"

    # Тест через IP:8888
    echo -n "  http://127.0.0.1:8888/media/$REL_PATH: "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8888/media/$REL_PATH" 2>/dev/null || echo "FAILED")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✓ 200 OK"
    else
        echo "❌ $HTTP_CODE"
    fi

    # Тест через домен (localhost, т.к. SSL)
    echo -n "  https://metateks-admin.vinodesign.ru/media/$REL_PATH: "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k "https://metateks-admin.vinodesign.ru/media/$REL_PATH" 2>/dev/null || echo "FAILED")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✓ 200 OK"
    else
        echo "❌ $HTTP_CODE"
        echo "  Проверяю логи nginx..."
        tail -5 /var/log/metateks/nginx/error.log 2>/dev/null | grep -i media || echo "  Нет ошибок в логах"
    fi
fi
echo ""

# 10. Перезагрузка nginx
echo "10. Перезагрузка nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✓ Конфигурация nginx корректна"
    systemctl reload nginx
    echo "✓ Nginx перезагружен"
else
    echo "❌ Ошибка в конфигурации nginx"
    nginx -t
fi
echo ""

echo "=============================================================================="
echo "ДИАГНОСТИКА ЗАВЕРШЕНА"
echo "=============================================================================="
echo ""
echo "Следующие шаги:"
echo "1. Откройте в браузере: https://metateks-admin.vinodesign.ru"
echo "2. Проверьте загрузку изображений (откройте консоль браузера F12)"
echo "3. Если изображения не грузятся, проверьте логи:"
echo "   tail -f /var/log/metateks/nginx/error.log"
echo "   tail -f /var/log/nginx/error.log"
echo ""

if [ -n "$TEST_IMAGE" ]; then
    REL_PATH=${TEST_IMAGE#/opt/metatecks/media/}
    echo "Для быстрой проверки можно открыть конкретный файл:"
    echo "  https://metateks-admin.vinodesign.ru/media/$REL_PATH"
    echo ""
fi

echo "=============================================================================="
