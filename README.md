# Инструкция по проекту metateks-dev

## 📋 Описание проекта

**Метатэкс** - это полнофункциональная платформа электронной коммерции, построенная на Django 4.2.13. Проект представляет собой интернет-магазин с интеграцией 1C, системой управления заказами, каталогом товаров, корзиной покупок и CMS.

## 🛠 Технологический стек

### Backend
- **Django 4.2.13** - основной веб-фреймворк
- **Python** - язык программирования
- **SQLite3** - база данных для разработки
- **PostgreSQL** - поддержка для продакшена
- **Celery 5.4.0** - асинхронная обработка задач
- **Redis** - брокер сообщений для Celery

### Frontend
- **jQuery 3.x**
- **LESS CSS** - препроцессор (компиляция на стороне клиента)
- **Swiper, Fancybox** - UI компоненты
- **PlayerJS** - видеоплеер

### Интеграции
- **1C (CommerceML)** - синхронизация каталога и заказов (HTTP Basic Auth)
- **IPInfo.io** - автоматическое определение города по IP

## 📁 Структура проекта

```
metateks-dev/
├── apps/              # Django приложения (15+ модулей)
│   ├── catalog/       # Каталог товаров, категории, бренды
│   ├── orders/        # Обработка заказов
│   ├── cart/          # Корзина покупок
│   ├── users/         # Пользователи и профили
│   ├── api/           # REST API
│   ├── content/       # CMS (страницы, новости)
│   ├── banners/       # Система баннеров
│   └── ...
├── assets/            # Статические файлы (CSS, JS, шрифты, изображения)
├── templates/         # HTML шаблоны (80+ файлов)
├── conf/              # Конфигурация сервера (nginx, uwsgi, supervisor)
├── docker/            # Docker конфигурация (nginx, entrypoint)
├── docs/              # Документация проекта
├── fixtures/          # Начальные данные для БД
├── main/              # Настройки Django проекта
├── media/             # Медиа-файлы CMS и 1С (на диске, в git ignore)
│   ├── banners/       # Изображения баннеров
│   ├── news/          # Фото новостей
│   ├── models/        # Фото товаров из 1С
│   └── ...
├── logs/              # Логи приложения (на диске, в git ignore)
├── scripts/           # Скрипты миграции и мониторинга
└── manage.py          # Django management скрипт
```

### 💾 Хранение данных

**База данных:**
- Docker Volume `metatecks_postgres_data` (персистентно)
- Автоматически сохраняется при остановке контейнеров

**Медиа-файлы и логи:**
- `./media/` - прямо в папке проекта (удобно для бэкапа и миграции)
- `./logs/` - прямо в папке проекта
- Видны на диске, доступны для редактирования
- Автоматически исключены из git

**Статические файлы:**
- Docker Volume `metatecks_static_volume`
- Собираются автоматически при запуске

## 🚀 Запуск проекта

### Вариант 1: Запуск через Docker (рекомендуется)

Docker обеспечивает изолированную среду со всеми необходимыми зависимостями.

#### Требования
- Docker версии 20.10+
- Docker Compose версии 2.0+

#### Быстрый старт

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd metateks-dev
   ```

2. **Скопируйте файл переменных окружения:**
   ```bash
   cp .env.docker .env
   ```

3. **Отредактируйте `.env` (опционально):**
   - Измените `SECRET_KEY` на случайную строку
   - Укажите свои домены в `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS`
   - Настройте пароли для PostgreSQL

4. **Запустите контейнеры:**
   ```bash
   docker-compose up -d
   ```

   Это запустит:
   - PostgreSQL (база данных)
   - Redis (брокер сообщений)
   - Django (веб-приложение)
   - Celery (обработчик задач)
   - Nginx (reverse proxy)

5. **Проверьте статус контейнеров:**
   ```bash
   docker-compose ps
   ```

6. **Создайте суперпользователя:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

7. **Откройте приложение:**
   - Сайт: http://localhost
   - Админ-панель: http://localhost/admin/

#### Полезные команды Docker

```bash
# Просмотр логов
docker-compose logs -f web
docker-compose logs -f celery

# Остановка контейнеров
docker-compose down

# Остановка с удалением данных
docker-compose down -v

# Перезапуск контейнеров
docker-compose restart

# Выполнение команд Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic

# Вход в контейнер
docker-compose exec web bash

# Пересборка образов
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

#### Структура Docker

