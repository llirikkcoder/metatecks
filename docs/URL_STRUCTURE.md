# Структура URL и доменов проекта Метатэкс

Документация по реализованным и требуемым URL-адресам и доменам.

---

## 📋 Текущие домены

### Production домены (из .env.docker)

```
✓ metateks-admin.vinodesign.ru              # Основной сайт
✓ metateks-admin.vinodesign.ru   # Админка (альтернативный домен)
✓ localhost                      # Локальная разработка
✓ 127.0.0.1                      # Локальная разработка
```

### Рекомендуемая структура доменов

```
🔹 www.metateks.ru              # Основной домен (требует настройки)
🔹 admin.metateks.ru            # Админка (требует настройки)
🔹 api.metateks.ru              # API endpoints (опционально)
```

---

## 🌐 Реализованные URL (Frontend)

### Главная страница
```
/                               ✓ Главная страница интернет-магазина
```

### Каталог товаров
```
/catalog/                       ✓ Главная каталога
/catalog/p/<id>/                ✓ Прямая ссылка на товар по ID
/catalog/<category>/            ✓ Страница категории
/catalog/<category>/<subcategory>/           ✓ Подкатегория
/catalog/<category>/<subcategory>/filter/    ✓ Подкатегория с фильтром
/catalog/<category>/<subcategory>/model<id>/ ✓ Фильтр по модели техники
/catalog/<category>/<subcategory>/<brand>/   ✓ Фильтр по бренду
/catalog/<category>/<subcategory>/<product>-<id>/ ✓ Страница товара
```

**Примеры:**
- `/catalog/zapchasti/` - категория "Запчасти"
- `/catalog/zapchasti/filtry/` - подкатегория "Фильтры"
- `/catalog/zapchasti/filtry/model123/` - фильтры для модели 123
- `/catalog/zapchasti/filtry/maslyanyj-filtr-12345/` - конкретный товар

### Бренды
```
/brands/                        ✓ Список всех брендов
/brands/<brand>/                ✓ Страница бренда
```

**Примеры:**
- `/brands/xcmg/` - бренд XCMG
- `/brands/sdlg/` - бренд SDLG

### О компании
```
/about/                         ✓ О компании (главная)
/about/video/                   ✓ Видео
/about/video/<tag>/             ✓ Видео по тегу
/about/photo/                   ✓ Фото
/about/photo/<tag>/             ✓ Фото по тегу
/about/files/                   ✓ Файлы для скачивания
/about/files/<tag>/             ✓ Файлы по тегу
```

### Новости
```
/news/                          ✓ Все новости
/news/<year>/                   ✓ Новости за год
/news/<category>/               ✓ Новости категории
/news/<year>/<category>/        ✓ Новости категории за год
/news/<date>/<slug>/            ✓ Конкретная новость
```

**Примеры:**
- `/news/2024/` - новости 2024
- `/news/company/` - новости компании
- `/news/2024-12-25/novyj-sklad/` - конкретная новость

### Статьи
```
/articles/                      ✓ Список статей
/articles/<slug>/               ✓ Конкретная статья
```

### Личный кабинет
```
/account/                       ✓ Главная ЛК
/account/orders/                ✓ История заказов
/account/addresses/             ✓ Адреса доставки
/account/favorites/             ✓ Избранное
/account/profile/               ✓ Профиль пользователя
/account/logout/                ✓ Выход (редирект на API)
```

### Корзина и заказы
```
/cart/                          ✓ Корзина
/promotions/                    ✓ Акции и спецпредложения
```

### Поиск
```
/search/                        ✓ Поиск по сайту
  ?q=<запрос>                   ✓ Параметр поискового запроса
```

### Динамические страницы (CMS)
```
/<slug>/                        ✓ Любая страница из CMS
```

**Примеры:**
- `/dostavka/` - страница доставки
- `/garantiya/` - страница гарантии
- `/kontakty/` - контакты

---

## 🔌 API Endpoints

### Префикс: `/api/`

#### Аутентификация (`/api/auth/`)
```
POST   /api/auth/login/         ✓ Вход пользователя
POST   /api/auth/logout/        ✓ Выход пользователя
POST   /api/auth/register/      ✓ Регистрация
POST   /api/auth/password-reset/ ✓ Восстановление пароля (требует проверки)
```

