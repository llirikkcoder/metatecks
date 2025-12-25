# Быстрая настройка Health Endpoint

Health endpoint критичен для работы Docker healthcheck.

## ⚡ Быстрая реализация (5 минут)

### Шаг 1: Создайте view

Создайте файл `apps/utils/health.py`:

```python
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
from django.conf import settings


def health_check(request):
    """
    Проверка здоровья приложения
    """
    health = {
        "status": "ok",
        "checks": {}
    }
    
    # Проверка БД
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["status"] = "error"
        health["checks"]["database"] = f"error: {str(e)}"
    
    # Проверка Redis (опционально)
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health["checks"]["redis"] = "ok"
    except Exception as e:
        health["checks"]["redis"] = f"warning: {str(e)}"
    
    status_code = 200 if health["status"] == "ok" else 503
    return JsonResponse(health, status=status_code)


def simple_health(request):
    """
    Простая проверка (только HTTP 200)
    Используется для healthcheck в Docker
    """
    return JsonResponse({"status": "ok"}, status=200)
```

### Шаг 2: Добавьте в URLs

В `main/urls.py`:

```python
from apps.utils.health import simple_health, health_check

urlpatterns = [
    # ... остальные URL ...
    
    # Health checks
    path('health/', simple_health, name='health'),
    path('health/full/', health_check, name='health-full'),
]
```

### Шаг 3: Проверьте

```bash
# Простая проверка
curl http://localhost/health/

# Полная проверка
curl http://localhost/health/full/
```

Ожидаемый ответ:
```json
{"status": "ok"}
```

---

## 🔧 Альтернативный вариант (без зависимостей)

Если не нужна проверка БД/Redis, используйте минимальную версию:

```python
# В main/urls.py
from django.http import JsonResponse

urlpatterns = [
    # ...
    path('health/', lambda request: JsonResponse({"status": "ok"}), name='health'),
]
```

---

## ✅ После реализации

1. **Обновите docker-compose.yml** (уже обновлен):
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
   ```

2. **Перезапустите контейнеры:**
   ```bash
   docker-compose restart web
   ```

3. **Проверьте healthcheck:**
   ```bash
   docker-compose ps
   # Должен показать "healthy" для сервиса web
   ```

---

## 🎯 Готово!

Теперь ваше приложение имеет health endpoint, который:
- Отвечает быстро (без тяжелых проверок)
- Работает для Docker healthcheck
- Можно расширить для мониторинга
