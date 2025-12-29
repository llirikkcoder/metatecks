#!/bin/bash
echo "========================================="
echo "ДИАГНОСТИКА CSRF ПРОБЛЕМЫ"
echo "========================================="
echo ""

cd /opt/metatecks

echo "1. Проверка кода на хосте:"
grep -A 1 "ALLOWED_HOSTS" main/settings/base.py
echo ""

echo "2. Проверка кода в контейнере:"
docker-compose exec -T web grep -A 1 "ALLOWED_HOSTS" /app/main/settings/base.py
echo ""

echo "3. Переменная окружения в контейнере:"
docker-compose exec -T web env | grep CSRF
echo ""

echo "4. Проверка Python:"
docker-compose exec -T web python -c "import os; print('ENV CSRF_TRUSTED_ORIGINS:', os.getenv('CSRF_TRUSTED_ORIGINS'))"
echo ""

echo "5. Проверка Django settings:"
docker-compose exec -T web python manage.py shell -c "from django.conf import settings; print('Django CSRF_TRUSTED_ORIGINS:', settings.CSRF_TRUSTED_ORIGINS)"
echo ""

echo "========================================="
echo "ЕСЛИ ПРОБЛЕМА НАЙДЕНА - ИСПРАВЛЯЕМ:"
echo "========================================="
echo ""

# Проверяем есть ли CSRF_TRUSTED_ORIGINS в коде контейнера
if docker-compose exec -T web grep -q "CSRF_TRUSTED_ORIGINS" /app/main/settings/base.py; then
    echo "✓ Код в контейнере ОБНОВЛЕН"
else
    echo "✗ Код в контейнере СТАРЫЙ - нужно пересобрать"
    echo ""
    echo "Пересборка образа..."
    docker-compose down
    docker-compose build --no-cache web celery
    docker-compose up -d
    echo ""
    echo "Подождите 30 секунд..."
    sleep 30
    echo ""
    echo "Проверка после пересборки:"
    docker-compose exec -T web python manage.py shell -c "from django.conf import settings; print('CSRF_TRUSTED_ORIGINS:', settings.CSRF_TRUSTED_ORIGINS)"
fi

echo ""
echo "========================================="
echo "ГОТОВО! Откройте:"
echo "http://5.188.138.16:8888/admin/"
echo "========================================="
