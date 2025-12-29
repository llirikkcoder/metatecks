# Где хранится CMS контент

## 📂 Полная карта хранения

CMS контент хранится в **3 основных местах**:

1. **База данных PostgreSQL** - текстовый контент
2. **Файловая система (media/)** - изображения и файлы
3. **Код приложения (apps/)** - логика и шаблоны

---

## 💾 1. База данных (PostgreSQL)

### Расположение данных:

**Docker volume:**
```
metatecks_postgres_data
```

**Физическое расположение в контейнере:**
```
/var/lib/postgresql/data
```

### Таблицы CMS в базе данных:

#### 📄 Страницы и контент (apps/content)

```sql
-- Страницы
content_page                      -- Статические страницы
content_news                      -- Новости
content_newscategory              -- Категории новостей
content_article                   -- Статьи
content_articlescategory          -- Категории статей

-- О компании
content_aboutcompany              -- Основная информация
content_aboutadvantage            -- Преимущества компании
content_aboutfact                 -- Факты о компании
content_aboutwarehouse            -- Склады компании
content_abouttransportcompany     -- Транспортные компании

-- Главная страница
content_homepage                  -- Настройки главной
content_homepageadvantage         -- Преимущества на главной
content_homepagefact              -- Факты на главной
content_homepagesalesmanager      -- Менеджеры по продажам
content_homepagesalesphone        -- Телефоны менеджеров
content_homepagewarehouse         -- Склады на главной

-- Футер
content_footerdata                -- Данные футера
content_footerfirstcolumnlink     -- Ссылки 1-й колонки
content_footersecondcolumnlink    -- Ссылки 2-й колонки
content_footerthirdcolumnlink     -- Ссылки 3-й колонки
content_footerfourthcolumnlink    -- Ссылки 4-й колонки
content_footersociallink          -- Соцсети в футере

-- Хедер
content_headerdata                -- Данные хедера
content_headerlink                -- Ссылки в хедере
```

#### 🎨 Баннеры и промо

```sql
banners_banner                    -- Баннеры
promotions_promotion              -- Промо-акции
promotions_promotion_extra_products_list  -- Товары в акциях
```

#### ⚙️ Настройки

```sql
settings_seosetting               -- SEO настройки
settings_sitesetting              -- Настройки сайта
```

#### 🎥 Медиа-контент

```sql
media_content_mediafile           -- Медиа-файлы (видео)
media_content_mediatag            -- Теги для медиа
```

### Просмотр таблиц:

```bash
# Список всех таблиц CMS
docker-compose exec db psql -U metateks -d metateks -c "\dt content_*"

# Просмотр структуры таблицы
docker-compose exec db psql -U metateks -d metateks -c "\d content_page"

# Просмотр данных
docker-compose exec db psql -U metateks -d metateks -c "SELECT id, title, slug FROM content_page LIMIT 10;"
```

### Резервное копирование данных:

```bash
# Дамп всех CMS таблиц
docker-compose exec db pg_dump -U metateks -d metateks \
  -t 'content_*' \
  -t 'banners_*' \
  -t 'promotions_*' \
  -t 'settings_*' \
  -F c -f /tmp/cms_backup.backup

# Скопировать на хост
docker cp metateks_db:/tmp/cms_backup.backup ./cms_backup.backup
```

---

## 📁 2. Файловая система (Media)

### Расположение медиа-файлов:

**Docker volume:**
```
metatecks_media_volume
```

**Путь в контейнере:**
```
/app/media/
```

**Путь на хосте (при volume mount):**
```
/mnt/c/_KIPOL/_WORK/_metatecks/media/
```

### Структура директорий media/:

