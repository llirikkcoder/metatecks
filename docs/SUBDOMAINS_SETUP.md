# Настройка поддоменов городов в Docker

**Ответ: ДА, текущая конфигурация Docker ПОЛНОСТЬЮ ГОТОВА для поддоменов!**

Нужны только изменения в конфигах, архитектура уже правильная.

---

## ✅ Что уже готово в Docker

Текущая архитектура **идеально подходит** для поддоменов:

```
✓ Nginx как reverse proxy      → один контейнер для всех доменов
✓ Django на 1 порту (8000)      → обрабатывает все запросы
✓ PostgreSQL (общая БД)         → одна база для всех городов
✓ Redis (сессии/кеш)            → общий кеш
✓ Celery (задачи)               → общие фоновые задачи
```

**Не нужно:**
- ❌ Создавать отдельные контейнеры для городов
- ❌ Менять docker-compose.yml
- ❌ Делать несколько баз данных
- ❌ Настраивать load balancer

---

## 🔧 Что нужно изменить (3 файла)

### 1. Nginx конфигурация

**Файл:** `docker/nginx/conf.d/default.conf`

**Было:**
```nginx
server {
    listen 80;
    server_name localhost;
    ...
}
```

**Станет:**
```nginx
server {
    listen 80;
    server_name metateks.ru *.metateks.ru admin.metateks.ru;
    charset utf-8;
    
    # Передаем оригинальный Host в Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;              # ← Важно!
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    ...
}
```

**Для SSL (production):**
```nginx
# HTTP → HTTPS редирект
server {
    listen 80;
    server_name metateks.ru *.metateks.ru;
    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name metateks.ru *.metateks.ru admin.metateks.ru;
    
    # Wildcard сертификат
    ssl_certificate /etc/letsencrypt/live/metateks.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/metateks.ru/privkey.pem;
    
    # ... остальная конфигурация
}
```

---

### 2. .env.docker

**Файл:** `.env.docker`

```bash
# ALLOWED_HOSTS - разрешить все поддомены
ALLOWED_HOSTS=metateks.ru *.metateks.ru admin.metateks.ru localhost 127.0.0.1

# CSRF - доверять всем поддоменам
CSRF_TRUSTED_ORIGINS=https://metateks.ru https://*.metateks.ru https://admin.metateks.ru http://localhost

# Session cookies - работать на всех поддоменах
SESSION_COOKIE_DOMAIN=.metateks.ru
CSRF_COOKIE_DOMAIN=.metateks.ru

# Основной сайт
DEFAULT_SCHEME=https
DEFAULT_SITENAME=metateks.ru
```

**Важно:** `.metateks.ru` (с точкой) означает "этот домен и все поддомены"

---

### 3. Django middleware (код)

**Создать:** `apps/addresses/subdomain_middleware.py`

```python
from django.utils.deprecation import MiddlewareMixin
from apps.addresses.models import City


class CitySubdomainMiddleware(MiddlewareMixin):
    """
    Определяет город по поддомену и сохраняет в request
    
    Примеры:
    msk.metateks.ru → Москва
    spb.metateks.ru → Санкт-Петербург
    metateks.ru → определение по IP
    """
    
    def process_request(self, request):
        host = request.get_host().lower()
        
        # Убираем порт если есть (localhost:8000)
        host = host.split(':')[0]
        
        # Извлекаем поддомен
        parts = host.split('.')
        
        # admin.metateks.ru → пропускаем
        if parts[0] == 'admin':
            request.city = None
            request.city_slug = None
            return
        
        # metateks.ru (без поддомена) → определение по IP
        if len(parts) <= 2:
            # Здесь логика определения города по IP
            request.city = self.detect_city_by_ip(request)
            request.city_slug = request.city.slug if request.city else None
            return
        
        # msk.metateks.ru → ищем город по slug
        city_slug = parts[0]
        
        try:
            city = City.objects.get(slug=city_slug)
            request.city = city
            request.city_slug = city_slug
        except City.DoesNotExist:
            # Неизвестный поддомен → редирект на главную или 404
            request.city = None
            request.city_slug = None
    
    def detect_city_by_ip(self, request):
        """
        Определение города по IP (уже есть в apps/addresses/geo_utils.py)
        """
        from apps.addresses.geo_utils import get_user_city
        return get_user_city(request)
```

