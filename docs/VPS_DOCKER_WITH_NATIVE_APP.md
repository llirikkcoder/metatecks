# Развертывание Docker проекта на VPS со старым проектом без Docker

## Обзор ситуации

На VPS уже работает **старый проект БЕЗ Docker** (классическое развертывание):
- Системный Nginx
- Системный PostgreSQL
- Python приложение в virtualenv
- Gunicorn/uWSGI

Нужно развернуть **новый проект В Docker**, не сломав старое приложение.

---

## 🔍 Шаг 1: Диагностика существующего окружения

### Подключиться к VPS

```bash
ssh username@your-vps-ip
```

### Проверить, что запущено

```bash
# Проверить запущенные процессы Python
ps aux | grep python

# Проверить Nginx
sudo systemctl status nginx

# Проверить PostgreSQL
sudo systemctl status postgresql

# Проверить Redis (если используется)
sudo systemctl status redis

# Проверить занятые порты
sudo netstat -tulpn | grep LISTEN
```

**Типичные занятые порты:**
- `80` - HTTP (системный Nginx)
- `443` - HTTPS (системный Nginx)
- `5432` - PostgreSQL
- `6379` - Redis (если установлен)
- `8000` или `8001` - Gunicorn/uWSGI

### Проверить структуру старого проекта

```bash
# Найти директорию проекта
ls -la /var/www/
ls -la /home/username/

# Проверить конфигурацию Nginx
sudo ls /etc/nginx/sites-enabled/
sudo cat /etc/nginx/sites-enabled/default

# Проверить systemd сервисы
sudo ls /etc/systemd/system/ | grep -E 'gunicorn|uwsgi|celery'
```

**Запишите:**
- Путь к старому проекту (например: `/var/www/old_project/`)
- Какие порты использует
- Какие домены настроены в Nginx
- Версии PostgreSQL, Python

---

## 📂 Структура на VPS

```
/
├── var/www/old_project/       # Старый проект БЕЗ Docker
│   ├── .git/
│   ├── venv/                  # Python virtualenv
│   ├── manage.py
│   └── ...
│
├── home/username/metateks/    # Новый проект В Docker
│   ├── .git/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── ...
│
├── etc/
│   ├── nginx/
│   │   ├── sites-available/
│   │   │   ├── old_project    # Конфигурация для старого
│   │   │   └── metateks       # Новая конфигурация
│   │   └── sites-enabled/
│   │       ├── old_project -> ../sites-available/old_project
│   │       └── metateks -> ../sites-available/metateks
│   │
│   └── systemd/system/
│       ├── old_project.service    # Systemd для старого
│       └── (Docker не нужен - управляется docker-compose)
```

---

## 📋 Пошаговая инструкция

### Шаг 1: Установить Docker (если еще не установлен)

```bash
# Обновить пакеты
sudo apt update

# Установить Docker
sudo apt install -y docker.io docker-compose

# Добавить текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиниться или выполнить
newgrp docker

# Проверить установку
docker --version
docker-compose --version
```

---

### Шаг 2: Создать директорию для нового проекта

```bash
# Создать директорию
mkdir -p ~/metateks
cd ~/metateks
```

**⚠️ НЕ создавайте внутри `/var/www/old_project/`!**

---

### Шаг 3: Клонировать Git репозиторий

```bash
# Клонировать
git clone https://github.com/your-username/metateks.git .

# Проверить
ls -la
```

---

### Шаг 4: Настроить docker-compose.yml

**ВАЖНО:** Все порты Docker контейнеров должны быть **внутренними** (не публиковаться на хосте), кроме одного порта для доступа через Nginx.