```
metateks-dev/
├── Dockerfile                    # Образ Django приложения
├── docker-compose.yml            # Оркестрация сервисов
├── docker-entrypoint.sh          # Скрипт инициализации
├── .env.docker                   # Переменные окружения (шаблон)
├── .dockerignore                 # Исключаемые файлы
└── docker/
    └── nginx/
        ├── nginx.conf            # Основная конфигурация Nginx
        └── conf.d/
            └── default.conf      # Конфигурация сайта
```

---

### Вариант 2: Локальный запуск (без Docker)

#### 1. Подготовка окружения

**Создайте файл `.env`:**
```bash
cp .env.example .env
```

Минимальная конфигурация `.env`:
```
DJANGO_ENV=local
```

#### 2. Установка зависимостей

**Вариант A - через conda (рекомендуется):**
```bash
conda install --file requirements-conda.txt
pip install -r requirements-pip.txt
```

**Вариант B - только pip:**
```bash
pip install -r requirements-conda.txt
pip install -r requirements-pip.txt
```

#### 3. Инициализация базы данных

```bash
# Применить миграции
python manage.py migrate

# Загрузить начальные данные (fixtures) в правильном порядке:
python manage.py loaddata fixtures/20240722_addresses.json
python manage.py loaddata fixtures/20240722_settings.json
python manage.py loaddata fixtures/20240722_content.json
python manage.py loaddata fixtures/20240901_categories_and_models.json
python manage.py loaddata fixtures/20240902_brands.json
python manage.py loaddata fixtures/20241105_attributes.json
python manage.py loaddata fixtures/20241201_banners.json
python manage.py loaddata fixtures/20241201_homepage.json
python manage.py loaddata fixtures/20250607_delivery_companies.json
python manage.py loaddata fixtures/20250820_cities.json

# Опционально - тестовые товары:
# python manage.py loaddata fixtures/20240722_catalog_samples.json

# Создать суперпользователя
python manage.py createsuperuser
```

#### 4. Запуск Redis

Redis необходим для работы Celery:

```bash
# Вариант A - локальная установка
redis-server

# Вариант B - через Docker
docker run -d -p 6379:6379 redis:latest
```

#### 5. Запуск Celery worker

В отдельном терминале:
```bash
celery -A main worker --loglevel=info
```

#### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

**Доступ к приложению:**
- Сайт: http://localhost:8000
- Админ-панель: http://localhost:8000/admin/

---

## 📦 Основные компоненты системы

### 1. **Каталог товаров** (`apps/catalog/`)
- Иерархические категории и подкатегории
- Бренды с логотипами
- Модели товаров с атрибутами, ценами, галереями
- Складской учет
- 3D-галереи и техническая документация
- Интеграция с 1C (синхронизация по UUID)

### 2. **Управление заказами** (`apps/orders/`)
- Обработка заказов с множественными статусами
- Поддержка разных способов доставки
- Выбор транспортных компаний
- Способы оплаты (наличные, карта, счет)
- Расчет скидок
- Экспорт в 1C

### 3. **Пользователи** (`apps/users/`)
- Аутентификация по email
- Профили с аватарами и контактной информацией
- Избранное
- Адресная книга
- Настройки доставки по умолчанию

### 4. **Корзина** (`apps/cart/`)
- Сессионная корзина для анонимных пользователей
- БД-корзина для авторизованных
- AJAX API для обновлений
- Управление количеством товаров

### 5. **CMS** (`apps/content/`)
- Настраиваемая главная страница
- Страницы с ЧПУ (slug-based URLs)
- Новости и статьи
- Информация о компании
- Интеграция YouTube видео

### 6. **API** (`apps/api/`)
- RESTful эндпоинты
- Регистрация/авторизация
- Операции с корзиной
- Оформление заказов
- Управление профилем
- Избранное

### 7. **Поиск** (`apps/search/`)
- Полнотекстовый поиск (django-watson)
- Поиск по товарам, категориям, страницам
- Поддержка русского языка

### 8. **Интеграция 1C** (`apps/third_party/cml/`)
- Протокол CommerceML 2.0
- Асинхронный импорт/экспорт через Celery
- Синхронизация каталога, цен, остатков
- Логирование операций
- **Аутентификация через Django пользователей** (HTTP Basic Auth, не требует API ключей)
- URL для 1C: `http://localhost/cml/1c_exchange.php`
- Автоматическая загрузка изображений товаров в `media/models/photos_1c/`

**Документация:**
- **[1C_INTEGRATION.md](docs/1C_INTEGRATION.md)** - Полная инструкция по настройке
- **[1C_MONITORING.md](docs/1C_MONITORING.md)** - Мониторинг и отладка
- **Скрипт мониторинга:** `./scripts/monitor_1c.sh`