```
media/
├── about/                        # О компании
│   ├── brands/                   # Логотипы брендов
│   │   └── *.svg
│   ├── delivery/                 # Логотипы транспортных компаний
│   │   └── *.svg
│   ├── files/                    # Документы для скачивания
│   │   └── *.pdf
│   ├── photos/                   # Фотогалерея компании
│   │   └── *.jpg
│   └── videos/                   # Видео о компании
│       └── thumbnails/
│
├── articles/                     # Статьи
│   ├── main_photos/              # Главные изображения статей
│   │   └── *.jpg
│   └── thumbnails/               # Миниатюры (auto-generated)
│
├── banners/                      # Баннеры
│   ├── desktop/                  # Изображения для десктопа
│   │   └── *.jpg
│   └── mobile/                   # Изображения для мобильных
│       └── *.jpg
│
├── brands/                       # Бренды
│   └── logos/                    # Логотипы брендов
│       └── *.svg, *.png
│
├── categories/                   # Категории товаров
│   ├── photos/                   # Изображения категорий
│   │   └── *.jpg
│   └── icons/                    # Иконки категорий
│       └── *.svg
│
├── homepage/                     # Главная страница
│   ├── advantages/               # Изображения преимуществ
│   ├── facts/                    # Изображения фактов
│   └── managers/                 # Фото менеджеров
│
├── models/                       # Товары (модели)
│   ├── photos/                   # Фото товаров (загруженные вручную)
│   ├── photos_1c/                # Фото товаров из 1С
│   │   └── *.jpg
│   └── thumbnails/               # Миниатюры (auto-generated)
│
├── news/                         # Новости
│   ├── main_photos/              # Главные изображения новостей
│   │   └── *.jpg
│   └── thumbnails/
│
├── pages/                        # Страницы
│   └── images/                   # Изображения в контенте страниц
│
├── promotions/                   # Промо-акции
│   ├── banners/                  # Баннеры акций
│   └── thumbnails/
│
├── users/                        # Пользователи
│   └── avatars/                  # Аватары пользователей
│       └── *.jpg
│
└── cml/                          # Интеграция с 1С
    └── tmp/                      # Временные файлы от 1С
        ├── import.xml
        ├── offers.xml
        └── *.jpg                 # Изображения (временно)
```

### Просмотр медиа-файлов:

```bash
# Список всех медиа-файлов
docker-compose exec web find /app/media -type f | head -50

# Размер директории media
docker-compose exec web du -sh /app/media/*

# Последние загруженные файлы
docker-compose exec web find /app/media -type f -mtime -7 -ls

# Изображения баннеров
docker-compose exec web ls -lh /app/media/banners/

# Изображения товаров из 1С
docker-compose exec web ls -lh /app/media/models/photos_1c/
```

### Резервное копирование медиа:

```bash
# Создать архив всех медиа-файлов
docker-compose exec web tar -czf /tmp/media_backup.tar.gz /app/media

# Скопировать на хост
docker cp metateks_web:/tmp/media_backup.tar.gz ./media_backup.tar.gz

# Или синхронизировать с rsync
rsync -avz --progress metateks_web:/app/media/ ./media_backup/
```

---

## 💻 3. Код приложения (Apps)

### Расположение кода CMS:

**На хосте:**
```
/mnt/c/_KIPOL/_WORK/_metatecks/apps/
```

**В контейнере:**
```
/app/apps/
```

### Структура приложения content (главное CMS приложение):

```
apps/content/
├── models/                       # Модели (структура БД)
│   ├── __init__.py
│   ├── pages.py                  # Модель страниц
│   ├── news.py                   # Модель новостей
│   ├── articles.py               # Модель статей
│   ├── homepage.py               # Модель главной страницы
│   ├── about_company.py          # Модель "О компании"
│   ├── header_data.py            # Модель хедера
│   └── footer_data.py            # Модель футера
│
├── admin/                        # Настройки админки
│   ├── __init__.py
│   ├── pages.py                  # Админка страниц
│   ├── news.py                   # Админка новостей
│   ├── articles.py               # Админка статей
│   ├── homepage.py               # Админка главной
│   ├── about_company.py          # Админка "О компании"
│   ├── header_data.py            # Админка хедера
│   └── footer_data.py            # Админка футера
│
├── views/                        # Представления (логика)
│   ├── __init__.py
│   ├── pages.py                  # Отображение страниц
│   ├── news.py                   # Отображение новостей
│   ├── articles.py               # Отображение статей
│   ├── homepage.py               # Отображение главной
│   └── about.py                  # Отображение "О компании"
│
├── urls/                         # URL маршруты
│   ├── __init__.py
│   ├── news.py                   # /news/
│   ├── articles.py               # /articles/
│   └── about.py                  # /about/
│
├── migrations/                   # Миграции БД
│   ├── 0001_initial.py
│   ├── 0002_load_data.py
│   └── ...
│
├── templatetags/                 # Шаблонные теги
│   └── base_tags.py              # Кастомные теги для шаблонов
│
├── context_processors.py         # Контекстные процессоры
├── admin_forms.py                # Формы для админки
├── app.py                        # Конфигурация приложения
└── __init__.py
```

