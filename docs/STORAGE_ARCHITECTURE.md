# Архитектура хранения данных

## 📦 Обзор

Проект использует **гибридную модель хранения** для оптимального баланса между производительностью, портативностью и удобством разработки.

---

## 🗂️ Три уровня хранения

```
┌─────────────────────────────────────────────────────────┐
│  1. Docker Volumes (PostgreSQL, Redis, Static)          │
│     - Персистентные                                      │
│     - Управляются Docker                                 │
│     - Автоматический бэкап при backup volumes            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. Папки проекта (media/, logs/)                       │
│     - Прямой доступ с диска                             │
│     - Видны в проводнике                                │
│     - Легко копировать и бэкапить                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. Код приложения (apps/, templates/, assets/)         │
│     - В git репозитории                                 │
│     - Синхронизируется автоматически                    │
└─────────────────────────────────────────────────────────┘
```

---

## 💾 Docker Volumes (Управляемые Docker)

### 1. PostgreSQL Database

**Volume:** `metatecks_postgres_data`
**Mountpoint:** `/var/lib/docker/volumes/metatecks_postgres_data/_data`
**Размер:** ~71 MB (растет с данными)

**Что хранится:**
- Пользователи (`users_user`)
- Заказы (`orders_order`, `orders_orderitem`)
- CMS контент (`content_page`, `content_news`, `content_article`)
- Каталог товаров (`catalog_product`, `catalog_category`) - из 1С
- Баннеры (`banners_banner`)
- Настройки (`settings_sitesetting`)
- История 1С обмена (`cml_exchange`)

**Особенности:**
- ✅ Автоматически сохраняется при `docker-compose down`
- ✅ НЕ удаляется при `docker-compose down` (только при `-v` флаге)
- ✅ Быстрый доступ (нативная файловая система контейнера)
- ⚠️ Требует `docker volume backup` для бэкапа

**Бэкап:**
```bash
# Создать дамп
docker-compose exec db pg_dump -U metateks -d metateks -F c -f /tmp/backup.backup
docker cp metateks_db:/tmp/backup.backup ./

# Восстановить
docker cp backup.backup metateks_db:/tmp/
docker-compose exec db pg_restore -U metateks -d metateks --clean /tmp/backup.backup
```

---

### 2. Redis Data

**Volume:** `metatecks_redis_data`
**Mountpoint:** `/var/lib/docker/volumes/metatecks_redis_data/_data`
**Размер:** ~16 KB

**Что хранится:**
- Celery очереди задач
- Кэш сессий (опционально)
- Временные данные

**Особенности:**
- ✅ Персистентный (appendonly mode)
- ⚠️ Можно очистить без потерь (временные данные)

---

### 3. Static Files

**Volume:** `metatecks_static_volume`
**Mountpoint:** `/var/lib/docker/volumes/metatecks_static_volume/_data`
**Размер:** ~67 MB

**Что хранится:**
- CSS/JS из `assets/`
- Django Admin статика
- Библиотеки (jQuery, Swiper, Fancybox)
- Шрифты, иконки

**Особенности:**
- ✅ Собирается автоматически при запуске (`collectstatic`)
- ⚠️ Можно безопасно удалить (пересоздастся)
- 📌 Используется Nginx для раздачи

---

## 📁 Папки проекта (На диске хоста)

### 1. media/ (Медиа-файлы CMS и 1С)

**Путь хоста:** `/mnt/c/_KIPOL/_WORK/_metatecks/media/`
**Путь в контейнере:** `/app/media/`
**Тип монтирования:** Bind mount (`./media:/app/media`)

**Структура:**
```
media/
├── banners/                    # Изображения баннеров
│   ├── desktop/
│   └── mobile/
├── news/                       # Новости
│   └── main_photos/
├── articles/                   # Статьи
│   └── main_photos/
├── models/                     # Товары
│   ├── photos_1c/              # Фото из 1С (автоматически)
│   ├── documents/              # Документация товаров
│   └── video/                  # Видео товаров
├── homepage/                   # Главная страница
│   ├── advantages/
│   └── videos/
├── about/                      # О компании
│   ├── brands/                 # Логотипы брендов
│   ├── delivery/               # Логотипы ТК
│   ├── files/                  # Документы
│   ├── photo/                  # Фотогалерея
│   └── video/                  # Видео
├── promotions/                 # Промо-акции
│   └── banners/
└── cml/                        # Временные файлы 1С
    └── tmp/                    # Загрузки из 1С (очищается)
```

**Особенности:**
- ✅ Прямой доступ с диска (можете открыть в проводнике)
- ✅ Легко копировать (rsync, scp)
- ✅ Видны изменения в реальном времени
- ✅ Git ignore (не попадают в репозиторий)
- ✅ Идеально для миграции (все в одном месте)

**Размер файлов (типичный):**
- Баннеры: 2-5 MB каждый
- Фото товаров: 100-500 KB каждое
- Документы PDF: 1-10 MB

**Права доступа:**
```bash
# Рекомендуемые права
chmod -R 755 media/
find media/ -type f -exec chmod 644 {} \;
```

---

### 2. logs/ (Логи приложения)

**Путь хоста:** `/mnt/c/_KIPOL/_WORK/_metatecks/logs/`
**Путь в контейнере:** `/app/logs/`
**Тип монтирования:** Bind mount (`./logs:/app/logs`)