## 🔧 Полезные команды

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Сбор статических файлов (для продакшена)
python manage.py collectstatic

# Расширенная Django shell
python manage.py shell_plus

# Построение поискового индекса
python manage.py buildwatson

# Синхронизация с 1C
python manage.py cmlpipelines
```

## 📝 Логирование

Логи сохраняются в директории `/logs/`:
- `debug.log` - отладочные сообщения
- `errors.log` - ошибки
- `cml_sync.log`, `cml_tasks.log`, `cml_utils.log` - логи интеграции 1C

## 🌐 Продакшн развертывание

Проект включает готовые конфигурации в `/conf/`:
- **nginx.conf** - конфигурация Nginx с HTTPS
- **uwsgi.ini** - настройки uWSGI (5 worker процессов)
- **supervisor.conf** - мониторинг процессов

Продакшн окружение:
- Домен: `metateks.vlch.dev`
- SSL сертификаты: Let's Encrypt
- Виртуальное окружение: `/home/mt/.virtualenvs/metateks/`

## 🎯 Ключевые возможности

✅ Мультискладская система
✅ Поддержка нескольких городов
✅ Автоматическая синхронизация с 1C
✅ Email уведомления о заказах
✅ Адаптивные изображения (30+ предустановленных размеров)
✅ SEO-оптимизация (мета-теги, ЧПУ)
✅ Русская локализация (часовой пояс: Europe/Moscow)
✅ Кастомизированная админ-панель (Django Suit)

## 🔐 Переменные окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```env
# Обязательные
DJANGO_ENV=local                    # local/production

# Опциональные
SECRET_KEY=your-secret-key          # Секретный ключ Django (авто-генерируется)
REDIS_URL=redis://localhost:6379/1  # URL Redis сервера (по умолчанию localhost)
ALLOWED_HOSTS=localhost,127.0.0.1   # Разрешенные хосты (по умолчанию *)
IPINFO_ACCESS_TOKEN=your-token      # Токен для IPInfo.io (опционально, работает без токена)

# Email (опционально, по умолчанию console backend)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL=Метатэкс <noreply@metateks.ru>

# Для продакшена
DATABASE_URL=postgres://...         # PostgreSQL connection string
DEFAULT_SCHEME=https                # http/https
DEFAULT_SITENAME=metateks.ru        # Имя сайта
```

## 🔌 Настройка интеграций

### 1C (CommerceML)

**📄 Полная документация: [docs/1C_INTEGRATION.md](docs/1C_INTEGRATION.md)**

**Что синхронизируется из 1С:**
- ✅ Категории товаров (иерархическая структура)
- ✅ Характеристики и свойства товаров
- ✅ Бренды (автоматическое извлечение)
- ✅ Товары с описаниями и ценами
- ✅ **Изображения товаров** 📸 (автоматическая загрузка и копирование)
- ✅ Склады
- ✅ Остатки на складах

**Что отправляется в 1С:**
- ✅ Заказы с полной информацией о клиенте

**Быстрая настройка:**

1. Создайте пользователя Django для 1C:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

2. Дайте пользователю права `cml.add_exchange` через админ-панель

3. URL для настройки в 1C:
   ```
   http://localhost:8000/1c_exchange.php
   или
   http://localhost:8000/exchange
   ```

4. В 1C укажите:
   - URL: `http://your-domain.com/1c_exchange.php`
   - Логин: имя пользователя Django
   - Пароль: пароль пользователя Django

**Как работает:**
- 1C отправляет XML файлы и изображения через HTTP Basic Auth
- Изображения загружаются в `media/cml/tmp/`, затем копируются в `media/models/photos_1c/`
- Django создает асинхронные задачи Celery для импорта
- Заказы экспортируются в 1C по запросу
- Все операции логируются в модели `Exchange` и `ExchangeParsing`

**Проверка синхронизации:**
```bash
# Проверка импортированных товаров
docker-compose exec web python manage.py shell
>>> from apps.third_party.cml.models import ImportedProduct
>>> ImportedProduct.objects.count()
>>> ImportedProduct.objects.filter(image_path__isnull=False).count()

# Проверка изображений
docker-compose exec web ls -lh /app/media/models/photos_1c/
```

### IPInfo.io (опционально)

**Без токена (бесплатно):**
- Работает из коробки
- Лимит: 50,000 запросов/месяц
- Базовые данные: город, регион, страна

**С токеном (расширенный):**
1. Зарегистрируйтесь на https://ipinfo.io/signup
2. Получите токен
3. Добавьте в `.env`:
   ```env
   IPINFO_ACCESS_TOKEN=your_token_here
   ```
