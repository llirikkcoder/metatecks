# Мониторинг интеграции с 1С

## 🔐 Как работает аутентификация

### ❌ НЕ НУЖЕН отдельный API ключ!

Интеграция использует **HTTP Basic Authentication** с обычными пользователями Django.

**Как это работает:**

1. 1С отправляет заголовок: `Authorization: Basic <base64(username:password)>`
2. Django декодирует логин и пароль
3. Проверяет пользователя через `authenticate(username, password)`
4. Проверяет право `cml.add_exchange`

**Исходный код:** `apps/third_party/cml/auth.py:25-41`

---

## ⚡ Быстрый старт мониторинга

### Интерактивный скрипт (рекомендуется)

```bash
./scripts/monitor_1c.sh
```

Меню с опциями:
- Все логи веб-сервера
- Только 1С запросы
- Логи синхронизации
- Логи Celery
- Проверка последних обменов
- Тестовый запрос

---

## 📊 Быстрые команды для мониторинга

### 1. Мониторинг запросов от 1С в реальном времени

```bash
# Все логи веб-сервера (включая 1С)
docker-compose logs -f web

# Только запросы к /1c_exchange.php
docker-compose logs -f web | grep "1c_exchange"

# Nginx access log (все HTTP запросы)
docker-compose exec nginx tail -f /var/log/nginx/metateks_access.log

# Фильтр только POST запросов (загрузка файлов от 1С)
docker-compose logs -f web | grep "POST.*1c_exchange"
```

### 2. Мониторинг обработки данных (Celery)

```bash
# Все логи Celery
docker-compose logs -f celery

# Только задачи импорта из 1С
docker-compose logs -f celery | grep "make_import"

# Синхронизация товаров
docker-compose logs -f celery | grep "sync_products"

# Импорт с деталями
docker-compose logs -f celery | grep -E "ImportedProduct|sync|CML"
```

### 3. Специализированные логи 1С

```bash
# Логи синхронизации
docker-compose exec web tail -f /app/logs/cml_sync.log

# Логи Celery задач
docker-compose exec web tail -f /app/logs/cml_tasks.log

# Логи парсинга XML
docker-compose exec web tail -f /app/logs/cml_utils.log

# Все логи 1С одновременно
docker-compose exec web tail -f /app/logs/cml_*.log
```

### 4. Проверка истории обменов (из БД)

```bash
docker-compose exec web python manage.py shell
```

```python
from apps.third_party.cml.models import Exchange, ExchangeParsing

# Последние 10 обменов
for ex in Exchange.objects.all().order_by('-created_at')[:10]:
    print(f"{ex.mode} - {ex.created_at} - {ex.status} - {ex.filename}")

# Последний успешный обмен
last = Exchange.objects.filter(status='success').order_by('-created_at').first()
print(f"Последняя синхронизация: {last.created_at if last else 'Нет'}")

# Количество обменов сегодня
from django.utils import timezone
from datetime import timedelta
today = timezone.now() - timedelta(days=1)
count = Exchange.objects.filter(created_at__gte=today).count()
print(f"Обменов за 24ч: {count}")
```

---

## 🔍 Отслеживание ПРЯМО СЕЙЧАС

### Вариант 1: Ждем запроса от 1С

Откройте терминал и запустите:

```bash
# Мониторинг в реальном времени
docker-compose logs -f web nginx | grep --line-buffered -E "1c_exchange|exchange\.php" --color=always
```

Теперь в 1С нажмите **"Выполнить обмен"** и вы увидите:

```
metateks_nginx | 192.168.1.100 - - [25/Dec/2025:10:30:15] "GET /1c_exchange.php?type=catalog&mode=checkauth HTTP/1.1" 200
metateks_web  | [25/Dec/2025 10:30:15] INFO: 1C checkauth request from user: 1c_user
metateks_nginx | 192.168.1.100 - - [25/Dec/2025:10:30:16] "GET /1c_exchange.php?type=catalog&mode=init HTTP/1.1" 200
metateks_nginx | 192.168.1.100 - - [25/Dec/2025:10:30:17] "POST /1c_exchange.php?type=catalog&mode=file&filename=import.xml HTTP/1.1" 200
```

