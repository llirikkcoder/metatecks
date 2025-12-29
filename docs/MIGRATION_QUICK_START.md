# Быстрый старт: Миграция с VPS

## 🚀 Самый простой способ (5 минут)

### Настройте доступ к VPS:

```bash
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"
export VPS_PATH="/home/mt/metateks-dev"
```

### Запустите автоматическую миграцию:

```bash
./scripts/migrate_from_vps.sh
```

**Готово!** Скрипт автоматически:
- ✅ Создаст дамп БД на VPS
- ✅ Скачает его
- ✅ Синхронизирует медиа-файлы → `media/`
- ✅ Восстановит БД в Docker PostgreSQL
- ✅ Проверит результат

---

## 📁 Куда попадут файлы

```
/mnt/c/_KIPOL/_WORK/_metatecks/
├── media/                    ← Все медиа с VPS
│   ├── banners/
│   ├── news/
│   ├── articles/
│   ├── models/photos_1c/
│   └── ...
├── logs/                     ← Логи приложения
├── metateks_dump_*.backup    ← Дамп БД (можно удалить после)
└── ...
```

**Преимущества:**
- Все в одной папке - легко бэкапить
- Видны файлы на диске - можете открыть в проводнике
- Портативно - просто скопируйте папку

---

## ✅ После миграции

### Проверьте что все работает:

```bash
# Сайт доступен
curl http://localhost/

# Админка работает
curl http://localhost/admin/

# Данные на месте
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
print(f"Пользователей: {User.objects.count()}")
print(f"Заказов: {Order.objects.count()}")
PYEOF
```

### Посмотрите медиа-файлы:

```bash
# На диске (прямой доступ!)
ls -la media/banners/
ls -la media/news/main_photos/

# В контейнере (должно быть то же самое)
docker-compose exec web ls -la /app/media/banners/
```

---

## 🔄 Настройте 1С (важно!)

После миграции каталог товаров будет **пустой** (это нормально).

Настройте 1С интеграцию, чтобы загрузить каталог:

```bash
# 1. Создайте пользователя для 1С
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from django.contrib.auth.models import Permission

user = User.objects.create_user(
    email='1c@metateks.ru',
    password='YourSecurePassword123'
)
user.is_staff = True
perm = Permission.objects.get(codename='add_exchange')
user.user_permissions.add(perm)
user.save()
print(f"Создан: {user.email}")
PYEOF

# 2. Настройте 1С на обмен
# URL: http://localhost/cml/1c_exchange.php
# Логин: 1c@metateks.ru
# Пароль: YourSecurePassword123

# 3. Запустите обмен в 1С
# Каталог загрузится автоматически
```

Подробнее: [docs/1C_INTEGRATION.md](1C_INTEGRATION.md)

---

## 🎯 Что НЕ нужно делать

**НЕ переносите каталог товаров вручную!**

Каталог придет из 1С:
- ❌ Товары - придут из 1С
- ❌ Категории - придут из 1С
- ❌ Цены - придут из 1С
- ❌ Изображения товаров - придут из 1С в `media/models/photos_1c/`

**Переносите только:**
- ✅ Пользователей
- ✅ Заказы
- ✅ CMS контент (страницы, новости)
- ✅ Баннеры + изображения
- ✅ Настройки сайта

---

## 💾 Структура хранения

### База данных PostgreSQL

**Docker Volume** (автоматически сохраняется):
```
metatecks_postgres_data → /var/lib/docker/volumes/
```

**Что хранится:**
- Пользователи, заказы
- CMS контент (страницы, новости)
- Настройки сайта
- Каталог из 1С (после синхронизации)

### Медиа-файлы

**Папка проекта** (видно на диске):
```
./media/ → /mnt/c/_KIPOL/_WORK/_metatecks/media/
```

**Что хранится:**
- Баннеры (`media/banners/`)
- Фото новостей (`media/news/`)
- Фото статей (`media/articles/`)
- Фото товаров из 1С (`media/models/photos_1c/`)
- Документы (`media/about/files/`)

---

## 🔧 Решение проблем

### "Permission denied" при миграции медиа

```bash
# Дайте права на папку
chmod -R 755 media/
```

### Медиа-файлы не отображаются на сайте

```bash
# Проверьте, что файлы примонтированы
docker-compose exec web ls -la /app/media/

# Перезапустите nginx
docker-compose restart nginx
```

### База данных не восстанавливается

```bash
# Полностью очистите и начните заново
docker-compose down -v
docker volume rm metatecks_postgres_data
./scripts/migrate_from_vps.sh
```

---

## 📋 Полная документация

- **Подробная миграция:** [MIGRATION_FROM_VPS.md](MIGRATION_FROM_VPS.md)
- **Нужна ли миграция:** [DATA_MIGRATION_DECISION.md](DATA_MIGRATION_DECISION.md)
- **Проверка данных VPS:** `./scripts/check_vps_data.sh`
- **1С интеграция:** [1C_INTEGRATION.md](1C_INTEGRATION.md)
- **CMS руководство:** [CMS_GUIDE.md](CMS_GUIDE.md)
- **Хранение данных:** [CMS_STORAGE.md](CMS_STORAGE.md)