```yaml
services:
  # База данных PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: metateks_db
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-metateks}
      POSTGRES_USER: ${POSTGRES_USER:-metateks}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-metateks_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # ⚠️ НЕ публикуем порт 5432 - старый PostgreSQL его использует!
    # ports:
    #   - "5432:5432"  # ← ЗАКОММЕНТИРОВАНО!
    networks:
      - metateks_network
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    container_name: metateks_redis
    volumes:
      - redis_data:/data
    # ⚠️ НЕ публикуем порт 6379
    networks:
      - metateks_network
    restart: unless-stopped

  # Django приложение
  web:
    build: .
    container_name: metateks_web
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 main.wsgi:application
    volumes:
      - static_volume:/app/static
      - ./media:/app/media
      - ./logs:/app/logs
    # ⚠️ Публикуем ВНУТРЕННИЙ порт для Nginx
    ports:
      - "127.0.0.1:8001:8000"  # ← Только localhost:8001!
    env_file:
      - .env.docker
    depends_on:
      - db
      - redis
    networks:
      - metateks_network
    restart: unless-stopped

  # Celery Worker
  celery:
    build: .
    container_name: metateks_celery
    command: celery -A main worker --loglevel=info
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs
    env_file:
      - .env.docker
    depends_on:
      - db
      - redis
    networks:
      - metateks_network
    restart: unless-stopped

  # ⚠️ НЕ запускаем Nginx в Docker!
  # Будем использовать системный Nginx как reverse proxy
  # nginx:
  #   ...

volumes:
  postgres_data:
    name: metateks_postgres_data
  redis_data:
    name: metateks_redis_data
  static_volume:
    name: metateks_static_volume

networks:
  metateks_network:
    name: metateks_network
    driver: bridge
```

**Ключевые изменения:**
- ✅ `ports: - "127.0.0.1:8001:8000"` - публикуем ТОЛЬКО на localhost
- ❌ НЕ публикуем PostgreSQL (5432) - старый использует
- ❌ НЕ публикуем Redis (6379)
- ❌ НЕ запускаем Nginx в Docker - используем системный

---

### Шаг 5: Настроить .env.docker

```bash
cp .env.example .env.docker
nano .env.docker
```

**Содержимое `.env.docker`:**

```env
# Django
DEBUG=False
SECRET_KEY=НОВЫЙ_УНИКАЛЬНЫЙ_КЛЮЧ_СГЕНЕРИРУЙТЕ
ALLOWED_HOSTS=new.yoursite.com,yoursite.com

# База данных (ОТДЕЛЬНАЯ для Docker!)
POSTGRES_DB=metateks
POSTGRES_USER=metateks
POSTGRES_PASSWORD=СИЛЬНЫЙ_ПАРОЛЬ

# Хост базы данных - ИМЯ Docker сервиса!
DATABASE_HOST=db  # ← НЕ localhost! Имя сервиса из docker-compose.yml
DATABASE_PORT=5432

# Redis
REDIS_HOST=redis  # ← Имя сервиса
REDIS_PORT=6379
```

---

### Шаг 6: Собрать и запустить Docker контейнеры

```bash
cd ~/metateks

# Собрать образы
docker-compose build

# Запустить контейнеры
docker-compose up -d

# Проверить статус
docker-compose ps
```

**Ожидаемый результат:**

```
NAME              STATUS
metateks_db       Up (healthy)
metateks_redis    Up (healthy)
metateks_web      Up
metateks_celery   Up
```

---

### Шаг 7: Проверить, что порты не конфликтуют

```bash
# Проверить порты
sudo netstat -tulpn | grep LISTEN
```

**Должны увидеть:**
- `0.0.0.0:80` - системный Nginx (старый проект)
- `0.0.0.0:443` - системный Nginx SSL (старый проект)
- `0.0.0.0:5432` - системный PostgreSQL (старый проект)
- `127.0.0.1:8001` - Docker Gunicorn (НОВЫЙ проект) ← только localhost!

**✅ Всё хорошо, если:**
- Старый PostgreSQL на 5432 (системный)
- Новый PostgreSQL внутри Docker (не виден снаружи)
- Новый Django доступен ТОЛЬКО на localhost:8001

---

### Шаг 8: Выполнить миграции и создать суперпользователя

