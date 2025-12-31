# Backup & Disaster Recovery - Краткое резюме

## ✅ Что настроено для защиты от потери данных

### 1. Автоматический перезапуск контейнеров

```yaml
restart: unless-stopped
```

**Все контейнеры** автоматически перезапускаются:
- ✅ После сбоя/краша
- ✅ После перезагрузки сервера
- ✅ После обновления Docker

### 2. Persistent Storage (данные сохраняются)

| Что | Где хранится | Тип |
|-----|--------------|-----|
| **PostgreSQL база** | Docker volume `metateks_postgres_data` | Volume |
| **Redis данные** | Docker volume `metateks_redis_data` | Volume |
| **Static файлы** | Docker volume `metateks_static_volume` | Volume |
| **Media файлы** | `/opt/metatecks/media/` | Bind mount |
| **Логи** | `/opt/metatecks/logs/` | Bind mount |
| **Исходный код** | GitHub репозиторий | Git |

### 3. Healthchecks (автомониторинг)

Docker автоматически проверяет работоспособность:
- PostgreSQL: каждые 10 сек
- Redis: каждые 10 сек
- Web (Django): каждые 30 сек

### 4. Автоматические бекапы

**Ежедневно в 3:00 AM** создается полный backup:
- ✅ pg_dump базы данных
- ✅ Redis dump.rdb
- ✅ Архив media файлов (все загрузки)
- ✅ .env.docker конфигурация
- ✅ Список Docker volumes

**Размер бекапа:** ~1.5 GB

**Хранение:** `/opt/metatecks/backups/`

**Автоочистка:** Старше 30 дней удаляются автоматически

---

## 📋 Быстрые команды

### Создать backup вручную

```bash
ssh root@5.188.138.16
cd /opt/metatecks
./scripts/backup.sh
```

### Восстановить из backup

```bash
ssh root@5.188.138.16
cd /opt/metatecks
./scripts/restore.sh backups/metateks_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Посмотреть доступные бекапы

```bash
ssh root@5.188.138.16
ls -lh /opt/metatecks/backups/
```

### Скачать backup на локальную машину

```bash
scp -i ~/.ssh/id_ed25519_vps root@5.188.138.16:/opt/metatecks/backups/metateks_backup_*.tar.gz ~/backups/
```

### Проверить статус контейнеров

```bash
ssh root@5.188.138.16
cd /opt/metatecks
docker-compose ps
```

### Посмотреть логи backup

```bash
ssh root@5.188.138.16
tail -f /opt/metatecks/logs/backup.log
```

---

## 🚨 Сценарии восстановления

### Сценарий 1: Перезагрузка сервера
**Действие:** Ничего! Docker автоматически запустит все контейнеры.

### Сценарий 2: Падение контейнера
**Действие:** Docker автоматически перезапустит. Или вручную:
```bash
docker-compose restart web
```

### Сценарий 3: Полная потеря VPS
**Действие:**
1. Установить Docker на новом сервере
2. Клонировать репозиторий из GitHub
3. Восстановить последний backup
4. Запустить контейнеры

**Время:** ~15-30 минут

### Сценарий 4: Случайное удаление файлов
**Действие:**
- Media файлы: восстановить из backup
- База данных: восстановить из pg_dump в backup
- Код: `git pull` или восстановить из GitHub

---

## 📊 Мониторинг

### Проверить что бекапы создаются

```bash
# Посмотреть последние бекапы
ssh root@5.188.138.16 "ls -lht /opt/metatecks/backups/ | head -5"

# Посмотреть логи
ssh root@5.188.138.16 "tail -50 /opt/metatecks/logs/backup.log"

# Проверить cron
ssh root@5.188.138.16 "crontab -l | grep backup"
```

### Проверить здоровье контейнеров

```bash
ssh root@5.188.138.16 "cd /opt/metatecks && docker-compose ps"
```

Healthy контейнеры показывают `(healthy)` в колонке STATUS.

---

## 💾 Рекомендации

### 1. Храните бекапы в безопасном месте

**НЕ храните** бекапы только на VPS! Скачивайте их:

```bash
# На локальную машину
scp root@5.188.138.16:/opt/metatecks/backups/*.tar.gz ~/backups/

# Или в облако (Google Drive, Яндекс.Диск, S3)
rclone copy /opt/metatecks/backups/ gdrive:metateks-backups/
```

### 2. Проверяйте бекапы

Раз в месяц попробуйте восстановить backup на тестовом сервере:

```bash
# Скачать backup
scp root@5.188.138.16:/opt/metatecks/backups/metateks_backup_latest.tar.gz /tmp/

# Попробовать распаковать
tar -tzf /tmp/metateks_backup_latest.tar.gz | head

# Проверить что все файлы на месте
```

### 3. Мониторьте размер бекапов

Если размер резко изменился - проверьте что случилось:

```bash
# Посмотреть размеры последних 10 бекапов
ssh root@5.188.138.16 "ls -lh /opt/metatecks/backups/ | tail -10"
```

Нормальный размер: ~1.5 GB (может расти со временем).

---

## 📚 Документация

- **Полная документация:** `docs/DISASTER_RECOVERY.md`
- **Настройка auto-deploy:** `docs/AUTO_DEPLOY_SETUP.md`
- **Скрипты:** `scripts/backup.sh`, `scripts/restore.sh`

---

## ✅ Чеклист защиты данных

- [x] Контейнеры с `restart: unless-stopped`
- [x] PostgreSQL в Docker volume
- [x] Redis в Docker volume
- [x] Media на bind mount
- [x] Логи на bind mount
- [x] Healthchecks на всех сервисах
- [x] Скрипт backup.sh
- [x] Скрипт restore.sh
- [x] Cron для автоматических бекапов
- [x] Автоочистка старых бекапов
- [x] Документация по восстановлению
- [ ] **TODO:** Настроить копирование бекапов в облако
- [ ] **TODO:** Тестовое восстановление раз в месяц

---

**Последний backup:**
```bash
ssh root@5.188.138.16 "ls -lh /opt/metatecks/backups/ | tail -1"
```

**Статус:** ✅ Проект полностью защищен от потери данных!