### Другие CMS приложения:

```
apps/
├── banners/                      # Баннеры
│   ├── models.py
│   ├── admin.py
│   └── manager.py                # Логика отображения баннеров
│
├── promotions/                   # Промо-акции
│   ├── models.py
│   ├── admin.py
│   └── manager.py
│
├── settings/                     # Настройки сайта
│   ├── models.py
│   ├── admin.py
│   └── context_processors.py     # Глобальные настройки
│
└── media_content/                # Медиа-контент
    ├── models.py
    └── admin.py
```

---

## 🎨 4. Шаблоны (Templates)

### Расположение:

**На хосте:**
```
/mnt/c/_KIPOL/_WORK/_metatecks/templates/
```

### Структура шаблонов CMS:

```
templates/
├── _base.html                    # Базовый шаблон
│
├── home.html                     # Главная страница
│
├── page.html                     # Страница (одиночная)
│
├── news.html                     # Список новостей
├── news-item.html                # Одна новость
│
├── articles.html                 # Список статей
├── articles-item.html            # Одна статья
│
├── about/                        # Шаблоны "О компании"
│   ├── _layout.html
│   ├── about_page.html
│   ├── files.html
│   ├── photo.html
│   ├── video.html
│   └── requisites.html
│
└── include/                      # Включаемые компоненты
    ├── header.html               # Хедер сайта
    ├── footer.html               # Футер сайта
    └── ...
```

---

## 🔄 5. Статические файлы (Static)

### Расположение:

**Исходники (на хосте):**
```
/mnt/c/_KIPOL/_WORK/_metatecks/assets/
```

**Собранные статические файлы (в контейнере):**
```
/app/static/
```

**Docker volume:**
```
metatecks_static_volume
```

### Структура:

```
assets/                           # Исходники
├── css/
│   ├── style_metateks.css
│   ├── style_metateks.less       # LESS файлы
│   └── extra.css
│
├── js/
│   ├── script_metateks.js
│   ├── jquery.min.js
│   └── ...
│
├── images/
│   └── ...
│
└── fonts/
    └── ...

static/                           # Собранные файлы
├── css/
├── js/
├── images/
├── fonts/
└── admin/                        # Статика Django Admin
```

---

## 📊 Сводная таблица

| Тип данных | Где хранится | Путь | Резервная копия |
|------------|--------------|------|-----------------|
| **Текстовый контент** | PostgreSQL | `/var/lib/postgresql/data` | `pg_dump` |
| **Изображения/файлы** | Файловая система | `/app/media/` | `tar` или `rsync` |
| **Код моделей** | Git репозиторий | `/app/apps/content/models/` | Git |
| **Код админки** | Git репозиторий | `/app/apps/content/admin/` | Git |
| **Шаблоны** | Git репозиторий | `/app/templates/` | Git |
| **Статика (CSS/JS)** | Файловая система | `/app/static/` | Не нужно (генерится) |

---

## 🔍 Как найти конкретный контент

### Найти где хранится страница "О доставке"

**1. В базе данных:**
```bash
docker-compose exec db psql -U metateks -d metateks -c \
  "SELECT id, title, slug FROM content_page WHERE slug = 'delivery';"
```

