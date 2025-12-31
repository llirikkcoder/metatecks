# Disaster Recovery - Восстановление проекта

Этот документ описывает как полностью восстановить проект после сбоя.

## Что защищено от потери

### Автоматически сохраняется:

1. **База данных PostgreSQL** → Docker volume `metateks_postgres_data`
2. **Redis данные** → Docker volume `metateks_redis_data`
3. **Static файлы** → Docker volume `metateks_static_volume`
4. **Media файлы** → `/opt/metatecks/media/` (bind mount)
5. **Логи приложения** → `/opt/metatecks/logs/` (bind mount)
6. **Исходный код** → Git репозиторий на GitHub

### Автоматический перезапуск:

Все контейнеры имеют `restart: unless-stopped` - они автоматически перезапускаются:
- После сбоя контейнера
- После перезагрузки сервера
- После обновления Docker

---

## Сценарий 1: Перезагрузка сервера

**Проблема:** VPS перезагрузился

**Решение:** Ничего делать не нужно!

Docker автоматически:
1. Запустит все контейнеры с `restart: unless-stopped`
2. Восстановит подключения к volumes
3. Выполнит healthchecks
4. Nginx дождется пока web станет healthy

**Проверка после перезагрузки:**

```bash
# Подключиться к VPS
ssh root@5.188.138.16

# Проверить статус контейнеров
cd /opt/metatecks
docker-compose ps

# Должны быть все Up и healthy
```

---

## Сценарий 2: Падение контейнера

**Проблема:** Контейнер упал (crash, OOM, ошибка)

**Решение:** Docker автоматически перезапустит контейнер

**Ручной перезапуск (если нужно):**

```bash
# Перезапустить конкретный сервис
docker-compose restart web

# Или все сервисы
docker-compose restart

# Посмотреть логи
docker-compose logs -f web
```

---

## Сценарий 3: Полная потеря проекта

**Проблема:** Удалили `/opt/metatecks` или весь VPS

**Решение:** Восстановить из backup

### Шаг 1: Установить зависимости на новом сервере

```bash
# Установить Docker
curl -fsSL https://get.docker.com | sh

# Установить Docker Compose
apt-get install docker-compose-plugin

# Клонировать репозиторий
cd /opt
git clone git@github.com:llirikkcoder/metatecks.git
cd metatecks
```

### Шаг 2: Восстановить из последнего backup

```bash
# Посмотреть доступные бекапы
ls -lh backups/

# Восстановить из бекапа
./scripts/restore.sh backups/metateks_backup_YYYYMMDD_HHMMSS.tar.gz

# Запустить контейнеры
docker-compose up -d

# Проверить статус
docker-compose ps
```

### Шаг 3: Настроить nginx (если нужно)

```bash
# Скопировать конфиги
sudo cp conf/vps/metateks-ip.conf /etc/nginx/sites-available/
sudo cp conf/vps/metateks-docker.conf /etc/nginx/sites-available/

# Создать симлинки
sudo ln -sf /etc/nginx/sites-available/metateks-ip.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/metateks-docker.conf /etc/nginx/sites-enabled/

# Проверить и перезагрузить
sudo nginx -t
sudo systemctl reload nginx
```

---

## Сценарий 4: Потеря Docker volumes

**Проблема:** Удалили Docker volumes (`docker volume rm metateks_postgres_data`)

**Решение:** Восстановить из backup

```bash
# Остановить контейнеры
docker-compose down

# Удалить старые volumes (если есть)
docker volume rm metateks_postgres_data metateks_redis_data metateks_static_volume

# Восстановить из бекапа
./scripts/restore.sh backups/metateks_backup_LATEST.tar.gz

# Запустить контейнеры (volumes пересоздадутся)
docker-compose up -d
```

---

## Создание backup вручную

```bash
# На VPS
cd /opt/metatecks

# Создать backup
./scripts/backup.sh

# Backup будет сохранен в:
# /opt/metatecks/backups/metateks_backup_YYYYMMDD_HHMMSS.tar.gz
```

---

## Автоматические backup (рекомендуется)

### Настроить cron для ежедневных бекапов

```bash
# Отредактировать crontab
crontab -e

# Добавить строку (backup каждый день в 3:00)
0 3 * * * /opt/metatecks/scripts/backup.sh >> /opt/metatecks/logs/backup.log 2>&1
```

Старые бекапы (>30 дней) автоматически удаляются скриптом.

---

## Копирование backup в безопасное место

**Важно!** Храните бекапы не только на VPS, но и в другом месте.

### Вариант 1: Скачать на локальную машину

```bash
# С локальной машины
scp root@5.188.138.16:/opt/metatecks/backups/metateks_backup_*.tar.gz ~/backups/
```

### Вариант 2: Загрузить в облако (S3, Яндекс.Облако, Google Drive)

```bash
# Установить rclone на VPS
curl https://rclone.org/install.sh | sudo bash

# Настроить remote (например, Google Drive)
rclone config

# Копировать бекапы в облако
rclone copy /opt/metatecks/backups/ gdrive:metateks-backups/
```

### Вариант 3: Отправить на другой сервер

```bash
# С VPS на backup-сервер
rsync -avz /opt/metatecks/backups/ backup-server:/backups/metateks/
```

---

## Проверка целостности данных

### Проверить базу данных

```bash
# Подключиться к PostgreSQL
docker-compose exec db psql -U metateks metateks

# Посмотреть количество записей
SELECT COUNT(*) FROM catalog_product;
SELECT COUNT(*) FROM addresses_city;

# Выйти
\q
```

### Проверить media файлы

```bash
# Посмотреть размер директории
du -sh /opt/metatecks/media/

# Посмотреть количество файлов
find /opt/metatecks/media/ -type f | wc -l
```

### Проверить Docker volumes

```bash
# Список volumes
docker volume ls | grep metateks

# Размер volumes
docker system df -v | grep metateks
```

---

## Мониторинг работоспособности

### Автоматические healthchecks

Docker автоматически проверяет:
- PostgreSQL: `pg_isready` каждые 10 сек
- Redis: `redis-cli ping` каждые 10 сек
- Web: `curl /health/` каждые 30 сек (после 180 сек start_period)

```bash
# Посмотреть health status
docker-compose ps

# Healthy контейнеры показывают (healthy) в колонке STATUS
```

### Ручная проверка

```bash
# Проверить доступность
curl -I http://127.0.0.1:8080/
curl -I https://metateks-admin.vinodesign.ru/

# Проверить логи
docker-compose logs --tail=50 web
docker-compose logs --tail=50 nginx

# Проверить использование ресурсов
docker stats --no-stream
```

---

## Контакты для экстренных ситуаций

- **GitHub репозиторий**: https://github.com/llirikkcoder/metatecks
- **Документация**: `/opt/metatecks/docs/`
- **Логи**: `/opt/metatecks/logs/`
- **Backups**: `/opt/metatecks/backups/`

---

## Чеклист восстановления

- [ ] Убедиться что Docker установлен
- [ ] Клонировать репозиторий из GitHub
- [ ] Восстановить backup (если есть)
- [ ] Создать `.env.docker` с правильными настройками
- [ ] Запустить контейнеры: `docker-compose up -d`
- [ ] Дождаться healthy статуса всех контейнеров
- [ ] Настроить nginx (если на новом сервере)
- [ ] Проверить доступность сайта
- [ ] Проверить логи на ошибки
- [ ] Создать новый backup для проверки

**Время полного восстановления:** ~15-30 минут (зависит от размера backup)