#### Корзина (`/api/cart/`)
```
GET    /api/cart/               ✓ Получить корзину
POST   /api/cart/add/           ✓ Добавить товар
POST   /api/cart/update/        ✓ Обновить количество
POST   /api/cart/remove/        ✓ Удалить товар
POST   /api/cart/clear/         ✓ Очистить корзину
```

#### Заказы (`/api/order/`)
```
POST   /api/order/create/       ✓ Создать заказ
GET    /api/order/<id>/         ✓ Получить заказ
POST   /api/order/<id>/cancel/  ✓ Отменить заказ (требует проверки)
```

#### Личный кабинет (`/api/account/`)
```
GET    /api/account/profile/    ✓ Получить профиль
POST   /api/account/profile/    ✓ Обновить профиль
POST   /api/account/password/   ✓ Сменить пароль
```

#### Избранное (`/api/favorites/`)
```
GET    /api/favorites/          ✓ Список избранного
POST   /api/favorites/add/      ✓ Добавить в избранное
POST   /api/favorites/remove/   ✓ Удалить из избранного
```

#### Адреса (`/api/addresses/`)
```
GET    /api/addresses/cities/   ✓ Список городов
GET    /api/addresses/warehouses/ ✓ Список складов
POST   /api/addresses/detect/   ✓ Определить город по IP (требует проверки)
```

---

## 🔧 Административные URL

### Django Admin
```
/admin/                         ✓ Админ-панель Django
/admin/login/                   ✓ Вход в админку
/admin/<app>/<model>/           ✓ Управление моделями
```

### Интеграция с 1С (CommerceML)
```
/cml/                           ✓ Главная страница интеграции
/cml/1c_exchange.php            ✓ Обмен с 1С (mode=checkauth,init,file,import)
  ?type=catalog                 ✓ Тип обмена: catalog или sale
  ?mode=checkauth               ✓ Проверка авторизации
  ?mode=init                    ✓ Инициализация
  ?mode=file                    ✓ Загрузка файла
  ?mode=import                  ✓ Импорт данных
```

**Важно:** Для работы 1С требуется Basic Auth с учетными данными пользователя с правами.

### Служебные URL
```
/images-handler/                ✓ Django-galleryfield (обработка изображений)
/tinymce/                       ✓ TinyMCE WYSIWYG редактор
/health/                        ❌ НЕ РЕАЛИЗОВАНО (требуется для healthcheck)
```

---

## ⚠️ Требуют реализации

### 1. Health Check Endpoint
```
GET /health/                    ❌ Endpoint для проверки здоровья приложения
```

**Необходимо для:**
- Docker healthcheck
- Мониторинга (Prometheus, etc.)
- Load balancer health checks

**Реализация:**
```python
# В main/urls.py добавить:
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

# В urlpatterns:
path('health/', health_check, name='health'),
```

### 2. Sitemap.xml
```
GET /sitemap.xml                ❌ Карта сайта для поисковиков
```

### 3. Robots.txt
```
GET /robots.txt                 ❌ Правила для поисковых роботов
```

### 4. Favicon
```
GET /favicon.ico                ⚠️  Проверить наличие
```

### 5. API документация
```
GET /api/docs/                  ❌ Swagger/OpenAPI документация
GET /api/schema/                ❌ OpenAPI схема
```

### 6. Подписка на рассылку
```
POST /api/newsletter/subscribe/ ❌ Подписка на новости
POST /api/newsletter/unsubscribe/ ❌ Отписка
```

### 7. Обратная связь
```
POST /api/feedback/             ⚠️  Проверить наличие
POST /api/callback/             ⚠️  Заказать звонок
```

### 8. Сравнение товаров
```
GET  /compare/                  ❌ Страница сравнения
POST /api/compare/add/          ❌ Добавить к сравнению
POST /api/compare/remove/       ❌ Удалить из сравнения
```

### 9. Отзывы
```
GET  /api/reviews/<product_id>/ ❌ Отзывы о товаре
POST /api/reviews/create/       ❌ Создать отзыв
```