**Файлы логов:**
```
logs/
├── debug.log              # Отладочные сообщения (DEBUG уровень)
├── errors.log             # Ошибки (ERROR уровень)
├── cml_sync.log           # Синхронизация с 1С
├── cml_tasks.log          # Celery задачи 1С
└── cml_utils.log          # Утилиты 1С
```

**Особенности:**
- ✅ Прямой доступ (tail -f logs/debug.log)
- ✅ Ротация логов (по размеру/дате)
- ⚠️ Могут занимать много места (очищайте периодически)

**Очистка:**
```bash
# Очистить все логи
rm -f logs/*.log

# Очистить логи старше 30 дней
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 🔄 Код приложения (Git репозиторий)

**Путь хоста:** `/mnt/c/_KIPOL/_WORK/_metatecks/`
**Путь в контейнере:** `/app/`
**Тип монтирования:** Bind mount (`.:/app`)

**Структура:**
```
/mnt/c/_KIPOL/_WORK/_metatecks/
├── apps/                  # Django приложения
├── templates/             # HTML шаблоны
├── assets/                # Статические файлы (CSS, JS)
├── docker/                # Docker конфигурация
├── docs/                  # Документация
├── fixtures/              # Начальные данные
├── main/                  # Настройки Django
├── scripts/               # Скрипты миграции
├── docker-compose.yml     # Docker Compose конфигурация
├── requirements-*.txt     # Зависимости Python
└── manage.py              # Django management
```

**Особенности:**
- ✅ Изменения кода сразу видны в контейнере (hot reload)
- ✅ Полный контроль версий (git)
- ✅ Легко редактировать в IDE

---

## 🎯 Сравнение методов хранения

| Тип данных | Где хранится | Почему | Доступ с хоста |
|------------|--------------|--------|----------------|
| **База данных** | Docker Volume | Производительность, изоляция | ❌ Только через docker exec |
| **Медиа CMS** | Папка проекта | Портативность, удобство | ✅ Прямой доступ |
| **Логи** | Папка проекта | Удобство отладки | ✅ Прямой доступ |
| **Статика** | Docker Volume | Автоматическая сборка | ❌ Не требуется |
| **Код** | Папка проекта | Разработка | ✅ Редактирование |

---

## 🔒 Что сохраняется при операциях

### docker-compose down
- ✅ PostgreSQL данные (volume)
- ✅ Redis данные (volume)
- ✅ Медиа-файлы (папка проекта)
- ✅ Логи (папка проекта)
- ✅ Статика (volume)

### docker-compose down -v
- ❌ PostgreSQL данные **УДАЛЯЮТСЯ**
- ❌ Redis данные **УДАЛЯЮТСЯ**
- ✅ Медиа-файлы (папка проекта)
- ✅ Логи (папка проекта)
- ❌ Статика **УДАЛЯЕТСЯ** (пересоберется)

### docker-compose restart
- ✅ Все данные сохраняются
- ✅ Контейнеры перезапускаются

---

## 📦 Полный бэкап проекта

### Что нужно бэкапить:

```bash
# 1. База данных (обязательно)
docker-compose exec db pg_dump -U metateks -d metateks -F c -f /tmp/db.backup
docker cp metateks_db:/tmp/db.backup ./backups/

# 2. Медиа-файлы (обязательно)
tar czf backups/media_$(date +%Y%m%d).tar.gz media/

# 3. .env файл (настройки)
cp .env backups/.env.backup

# 4. Код (опционально, если не в git)
git push origin main
```

### Что НЕ нужно бэкапить:

- ❌ Статика (`static/`) - пересоберется из `assets/`
- ❌ Python зависимости (из `requirements-*.txt`)
- ❌ Логи (если не критичны)
- ❌ Redis данные (временные)

---

## 🚀 Восстановление из бэкапа

```bash
# 1. Восстановить код
git clone <repo> && cd metateks-dev
cp backups/.env.backup .env

# 2. Восстановить медиа
tar xzf backups/media_20241225.tar.gz

# 3. Запустить контейнеры
docker-compose up -d

# 4. Восстановить БД
docker cp backups/db.backup metateks_db:/tmp/
docker-compose exec db pg_restore -U metateks -d metateks --clean /tmp/db.backup

# 5. Проверить
docker-compose ps
curl http://localhost/
```

---

## 💡 Рекомендации

### Для разработки:
- ✅ Используйте текущую структуру (медиа в папке проекта)
- ✅ Регулярно делайте `git commit` и `git push`
- ✅ Периодически экспортируйте БД (1 раз в неделю)

### Для продакшена:
- ✅ Настройте автоматический бэкап PostgreSQL
- ✅ Используйте отдельное хранилище для медиа (S3, MinIO)
- ✅ Настройте ротацию логов
- ✅ Мониторьте размер volumes

### Для миграции:
- ✅ Весь проект в одной папке - легко переносить
- ✅ Один `rsync` команда копирует все
- ✅ Docker volumes пересоздаются автоматически

---

## 📊 Типичные размеры

```
metatecks_postgres_data    71 MB      (растет с данными)
metatecks_static_volume    67 MB      (статичный)
metatecks_redis_data       16 KB      (статичный)
media/                     0-500 MB   (зависит от контента)
logs/                      0-100 MB   (ротация)
```

**Общий размер проекта:** 150-700 MB

---

## 🔗 Связанная документация

- **[CMS_STORAGE.md](CMS_STORAGE.md)** - Детали хранения CMS
- **[MIGRATION_FROM_VPS.md](MIGRATION_FROM_VPS.md)** - Миграция данных
- **[1C_INTEGRATION.md](1C_INTEGRATION.md)** - Где хранятся файлы из 1С
