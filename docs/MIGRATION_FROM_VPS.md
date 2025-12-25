# Миграция с VPS на локальный Docker

## ✅ Что изменилось

**Медиа и логи теперь хранятся в папках проекта** для удобной миграции:

```
/mnt/c/_KIPOL/_WORK/_metatecks/
├── media/              ← Все медиа-файлы CMS и 1С
├── logs/               ← Логи приложения
├── static/             ← Статические файлы (в Docker volume)
├── apps/
├── docker-compose.yml
└── ...
```

**Преимущества:**
- ✅ Все в одном месте - один `rsync` и готово
- ✅ Видны файлы на диске
- ✅ Простой бэкап/восстановление
- ✅ Git игнорирует `media/*` и `logs/*`

---

## 🚀 Быстрая миграция (Рекомендуется)

### Шаг 1: Подготовка на VPS

```bash
# Подключитесь к VPS
ssh user@your_vps_ip

cd /home/mt/metateks-dev

# Активируйте виртуальное окружение
source ~/.virtualenvs/metateks/bin/activate

# Создайте дамп базы данных
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions.session \
  --exclude admin.logentry \
  --indent 2 \
  > metateks_full_dump.json

# Проверьте размер дампа
ls -lh metateks_full_dump.json

# Создайте архив медиа-файлов (если есть)
tar czf media_files.tar.gz media/

# Список того, что нужно скачать:
ls -lh metateks_full_dump.json media_files.tar.gz
```

---

### Шаг 2: Скачивание на локальный компьютер

```bash
# На вашем локальном компьютере (WSL)
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Скачайте дамп базы данных
scp user@your_vps_ip:/home/mt/metateks-dev/metateks_full_dump.json ./

# Скачайте медиа-файлы
scp user@your_vps_ip:/home/mt/metateks-dev/media_files.tar.gz ./

# Распакуйте медиа в папку проекта
tar xzf media_files.tar.gz

# Проверьте содержимое
ls -la media/
```

**Альтернатива (rsync - быстрее и удобнее):**

```bash
# Синхронизация медиа напрямую
rsync -avz --progress \
  user@your_vps_ip:/home/mt/metateks-dev/media/ \
  ./media/

# Синхронизация дампа
rsync -avz \
  user@your_vps_ip:/home/mt/metateks-dev/metateks_full_dump.json \
  ./
```

---

### Шаг 3: Восстановление в Docker

```bash
# Убедитесь, что контейнеры запущены
docker-compose up -d

# Дождитесь готовности БД
docker-compose exec db pg_isready -U metateks

# Очистите текущую базу (если нужно)
docker-compose exec db psql -U metateks -d metateks -c "
  DO \$\$ DECLARE
    r RECORD;
  BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
      EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
  END \$\$;
"

# Запустите миграции заново
docker-compose exec web python manage.py migrate

# Загрузите данные из дампа
docker-compose exec -T web python manage.py loaddata < metateks_full_dump.json

# Проверьте что данные загрузились
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
from apps.content.models import Page, News

print(f"Пользователей: {User.objects.count()}")
print(f"Заказов: {Order.objects.count()}")
print(f"Страниц: {Page.objects.count()}")
print(f"Новостей: {News.objects.count()}")
PYEOF
```

---

### Шаг 4: Проверка

```bash
# Проверьте что медиа-файлы доступны
ls -la media/

# Проверьте что сайт работает
curl -I http://localhost/

# Войдите в админку
# http://localhost/admin/
# Используйте свой email/пароль с VPS
```

---

## 🔄 Альтернативный метод (PostgreSQL напрямую)

Если у вас PostgreSQL на VPS:

### На VPS:

```bash
# Создайте бинарный дамп
pg_dump -U metateks -d metateks -F c -f metateks_db.backup

# Скачайте на локальный компьютер
scp user@vps:/path/to/metateks_db.backup ./
```

### На локальном Docker:

```bash
# Скопируйте дамп в контейнер БД
docker cp metateks_db.backup metateks_db:/tmp/

# Восстановите БД
docker-compose exec db pg_restore \
  -U metateks \
  -d metateks \
  --clean \
  --if-exists \
  /tmp/metateks_db.backup
```

---

## 📋 Что мигрирует, а что нет

### ✅ Нужно мигрировать:

| Данные | Как | Откуда |
|--------|-----|--------|
| **Пользователи** | База данных | Django |
| **Заказы** | База данных | Django |
| **CMS контент** | База данных | Django |
| **Баннеры** | База данных + медиа | Django + media/ |
| **Промо-акции** | База данных + медиа | Django + media/ |
| **Настройки сайта** | База данных | Django |
| **Изображения CMS** | Файлы | media/banners/, media/news/, и т.д. |

### ❌ НЕ нужно мигрировать:

| Данные | Почему | Откуда придет |
|--------|--------|---------------|
| **Каталог товаров** | Придет из 1С | 1С синхронизация |
| **Цены** | Придет из 1С | 1С синхронизация |
| **Остатки** | Придет из 1С | 1С синхронизация |
| **Изображения товаров** | Придут из 1С | media/models/photos_1c/ |
| **Категории** | Придут из 1С | 1С синхронизация |
| **Бренды** | Придут из 1С | 1С синхронизация |

