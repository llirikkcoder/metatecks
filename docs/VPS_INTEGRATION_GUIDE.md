# Интеграция данных с VPS в новый Docker проект

Пошаговая инструкция по переносу недостающих файлов с VPS в локальный Docker проект.

---

## 📋 Ситуация

**VPS:** `/usr/app/back/` - старый проект (тот же первый коммит)
**Локально:** Новый Docker проект с обновленной конфигурацией

**Цель:** Забрать с VPS только недостающие данные (медиа, БД, возможно статику)

---

## 🎯 Что нужно забрать

### ✅ Обязательно
1. **База данных** (PostgreSQL дамп)
2. **Media файлы** (`/usr/app/back/media/`)

### ⚠️ Желательно
3. **Static/Assets** (`/usr/app/back/static/`) - если там есть кастомизация
4. **SSL сертификаты** (для справки)

### ❌ НЕ нужно
- `.git/` - уже есть локально
- `__pycache__/` - пересоберется
- `conf/` - уже настроены для Docker
- Код приложений - уже есть в Git

---

## 🚀 Шаг 1: Подготовка на VPS

### 1.1 Подключитесь к VPS

```bash
# Замените на ваши данные
ssh ваш_пользователь@IP_VPS

# Перейдите в директорию проекта
cd /usr/app/back
```

### 1.2 Проверьте что есть

```bash
# Структура проекта
ls -la

# Размер медиа (1,7G)
du -sh media/

# Проверка статики (66M)
du -sh static/

# Количество медиа файлов (3361)
find media/ -type f | wc -l
```

### 1.3 Создайте дамп базы данных

**Вариант A: Django dumpdata (Рекомендуется)**

```bash
# Активируйте virtualenv (если есть)
source ~/.virtualenvs/metateks/bin/activate
# или
source venv/bin/activate

# Создайте JSON дамп
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions.session \
  --exclude admin.logentry \
  --indent 2 \
  > metateks_dump_$(date +%Y%m%d).json

# Проверьте размер
ls -lh metateks_dump_*.json
```

**Вариант B: PostgreSQL pg_dump**

```bash
# Узнайте параметры БД
cat .env 2>/dev/null || cat main/settings/base.py | grep DATABASE -A 10

# Создайте дамп
pg_dump -U metateks -d metateks -F c -f metateks_db_$(date +%Y%m%d).backup

# Или SQL формат
pg_dump -U metateks -d metateks > metateks_db_$(date +%Y%m%d).sql

# Проверьте
ls -lh metateks_db_*
```

### 1.4 Проверьте что создалось

```bash
# Список файлов для скачивания
echo "=== Файлы готовые для скачивания ==="
ls -lh metateks_dump_*.json metateks_db_*.backup metateks_db_*.sql 2>/dev/null

# Проверьте медиа
echo "=== Размер медиа ==="
du -sh media/
echo "Файлов: $(find media/ -type f | wc -l)"

# Проверьте статику
echo "=== Размер статики ==="
du -sh static/ assets/ 2>/dev/null
```

---

## 📥 Шаг 2: Скачивание на локальный компьютер

### 2.1 Подготовьте локальную папку

```bash
# На ЛОКАЛЬНОМ компьютере (WSL)
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Создайте временную папку для данных с VPS
mkdir -p vps_import
cd vps_import
```

### 2.2 Скачайте дамп БД

**Вариант 1: SCP (для отдельных файлов)**

```bash
# Замените на ваши данные
VPS_USER="ваш_пользователь"
VPS_HOST="IP_VPS"

# Скачайте дамп
scp ${VPS_USER}@${VPS_HOST}:/usr/app/back/metateks_dump_*.json ./

# Или PostgreSQL дамп
scp ${VPS_USER}@${VPS_HOST}:/usr/app/back/metateks_db_*.backup ./
```

**Вариант 2: RSYNC (Рекомендуется)**

```bash
# Синхронизация дампа
rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/metateks_dump_*.json \
  ./
```

### 2.3 Синхронизируйте медиа-файлы

```bash
# ВАЖНО: Создайте папку media в основном проекте
cd /mnt/c/_KIPOL/_WORK/_metatecks/
mkdir -p media

# Синхронизация медиа напрямую в проект
rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/media/ \
  ./media/

# Проверьте что скачалось
ls -la media/
find media/ -type f | wc -l
```

### 2.4 (Опционально) Скачайте статику

```bash
# Если на VPS есть кастомная статика
rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/static/ \
  ./vps_import/static_vps/

# Проверьте что там
ls -la vps_import/static_vps/
```

### 2.5 (Опционально) Скачайте SSL сертификаты

```bash
# Для справки или переноса
rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/etc/letsencrypt/live/metateks-admin.vinodesign.ru/ \
  ./vps_import/ssl_admin/ \
  2>/dev/null || echo "Нет доступа к SSL (это нормально)"

rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/etc/letsencrypt/live/metateks-admin.vinodesign.ru/ \
  ./vps_import/ssl_main/ \
  2>/dev/null || echo "Нет доступа к SSL (это нормально)"
```