### 10. Быстрый заказ
```
POST /api/quick-order/          ❌ Быстрый заказ в 1 клик
```

---

## 🔐 Безопасность URL

### HTTPS редиректы
В production все HTTP запросы должны редиректиться на HTTPS.

**Nginx конфиг:**
```nginx
server {
    listen 80;
    server_name metateks.ru www.metateks.ru;
    return 301 https://www.metateks.ru$request_uri;
}
```

### CSRF Protection
Все POST/PUT/DELETE запросы к API требуют CSRF токен.

**Настройки:**
```python
CSRF_TRUSTED_ORIGINS = [
    'https://metateks.ru',
    'https://www.metateks.ru',
    'https://admin.metateks.ru',
]
```

### Rate Limiting
❌ **НЕ РЕАЛИЗОВАНО** - требуется ограничение частоты запросов к API.

Рекомендуется: django-ratelimit или nginx limit_req.

---

## 📊 SEO оптимизация URL

### ЧПУ (Clean URLs) ✓
Все URL используют человеко-читаемые slug'и:
- ✓ `/catalog/zapchasti/filtry/` вместо `/catalog/1/2/`
- ✓ `/brands/xcmg/` вместо `/brands?id=5`

### Структура URL для SEO
```
✓ Короткие и понятные
✓ Используют дефисы вместо подчеркиваний
✓ Нет лишних параметров
✓ Иерархическая структура
```

### Канонические URL
❌ **Требуется:** Добавить canonical links в шаблонах для избежания дублей.

---

## 🚀 Настройка доменов

### Текущая конфигурация (.env.docker)
```bash
ALLOWED_HOSTS=localhost 127.0.0.1 metateks-admin.vinodesign.ru metateks-admin.vinodesign.ru
CSRF_TRUSTED_ORIGINS=http://localhost http://127.0.0.1 https://metateks-admin.vinodesign.ru https://metateks-admin.vinodesign.ru
```

### Рекомендуемая production конфигурация
```bash
# Основной домен
ALLOWED_HOSTS=metateks.ru www.metateks.ru admin.metateks.ru

# CSRF защита
CSRF_TRUSTED_ORIGINS=https://metateks.ru https://www.metateks.ru https://admin.metateks.ru

# Основной сайт
DEFAULT_SCHEME=https
DEFAULT_SITENAME=www.metateks.ru

# Cookies для всех поддоменов
SESSION_COOKIE_DOMAIN=.metateks.ru
```

### Nginx конфигурация для поддоменов