```bash
# Миграции
docker-compose exec web python manage.py migrate

# Суперпользователь
docker-compose exec web python manage.py createsuperuser

# Собрать статику
docker-compose exec web python manage.py collectstatic --noinput
```

---

### Шаг 9: Настроить системный Nginx как reverse proxy

**Создать конфигурацию для нового проекта:**

```bash
sudo nano /etc/nginx/sites-available/metateks
```

**Вариант 1: Отдельный поддомен**

```nginx
# /etc/nginx/sites-available/metateks

upstream metateks_backend {
    server 127.0.0.1:8001;  # Docker контейнер на localhost:8001
}

server {
    listen 80;
    server_name new.yoursite.com metateks.yoursite.com;

    # Статические файлы из Docker volume
    location /static/ {
        alias /var/lib/docker/volumes/metateks_static_volume/_data/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media файлы из bind mount
    location /media/ {
        alias /home/username/metateks/media/;
        expires 7d;
    }

    # Прокси на Django в Docker
    location / {
        proxy_pass http://metateks_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Логи
    access_log /var/log/nginx/metateks_access.log;
    error_log /var/log/nginx/metateks_error.log;
}
```

**Вариант 2: Отдельный путь на том же домене**

```nginx
# Добавить в существующую конфигурацию старого проекта

# В файле /etc/nginx/sites-available/old_project добавить:

upstream metateks_backend {
    server 127.0.0.1:8001;
}

# Внутри основного server { ... } блока добавить:

    # Новый проект на /new/
    location /new/ {
        proxy_pass http://metateks_backend/;  # ← Обратите внимание на / в конце!
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /new/static/ {
        alias /var/lib/docker/volumes/metateks_static_volume/_data/;
    }

    location /new/media/ {
        alias /home/username/metateks/media/;
    }
```

**Активировать конфигурацию:**

```bash
# Создать символическую ссылку (только для Варианта 1)
sudo ln -s /etc/nginx/sites-available/metateks /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

# Если OK, перезагрузить Nginx
sudo systemctl reload nginx
```

---

### Шаг 10: Настроить DNS (для поддомена)

Если используете поддомен `new.yoursite.com`:

**В панели управления доменом:**

```
Type  Name   Value           TTL
A     new    VPS_IP_ADDRESS  3600
```

Подождите 5-10 минут для распространения DNS.

---

### Шаг 11: Проверить работу

**Откройте в браузере:**

- Старый проект: `http://yoursite.com/` ✅
- Новый проект: `http://new.yoursite.com/` ✅

Или если используете путь:
- Старый: `http://yoursite.com/`
- Новый: `http://yoursite.com/new/`

**Проверьте админку:**
- `http://new.yoursite.com/admin/`

---

### Шаг 12: Настроить SSL/HTTPS

```bash
# Установить Certbot (если еще нет)
sudo apt install certbot python3-certbot-nginx

# Получить SSL сертификат для нового поддомена
sudo certbot --nginx -d new.yoursite.com

# Certbot автоматически настроит HTTPS!
```

**После этого:**
- `https://yoursite.com/` - старый проект (SSL)
- `https://new.yoursite.com/` - новый проект (SSL)

---

## 🔒 Изоляция и безопасность

### Что изолировано:

| Ресурс | Старый проект | Новый проект |
|--------|---------------|--------------|
| **PostgreSQL** | Системный (порт 5432) | Docker (внутренний) |
| **База данных** | `old_db` | `metateks` (отдельная!) |
| **Redis** | Системный (порт 6379) | Docker (внутренний) |
| **Python** | virtualenv `/var/www/old_project/venv/` | Docker образ |
| **Статика** | `/var/www/old_project/static/` | Docker volume |
| **Media** | `/var/www/old_project/media/` | `~/metateks/media/` |
| **Логи** | `/var/log/old_project/` | `~/metateks/logs/` |
| **Код** | `/var/www/old_project/` | `~/metateks/` |

### Порты:

- `80, 443` - Системный Nginx (обслуживает ОБА проекта)
- `5432` - Системный PostgreSQL (ТОЛЬКО старый проект)
- `6379` - Системный Redis (ТОЛЬКО старый проект, если есть)
- `8001` - Docker Gunicorn (ТОЛЬКО localhost, через Nginx)
- Docker PostgreSQL/Redis - внутренние (не видны снаружи)

---

## 📊 Управление проектами

### Старый проект (БЕЗ Docker)

```bash
# Перейти в директорию
cd /var/www/old_project/

# Активировать virtualenv
source venv/bin/activate

# Django команды
python manage.py migrate
python manage.py collectstatic

# Перезапустить Gunicorn (если используется systemd)
sudo systemctl restart old_project
sudo systemctl status old_project

# Деактивировать virtualenv
deactivate
```

### Новый проект (В Docker)

```bash
# Перейти в директорию
cd ~/metateks/

# Docker Compose команды
docker-compose ps
docker-compose logs -f web
docker-compose restart web
docker-compose down
docker-compose up -d

# Django команды внутри контейнера
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py createsuperuser
```

---

## 🔄 Обновление проектов

### Старый проект

```bash
cd /var/www/old_project/
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart old_project
deactivate
```

### Новый проект

```bash
cd ~/metateks/
git pull
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

**⚠️ Обновления независимы - не влияют друг на друга!**

---

## 🛡️ Безопасность

### Firewall (UFW)

```bash
# Разрешить SSH
sudo ufw allow 22/tcp

# Разрешить HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# ⚠️ НЕ открывайте 5432, 6379, 8001 - они должны быть внутренними!

# Включить firewall
sudo ufw enable

# Проверить
sudo ufw status
```

### Проверить открытые порты

```bash
# Порты, доступные снаружи
sudo netstat -tulpn | grep -E ':80|:443|:5432|:6379|:8001'
```

**Должно быть:**
- ✅ `0.0.0.0:80` и `0.0.0.0:443` - Nginx
- ✅ `127.0.0.1:8001` - Docker (ТОЛЬКО localhost!)
- ❌ `0.0.0.0:5432` - PostgreSQL НЕ должен быть доступен извне!
- ❌ `0.0.0.0:6379` - Redis НЕ должен быть доступен извне!

**Если PostgreSQL/Redis доступны извне:**

```bash
# Настроить PostgreSQL слушать только localhost
sudo nano /etc/postgresql/15/main/postgresql.conf

# Изменить:
listen_addresses = 'localhost'  # было '*'

# Перезапустить
sudo systemctl restart postgresql
```

---

## 🗄️ Резервное копирование

### Backup старого проекта (системная БД)

```bash
# PostgreSQL
sudo -u postgres pg_dump old_db > /home/username/backups/old_$(date +%Y%m%d).sql

# Файлы
tar -czf /home/username/backups/old_files_$(date +%Y%m%d).tar.gz /var/www/old_project/media/
```

### Backup нового проекта (Docker)

```bash
# PostgreSQL из Docker
docker exec metateks_db pg_dump -U metateks metateks > /home/username/backups/metateks_$(date +%Y%m%d).sql

# Docker volumes
docker run --rm \
  -v metateks_postgres_data:/data \
  -v /home/username/backups:/backup \
  alpine tar czf /backup/metateks_postgres_$(date +%Y%m%d).tar.gz /data

# Файлы media
tar -czf /home/username/backups/metateks_media_$(date +%Y%m%d).tar.gz ~/metateks/media/
```

### Автоматический backup (cron)

```bash
crontab -e
```

```cron
# Backup старого проекта каждый день в 2:00
0 2 * * * sudo -u postgres pg_dump old_db > /home/username/backups/old_$(date +\%Y\%m\%d).sql

