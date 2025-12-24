# Инструкция по миграции базы данных с VPS на локальный Docker

## 📋 Обзор

Эта инструкция поможет перенести базу данных PostgreSQL с VPS на локальный компьютер с Docker.

---

## Вариант 1: Миграция PostgreSQL → PostgreSQL (рекомендуется)

### Шаг 1: Создание дампа базы данных на VPS

**На VPS выполните:**

```bash
# Перейдите в директорию проекта
cd /home/mt/metateks-dev

# Создайте дамп базы данных PostgreSQL
# Замените параметры на ваши реальные значения
pg_dump -h localhost -U metateks -d metateks -F c -b -v -f metateks_dump.backup

# Или если используется docker на VPS:
# docker exec -t <имя_контейнера_postgres> pg_dump -U metateks -d metateks -F c -b -v > metateks_dump.backup

# Или создайте SQL дамп (текстовый формат):
pg_dump -h localhost -U metateks -d metateks -F p -f metateks_dump.sql
```

**Опции pg_dump:**
- `-h localhost` - хост базы данных
- `-U metateks` - имя пользователя БД
- `-d metateks` - имя базы данных
- `-F c` - формат custom (сжатый binary формат)
- `-F p` - формат plain SQL (текстовый)
- `-b` - включить большие объекты
- `-v` - verbose (подробный вывод)
- `-f` - файл для сохранения

### Шаг 2: Скачивание дампа на локальный компьютер

**На локальном компьютере выполните:**

```bash
# Скачайте дамп с VPS через SCP
scp user@your-vps-ip:/home/mt/metateks-dev/metateks_dump.backup ~/Downloads/

# Или если используете определенный SSH ключ:
scp -i ~/.ssh/your_key user@your-vps-ip:/home/mt/metateks-dev/metateks_dump.backup ~/Downloads/

# Переместите дамп в директорию проекта
mv ~/Downloads/metateks_dump.backup /mnt/c/_KIPOL/_WORK/_metatecks/
```

### Шаг 3: Остановка и очистка локальной базы данных

**На локальном компьютере:**

```bash
cd /mnt/c/_KIPOL/_WORK/_metatecks

# Остановите контейнеры
docker-compose down

# Удалите volume с базой данных (ВНИМАНИЕ: все локальные данные будут удалены!)
docker volume rm metatecks_postgres_data

# Запустите только базу данных и redis
docker-compose up -d db redis
```

### Шаг 4: Восстановление дампа в Docker

**Вариант A: Custom формат (.backup)**

```bash
# Скопируйте дамп в контейнер
docker cp metateks_dump.backup metateks_db:/tmp/

# Восстановите дамп
docker-compose exec db pg_restore -U metateks -d metateks -v -c /tmp/metateks_dump.backup

# Или если возникают ошибки, используйте --no-owner --no-acl:
docker-compose exec db pg_restore -U metateks -d metateks -v -c --no-owner --no-acl /tmp/metateks_dump.backup
```

**Вариант B: SQL формат (.sql)**

```bash
# Скопируйте дамп в контейнер
docker cp metateks_dump.sql metateks_db:/tmp/

# Восстановите дамп
docker-compose exec db psql -U metateks -d metateks -f /tmp/metateks_dump.sql
```

### Шаг 5: Запуск всех контейнеров

```bash
# Запустите все сервисы
docker-compose up -d

# Проверьте логи
docker-compose logs -f web

# Проверьте статус
docker-compose ps
```

### Шаг 6: Проверка данных

```bash
# Войдите в Django shell
docker-compose exec web python manage.py shell

# Проверьте количество объектов
from apps.catalog.models import Product, Category
from apps.orders.models import Order
from apps.users.models import User

print(f"Категорий: {Category.objects.count()}")
print(f"Товаров: {Product.objects.count()}")
print(f"Заказов: {Order.objects.count()}")
print(f"Пользователей: {User.objects.count()}")
```

---

## Вариант 2: Миграция SQLite → PostgreSQL

Если на VPS используется SQLite (файл `db.sqlite3`):