**2. Модель в коде:**
```bash
# Файл: apps/content/models/pages.py
cat apps/content/models/pages.py
```

**3. Админка в коде:**
```bash
# Файл: apps/content/admin/pages.py
cat apps/content/admin/pages.py
```

**4. Шаблон:**
```bash
# Файл: templates/page.html
cat templates/page.html
```

---

### Найти где хранятся изображения баннера

**1. Запись в БД:**
```bash
docker-compose exec db psql -U metateks -d metateks -c \
  "SELECT id, title, image_desktop, image_mobile FROM banners_banner LIMIT 5;"
```

**2. Файлы на диске:**
```bash
docker-compose exec web ls -lh /app/media/banners/desktop/
docker-compose exec web ls -lh /app/media/banners/mobile/
```

**3. Модель в коде:**
```bash
cat apps/banners/models.py
```

---

### Найти где хранятся новости

**1. В БД:**
```bash
docker-compose exec db psql -U metateks -d metateks -c \
  "SELECT id, title, slug, created_at FROM content_news ORDER BY created_at DESC LIMIT 10;"
```

**2. Изображения:**
```bash
docker-compose exec web ls -lh /app/media/news/main_photos/
```

**3. Модель:**
```bash
cat apps/content/models/news.py
```

**4. Шаблоны:**
```bash
ls -l templates/news*.html
```

---

## 💾 Полное резервное копирование CMS

### Скрипт полного бэкапа:

```bash
#!/bin/bash

BACKUP_DIR="./cms_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "1. Резервная копия БД..."
docker-compose exec db pg_dump -U metateks -d metateks \
  -F c -f /tmp/cms_db.backup
docker cp metateks_db:/tmp/cms_db.backup $BACKUP_DIR/

echo "2. Резервная копия медиа-файлов..."
docker-compose exec web tar -czf /tmp/media.tar.gz /app/media
docker cp metateks_web:/tmp/media.tar.gz $BACKUP_DIR/

echo "3. Копирование кода (опционально)..."
cp -r apps/content $BACKUP_DIR/
cp -r apps/banners $BACKUP_DIR/
cp -r apps/promotions $BACKUP_DIR/
cp -r templates $BACKUP_DIR/

echo "Готово! Бэкап в: $BACKUP_DIR"
```

---

## 🔧 Полезные команды

### Просмотр размера данных:

```bash
# Размер БД
docker-compose exec db psql -U metateks -d metateks -c \
  "SELECT pg_size_pretty(pg_database_size('metateks'));"

# Размер медиа-файлов
docker-compose exec web du -sh /app/media

# Размер по категориям
docker-compose exec web du -sh /app/media/*
```

### Очистка старых файлов:

```bash
# Удалить временные файлы 1С старше 7 дней
docker-compose exec web find /app/media/cml/tmp -type f -mtime +7 -delete

# Удалить неиспользуемые миниатюры
docker-compose exec web python manage.py thumbnail_cleanup
```

---

## 📚 Итого: Карта хранения CMS

```
┌─────────────────────────────────────────────────────────┐
│                    CMS КОНТЕНТ                          │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐
      │PostgreSQL│    │   Media   │   │  Code   │
      │   БД     │    │   Files   │   │  (Git)  │
      └─────────┘    └───────────┘   └─────────┘
           │               │               │
     ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
     │ Таблицы:  │   │Директории:│   │Приложения:│
     │           │   │           │   │           │
     │content_*  │   │banners/   │   │content/   │
     │banners_*  │   │news/      │   │banners/   │
     │promotions*│   │articles/  │   │promotions/│
     │settings_* │   │models/    │   │settings/  │
     └───────────┘   └───────────┘   └───────────┘

      Volume:          Volume:         Git Repo:
postgres_data     media_volume    /mnt/c/.../apps/
```

**Все данные CMS распределены между:**
1. ✅ **База данных** - текст, настройки, связи
2. ✅ **Медиа-файлы** - изображения, документы
3. ✅ **Код** - модели, админка, шаблоны
