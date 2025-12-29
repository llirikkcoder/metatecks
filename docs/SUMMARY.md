# Итоговая конфигурация проекта

## ✅ Что сделано

### 1. Docker контейнеризация
- ✅ PostgreSQL 15 - основная база данных
- ✅ Redis 7 - очереди задач
- ✅ Django + Gunicorn - веб-приложение
- ✅ Celery - асинхронные задачи
- ✅ Nginx - reverse proxy

**Запуск:** `docker-compose up -d`
**Доступ:** http://localhost

---

### 2. Хранение данных (НОВОЕ!)

**Изменено для удобной миграции:**

```
До (неудобно):
├── /var/lib/docker/volumes/media_volume/    ← Медиа в Docker volume
└── /var/lib/docker/volumes/logs_volume/     ← Логи в Docker volume

После (удобно):
├── ./media/              ← Медиа прямо в папке проекта ✅
└── ./logs/               ← Логи прямо в папке проекта ✅
```

**Преимущества:**
- ✅ Все в одном месте - легко переносить
- ✅ Видны файлы на диске (можете открыть в проводнике)
- ✅ Один `rsync` и готово
- ✅ Простой бэкап (просто копируете папку)

---

### 3. Структура проекта

```
/mnt/c/_KIPOL/_WORK/_metatecks/
├── media/                    ← НОВОЕ: Медиа на диске
│   ├── banners/              ← Баннеры CMS
│   ├── news/                 ← Фото новостей
│   ├── models/photos_1c/     ← Фото товаров (из 1С)
│   └── ...
├── logs/                     ← НОВОЕ: Логи на диске
│   ├── debug.log
│   ├── errors.log
│   └── cml_*.log
├── apps/                     ← Код приложения
├── docker-compose.yml        ← ИЗМЕНЕНО: новые mount points
├── docs/                     ← НОВОЕ: Полная документация
└── scripts/                  ← НОВОЕ: Скрипты миграции
```

---

### 4. CMS (Django Admin)

**Доступ:**
- URL: http://localhost/admin/
- Email: admin@test.ru
- Пароль: admin123

**Возможности:**
- ✅ Управление страницами, новостями, статьями
- ✅ Баннеры и промо-акции
- ✅ Просмотр и обработка заказов
- ✅ Управление пользователями
- ✅ SEO настройки
- ✅ WYSIWYG редактор (TinyMCE)

**Документация:** [docs/CMS_GUIDE.md](CMS_GUIDE.md)

---

### 5. Интеграция с 1С

**Настройка:**
- URL для 1С: `http://localhost/cml/1c_exchange.php`
- Аутентификация: HTTP Basic Auth (Django пользователи)
- Протокол: CommerceML 2.0

**Что синхронизируется:**
- ✅ Каталог товаров → `catalog_product`
- ✅ Категории → `catalog_category`
- ✅ Цены → `catalog_product.price`
- ✅ Остатки → `catalog_product.quantity`
- ✅ Изображения → `media/models/photos_1c/`

**Документация:**
- [docs/1C_INTEGRATION.md](1C_INTEGRATION.md) - Настройка
- [docs/1C_MONITORING.md](1C_MONITORING.md) - Мониторинг
- `./scripts/monitor_1c.sh` - Скрипт мониторинга

---

### 6. Миграция с VPS

**Автоматическая миграция (рекомендуется):**

```bash
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"
export VPS_PATH="/home/mt/metateks-dev"

./scripts/migrate_from_vps.sh
```

**Что мигрирует:**
- ✅ Пользователи и заказы → PostgreSQL
- ✅ CMS контент → PostgreSQL
- ✅ Медиа-файлы → `./media/` (прямо в папку проекта!)
- ❌ Каталог товаров - **придет из 1С**

**Документация:**
- [docs/MIGRATION_QUICK_START.md](MIGRATION_QUICK_START.md) - 5 минут
- [docs/MIGRATION_FROM_VPS.md](MIGRATION_FROM_VPS.md) - Подробно
- [docs/DATA_MIGRATION_DECISION.md](DATA_MIGRATION_DECISION.md) - Нужна ли миграция?
- `./scripts/check_vps_data.sh` - Проверка данных на VPS

---

## 📊 Где что хранится

| Данные | Где | Доступ с хоста | Персистентно |
|--------|-----|----------------|--------------|
| **База PostgreSQL** | Docker Volume | ❌ (через docker exec) | ✅ |
| **Медиа CMS** | `./media/` | ✅ Прямой | ✅ |
| **Логи** | `./logs/` | ✅ Прямой | ✅ |
| **Статика** | Docker Volume | ❌ (auto-collect) | ✅ |
| **Код** | `./*` | ✅ Редактирование | ✅ (git) |

**Подробнее:** [docs/STORAGE_ARCHITECTURE.md](STORAGE_ARCHITECTURE.md)

---

## 🚀 Быстрый старт

### Новая установка (без миграции):