**www.metateks.ru (основной сайт):**
```nginx
server {
    listen 443 ssl http2;
    server_name www.metateks.ru metateks.ru;
    
    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/metateks.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/metateks.ru/privkey.pem;
    
    # Proxy к Django
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**admin.metateks.ru (админка):**
```nginx
server {
    listen 443 ssl http2;
    server_name admin.metateks.ru;
    
    # Ограничить доступ по IP (опционально)
    # allow 192.168.1.0/24;
    # deny all;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 📝 Проверочный список

### Текущие URL
- [x] Главная страница
- [x] Каталог с фильтрами
- [x] Страницы товаров
- [x] Личный кабинет
- [x] Корзина
- [x] API endpoints
- [x] Админ-панель
- [x] Интеграция с 1С

### Требуют внимания
- [ ] /health/ endpoint
- [ ] /sitemap.xml
- [ ] /robots.txt
- [ ] API документация
- [ ] Rate limiting
- [ ] Обратная связь
- [ ] Сравнение товаров
- [ ] Отзывы о товарах

### Безопасность
- [x] CSRF защита
- [x] HTTPS ready (nginx config)
- [ ] Rate limiting
- [ ] IP whitelisting для админки (опционально)
- [ ] Двухфакторная аутентификация (опционально)

---

## 🔍 Тестирование URL

### Проверка основных страниц
```bash
# Главная
curl http://localhost/

# Каталог
curl http://localhost/catalog/

# API
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.ru", "password": "password"}'

# Админка
curl http://localhost/admin/login/

# 1С интеграция
curl -u "1c_user:password" \
  "http://localhost/cml/1c_exchange.php?type=catalog&mode=checkauth"
```

### Проверка редиректов
```bash
# Должен редиректить на HTTPS (в production)
curl -I http://metateks.ru/
```

---

## 📚 Дополнительные ресурсы

- Django URL dispatcher: https://docs.djangoproject.com/en/4.2/topics/http/urls/
- SEO best practices: https://developers.google.com/search/docs/crawling-indexing/url-structure
- Django REST API: https://www.django-rest-framework.org/

---

**Последнее обновление:** 2025-12-25  
**Версия:** 1.0

---

## 🎨 Статические файлы и Media

### Статические файлы (assets)
```
/css/                           ✓ CSS файлы
/js/                            ✓ JavaScript
/fonts/                         ✓ Шрифты
/images/                        ✓ Статические изображения
```

**Расположение на диске:**
- Исходники: `./assets/`
- Собранные: `./static/` (после collectstatic)

### Media файлы (загрузки)
```
/media/                         ✓ Загруженные файлы
/media/banners/                 ✓ Баннеры CMS
/media/news/                    ✓ Новости
/media/models/photos_1c/        ✓ Фото товаров из 1С
/media/cml/                     ✓ Временные файлы 1С
```

**Расположение на диске:** `./media/`

### Nginx отдача статики

**Текущая конфигурация (`docker/nginx/conf.d/default.conf`):**
```nginx
location /static/ {
    alias /app/static/;
    expires 30d;
}

location /media/ {
    alias /app/media/;
    expires 7d;
}

location ~* ^/(css|js|fonts|images)/ {
    alias /app/assets/;
    expires 30d;
}
```

---

## 🔗 Внешние интеграции

### 1С:Предприятие (CommerceML)
```
URL: http://localhost/cml/1c_exchange.php
Auth: Basic Authentication
User: (создается в админке с правами add_exchange)
```

**Режимы работы:**
- `?mode=checkauth` - проверка авторизации
- `?mode=init` - инициализация обмена
- `?mode=file` - загрузка файла
- `?mode=import` - импорт данных

**Типы обмена:**
- `?type=catalog` - обмен каталогом товаров
- `?type=sale` - обмен заказами

### Webhooks
```
POST /api/webhooks/payment/webhook/   ✅ Колбэк Альфа-Банка (если настроен в личном кабинете мерчанта)
GET  /api/webhooks/payment/return/    ✅ returnUrl — пользователь вернулся после оплаты
GET  /api/webhooks/payment/fail/      ✅ failUrl — оплата отклонена/отменена пользователем
POST /api/webhooks/delivery/          ❌ Уведомления от служб доставки
```

---

## 📱 Мобильная версия / PWA

### Текущее состояние
- ✓ Адаптивная верстка (responsive)
- ❌ PWA манифест
- ❌ Service Workers
- ❌ Offline режим

### Требуется для PWA
```
GET /manifest.json              ❌ Web App Manifest
GET /service-worker.js          ❌ Service Worker
```

---

## 🌍 Мультиязычность

### Текущее состояние
- Язык: Русский (ru-RU)
- Мультиязычность: ❌ не реализована

### Для реализации
```
/en/                            ❌ Английская версия
/ru/                            ❌ Русская версия (явный префикс)
```

Django i18n URL patterns - требует настройки.


---

## 🏙️ Поддомены городов (Планируется)

### Текущее состояние
- Архитектура: ✅ ГОТОВА для поддоменов
- Docker конфигурация: ✅ ГОТОВА
- Требуется: Только обновить конфиги

### Планируемая структура

```
metateks.ru                    → Определение города по IP → редирект
msk.metateks.ru               → Москва
spb.metateks.ru               → Санкт-Петербург  
ekb.metateks.ru               → Екатеринбург
nsk.metateks.ru               → Новосибирск
admin.metateks.ru             → Админка (отдельный поддомен)
```

### Как это работает

**Пример URL товара:**
```
https://msk.metateks.ru/catalog/zapchasti/filtry/maslyanyj-filtr-12345/
```

**Логика:**
1. Nginx получает запрос на `msk.metateks.ru`
2. Передает Host header в Django
3. Django middleware извлекает `msk` из домена
4. Находит город: `City.objects.get(slug='msk')`
5. Сохраняет в `request.city`
6. View фильтрует товары по складам Москвы

### Преимущества поддоменов

✅ **SEO:** Каждый город - отдельный сайт в глазах поисковиков
✅ **UX:** Пользователь видит свой город в URL
✅ **Логика:** Разные остатки, цены, условия доставки
✅ **Масштабируемость:** Легко добавить новый город
✅ **Один Docker:** Всё работает в одном контейнере

### Технические детали

**Nginx:**
```nginx
server {
    listen 443 ssl http2;
    server_name metateks.ru *.metateks.ru admin.metateks.ru;
    
    ssl_certificate /etc/letsencrypt/live/metateks.ru/fullchain.pem;  # Wildcard
    
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;  # Передаем поддомен в Django
    }
}
```

**Django settings:**
```python
ALLOWED_HOSTS = ['metateks.ru', '*.metateks.ru', 'admin.metateks.ru']
SESSION_COOKIE_DOMAIN = '.metateks.ru'  # Общие сессии для всех поддоменов
CSRF_COOKIE_DOMAIN = '.metateks.ru'
```

**Middleware:**
```python
class CitySubdomainMiddleware:
    def process_request(self, request):
        host = request.get_host()
        if 'msk.metateks.ru':
            request.city = City.objects.get(slug='msk')
```

### DNS настройки

У регистратора домена:
```
Type   Name    Value           TTL
A      @       ВАШ_IP_СЕРВЕРА  3600    # metateks.ru
A      *       ВАШ_IP_СЕРВЕРА  3600    # *.metateks.ru (все поддомены)
A      admin   ВАШ_IP_СЕРВЕРА  3600    # admin.metateks.ru
```

### SSL сертификат

**Wildcard сертификат** (покрывает все поддомены):
```bash
certbot certonly --manual --preferred-challenges=dns \
  -d metateks.ru -d *.metateks.ru
```

### Что НЕ нужно менять

❌ Docker архитектуру - уже правильная
❌ База данных - одна для всех городов
❌ Код views - работает без изменений
❌ API - продолжает работать
❌ Админка - доступна на admin.metateks.ru

### Локальное тестирование

**Без DNS (через /etc/hosts):**
```bash
# /etc/hosts
127.0.0.1  metateks.local msk.metateks.local spb.metateks.local

# Тест
curl http://msk.metateks.local/catalog/
```

### План внедрения

1. ✅ Купить домен `metateks.ru`
2. ✅ Настроить DNS (A-записи для wildcard)
3. ✅ Получить Wildcard SSL сертификат
4. ✅ Обновить nginx конфиг (3 строки)
5. ✅ Обновить .env.docker (4 переменные)
6. ✅ Добавить middleware (1 файл Python)
7. ✅ Деплой: `docker-compose restart web nginx`

**Время внедрения:** 1-2 часа

### Документация

- **[SUBDOMAINS_SETUP.md](SUBDOMAINS_SETUP.md)** - Полная инструкция по настройке
- **[SUBDOMAINS_CHECKLIST.md](SUBDOMAINS_CHECKLIST.md)** - Чеклист для быстрого внедрения

---

## 🎯 Итого по доменам

### Текущие (разработка)
```
localhost:80                   # Через nginx
localhost:8000                 # Прямой доступ к Django
```

### Production (рекомендуемые)
```
metateks.ru                    # Основной → редирект по гео
msk.metateks.ru               # Москва
spb.metateks.ru               # Санкт-Петербург
[city].metateks.ru            # Другие города
admin.metateks.ru             # Админка
```

### SSL
```
*.metateks.ru                  # Wildcard сертификат (покрывает всё)
```

### Docker
```
✅ Один nginx контейнер       # Обрабатывает все домены
✅ Один Django контейнер      # Один код, одна БД
✅ Один PostgreSQL            # Общая база
✅ Один Redis                 # Общий кеш/сессии
```

**Текущая архитектура Docker ИДЕАЛЬНО подходит для multi-tenant по поддоменам!**