---

## 🎯 Структура медиа-файлов

После миграции у вас должна быть такая структура:

```
media/
├── banners/                    ← Баннеры CMS
│   ├── desktop/
│   └── mobile/
├── news/                       ← Новости
│   └── main_photos/
├── articles/                   ← Статьи
│   └── main_photos/
├── models/                     ← НЕ ТРОГАТЬ! Сюда 1С загрузит фото
│   └── photos_1c/              ← Будет заполнено из 1С
├── homepage/                   ← Главная страница
├── about/                      ← О компании
│   ├── brands/
│   ├── delivery/
│   └── files/
└── cml/                        ← НЕ ТРОГАТЬ! Временные файлы 1С
    └── tmp/
```

**Важно:**
- `media/models/photos_1c/` - будет заполнена из 1С автоматически
- `media/cml/tmp/` - временные файлы обмена с 1С

---

## 🔧 Решение проблем

### Проблема: "duplicate key value violates unique constraint"

**Причина:** В базе уже есть данные с такими ID

**Решение:**
```bash
# Полностью очистите базу перед загрузкой
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py migrate
docker-compose exec -T web python manage.py loaddata < metateks_full_dump.json
```

---

### Проблема: Медиа-файлы не отображаются

**Проверка прав:**
```bash
# На хосте
chmod -R 755 media/
find media/ -type f -exec chmod 644 {} \;

# Перезапустите nginx
docker-compose restart nginx
```

**Проверка монтирования:**
```bash
# Убедитесь, что медиа примонтирована в контейнер
docker-compose exec web ls -la /app/media/

# Должны быть видны ваши файлы
```

---

### Проблема: Изображения есть, но не открываются

**Проверка nginx:**
```bash
# Проверьте конфиг nginx
docker-compose exec nginx cat /etc/nginx/conf.d/metateks.conf | grep media

# Должно быть:
# location /media/ {
#     alias /app/media/;
# }
```

---

## 📦 Бэкап перед миграцией

Перед миграцией создайте резервную копию:

```bash
# На VPS
cd /home/mt/metateks-dev

# База данных
pg_dump -U metateks -d metateks -F c -f backup_$(date +%Y%m%d).backup

# Медиа-файлы
tar czf media_backup_$(date +%Y%m%d).tar.gz media/

# Код (на всякий случай)
tar czf code_backup_$(date +%Y%m%d).tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='*.log' \
  --exclude='db.sqlite3' \
  .

# Скачайте бэкапы в безопасное место
scp backup_*.backup media_backup_*.tar.gz code_backup_*.tar.gz user@safe-server:/backups/
```

---

## ✅ Проверочный список после миграции

- [ ] База данных загружена (`Order.objects.count()` > 0)
- [ ] Пользователи перенесены (можете войти в админку)
- [ ] Медиа-файлы доступны (изображения открываются)
- [ ] CMS работает (страницы, новости открываются)
- [ ] Баннеры отображаются на главной
- [ ] Настройки сайта сохранены
- [ ] 1С интеграция настроена (см. docs/1C_INTEGRATION.md)
- [ ] Каталог синхронизируется с 1С

---

## 🚀 После миграции

### Настройте 1С интеграцию:

```bash
# Создайте пользователя для 1С (если еще нет)
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from django.contrib.auth.models import Permission

user = User.objects.create_user(
    email='1c@metateks.ru',
    password='SecurePassword123'
)
user.is_staff = True
perm = Permission.objects.get(codename='add_exchange')
user.user_permissions.add(perm)
user.save()
print(f"Пользователь создан: {user.email}")
PYEOF

# Настройте 1С на обмен
# URL: http://localhost/cml/1c_exchange.php
# Логин: 1c@metateks.ru
# Пароль: SecurePassword123
```

Полная инструкция: [docs/1C_INTEGRATION.md](1C_INTEGRATION.md)

---

## 💡 Автоматический скрипт миграции

Создан скрипт для автоматической миграции:

```bash
# Настройте переменные окружения
export VPS_USER="your_user"
export VPS_HOST="your_vps_ip"
export VPS_PATH="/home/mt/metateks-dev"

# Запустите миграцию
./scripts/migrate_from_vps.sh
```

Скрипт автоматически:
1. Создает дамп на VPS
2. Скачивает его
3. Синхронизирует медиа-файлы
4. Восстанавливает БД в Docker
5. Проверяет результат

---

## 📞 Дополнительная помощь

- **Решение о миграции:** [docs/DATA_MIGRATION_DECISION.md](DATA_MIGRATION_DECISION.md)
- **Проверка данных на VPS:** `./scripts/check_vps_data.sh`
- **1С интеграция:** [docs/1C_INTEGRATION.md](1C_INTEGRATION.md)
- **CMS руководство:** [docs/CMS_GUIDE.md](CMS_GUIDE.md)
- **Хранилище CMS:** [docs/CMS_STORAGE.md](CMS_STORAGE.md)
