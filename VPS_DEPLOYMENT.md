# Инструкция по развертыванию на VPS

## Текущая ситуация
- ✅ Docker установлен
- ✅ Репозиторий склонирован в `/opt/metatecks`
- ✅ `.env.docker` создан
- ⚠️ Порт 80 занят системным Nginx

## Решение
Docker приложение слушает на localhost-only портах:
- `127.0.0.1:8080` - Docker Nginx
- `127.0.0.1:8001` - Django/Gunicorn

Системный Nginx проксирует запросы в Docker.

---

## Шаг 1: Обновите код на VPS

```bash
cd /opt/metatecks

# Подтяните последние изменения
git pull origin main

# Пересоздайте контейнеры с новыми портами
docker-compose down
docker-compose up -d
```

## Шаг 2: Проверьте что контейнеры запустились

```bash
# Проверьте статус
docker-compose ps

# Должно быть:
# metateks_db      healthy
# metateks_redis   healthy
# metateks_web     healthy
# metateks_nginx   up
# metateks_celery  up

# Проверьте логи
docker-compose logs -f web
# Ctrl+C чтобы выйти
```

## Шаг 3: Проверьте что приложение работает локально

```bash
# Проверьте что порт 8080 слушает
curl http://127.0.0.1:8080

# Должна вернуться HTML страница
```

## Шаг 4: Настройте системный Nginx

```bash
# Скопируйте конфигурацию
cp /opt/metatecks/docker/nginx/metateks-vps.conf /etc/nginx/sites-available/metateks

# Отредактируйте - замените your-domain.com на ваш домен
nano /etc/nginx/sites-available/metateks

# Создайте симлинк
ln -s /etc/nginx/sites-available/metateks /etc/nginx/sites-enabled/

# Проверьте конфигурацию
nginx -t

# Перезагрузите nginx
systemctl reload nginx
```

## Шаг 5: Проверьте доступность сайта

```bash
# Проверьте с сервера
curl http://your-domain.com

# Проверьте с вашего компьютера
# Откройте в браузере: http://your-domain.com
```

---

## Шаг 6 (опционально): Настройте HTTPS

```bash
# Установите certbot
apt install certbot python3-certbot-nginx -y

# Получите SSL сертификат
certbot --nginx -d your-domain.com -d www.your-domain.com

# Certbot автоматически настроит HTTPS
# Перезагрузите nginx
systemctl reload nginx
```

---

## Проверка работоспособности

### 1. Проверьте Docker контейнеры
```bash
docker-compose ps
# Все контейнеры должны быть UP и healthy
```

### 2. Проверьте логи
```bash
# Web логи
docker-compose logs web

# Nginx логи
docker-compose logs nginx

# Системный nginx логи
tail -f /var/log/nginx/metateks_access.log
```

### 3. Проверьте доступность
```bash
# Локально
curl http://127.0.0.1:8080

# Через домен
curl http://your-domain.com

# Статика
curl http://your-domain.com/static/admin/css/base.css

# Media
curl http://your-domain.com/media/
```

---

## Управление приложением

### Запуск
```bash
cd /opt/metatecks
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

### Просмотр логов
```bash
docker-compose logs -f
docker-compose logs -f web
docker-compose logs -f nginx
```

### Выполнение команд Django
```bash
# Создание миграций
docker-compose exec web python manage.py makemigrations

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сбор статики
docker-compose exec web python manage.py collectstatic --noinput

# Shell
docker-compose exec web python manage.py shell
```

### Обновление кода
```bash
cd /opt/metatecks

# Подтянуть изменения
git pull origin main

# Пересобрать образы (если изменился код Python)
docker-compose build --no-cache web celery

# Перезапустить
docker-compose up -d
```

---

## Резервное копирование

### База данных
```bash
# Создать бэкап
docker-compose exec db pg_dump -U metateks metateks > /opt/metatecks/backups/db_$(date +%Y%m%d_%H%M%S).sql

# Восстановить из бэкапа
docker-compose exec -T db psql -U metateks metateks < /opt/metatecks/backups/db_20241227_120000.sql
```

### Media файлы
```bash
# Создать архив
tar -czf /opt/metatecks/backups/media_$(date +%Y%m%d_%H%M%S).tar.gz /opt/metatecks/media/

# Восстановить
tar -xzf /opt/metatecks/backups/media_20241227_120000.tar.gz -C /opt/metatecks/
```

---

## Устранение проблем

### Контейнеры не запускаются
```bash
# Проверьте логи
docker-compose logs

# Проверьте что порты не заняты
netstat -tlnp | grep -E ":(8080|8001)"

# Пересоздайте контейнеры
docker-compose down
docker-compose up -d --force-recreate
```

### Ошибка "address already in use"
```bash
# Найдите что занимает порт
sudo lsof -i :8080
sudo lsof -i :8001

# Остановите конфликтующий процесс или измените порты в docker-compose.yml
```

### Nginx 502 Bad Gateway
```bash
# Проверьте что Docker nginx работает
curl http://127.0.0.1:8080

# Проверьте логи
docker-compose logs nginx
tail -f /var/log/nginx/metateks_error.log

# Перезапустите
docker-compose restart nginx
systemctl restart nginx
```

### Статика не загружается
```bash
# Проверьте что volume создан
docker volume ls | grep static

# Пересоберите статику
docker-compose exec web python manage.py collectstatic --noinput

# Проверьте права
ls -la /var/lib/docker/volumes/metateks_static_volume/_data/
```

---

## Структура портов

| Сервис | Порт в Docker | Порт на VPS | Доступ |
|--------|---------------|-------------|--------|
| PostgreSQL | 5432 | - | Только внутри Docker |
| Redis | 6379 | - | Только внутри Docker |
| Django/Gunicorn | 8000 | 127.0.0.1:8001 | Только localhost |
| Docker Nginx | 80 | 127.0.0.1:8080 | Только localhost |
| System Nginx | - | 0.0.0.0:80 | Публичный доступ |
| System Nginx (HTTPS) | - | 0.0.0.0:443 | Публичный доступ |

---

## Безопасность

1. **Никогда не открывайте порты БД наружу** - они доступны только внутри Docker
2. **Django работает только на localhost** - доступ через системный Nginx
3. **Обязательно настройте HTTPS** - Let's Encrypt бесплатный
4. **Регулярно делайте бэкапы** - БД и media файлы
5. **Обновляйте образы** - `docker-compose pull && docker-compose up -d`

---

## Мониторинг

```bash
# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f --tail=100

# Статус всех сервисов
docker-compose ps
systemctl status nginx
```

---

**Готово!** Приложение должно быть доступно по вашему домену.