**Добавить в settings:**
```python
MIDDLEWARE = [
    # ... другие middleware
    'apps.addresses.subdomain_middleware.CitySubdomainMiddleware',
    # ... 
]
```

---

## 📊 Как это работает

```
Пользователь → msk.metateks.ru
    ↓
DNS → IP вашего сервера
    ↓
Nginx (порт 80/443)
    ↓
Видит: server_name *.metateks.ru → OK
Передает: Host: msk.metateks.ru → Django
    ↓
Django middleware
    ↓
Извлекает: "msk" из "msk.metateks.ru"
    ↓
Находит: City.objects.get(slug='msk')
    ↓
Сохраняет: request.city = <Москва>
    ↓
View использует: request.city для фильтрации товаров
```

---

## 🗺️ Логика городов в коде

**В views используйте:**

```python
def product_list(request):
    city = request.city  # Из middleware
    
    if city:
        # Показываем товары для конкретного города
        products = Product.objects.filter(
            warehouses__city=city,
            is_available=True
        )
    else:
        # Показываем все товары или редирект
        products = Product.objects.all()
    
    return render(request, 'catalog.html', {
        'products': products,
        'city': city,
    })
```

---

## 🔐 SSL сертификат (Wildcard)

### Вариант 1: Let's Encrypt (бесплатно)

```bash
# Установите certbot
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly \
  --manual \
  --preferred-challenges=dns \
  -d metateks.ru \
  -d *.metateks.ru
```

**Потребуется:** Добавить TXT запись в DNS для подтверждения

### Вариант 2: Купить Wildcard сертификат

У любого регистратора доменов (RU-CENTER, REG.RU и т.д.)

---

## 🌐 Настройка DNS

**У регистратора домена добавьте A-записи:**

```
Type   Name    Value           TTL
A      @       ВАШ_IP_СЕРВЕРА  3600
A      *       ВАШ_IP_СЕРВЕРА  3600
A      admin   ВАШ_IP_СЕРВЕРА  3600
```

**Расшифровка:**
- `@` → `metateks.ru`
- `*` → `любой-поддомен.metateks.ru`
- `admin` → `admin.metateks.ru`

Все указывают на один IP (ваш сервер с Docker).

---

## 🧪 Локальное тестирование (без DNS)

**Отредактируйте `/etc/hosts`:**

```bash
# Linux/Mac
sudo nano /etc/hosts

# Windows
notepad C:\Windows\System32\drivers\etc\hosts
```

**Добавьте:**
```
127.0.0.1   metateks.local
127.0.0.1   msk.metateks.local
127.0.0.1   spb.metateks.local
127.0.0.1   admin.metateks.local
```

**Обновите nginx:**
```nginx
server_name metateks.local *.metateks.local;
```

**Тестируйте:**
```bash
curl http://msk.metateks.local/
curl http://spb.metateks.local/
```

---

## 📝 Пошаговый план внедрения

### Этап 1: Подготовка (локально)

1. Создайте middleware `subdomain_middleware.py`
2. Добавьте в MIDDLEWARE
3. Обновите `.env.docker`
4. Тестируйте через `/etc/hosts`

### Этап 2: Тестирование

1. Запустите: `docker-compose restart web nginx`
2. Проверьте: `curl -H "Host: msk.metateks.local" http://localhost/`
3. Убедитесь что `request.city` работает

### Этап 3: Production

1. Купите домен `metateks.ru`
2. Настройте DNS (A-записи)
3. Получите Wildcard SSL
4. Обновите nginx конфиг (добавьте SSL)
5. Обновите `.env.docker` (правильные домены)
6. Деплой: `docker-compose up -d --build`

