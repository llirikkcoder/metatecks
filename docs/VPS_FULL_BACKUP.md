# Полная выгрузка данных с VPS

Пошаговая инструкция по загрузке ВСЕХ данных с VPS на локальный компьютер.

---

## 📋 Что будем выгружать

```
VPS → Локально
├── База данных (PostgreSQL/SQLite)      → ./dump.json или ./backup.sql
├── Медиа-файлы (media/)                 → ./media/
├── Статические файлы (static/assets/)   → ./assets/ (опционально)
├── Конфигурация (.env, settings)        → для справки
└── Логи (logs/)                         → ./logs_vps/ (опционально)
```

---

## 🚀 Быстрый старт (Автоматический скрипт)

### Вариант 1: Автоматическая выгрузка

```bash
# На локальном компьютере (WSL)
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Установите переменные
export VPS_USER="ваш_пользователь"
export VPS_HOST="IP_или_домен_VPS"
export VPS_PATH="/home/mt/metateks-dev"

# Запустите скрипт
./scripts/migrate_from_vps.sh
```

Скрипт автоматически:
1. ✅ Создаст дамп БД на VPS
2. ✅ Скачает дамп
3. ✅ Синхронизирует все медиа-файлы
4. ✅ Загрузит данные в Docker

---

## 📝 Ручная выгрузка (Пошагово)

### Шаг 1: Подключитесь к VPS

```bash
ssh ваш_пользователь@IP_VPS

# Перейдите в директорию проекта
cd /home/mt/metateks-dev
# или
cd /путь/к/вашему/проекту
```

---

### Шаг 2: Проверьте что есть на VPS

```bash
# Проверьте структуру
ls -la

# Должны увидеть:
# - manage.py
# - apps/
# - media/
# - static/ или assets/
# - .env или settings.py

# Проверьте размер медиа
du -sh media/

# Проверьте базу данных
python manage.py dbshell
# или
psql -U user -d database_name
```

---

### Шаг 3: Создайте дамп базы данных

#### Вариант A: Django dumpdata (Рекомендуется)

```bash
# Активируйте virtualenv (если есть)
source ~/.virtualenvs/metateks/bin/activate
# или
source venv/bin/activate

# Создайте полный дамп
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions.session \
  --exclude admin.logentry \
  --indent 2 \
  > metateks_full_dump_$(date +%Y%m%d).json

# Проверьте размер
ls -lh metateks_full_dump_*.json
```

**Преимущества:**
- ✅ Независимо от версии PostgreSQL
- ✅ Можно выбирать что выгружать
- ✅ Работает с любой БД (PostgreSQL, MySQL, SQLite)

#### Вариант B: PostgreSQL pg_dump

```bash
# Узнайте параметры подключения
cat .env | grep DATABASE
# или
cat main/settings/base.py | grep DATABASES -A 10

# Создайте дамп (binary format - быстрее)
pg_dump -U metateks -d metateks -F c -f metateks_db_$(date +%Y%m%d).backup

# Или SQL формат (для просмотра)
pg_dump -U metateks -d metateks -f metateks_db_$(date +%Y%m%d).sql

# Проверьте
ls -lh metateks_db_*
```

**Преимущества:**
- ✅ Быстрее для больших БД
- ✅ Сохраняет всю структуру

---

### Шаг 4: Создайте архивы медиа-файлов

```bash
# Архив медиа (сжатый)
tar czf media_$(date +%Y%m%d).tar.gz media/

# Проверьте размер
ls -lh media_*.tar.gz

# Архив статики (опционально - можно пересобрать локально)
tar czf static_$(date +%Y%m%d).tar.gz static/ assets/

# Список файлов
tar -tzf media_*.tar.gz | head -20
```

---

### Шаг 5: (Опционально) Сохраните конфигурацию

```bash
# Скопируйте .env (ВНИМАНИЕ: содержит пароли!)
cp .env env_backup_$(date +%Y%m%d).txt

# Или создайте архив конфигов
tar czf config_$(date +%Y%m%d).tar.gz \
  .env* \
  conf/ \
  main/settings/ \
  requirements*.txt \
  docker-compose.yml 2>/dev/null || true

ls -lh config_*.tar.gz
```

---

### Шаг 6: (Опционально) Логи

```bash
# Если хотите сохранить логи
tar czf logs_$(date +%Y%m%d).tar.gz logs/ /var/log/metateks/ 2>/dev/null || true

ls -lh logs_*.tar.gz
```

---

### Шаг 7: Проверьте что получилось