4. Преимущества:
   - Увеличенный лимит запросов
   - Дополнительные данные (координаты, ASN, компания)
   - Приоритетная поддержка

## 🐛 Отладка

При возникновении проблем:

1. Проверьте логи в директории `/logs/`
2. Убедитесь, что Redis запущен: `redis-cli ping` (должен вернуть `PONG`)
3. Проверьте статус Celery worker
4. В режиме разработки (`DJANGO_ENV=local`) включен DEBUG режим с детальными ошибками

## 📚 Дополнительная информация

### Django приложения в проекте

- `addresses` - Управление локациями/складами
- `api` - REST API эндпоинты
- `banners` - Система баннеров
- `cart` - Корзина покупок
- `catalog` - Каталог товаров (категории, бренды, товары)
- `content` - CMS контент (страницы, новости, статьи)
- `feedback` - Формы обратной связи
- `media_content` - Управление медиа-файлами
- `orders` - Обработка заказов
- `promotions` - Акции и промо-кампании
- `search` - Функционал поиска
- `settings` - Глобальные настройки сайта
- `third_party` - Внешние интеграции (1C, кастомизации Django)
- `users` - Аутентификация и профили пользователей
- `utils` - Общие утилиты и миксины

---

## 📚 Документация

Полный набор документации доступен в папке `docs/`:

### CMS и управление контентом:
- **[CMS_GUIDE.md](docs/CMS_GUIDE.md)** - Полное руководство по работе с CMS (Django Admin)
  - Вход в админку: `http://localhost/admin/` (admin@test.ru / admin123)
  - Управление страницами, новостями, статьями
  - Баннеры и промо-акции
  - Управление заказами
  - SEO оптимизация
- **[CMS_STORAGE.md](docs/CMS_STORAGE.md)** - Где хранится контент CMS
  - База данных (PostgreSQL)
  - Медиа-файлы (`./media/`)
  - Структура хранения
  - Бэкапы и восстановление

### Интеграция с 1С:
- **[1C_INTEGRATION.md](docs/1C_INTEGRATION.md)** - Настройка интеграции с 1С
  - Протокол CommerceML 2.0
  - HTTP Basic Auth (без API ключей)
  - Синхронизация каталога и изображений
  - Пошаговая инструкция
- **[1C_MONITORING.md](docs/1C_MONITORING.md)** - Мониторинг обмена с 1С
  - Отслеживание запросов
  - Просмотр логов
  - Celery задачи
  - Решение проблем
- **Скрипт мониторинга:** `./scripts/monitor_1c.sh` (интерактивное меню)

### Миграция данных:
- **[MIGRATION_QUICK_START.md](docs/MIGRATION_QUICK_START.md)** - Быстрый старт (5 минут)
- **[MIGRATION_FROM_VPS.md](docs/MIGRATION_FROM_VPS.md)** - Подробная инструкция
- **[DATA_MIGRATION_DECISION.md](docs/DATA_MIGRATION_DECISION.md)** - Нужна ли миграция?
- **Скрипты:**
  - `./scripts/migrate_from_vps.sh` - Автоматическая миграция
  - `./scripts/check_vps_data.sh` - Проверка данных на VPS

---

## 🔄 Миграция с VPS

### Быстрый старт (автоматическая миграция):

```bash
# Настройте доступ к VPS
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"
export VPS_PATH="/home/mt/metateks-dev"

# Запустите автоматическую миграцию
./scripts/migrate_from_vps.sh
```

Скрипт автоматически:
- ✅ Создаст дамп БД на VPS
- ✅ Скачает его
- ✅ Синхронизирует медиа → `./media/`
- ✅ Восстановит БД в Docker
- ✅ Проверит результат

### Документация по миграции:

| Документ | Описание |
|----------|----------|
| **[MIGRATION_QUICK_START.md](docs/MIGRATION_QUICK_START.md)** | Быстрый старт (5 минут) |
| **[MIGRATION_FROM_VPS.md](docs/MIGRATION_FROM_VPS.md)** | Подробная инструкция |
| **[DATA_MIGRATION_DECISION.md](docs/DATA_MIGRATION_DECISION.md)** | Нужна ли миграция? |
| **Скрипт проверки** | `./scripts/check_vps_data.sh` |

### Что мигрирует:

- ✅ Пользователи и заказы → PostgreSQL
- ✅ CMS контент (страницы, новости) → PostgreSQL
- ✅ Медиа-файлы → `./media/` (на диске!)
- ❌ Каталог товаров - **придет из 1С автоматически**

---

**Проект готов к разработке после выполнения всех шагов выше!**
