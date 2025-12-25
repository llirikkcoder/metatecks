# Быстрая выгрузка с VPS - Шпаргалка

Краткая инструкция для тех, кто знает что делает.

---

## ⚡ Самый быстрый способ

```bash
# 1. Установите переменные
export VPS_USER="ваш_пользователь"
export VPS_HOST="IP_VPS"
export VPS_PATH="/home/mt/metateks-dev"

# 2. Запустите скрипт
./scripts/full_vps_download.sh

# 3. Дождитесь завершения и следуйте инструкциям
```

**Скрипт автоматически:**
- ✅ Создаст дамп БД на VPS
- ✅ Скачает дамп
- ✅ Синхронизирует все медиа-файлы
- ✅ Спросит про статику, конфиги, логи
- ✅ Создаст папку `vps_backup_YYYYMMDD_HHMMSS/`

---

## 🔧 Ручной способ (если нужен контроль)

### На VPS:

```bash
ssh user@VPS_IP
cd /home/mt/metateks-dev

# Создать дамп
source ~/.virtualenvs/metateks/bin/activate
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions.session \
  --exclude admin.logentry \
  > dump_$(date +%Y%m%d).json

ls -lh dump_*.json
```

### На локальном:

```bash
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# Скачать дамп
rsync -avz --progress user@VPS_IP:/home/mt/metateks-dev/dump_*.json ./

# Скачать медиа
rsync -avz --progress user@VPS_IP:/home/mt/metateks-dev/media/ ./media/
```

---

## 📦 Загрузка в Docker

```bash
# Запустить контейнеры
docker-compose up -d

# Дождаться готовности БД
docker-compose exec db pg_isready -U metateks

# Загрузить дамп
docker-compose exec -T web python manage.py loaddata < dump_*.json

# Проверить
docker-compose exec web python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
print(f"Users: {User.objects.count()}")
print(f"Orders: {Order.objects.count()}")
PYEOF
```

---

## ✅ Быстрая проверка

```bash
# БД
docker-compose exec web python manage.py shell -c "from apps.users.models import User; print(User.objects.count())"

# Медиа
find media/ -type f | wc -l

# Админка
curl -I http://localhost/admin/login/

# Медиа файлы
curl -I http://localhost/media/
```

---

## 🚨 Если что-то не так

**Ошибка при loaddata:**
```bash
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py migrate
docker-compose exec -T web python manage.py loaddata < dump.json
```

**Медиа не отображаются:**
```bash
# Проверьте права
chmod -R 755 media/
find media/ -type f -exec chmod 644 {} \;

# Перезапустите nginx
docker-compose restart nginx
```

**Большой дамп долго загружается:**
```bash
# Разбейте на части
python manage.py dumpdata users > users.json
python manage.py dumpdata orders > orders.json
python manage.py dumpdata content > content.json

# Загружайте по одной
docker-compose exec -T web python manage.py loaddata < users.json
```

---

## 📊 Что выгружать

| Данные | Обязательно | Откуда |
|--------|-------------|--------|
| **БД (дамп)** | ✅ ДА | Django dumpdata |
| **media/** | ✅ ДА | Все файлы |
| **static/** | ❌ НЕТ | Можно пересобрать `collectstatic` |
| **assets/** | ⚠️ ЖЕЛАТЕЛЬНО | Если кастомизировали |
| **.env** | ⚠️ ДЛЯ СПРАВКИ | Содержит пароли! |
| **logs/** | ❌ НЕТ | Опционально |

---

## 💡 Полезные команды

```bash
# Размер папок на VPS
ssh user@VPS_IP "cd /home/mt/metateks-dev && du -sh media/ static/ logs/"

# Количество файлов
ssh user@VPS_IP "cd /home/mt/metateks-dev && find media/ -type f | wc -l"

# Проверка БД на VPS
ssh user@VPS_IP "cd /home/mt/metateks-dev && python manage.py shell -c 'from apps.users.models import User; print(User.objects.count())'"

# Синхронизация с исключениями
rsync -avz --progress \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  user@VPS_IP:/home/mt/metateks-dev/media/ ./media/
```

---

## 📚 Подробная документация

Если нужны детали → [VPS_FULL_BACKUP.md](VPS_FULL_BACKUP.md)