```bash
# Список всех созданных файлов
ls -lh metateks_* media_* static_* config_* logs_* 2>/dev/null

# Итоговый список для скачивания
echo "=== Файлы для скачивания ==="
ls -lh *.json *.backup *.sql *.tar.gz 2>/dev/null | tail -10
```

**Должны увидеть примерно:**
```
metateks_full_dump_20251225.json    # База данных (Django)
media_20251225.tar.gz               # Медиа-файлы
static_20251225.tar.gz              # Статика (опционально)
config_20251225.tar.gz              # Конфиги (опционально)
logs_20251225.tar.gz                # Логи (опционально)
```

---

## 📥 Скачивание на локальный компьютер

### Вариант 1: SCP (для небольших объемов)

```bash
# На ЛОКАЛЬНОМ компьютере (WSL)
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Создайте папку для бэкапов
mkdir -p vps_backup
cd vps_backup

# Скачайте дамп БД
scp user@VPS_IP:/home/mt/metateks-dev/metateks_full_dump_*.json ./

# Скачайте медиа
scp user@VPS_IP:/home/mt/metateks-dev/media_*.tar.gz ./

# Скачайте статику (опционально)
scp user@VPS_IP:/home/mt/metateks-dev/static_*.tar.gz ./

# Скачайте конфиги (опционально)
scp user@VPS_IP:/home/mt/metateks-dev/config_*.tar.gz ./

# Скачайте логи (опционально)
scp user@VPS_IP:/home/mt/metateks-dev/logs_*.tar.gz ./
```

### Вариант 2: RSYNC (Рекомендуется - быстрее, можно возобновить)

```bash
# На ЛОКАЛЬНОМ компьютере
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Синхронизация медиа напрямую (без архива)
rsync -avz --progress \
  user@VPS_IP:/home/mt/metateks-dev/media/ \
  ./media/

# Скачать дамп БД
rsync -avz --progress \
  user@VPS_IP:/home/mt/metateks-dev/metateks_full_dump_*.json \
  ./

# Скачать все архивы
rsync -avz --progress \
  user@VPS_IP:/home/mt/metateks-dev/*.tar.gz \
  ./vps_backup/
```

**Преимущества rsync:**
- ✅ Можно прервать и продолжить
- ✅ Синхронизирует только измененные файлы
- ✅ Показывает прогресс
- ✅ Сжатие на лету (-z)

---

## 📦 Распаковка на локальном компьютере

```bash
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Распакуйте медиа (если скачали архивом)
tar xzf vps_backup/media_*.tar.gz

# Распакуйте статику (опционально)
tar xzf vps_backup/static_*.tar.gz

# Распакуйте конфиги (для справки)
tar xzf vps_backup/config_*.tar.gz -C vps_backup/

# Проверьте что распаковалось
ls -la media/
ls -la static/
ls -la vps_backup/
```

---

## 🔄 Загрузка в Docker

### Шаг 1: Убедитесь что контейнеры запущены

```bash
docker-compose up -d

# Дождитесь готовности БД
docker-compose exec db pg_isready -U metateks
```

### Шаг 2: Загрузите дамп

```bash
# Если использовали Django dumpdata
docker-compose exec -T web python manage.py loaddata < metateks_full_dump_*.json

# Если использовали pg_dump (binary)
docker cp metateks_db_*.backup metateks_db:/tmp/
docker-compose exec db pg_restore \
  -U metateks -d metateks \
  --clean --if-exists \
  /tmp/metateks_db_*.backup

# Если использовали pg_dump (SQL)
docker cp metateks_db_*.sql metateks_db:/tmp/
docker-compose exec -T db psql -U metateks -d metateks < /tmp/metateks_db_*.sql
```

### Шаг 3: Проверьте данные

```bash
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
from apps.content.models import News, Page

print(f"Пользователей: {User.objects.count()}")
print(f"Заказов: {Order.objects.count()}")
print(f"Новостей: {News.objects.count()}")
print(f"Страниц: {Page.objects.count()}")
PYEOF
```

### Шаг 4: Проверьте медиа-файлы

```bash
# Проверьте что медиа доступны
ls -la media/ | head -20

# Проверьте через браузер
# http://localhost/media/banners/
# http://localhost/media/news/
```

---

## 🔍 Проверка что ничего не потеряли

### Чеклист на VPS (ДО выгрузки)