### Вариант 2: Тестовый запрос прямо сейчас

```bash
# Без аутентификации (должен вернуть 401)
curl -i http://localhost/1c_exchange.php?type=catalog\&mode=checkauth

# Ожидаемый ответ:
# HTTP/1.1 401 Unauthorized
# WWW-Authenticate: Basic realm=""
```

```bash
# С аутентификацией (замените username:password)
curl -i -u "your_user:your_password" http://localhost/1c_exchange.php?type=catalog\&mode=checkauth

# Ожидаемый ответ:
# HTTP/1.1 200 OK
# success
# PHPSESSID
# <session_id>
```

### Вариант 3: Проверка текущего состояния

```bash
# Проверка последних обменов
docker-compose exec web python manage.py shell -c "
from apps.third_party.cml.models import Exchange
for ex in Exchange.objects.all().order_by('-created_at')[:5]:
    print(f'{ex.created_at} | {ex.mode} | {ex.status}')
"

# Проверка импортированных товаров
docker-compose exec web python manage.py shell -c "
from apps.third_party.cml.models import ImportedProduct
print(f'Всего товаров из 1С: {ImportedProduct.objects.count()}')
print(f'С изображениями: {ImportedProduct.objects.filter(image_path__isnull=False).count()}')
"

# Проверка синхронизированных товаров
docker-compose exec web python manage.py shell -c "
from apps.catalog.models import ProductModel, Product
print(f'Моделей товаров (синх. с 1С): {ProductModel.objects.filter(is_synced_with_1c=True).count()}')
print(f'Товаров (синх. с 1С): {Product.objects.filter(is_synced_with_1c=True).count()}')
"
```

---

## 🔎 Детальная диагностика

### Проверка endpoints

```bash
# Проверка доступности endpoint
curl -i http://localhost/1c_exchange.php

# Проверка альтернативного URL
curl -i http://localhost/exchange
```

### Проверка пользователей с правами для 1С

```bash
docker-compose exec web python manage.py shell
```

```python
from django.contrib.auth.models import User, Permission

# Найти право для 1С
perm = Permission.objects.get(codename='add_exchange', content_type__app_label='cml')
print(f"Право: {perm}")

# Найти пользователей с этим правом
users_with_perm = User.objects.filter(
    Q(user_permissions=perm) | Q(groups__permissions=perm)
).distinct()

print("\nПользователи с доступом к 1С:")
for user in users_with_perm:
    print(f"  - {user.username} (is_active: {user.is_active})")
```

### Проверка файлов от 1С

```bash
# Временные файлы от 1С
docker-compose exec web ls -lht /app/media/cml/tmp/ | head -20

# Постоянные изображения
docker-compose exec web ls -lht /app/media/models/photos_1c/ | head -20

# Размер директорий
docker-compose exec web du -sh /app/media/cml/tmp/
docker-compose exec web du -sh /app/media/models/photos_1c/
```

---

## 📈 Monitoring Dashboard (ручной)

Создайте простую проверку состояния:

```bash
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.third_party.cml.models import Exchange, ImportedProduct
from apps.catalog.models import ProductModel, Product
from django.utils import timezone
from datetime import timedelta

print("\n" + "=" * 60)
print("  DASHBOARD ИНТЕГРАЦИИ С 1С")
print("=" * 60)

# Последний обмен
last_exchange = Exchange.objects.order_by('-created_at').first()
if last_exchange:
    time_ago = timezone.now() - last_exchange.created_at
    hours = int(time_ago.total_seconds() / 3600)
    print(f"\n🕐 Последний обмен: {hours}ч назад ({last_exchange.created_at.strftime('%d.%m.%Y %H:%M')})")
    print(f"   Режим: {last_exchange.mode}")
    print(f"   Статус: {last_exchange.status}")
else:
    print("\n❌ Обменов еще не было")

# Статистика за 24 часа
yesterday = timezone.now() - timedelta(hours=24)
exchanges_24h = Exchange.objects.filter(created_at__gte=yesterday).count()
print(f"\n📊 Обменов за 24ч: {exchanges_24h}")

# Товары
imported_count = ImportedProduct.objects.count()
synced_count = Product.objects.filter(is_synced_with_1c=True).count()
with_images = ImportedProduct.objects.filter(image_path__isnull=False).count()

print(f"\n📦 Товары:")
print(f"   Импортировано из 1С: {imported_count}")
print(f"   Синхронизировано: {synced_count}")
print(f"   С изображениями: {with_images}")

# Celery задачи
from celery import current_app
try:
    inspect = current_app.control.inspect()
    active_tasks = inspect.active()
    if active_tasks:
        total = sum(len(tasks) for tasks in active_tasks.values())
        print(f"\n⚙️  Активных Celery задач: {total}")
    else:
        print(f"\n✅ Celery задач нет")
except Exception:
    print(f"\n❓ Celery статус недоступен")

print("\n" + "=" * 60 + "\n")
PYEOF
```

---

## 🚨 Частые проблемы и решения

### Проблема: Не видно запросов от 1С

**Проверка:**

```bash
# 1. Проверьте, что контейнеры запущены
docker-compose ps

# 2. Проверьте доступность endpoint
curl http://localhost/1c_exchange.php

# 3. Проверьте Nginx конфигурацию
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf | grep 1c_exchange
```

### Проблема: 401 Unauthorized

**Решение:**

```bash
# Проверьте пользователя
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='your_username')
print(f'Активен: {user.is_active}')
print(f'Есть право cml.add_exchange: {user.has_perm(\"cml.add_exchange\")}')
"
```

### Проблема: Файлы загружаются, но не обрабатываются

**Проверка:**

```bash
# 1. Проверьте Celery worker
docker-compose ps celery  # Должен быть Up

# 2. Проверьте логи Celery
docker-compose logs celery | tail -50

# 3. Проверьте очередь задач
docker-compose exec celery celery -A main inspect active
```

---

## 📋 Чек-лист для диагностики

- [ ] Контейнеры запущены (`docker-compose ps`)
- [ ] Endpoint доступен (`curl http://localhost/1c_exchange.php`)
- [ ] Пользователь создан и имеет права
- [ ] Celery worker работает
- [ ] Redis доступен
- [ ] Директории для файлов созданы (`media/cml/tmp/`, `media/models/photos_1c/`)
- [ ] Логи пишутся (`logs/cml_*.log`)

---

## 🎯 Рекомендуемый workflow мониторинга

### При первой настройке:

```bash
# Терминал 1: Веб-логи
docker-compose logs -f web

# Терминал 2: Celery логи
docker-compose logs -f celery

# Терминал 3: Специализированные логи
docker-compose exec web tail -f /app/logs/cml_*.log
```

### В продакшене:

```bash
# Используйте интерактивный скрипт
./scripts/monitor_1c.sh

# Или настройте мониторинг (например, через Grafana + Loki)
```

---

## 💡 Полезные алиасы

Добавьте в `~/.bashrc`:

```bash
alias 1c-logs='docker-compose logs -f web | grep 1c_exchange'
alias 1c-celery='docker-compose logs -f celery | grep -E "make_import|sync"'
alias 1c-check='docker-compose exec web python manage.py shell -c "from apps.third_party.cml.models import Exchange; print(Exchange.objects.order_by(\"-created_at\").first())"'
alias 1c-monitor='cd /mnt/c/_KIPOL/_WORK/_metatecks && ./scripts/monitor_1c.sh'
```

Затем:

```bash
source ~/.bashrc

# Использование
1c-logs
1c-celery
1c-check
1c-monitor
```

---

## 🔗 Связанные документы

- [Полная документация по интеграции с 1С](1C_INTEGRATION.md)
- [README.md](../README.md)
- [Миграция БД](../DATABASE_MIGRATION.md)
