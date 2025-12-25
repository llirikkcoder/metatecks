#!/bin/bash

# ============================================================================
# Скрипт мониторинга интеграции с 1С в реальном времени
# ============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Мониторинг интеграции с 1С${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Функция для вывода меню
show_menu() {
    echo -e "${YELLOW}Выберите режим мониторинга:${NC}"
    echo ""
    echo "  1) Все логи веб-сервера (включая 1С запросы)"
    echo "  2) Только запросы к /1c_exchange.php"
    echo "  3) Логи синхронизации (cml_sync.log)"
    echo "  4) Логи Celery задач (cml_tasks.log)"
    echo "  5) Логи парсинга XML (cml_utils.log)"
    echo "  6) Все логи 1С интеграции (sync + tasks + utils)"
    echo "  7) Логи Celery worker (обработка импорта)"
    echo "  8) Nginx access log (все HTTP запросы)"
    echo "  9) Проверка последних обменов (из БД)"
    echo " 10) Тестовый запрос к 1С endpoint"
    echo "  0) Выход"
    echo ""
}

# Функция для логов веб-сервера
monitor_web_logs() {
    echo -e "${BLUE}📊 Мониторинг логов веб-сервера...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""
    docker-compose logs -f web
}

# Функция для фильтрации 1С запросов
monitor_1c_requests() {
    echo -e "${BLUE}📊 Мониторинг запросов к /1c_exchange.php...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""
    docker-compose logs -f web nginx | grep -E "1c_exchange|exchange\.php" --color=always
}

# Функция для логов синхронизации
monitor_sync_logs() {
    echo -e "${BLUE}📊 Мониторинг логов синхронизации...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""

    # Проверяем существование файла
    if docker-compose exec -T web test -f /app/logs/cml_sync.log; then
        docker-compose exec web tail -f /app/logs/cml_sync.log
    else
        echo -e "${RED}Файл /app/logs/cml_sync.log не найден${NC}"
        echo "Возможно, синхронизация еще не запускалась."
    fi
}

# Функция для логов Celery задач
monitor_tasks_logs() {
    echo -e "${BLUE}📊 Мониторинг логов Celery задач...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""

    if docker-compose exec -T web test -f /app/logs/cml_tasks.log; then
        docker-compose exec web tail -f /app/logs/cml_tasks.log
    else
        echo -e "${RED}Файл /app/logs/cml_tasks.log не найден${NC}"
        echo "Возможно, задачи еще не выполнялись."
    fi
}

# Функция для логов парсинга
monitor_utils_logs() {
    echo -e "${BLUE}📊 Мониторинг логов парсинга XML...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""

    if docker-compose exec -T web test -f /app/logs/cml_utils.log; then
        docker-compose exec web tail -f /app/logs/cml_utils.log
    else
        echo -e "${RED}Файл /app/logs/cml_utils.log не найден${NC}"
        echo "Возможно, парсинг еще не выполнялся."
    fi
}

# Функция для всех логов 1С
monitor_all_cml_logs() {
    echo -e "${BLUE}📊 Мониторинг всех логов 1С интеграции...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""

    # Используем multitail или запускаем tail для всех файлов
    docker-compose exec web bash -c "tail -f /app/logs/cml_*.log 2>/dev/null || echo 'Нет логов 1С'"
}

# Функция для логов Celery worker
monitor_celery_logs() {
    echo -e "${BLUE}📊 Мониторинг Celery worker (обработка импорта)...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""
    docker-compose logs -f celery | grep -E "make_import|sync|CML|1C|ImportedProduct" --color=always
}

# Функция для Nginx access log
monitor_nginx_logs() {
    echo -e "${BLUE}📊 Мониторинг Nginx access log...${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для выхода${NC}"
    echo ""
    docker-compose exec nginx tail -f /var/log/nginx/metateks_access.log
}

# Функция для проверки последних обменов из БД
check_recent_exchanges() {
    echo -e "${BLUE}📊 Проверка последних обменов с 1С (из БД)...${NC}"
    echo ""

    docker-compose exec -T web python manage.py shell << 'PYEOF'
from apps.third_party.cml.models import Exchange, ExchangeParsing
from django.utils import timezone
from datetime import timedelta

print("=" * 60)
print("ПОСЛЕДНИЕ ОБМЕНЫ С 1С")
print("=" * 60)

# Последние 10 обменов
exchanges = Exchange.objects.all().order_by('-created_at')[:10]

if not exchanges:
    print("\n❌ Обменов с 1С еще не было")
else:
    for ex in exchanges:
        status = "✅" if ex.status == 'success' else "⏳" if ex.status == 'progress' else "❌"
        print(f"\n{status} {ex.mode.upper()} - {ex.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Пользователь: {ex.user.username if ex.user else 'Неизвестен'}")
        print(f"   Файл: {ex.filename or 'N/A'}")
        print(f"   Статус: {ex.status}")

        # Парсинги для этого обмена
        parsings = ex.parsings.all()
        if parsings:
            print(f"   Обработано файлов: {parsings.count()}")
            for p in parsings:
                print(f"     - {p.filename}")

print("\n" + "=" * 60)

# Статистика за последние 24 часа
yesterday = timezone.now() - timedelta(hours=24)
recent_count = Exchange.objects.filter(created_at__gte=yesterday).count()
print(f"\n📊 Обменов за последние 24 часа: {recent_count}")

# Последняя успешная синхронизация
last_success = Exchange.objects.filter(status='success').order_by('-created_at').first()
if last_success:
    time_ago = timezone.now() - last_success.created_at
    hours = int(time_ago.total_seconds() / 3600)
    print(f"✅ Последняя успешная синхронизация: {hours}ч назад ({last_success.created_at.strftime('%Y-%m-%d %H:%M:%S')})")
else:
    print("❌ Успешных синхронизаций еще не было")

print("")
PYEOF
}

# Функция для тестового запроса
test_1c_endpoint() {
    echo -e "${BLUE}📊 Тестовый запрос к 1С endpoint...${NC}"
    echo ""

    echo "Без аутентификации (должен вернуть 401):"
    curl -i http://localhost/1c_exchange.php?type=catalog\&mode=checkauth

    echo ""
    echo ""
    echo "С базовой аутентификацией (если есть пользователь):"
    echo "Введите имя пользователя (или Enter для пропуска):"
    read username

    if [ -n "$username" ]; then
        echo "Введите пароль:"
        read -s password
        echo ""
        curl -i -u "$username:$password" http://localhost/1c_exchange.php?type=catalog\&mode=checkauth
    fi
}

# Главный цикл
while true; do
    show_menu
    read -p "Ваш выбор: " choice
    echo ""

    case $choice in
        1) monitor_web_logs ;;
        2) monitor_1c_requests ;;
        3) monitor_sync_logs ;;
        4) monitor_tasks_logs ;;
        5) monitor_utils_logs ;;
        6) monitor_all_cml_logs ;;
        7) monitor_celery_logs ;;
        8) monitor_nginx_logs ;;
        9) check_recent_exchanges ;;
        10) test_1c_endpoint ;;
        0)
            echo "Выход..."
            exit 0
            ;;
        *)
            echo -e "${RED}Неверный выбор. Попробуйте снова.${NC}"
            echo ""
            ;;
    esac

    echo ""
    echo -e "${YELLOW}Нажмите Enter для возврата в меню...${NC}"
    read
    clear
done