```bash
# На VPS
ssh user@VPS_IP

cd /home/mt/metateks-dev

# Посчитайте записи в БД
python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
from apps.content.models import News, Page
from apps.catalog.models import Product

print(f"Users: {User.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"News: {News.objects.count()}")
print(f"Pages: {Page.objects.count()}")
print(f"Products: {Product.objects.count()}")
PYEOF

# Посчитайте медиа файлы
find media/ -type f | wc -l
du -sh media/

# Сохраните результаты
python manage.py shell -c "
from apps.users.models import User
from apps.orders.models import Order
print(f'Users: {User.objects.count()}')
print(f'Orders: {Order.objects.count()}')
" > vps_stats.txt

find media/ -type f | wc -l >> vps_stats.txt
```

### Чеклист на локальном (ПОСЛЕ загрузки)

```bash
# На локальном
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
from apps.content.models import News, Page

print(f"Users: {User.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"News: {News.objects.count()}")
print(f"Pages: {Page.objects.count()}")
PYEOF

# Посчитайте медиа файлы
find media/ -type f | wc -l
du -sh media/

# Сравните с vps_stats.txt
```

**Должны совпадать:**
- ✅ Количество пользователей
- ✅ Количество заказов
- ✅ Количество медиа-файлов
- ✅ Размер папки media/

---

## 🚨 Решение проблем

### Проблема: Большой размер медиа

**Если media/ очень большая (> 10GB):**

```bash
# Вариант 1: Сжатие с прогрессом
tar czf - media/ | pv > media.tar.gz

# Вариант 2: Разбить на части по 2GB
tar czf - media/ | split -b 2G - media_part_

# Скачать части
scp user@VPS_IP:/path/media_part_* ./

# Собрать обратно
cat media_part_* | tar xzf -
```

### Проблема: Медленная загрузка дампа

**Если loaddata долго работает:**

```bash
# Попробуйте загрузить по частям
python manage.py dumpdata users > users.json
python manage.py dumpdata orders > orders.json
python manage.py dumpdata content > content.json

# Загружайте по одной
docker-compose exec -T web python manage.py loaddata < users.json
docker-compose exec -T web python manage.py loaddata < orders.json
```

### Проблема: Ошибки при loaddata

**"duplicate key" ошибки:**

```bash
# Очистите БД перед загрузкой
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py migrate
docker-compose exec -T web python manage.py loaddata < dump.json
```

### Проблема: Не хватает места

**Проверьте место на диске:**

```bash
# На VPS
df -h
du -sh media/ static/ logs/

# На локальном
df -h /mnt/c/
du -sh ./
```

**Очистите лишнее:**

```bash
# На VPS (после успешной загрузки)
rm *.tar.gz *.json *.backup

# Очистите старые логи
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 📊 Проверка целостности

### После загрузки всего:

```bash
# 1. Проверьте БД
docker-compose exec web python manage.py check

# 2. Проверьте миграции
docker-compose exec web python manage.py showmigrations

# 3. Проверьте админку
curl http://localhost/admin/login/ -I

# 4. Проверьте медиа
curl http://localhost/media/ -I

# 5. Попробуйте войти
# http://localhost/admin/
# Используйте email/пароль с VPS
```

---

## 🎯 Финальный чеклист

- [ ] Дамп БД создан и скачан
- [ ] Все медиа-файлы синхронизированы
- [ ] Статика скачана (опционально)
- [ ] Конфигурация сохранена для справки
- [ ] Дамп загружен в Docker
- [ ] Количество записей совпадает с VPS
- [ ] Медиа файлы доступны через браузер
- [ ] Можете войти в админку
- [ ] Все страницы открываются
- [ ] Изображения отображаются

---

## 💾 Создание резервной копии

После успешной миграции создайте локальный бэкап:

```bash
# Дамп локальной БД
docker-compose exec db pg_dump -U metateks -d metateks -F c \
  > backup_local_$(date +%Y%m%d).backup

# Архив всего проекта
tar czf metateks_full_backup_$(date +%Y%m%d).tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='node_modules' \
  --exclude='.git' \
  media/ backup_local_*.backup docker-compose.yml .env.docker

# Сохраните в безопасном месте
mv metateks_full_backup_*.tar.gz /path/to/backup/location/
```

---

## 📞 Помощь

**Если что-то пошло не так:**

1. Проверьте логи:
   ```bash
   docker-compose logs -f web
   tail -f logs/*.log
   ```

2. Проверьте статус контейнеров:
   ```bash
   docker-compose ps
   ```

3. Попробуйте перезапустить:
   ```bash
   docker-compose restart web
   ```

4. В крайнем случае - начните заново:
   ```bash
   docker-compose down -v
   docker-compose up -d
   # Повторите загрузку дампа
   ```

---

**Важно:** Не удаляйте данные на VPS до полной проверки работы на локальном!