### 2.6 (Опционально) Скачайте конфиги для справки

```bash
# Конфиги VPS (для анализа, не для использования)
rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/conf/ \
  ./vps_import/conf_vps/
```

---

## 🔄 Шаг 3: Интеграция в Docker проект

### 3.1 Проверьте структуру

```bash
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Должна быть такая структура:
tree -L 2 -d
# .
# ├── media/                  ← Медиа с VPS
# ├── vps_import/             ← Временная папка
# │   ├── metateks_dump_*.json
# │   ├── static_vps/
# │   ├── conf_vps/
# │   └── ssl_*/
# ├── apps/
# ├── docker-compose.yml
# └── ...
```

### 3.2 Проверьте права доступа

```bash
# Медиа должны быть доступны для чтения
chmod -R 755 media/
find media/ -type f -exec chmod 644 {} \;

# Проверьте владельца
ls -la media/
```

### 3.3 Запустите Docker (если еще не запущен)

```bash
# Запустите контейнеры
docker-compose up -d

# Дождитесь готовности БД
docker-compose exec db pg_isready -U metateks

# Проверьте статус
docker-compose ps
```

### 3.4 Загрузите дамп БД

**Вариант A: Django loaddata (если использовали dumpdata)**

```bash
# Загрузите дамп
docker-compose exec -T web python manage.py loaddata < vps_import/metateks_dump_*.json

# Проверьте данные
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
from apps.content.models import News, Page

print(f"✓ Пользователей: {User.objects.count()}")
print(f"✓ Заказов: {Order.objects.count()}")
print(f"✓ Новостей: {News.objects.count()}")
print(f"✓ Страниц: {Page.objects.count()}")
PYEOF
```

**Вариант B: PostgreSQL pg_restore (если использовали pg_dump)**

```bash
# Скопируйте дамп в контейнер БД
docker cp vps_import/metateks_db_*.backup metateks_db:/tmp/

# Восстановите
docker-compose exec db pg_restore \
  -U metateks \
  -d metateks \
  --clean \
  --if-exists \
  /tmp/metateks_db_*.backup

# Или SQL формат
docker cp vps_import/metateks_db_*.sql metateks_db:/tmp/
docker-compose exec -T db psql -U metateks -d metateks < vps_import/metateks_db_*.sql
```

### 3.5 Проверьте медиа-файлы

```bash
# Проверьте что медиа доступны в контейнере
docker-compose exec web ls -la /app/media/ | head -20

# Проверьте через nginx
curl -I http://localhost/media/

# Откройте в браузере
# http://localhost/media/banners/
# http://localhost/media/news/
```

### 3.6 (Опционально) Интегрируйте статику

```bash
# Если на VPS была кастомная статика
cp -r vps_import/static_vps/* ./static/ 2>/dev/null || true

# Пересоберите статику
docker-compose exec web python manage.py collectstatic --noinput
```

---

## ✅ Шаг 4: Проверка интеграции

### 4.1 Проверьте базу данных

```bash
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
from apps.catalog.models import Product, Category
from apps.content.models import News, Page

print("\n=== Статистика БД ===")
print(f"Пользователей: {User.objects.count()}")
print(f"Заказов: {Order.objects.count()}")
print(f"Товаров: {Product.objects.count()}")
print(f"Категорий: {Category.objects.count()}")
print(f"Новостей: {News.objects.count()}")
print(f"Страниц: {Page.objects.count()}")
PYEOF
```

### 4.2 Проверьте медиа

```bash
# Количество файлов
echo "Медиа файлов на диске:"
find media/ -type f | wc -l

echo "Медиа файлов в контейнере:"
docker-compose exec web find /app/media/ -type f | wc -l

# Размер
echo "Размер медиа:"
du -sh media/
```

### 4.3 Проверьте админку

```bash
# Откройте в браузере
echo "Админка: http://localhost/admin/"

# Проверьте доступ через curl
curl -I http://localhost/admin/login/
```

### 4.4 Проверьте сайт

```bash
# Главная
curl -I http://localhost/

# Каталог
curl -I http://localhost/catalog/

# Медиа файлы
curl -I http://localhost/media/

# API
curl -I http://localhost/api/
```

---

## 🔧 Шаг 5: Что делать с разными файлами

### Media файлы

**Где должны быть:** `./media/`

**Структура:**
```
media/
├── banners/              ← Баннеры CMS
├── news/                 ← Новости
├── articles/             ← Статьи
├── homepage/             ← Главная
├── about/                ← О компании
├── models/photos_1c/     ← Фото товаров (если были)
└── cml/                  ← Временные файлы 1С
```

**Действие:** Оставить как есть, монтируется в Docker

---

### Static файлы

**С VPS:** `/usr/app/back/static/` → `./vps_import/static_vps/`

**Наш проект:** `./assets/` (исходники) → `./static/` (собранные)

**Действие:**
```bash
# Если на VPS была кастомизация CSS/JS
# Проверьте vps_import/static_vps/
# Скопируйте нужное в ./assets/

# Пересоберите
docker-compose exec web python manage.py collectstatic --noinput
```

---