### Шаг 1: Скачивание SQLite базы с VPS

```bash
# Скачайте файл базы данных
scp user@your-vps-ip:/home/mt/metateks-dev/db.sqlite3 /mnt/c/_KIPOL/_WORK/_metatecks/db_from_vps.sqlite3
```

### Шаг 2: Создание JSON дампа из SQLite

**На локальном компьютере (вне Docker, с SQLite):**

```bash
cd /mnt/c/_KIPOL/_WORK/_metatecks

# Создайте временное окружение с правильными настройками
# Временно измените DATABASE_URL в .env на SQLite
export DATABASE_URL=""

# Создайте дамп всех данных в JSON
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude admin.logentry \
  --exclude sessions.session \
  --indent 2 \
  -o full_database_dump.json

# Или создайте дампы по приложениям
python manage.py dumpdata addresses -o dump_addresses.json --indent 2
python manage.py dumpdata catalog -o dump_catalog.json --indent 2
python manage.py dumpdata orders -o dump_orders.json --indent 2
python manage.py dumpdata users -o dump_users.json --indent 2
python manage.py dumpdata content -o dump_content.json --indent 2
python manage.py dumpdata banners -o dump_banners.json --indent 2
python manage.py dumpdata settings -o dump_settings.json --indent 2
```

### Шаг 3: Загрузка данных в PostgreSQL (Docker)

```bash
# Убедитесь, что используется PostgreSQL
docker-compose down -v
docker-compose up -d db redis
sleep 10

# Запустите миграции
docker-compose run --rm web python manage.py migrate

# Загрузите данные
docker-compose run --rm web python manage.py loaddata full_database_dump.json

# Или по частям:
docker-compose run --rm web python manage.py loaddata dump_addresses.json
docker-compose run --rm web python manage.py loaddata dump_catalog.json
docker-compose run --rm web python manage.py loaddata dump_orders.json
docker-compose run --rm web python manage.py loaddata dump_users.json
docker-compose run --rm web python manage.py loaddata dump_content.json
docker-compose run --rm web python manage.py loaddata dump_banners.json
docker-compose run --rm web python manage.py loaddata dump_settings.json
```

---

## Вариант 3: Использование django-dumpdata/loaddata (универсальный)

### Шаг 1: Создание JSON дампа на VPS

**На VPS:**

```bash
cd /home/mt/metateks-dev

# Активируйте виртуальное окружение
source ~/.virtualenvs/metateks/bin/activate

# Создайте полный дамп
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude admin.logentry \
  --exclude sessions.session \
  --indent 2 \
  -o production_dump_$(date +%Y%m%d).json
```

### Шаг 2: Скачивание на локальный компьютер

```bash
scp user@your-vps-ip:/home/mt/metateks-dev/production_dump_*.json /mnt/c/_KIPOL/_WORK/_metatecks/
```

### Шаг 3: Загрузка в Docker

```bash
cd /mnt/c/_KIPOL/_WORK/_metatecks

# Остановите и пересоздайте базу
docker-compose down -v
docker-compose up -d db redis
sleep 10

# Запустите миграции
docker-compose run --rm web python manage.py migrate

# Загрузите данные
docker-compose run --rm web python manage.py loaddata production_dump_*.json

# Запустите все сервисы
docker-compose up -d
```

---

## Миграция медиа-файлов

Не забудьте также перенести загруженные файлы (изображения, документы):

```bash
# Создайте архив медиа-файлов на VPS
tar -czf media_files.tar.gz -C /home/mt/metateks-dev/media .

# Скачайте на локальный компьютер
scp user@your-vps-ip:/home/mt/metateks-dev/media_files.tar.gz ~/Downloads/

# Распакуйте в media директорию проекта
cd /mnt/c/_KIPOL/_WORK/_metatecks
mkdir -p media
tar -xzf ~/Downloads/media_files.tar.gz -C media/

# Или используйте rsync для синхронизации:
rsync -avz --progress user@your-vps-ip:/home/mt/metateks-dev/media/ /mnt/c/_KIPOL/_WORK/_metatecks/media/
```

