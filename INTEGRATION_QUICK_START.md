# Быстрая интеграция VPS → Docker

3 команды для переноса данных с VPS в локальный Docker проект.

---

## ⚡ Экспресс-метод

### На VPS (подключитесь SSH):

```bash
ssh ваш_пользователь@IP_VPS
cd /usr/app/back

# 1. Создайте дамп БД
source ~/.virtualenvs/metateks/bin/activate
python manage.py dumpdata \
  --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.permission \
  --exclude sessions.session --exclude admin.logentry \
  --indent 2 > metateks_dump_$(date +%Y%m%d).json

# Проверьте
ls -lh metateks_dump_*.json
du -sh media/
```

### На локальном (WSL):

```bash
cd /mnt/c/_KIPOL/_WORK/_metatecks/

# 2. Скачайте данные
export VPS_USER="ваш_пользователь"
export VPS_HOST="IP_VPS"

# Дамп БД
rsync -avz --progress ${VPS_USER}@${VPS_HOST}:/usr/app/back/metateks_dump_*.json ./

# Медиа-файлы
rsync -avz --progress ${VPS_USER}@${VPS_HOST}:/usr/app/back/media/ ./media/

# 3. Загрузите в Docker
docker-compose up -d
docker-compose exec db pg_isready -U metateks
docker-compose exec -T web python manage.py loaddata < metateks_dump_*.json
```

---

## ✅ Проверка

```bash
# БД
docker-compose exec web python manage.py shell -c "from apps.users.models import User; print(f'Users: {User.objects.count()}')"

# Медиа
find media/ -type f | wc -l

# Сайт
curl http://localhost/
curl http://localhost/admin/login/
```

---

## 🚀 Автоматический скрипт (рекомендуется)

```bash
export VPS_USER="ваш_пользователь"
export VPS_HOST="IP_VPS"
export VPS_PATH="/usr/app/back"

./scripts/full_vps_download.sh
```

Скрипт сделает всё автоматически!

---

## 📚 Полная документация

- **[VPS_INTEGRATION_GUIDE.md](docs/VPS_INTEGRATION_GUIDE.md)** - Пошаговая инструкция
- **[VPS_FULL_BACKUP.md](docs/VPS_FULL_BACKUP.md)** - Детальная выгрузка
- **[VPS_QUICK_DOWNLOAD.md](docs/VPS_QUICK_DOWNLOAD.md)** - Команды

---

## 🎯 Что получите

```
После выполнения:

./media/              ← Все медиа с VPS
PostgreSQL в Docker   ← БД с данными VPS
http://localhost/     ← Рабочий сайт
http://localhost/admin/ ← Админка (используйте данные с VPS)
```

**Время:** 15-30 минут
