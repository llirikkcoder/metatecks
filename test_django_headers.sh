#!/bin/bash
#
# Создание тестового endpoint для проверки заголовков Django
#

set -e

echo "=============================================================================="
echo "СОЗДАНИЕ ТЕСТОВОГО ENDPOINT ДЛЯ ПРОВЕРКИ ЗАГОЛОВКОВ"
echo "=============================================================================="
echo ""

cd /opt/metatecks

echo "1. Создание тестового view..."
cat > /tmp/test_headers_view.py << 'PYEOF'
from django.http import HttpResponse

def test_headers(request):
    lines = [
        "=== Django Request Info ===",
        "",
        f"request.get_host() = {request.get_host()}",
        f"request.is_secure() = {request.is_secure()}",
        f"request.scheme = {request.scheme}",
        f"request.build_absolute_uri('/media/test.jpg') = {request.build_absolute_uri('/media/test.jpg')}",
        "",
        "=== HTTP Headers ===",
        "",
        f"HTTP_HOST = {request.META.get('HTTP_HOST', 'NOT SET')}",
        f"HTTP_X_FORWARDED_PROTO = {request.META.get('HTTP_X_FORWARDED_PROTO', 'NOT SET')}",
        f"HTTP_X_FORWARDED_HOST = {request.META.get('HTTP_X_FORWARDED_HOST', 'NOT SET')}",
        f"HTTP_X_FORWARDED_PORT = {request.META.get('HTTP_X_FORWARDED_PORT', 'NOT SET')}",
        f"HTTP_X_FORWARDED_FOR = {request.META.get('HTTP_X_FORWARDED_FOR', 'NOT SET')}",
        f"HTTP_X_REAL_IP = {request.META.get('HTTP_X_REAL_IP', 'NOT SET')}",
        "",
        "=== Django Settings ===",
        "",
    ]

    from django.conf import settings
    lines.append(f"ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
    lines.append(f"CSRF_TRUSTED_ORIGINS = {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET')}")
    lines.append(f"USE_X_FORWARDED_HOST = {getattr(settings, 'USE_X_FORWARDED_HOST', False)}")
    lines.append(f"USE_X_FORWARDED_PORT = {getattr(settings, 'USE_X_FORWARDED_PORT', False)}")
    lines.append(f"SECURE_PROXY_SSL_HEADER = {getattr(settings, 'SECURE_PROXY_SSL_HEADER', 'NOT SET')}")

    return HttpResponse('\n'.join(lines), content_type='text/plain')
PYEOF

docker cp /tmp/test_headers_view.py metateks_web:/tmp/
echo "✓ View файл скопирован в контейнер"
echo ""

echo "2. Добавление URL в Django..."
cat > /tmp/add_test_url.py << 'PYEOF'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.urls import path
from main import urls
import sys
sys.path.insert(0, '/tmp')
from test_headers_view import test_headers

# Добавляем URL если его еще нет
test_path = path('test-headers-debug/', test_headers)
if not any(p.pattern._route == 'test-headers-debug/' for p in urls.urlpatterns if hasattr(p, 'pattern')):
    urls.urlpatterns.insert(0, test_path)
    print("✓ URL добавлен: /test-headers-debug/")
else:
    print("✓ URL уже существует")
PYEOF

docker cp /tmp/add_test_url.py metateks_web:/tmp/
docker-compose exec web python /tmp/add_test_url.py
echo ""

echo "3. Тестирование endpoint..."
echo "----------------------------"
echo ""
curl -s https://metateks-admin.vinodesign.ru/test-headers-debug/
echo ""
echo ""

echo "=============================================================================="
echo "ПРОВЕРЬТЕ ВЫВОД ВЫШЕ:"
echo "=============================================================================="
echo ""
echo "Важные параметры:"
echo "  - request.is_secure() должен быть True"
echo "  - request.scheme должен быть 'https'"
echo "  - HTTP_X_FORWARDED_PROTO должен быть 'https'"
echo "  - HTTP_X_FORWARDED_HOST должен быть 'metateks-admin.vinodesign.ru'"
echo "  - request.build_absolute_uri() должен начинаться с https://"
echo ""
echo "Тестовый endpoint доступен по адресу:"
echo "  https://metateks-admin.vinodesign.ru/test-headers-debug/"
echo ""