# Backup нового проекта каждый день в 3:00
0 3 * * * docker exec metateks_db pg_dump -U metateks metateks > /home/username/backups/metateks_$(date +\%Y\%m\%d).sql
```

---

## 🚨 Решение проблем

### Проблема: Nginx не может прочитать Docker volume

**Ошибка в логах:**
```
Permission denied: /var/lib/docker/volumes/metateks_static_volume/_data/
```

**Решение:**

```bash
# Дать Nginx доступ к Docker volumes
sudo usermod -aG docker www-data
sudo systemctl restart nginx

# Или скопировать статику в доступную директорию
docker-compose exec web python manage.py collectstatic --noinput
sudo cp -r /var/lib/docker/volumes/metateks_static_volume/_data/* /var/www/metateks_static/
sudo chown -R www-data:www-data /var/www/metateks_static/

# В Nginx использовать:
# location /static/ {
#     alias /var/www/metateks_static/;
# }
```

---

### Проблема: 502 Bad Gateway

**Причины:**
1. Docker контейнер не запущен
2. Неправильный порт в Nginx
3. Firewall блокирует localhost

**Решение:**

```bash
# 1. Проверить контейнер
docker-compose ps
docker-compose logs web

# 2. Проверить порт
curl http://127.0.0.1:8001/
# Должен вернуть HTML

# 3. Проверить Nginx upstream
sudo nano /etc/nginx/sites-available/metateks
# Убедитесь: server 127.0.0.1:8001;

# Перезагрузить Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

### Проблема: Конфликт PostgreSQL портов

**Ошибка:**
```
Error: bind: address already in use (port 5432)
```

**Решение:**
Убедитесь, что в `docker-compose.yml` **НЕТ** публикации порта PostgreSQL:

```yaml
db:
  ports:
    # - "5432:5432"  # ← Должно быть закомментировано!
```

---

### Проблема: Django не может подключиться к БД

**Ошибка:**
```
django.db.utils.OperationalError: could not connect to server: Connection refused
```

**Решение:**
В `.env.docker` используйте **имя сервиса Docker**, НЕ `localhost`:

```env
DATABASE_HOST=db  # ← НЕ localhost!
DATABASE_PORT=5432
```

---

## 📈 Мониторинг

### Проверить ресурсы

```bash
# CPU и память Docker контейнеров
docker stats

# Процессы старого проекта
ps aux | grep gunicorn
ps aux | grep python

# Общие ресурсы VPS
htop
free -h
df -h
```

### Логи

```bash
# Системный Nginx (оба проекта)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/metateks_access.log

# Старый проект
sudo journalctl -u old_project -f

# Новый проект (Docker)
docker-compose logs -f web
docker-compose logs -f celery
```

---

## ✅ Итоговый чеклист

- [ ] Проверили что запущено на VPS (Nginx, PostgreSQL, Python)
- [ ] Записали занятые порты и пути
- [ ] Установили Docker и Docker Compose
- [ ] Создали отдельную директорию `~/metateks/`
- [ ] Клонировали Git репозиторий
- [ ] Настроили `docker-compose.yml` (порты ТОЛЬКО localhost!)
- [ ] Настроили `.env.docker` (DATABASE_HOST=db)
- [ ] Запустили `docker-compose up -d`
- [ ] Проверили, что контейнеры работают
- [ ] Выполнили миграции и создали суперпользователя
- [ ] Настроили системный Nginx как reverse proxy
- [ ] Проверили доступ к обоим проектам
- [ ] Настроили SSL/HTTPS
- [ ] Настроили firewall
- [ ] Настроили резервное копирование
- [ ] Убедились, что старый проект работает как раньше ✅

---

## 🎉 Результат

✅ **Два проекта на одном VPS:**
- Старый: классическое развертывание (Nginx + systemd + virtualenv)
- Новый: Docker контейнеры
- Полная изоляция
- Один системный Nginx обслуживает оба проекта
- Независимые обновления и управление

✅ **Безопасность:**
- БД и Redis в Docker не доступны извне
- Firewall настроен
- SSL сертификаты

✅ **Надежность:**
- Старый проект работает как раньше
- Новый проект изолирован в Docker
- Автоматические backup'ы

---

**Успешного развертывания! 🚀**
