#!/bin/bash
#
# Полное исправление Mixed Content проблемы
# Запускает все шаги по порядку
#

set -e

echo "=============================================================================="
echo "ПОЛНОЕ ИСПРАВЛЕНИЕ MIXED CONTENT"
echo "=============================================================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите с sudo: sudo bash fix_all_mixed_content.sh"
    exit 1
fi

cd /opt/metatecks

# Шаг 1: Диагностика
echo "ШАГ 1: ДИАГНОСТИКА ТЕКУЩЕГО СОСТОЯНИЯ"
echo "======================================"
bash diagnose_mixed_content.sh
echo ""
read -p "Нажмите Enter чтобы продолжить..."
echo ""

# Шаг 2: Исправление ALLOWED_HOSTS
echo "ШАГ 2: ИСПРАВЛЕНИЕ ALLOWED_HOSTS"
echo "================================="
bash fix_allowed_hosts.sh
echo ""
read -p "Нажмите Enter чтобы продолжить..."
echo ""

# Шаг 3: Тестирование заголовков
echo "ШАГ 3: ПРОВЕРКА ЗАГОЛОВКОВ DJANGO"
echo "=================================="
bash test_django_headers.sh
echo ""
read -p "Нажмите Enter чтобы продолжить..."
echo ""

# Шаг 4: Финальная проверка
echo "ШАГ 4: ФИНАЛЬНАЯ ПРОВЕРКА"
echo "========================="
echo ""
echo "Проверка что генерирует Django в HTML:"
curl -s https://metateks-admin.vinodesign.ru/ | grep -o 'src="[^"]*media[^"]*"' | head -5
echo ""
echo ""

echo "=============================================================================="
echo "РЕЗУЛЬТАТ:"
echo "=============================================================================="
echo ""

# Анализ результата
if curl -s https://metateks-admin.vinodesign.ru/ | grep -q 'src="https://metateks-admin.vinodesign.ru/media/'; then
    echo "✅ УСПЕХ! Django генерирует HTTPS ссылки!"
    echo ""
    echo "Действия:"
    echo "  1. Очистите кэш браузера (Ctrl+Shift+R)"
    echo "  2. Откройте: https://metateks-admin.vinodesign.ru"
    echo "  3. Mixed Content ошибка должна исчезнуть!"
    echo ""
elif curl -s https://metateks-admin.vinodesign.ru/ | grep -q 'src="http://5.188.138.16/media/'; then
    echo "❌ ПРОБЛЕМА НЕ РЕШЕНА - все еще http://5.188.138.16"
    echo ""
    echo "Возможные причины:"
    echo "  1. Django кэширует старые данные - попробуйте:"
    echo "     docker-compose restart"
    echo "  2. Заголовки не доходят до Django - проверьте вывод Шага 3"
    echo "  3. В базе данных сохранены старые абсолютные URL"
    echo ""
    echo "Для дальнейшей диагностики откройте:"
    echo "  https://metateks-admin.vinodesign.ru/test-headers-debug/"
    echo ""
elif curl -s https://metateks-admin.vinodesign.ru/ | grep -q 'src="/media/'; then
    echo "✅ ЧАСТИЧНЫЙ УСПЕХ! Django генерирует относительные ссылки"
    echo ""
    echo "Это правильно! Относительные ссылки /media/... работают и с HTTP и с HTTPS."
    echo ""
    echo "Действия:"
    echo "  1. Очистите кэш браузера (Ctrl+Shift+R)"
    echo "  2. Откройте: https://metateks-admin.vinodesign.ru"
    echo "  3. Mixed Content ошибка должна исчезнуть!"
    echo ""
else
    echo "⚠ Не удалось определить формат ссылок"
    echo "Проверьте вручную исходный код страницы"
fi

echo "=============================================================================="