```bash
# 1. Запустить контейнеры
docker-compose up -d

# 2. Создать админа
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
User.objects.create_superuser(
    email='admin@test.ru',
    password='admin123'
)
PYEOF

# 3. Войти в админку
# http://localhost/admin/

# 4. Настроить 1С (см. docs/1C_INTEGRATION.md)
```

---

### Миграция с VPS:

```bash
# 1. Настроить доступ
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"

# 2. Запустить миграцию
./scripts/migrate_from_vps.sh

# 3. Проверить
docker-compose ps
curl http://localhost/

# 4. Настроить 1С для каталога
```

---

## 📚 Полная документация

### CMS:
- [CMS_GUIDE.md](CMS_GUIDE.md) - Руководство пользователя
- [CMS_STORAGE.md](CMS_STORAGE.md) - Где хранится контент

### 1С:
- [1C_INTEGRATION.md](1C_INTEGRATION.md) - Настройка интеграции
- [1C_MONITORING.md](1C_MONITORING.md) - Мониторинг и отладка

### Миграция:
- [MIGRATION_QUICK_START.md](MIGRATION_QUICK_START.md) - Быстрый старт
- [MIGRATION_FROM_VPS.md](MIGRATION_FROM_VPS.md) - Подробная инструкция
- [DATA_MIGRATION_DECISION.md](DATA_MIGRATION_DECISION.md) - Нужна ли миграция?

### Архитектура:
- [STORAGE_ARCHITECTURE.md](STORAGE_ARCHITECTURE.md) - Полная архитектура хранения

---

## 🔧 Полезные команды

### Docker:
```bash
docker-compose up -d              # Запустить все
docker-compose down               # Остановить (данные сохранятся)
docker-compose restart web        # Перезапустить Django
docker-compose logs -f web        # Логи Django
docker-compose ps                 # Статус контейнеров
```

### Django:
```bash
# Войти в shell
docker-compose exec web python manage.py shell

# Миграции
docker-compose exec web python manage.py migrate

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser
```

### Бэкап:
```bash
# БД
docker-compose exec db pg_dump -U metateks -d metateks -F c > backup.backup

# Медиа (просто копировать папку!)
cp -r media/ /path/to/backup/media/
# или
tar czf media_backup.tar.gz media/
```

### Мониторинг 1С:
```bash
# Интерактивное меню
./scripts/monitor_1c.sh

# Логи 1С
docker-compose logs -f celery | grep cml
tail -f logs/cml_sync.log
```

---

## ✅ Проверочный список

После настройки убедитесь:

- [ ] Контейнеры запущены (`docker-compose ps`)
- [ ] Сайт доступен (`curl http://localhost/`)
- [ ] Админка работает (`http://localhost/admin/`)
- [ ] Можете войти (admin@test.ru / admin123)
- [ ] Папка `media/` создана и доступна
- [ ] Папка `logs/` создана и пишутся логи
- [ ] Медиа файлы видны на диске (`ls -la media/`)
- [ ] 1С endpoint отвечает (`curl http://localhost/cml/1c_exchange.php`)

**Если мигрировали с VPS:**
- [ ] Пользователи перенесены
- [ ] Заказы на месте
- [ ] CMS контент работает
- [ ] Медиа-файлы отображаются
- [ ] 1С настроена на новый URL

---

## 🎯 Следующие шаги

1. **Настройте 1С интеграцию:**
   - Создайте пользователя для 1С
   - Настройте обмен в 1С
   - Дождитесь первой синхронизации каталога

2. **Заполните CMS:**
   - Создайте страницы (О компании, Доставка, Контакты)
   - Добавьте новости
   - Настройте баннеры на главной

3. **Настройте продакшн:**
   - Смените `SECRET_KEY` в `.env`
   - Настройте HTTPS
   - Настройте email для уведомлений
   - Настройте автоматический бэкап

---

## 💡 Важно помнить

### Данные НЕ потеряются при:
- ✅ `docker-compose down` (просто остановка)
- ✅ `docker-compose restart` (перезапуск)
- ✅ Обновлении образов
- ✅ Перезагрузке компьютера

### Данные ПОТЕРЯЮТСЯ при:
- ❌ `docker-compose down -v` (флаг -v удаляет volumes)
- ❌ `docker volume rm metatecks_postgres_data`
- ❌ Удалении папок `media/` или `logs/` вручную

### Каталог товаров:
- ❌ НЕ нужно переносить вручную
- ✅ Придет из 1С автоматически при первом обмене
- ⏱️ Время загрузки: 1-60 минут (зависит от количества)

---

## 📞 Поддержка

**Документация:** `docs/` (10+ подробных документов)

**Скрипты:**
- `./scripts/migrate_from_vps.sh` - Автоматическая миграция
- `./scripts/check_vps_data.sh` - Проверка VPS
- `./scripts/monitor_1c.sh` - Мониторинг 1С

**Логи:**
- Django: `docker-compose logs -f web`
- Celery: `docker-compose logs -f celery`
- Nginx: `docker-compose logs -f nginx`
- Файлы: `logs/debug.log`, `logs/errors.log`

---

**Проект готов к работе!** 🚀