---

## ✅ Проверка что всё работает

```bash
# Проверка nginx
docker-compose exec nginx nginx -t

# Проверка Django
docker-compose exec web python manage.py shell << 'PYEOF'
from django.test import RequestFactory
from apps.addresses.subdomain_middleware import CitySubdomainMiddleware

factory = RequestFactory()
request = factory.get('/', HTTP_HOST='msk.metateks.ru')

middleware = CitySubdomainMiddleware(lambda r: None)
middleware.process_request(request)

print(f"City: {request.city}")
print(f"Slug: {request.city_slug}")
PYEOF

# Проверка через curl
curl -H "Host: msk.metateks.ru" http://localhost/
curl -H "Host: spb.metateks.ru" http://localhost/
```

---

## 🚀 Преимущества текущей архитектуры

**Почему Docker идеален для этого:**

✅ **Один контейнер Django** обрабатывает все поддомены
✅ **Одна база данных** для всех городов
✅ **Nginx в Docker** легко масштабируется
✅ **Общие сессии** работают на всех поддоменах
✅ **Простой деплой** - один docker-compose up
✅ **Легко добавить города** - просто создать запись в БД

**Не нужно:**
- ❌ Поднимать отдельные сервера для городов
- ❌ Синхронизировать базы
- ❌ Настраивать сложный роутинг

---

## 💡 Дополнительные фишки

### Автоматическое создание поддоменов

```python
# В admin.py для модели City
from django.contrib import admin
from .models import City

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'subdomain_url']
    
    def subdomain_url(self, obj):
        from django.conf import settings
        scheme = settings.DEFAULT_SCHEME
        domain = settings.DEFAULT_SITENAME.split('.', 1)[-1]  # metateks.ru
        return f"{scheme}://{obj.slug}.{domain}"
    
    subdomain_url.short_description = 'Поддомен'
```

### Автоматический редирект на поддомен

```python
# В middleware
def process_request(self, request):
    host = request.get_host()
    
    # Если пользователь на metateks.ru без поддомена
    if host == 'metateks.ru':
        city = self.detect_city_by_ip(request)
        if city:
            # Редирект на поддомен города
            return HttpResponseRedirect(
                f"https://{city.slug}.metateks.ru{request.path}"
            )
```

---

## 📊 Итоговая схема

```
                    ┌─────────────────────┐
                    │   DNS (A-records)   │
                    │  *.metateks.ru      │
                    │  → ВАШ_IP           │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Docker: Nginx      │
                    │  Port 80/443        │
                    │  server_name:       │
                    │  *.metateks.ru      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Docker: Django     │
                    │  Port 8000          │
                    │  + Middleware       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌─────────┐      ┌─────────┐     ┌─────────┐
        │ PostgreSQL│      │  Redis  │     │ Celery  │
        │ (общая БД)│      │ (кеш)   │     │ (задачи)│
        └─────────┘      └─────────┘     └─────────┘

Один сервер, один Docker, все поддомены работают!
```

---

## 🎯 Ответ на вопрос

**Вопрос:** Сможем ли при данной конфигурации Docker настроить позже такие домены и поддомены?

**Ответ:** 
# ДА! Абсолютно. Более того - текущая конфигурация ИДЕАЛЬНА для этого.

**Что нужно:**
- ✅ Изменить 3 конфига (nginx, .env, middleware)
- ✅ Настроить DNS
- ✅ Получить SSL сертификат
- ✅ Деплой за 5 минут

**Что НЕ нужно:**
- ❌ Менять архитектуру Docker
- ❌ Добавлять контейнеры
- ❌ Менять базу данных
- ❌ Переписывать код

Текущая архитектура уже правильная для multi-tenant по поддоменам!

---

**Дополнительная документация:**
- Реализация middleware: см. выше
- Настройка nginx: см. выше  
- Тестирование локально: см. выше

Готово к внедрению когда купите домен!