### Конфиги VPS

**С VPS:** `/usr/app/back/conf/` → `./vps_import/conf_vps/`

**Наш проект:** `./conf/vps/` (для справки), `./docker/nginx/` (рабочие)

**Действие:**
```bash
# Конфиги VPS уже сохранены для справки
# Используются новые конфиги для Docker
# Ничего делать не нужно
```

---

### SSL сертификаты

**С VPS:** `/etc/letsencrypt/` → `./vps_import/ssl_*/`

**Действие:**
```bash
# Для продакшена получите новые сертификаты
# Или используйте скачанные (если те же домены)

# Поместите в Docker:
# docker/ssl/fullchain.pem
# docker/ssl/privkey.pem
```

---

## 🚨 Решение проблем

### Ошибка при loaddata

```bash
# Очистите БД
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py migrate
docker-compose exec -T web python manage.py loaddata < vps_import/metateks_dump_*.json
```

### Медиа не отображаются

```bash
# Проверьте права
chmod -R 755 media/
find media/ -type f -exec chmod 644 {} \;

# Проверьте монтирование
docker-compose exec web ls -la /app/media/

# Перезапустите nginx
docker-compose restart nginx
```

### "Permission denied" при доступе к VPS

```bash
# Настройте SSH ключ
ssh-copy-id ${VPS_USER}@${VPS_HOST}

# Или используйте пароль
rsync -avz --progress \
  -e "ssh" \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/media/ \
  ./media/
```

### Большой размер медиа

```bash
# Используйте сжатие rsync
rsync -avz --progress --compress-level=9 \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/media/ \
  ./media/

# Или скачайте по частям
rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/media/banners/ \
  ./media/banners/

rsync -avz --progress \
  ${VPS_USER}@${VPS_HOST}:/usr/app/back/media/news/ \
  ./media/news/
```

---

## 📊 Проверочный список

После интеграции проверьте:

- [ ] Дамп БД загружен успешно
- [ ] Количество записей совпадает с VPS
- [ ] Все медиа-файлы скачаны
- [ ] Медиа отображаются в браузере
- [ ] Админка доступна
- [ ] Можете войти (используйте данные с VPS)
- [ ] Сайт открывается
- [ ] Статика работает (CSS/JS загружаются)
- [ ] API отвечает
- [ ] Нет ошибок в логах

---

## 🧹 Шаг 6: Очистка

После успешной интеграции:

```bash
# На VPS (опционально)
ssh ${VPS_USER}@${VPS_HOST}
cd /usr/app/back
rm -f metateks_dump_*.json metateks_db_*.backup metateks_db_*.sql

# Локально
# Можете удалить vps_import/ после проверки
# НО СНАЧАЛА убедитесь что всё работает!

# Создайте бэкап перед удалением
tar czf vps_import_backup.tar.gz vps_import/
# rm -rf vps_import/  # Удалите только когда уверены
```

---

## 📚 Автоматический скрипт

Создан скрипт для автоматизации: `scripts/full_vps_download.sh`

```bash
# Установите параметры
export VPS_USER="ваш_пользователь"
export VPS_HOST="IP_VPS"
export VPS_PATH="/usr/app/back"

# Запустите
./scripts/full_vps_download.sh
```

Скрипт автоматически:
- Подключится к VPS
- Создаст дамп БД
- Скачает все необходимое
- Создаст структурированную папку

---

## 🎯 Итоговая структура после интеграции

```
/mnt/c/_KIPOL/_WORK/_metatecks/
├── media/                          ← Медиа с VPS ✅
│   ├── banners/
│   ├── news/
│   ├── articles/
│   └── ...
├── vps_import/                     ← Временные данные
│   ├── metateks_dump_20251225.json ← Дамп БД ✅
│   ├── static_vps/                 ← Статика VPS (для справки)
│   ├── conf_vps/                   ← Конфиги VPS (для справки)
│   └── ssl_*/                      ← SSL (для справки)
├── apps/                           ← Код (из Git)
├── docker-compose.yml              ← Docker конфигурация
├── .env.docker                     ← Настройки
└── ...

Docker containers:
├── PostgreSQL                      ← БД с данными VPS ✅
├── Django                          ← Приложение с медиа ✅
└── Nginx                           ← Раздача медиа ✅
```

---

## 💡 Важные замечания

1. **Не удаляйте данные на VPS** до полной проверки локального проекта
2. **Медиа монтируются** - изменения на диске = изменения в Docker
3. **БД в Docker volume** - используйте дампы для бэкапа
4. **Конфиги VPS не используются** - работают Docker конфиги
5. **SSL сертификаты** - получите новые для локального dev или production

---

**Полная документация:**
- [VPS_FULL_BACKUP.md](VPS_FULL_BACKUP.md) - Детальная выгрузка
- [VPS_QUICK_DOWNLOAD.md](VPS_QUICK_DOWNLOAD.md) - Быстрая шпаргалка
- [MIGRATION_FROM_VPS.md](MIGRATION_FROM_VPS.md) - Миграция

**Время выполнения:** 30-60 минут (зависит от размера медиа)