---

## Решение проблем

### Ошибка: "role does not exist"

```bash
# Создайте пользователя в PostgreSQL
docker-compose exec db psql -U postgres -c "CREATE USER metateks WITH PASSWORD 'metateks_password';"
docker-compose exec db psql -U postgres -c "ALTER USER metateks CREATEDB;"
docker-compose exec db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE metateks TO metateks;"
```

### Ошибка: "relation already exists"

Используйте флаг `--clean` при pg_restore:

```bash
docker-compose exec db pg_restore -U metateks -d metateks -v -c --clean --if-exists /tmp/metateks_dump.backup
```

### Ошибка при loaddata: "matching query does not exist"

Загружайте данные в правильном порядке:

```bash
# Сначала справочники
python manage.py loaddata dump_addresses.json
python manage.py loaddata dump_settings.json

# Затем пользователи
python manage.py loaddata dump_users.json

# Затем каталог
python manage.py loaddata dump_catalog.json

# В конце заказы
python manage.py loaddata dump_orders.json
```

### Очистка кэша после миграции

```bash
# Очистите Redis кэш
docker-compose exec redis redis-cli FLUSHALL

# Пересоздайте поисковый индекс
docker-compose exec web python manage.py buildwatson
```

---

## Проверка успешной миграции

```bash
# 1. Проверьте работу сайта
curl http://localhost/

# 2. Проверьте админку
curl http://localhost/admin/

# 3. Проверьте подключение к базе
docker-compose exec web python manage.py dbshell

# 4. Проверьте логи
docker-compose logs web
docker-compose logs celery

# 5. Проверьте количество записей
docker-compose exec web python manage.py shell -c "
from apps.catalog.models import Product, Category
from apps.orders.models import Order
from apps.users.models import User
print('Категорий:', Category.objects.count())
print('Товаров:', Product.objects.count())
print('Заказов:', Order.objects.count())
print('Пользователей:', User.objects.count())
"
```

---

## Быстрый скрипт для автоматизации

Создайте файл `migrate_db.sh`:

```bash
#!/bin/bash

VPS_USER="your_user"
VPS_HOST="your_vps_ip"
VPS_PATH="/home/mt/metateks-dev"
DUMP_FILE="metateks_dump_$(date +%Y%m%d_%H%M%S).backup"

echo "==> Создание дампа на VPS..."
ssh $VPS_USER@$VPS_HOST "cd $VPS_PATH && pg_dump -U metateks -d metateks -F c -b -v -f $DUMP_FILE"

echo "==> Скачивание дампа..."
scp $VPS_USER@$VPS_HOST:$VPS_PATH/$DUMP_FILE .

echo "==> Остановка локальных контейнеров..."
docker-compose down -v

echo "==> Запуск базы данных..."
docker-compose up -d db redis
sleep 10

echo "==> Копирование дампа в контейнер..."
docker cp $DUMP_FILE metateks_db:/tmp/

echo "==> Восстановление дампа..."
docker-compose exec db pg_restore -U metateks -d metateks -v -c --no-owner --no-acl /tmp/$DUMP_FILE

echo "==> Запуск всех сервисов..."
docker-compose up -d

echo "==> Готово! Проверьте http://localhost"
```

Сделайте скрипт исполняемым:

```bash
chmod +x migrate_db.sh
./migrate_db.sh
```

---

## 🔒 Безопасность

**ВАЖНО:**
- Не храните дампы базы данных в публичных местах
- Удаляйте дампы после успешной миграции
- Используйте `.gitignore` для исключения `*.backup`, `*.sql`, `*_dump.json`
- Не коммитьте базы данных в Git

```bash
# Добавьте в .gitignore
echo "*.backup" >> .gitignore
echo "*.sql" >> .gitignore
echo "*_dump.json" >> .gitignore
echo "db_from_vps.sqlite3" >> .gitignore
```

---

**Готово!** После выполнения этих шагов ваша локальная база данных будет полностью синхронизирована с VPS.
