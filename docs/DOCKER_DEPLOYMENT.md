# Развертывание Docker приложения на новом сервере

## 📋 Обзор

Проект использует **stateless** архитектуру Docker контейнеров:
- Код приложения находится **внутри Docker образа**
- Данные хранятся отдельно: volumes + media/logs папки
- Легко переносится между серверами

---

## 🚀 План переезда

```
Старый сервер                          Новый сервер
┌─────────────────────┐               ┌─────────────────────┐
│ Docker образы       │   ───────>    │ Docker образы       │
│ ├─ web (Django)     │   copy images │ ├─ web (Django)     │
│ ├─ celery           │               │ ├─ celery           │
│ └─ nginx (alpine)   │               │ └─ nginx (alpine)   │
└─────────────────────┘               └─────────────────────┘
        │                                     │
        ▼                                     ▼
┌─────────────────────┐               ┌─────────────────────┐
│ Данные              │   ───────>    │ Данные              │
│ ├─ postgres_volume  │   backup/     │ ├─ postgres_volume  │
│ ├─ redis_volume     │   restore     │ ├─ redis_volume     │
│ ├─ static_volume    │               │ ├─ static_volume    │
│ ├─ media/           │               │ ├─ media/           │
│ └─ logs/            │               │ └─ logs/            │
└─────────────────────┘               └─────────────────────┘
        │                                     │
        ▼                                     ▼
┌─────────────────────┐               ┌─────────────────────┐
│ Конфигурация        │   ───────>    │ Конфигурация        │
│ ├─ .env.docker      │   copy        │ ├─ .env.docker      │
│ ├─ docker-compose.yml│              │ ├─ docker-compose.yml│
│ └─ docker/nginx/    │               │ └─ docker/nginx/    │
└─────────────────────┘               └─────────────────────┘
```

---

## 📦 Способ 1: Полный перенос (рекомендуется для продакшена)

### Шаг 1: Подготовка на исходном сервере

#### 1.1. Сохраните Docker образы

```bash
# На исходном сервере
docker save metatecks-web metatecks-celery | gzip > metateks_images.tar.gz

ls -lh metateks_images.tar.gz
# Примерный размер: 500 MB - 2 GB
```

#### 1.2. Бэкап PostgreSQL

```bash
# Создайте дамп БД
docker exec metateks_db pg_dump -U metateks -d metateks -F c -f /tmp/db_backup.backup
docker cp metateks_db:/tmp/db_backup.backup ./db_backup_$(date +%Y%m%d).backup

# Проверьте размер
ls -lh db_backup_*.backup
```

#### 1.3. Бэкап Redis (опционально)

```bash
# Redis кэш можно не бэкапить (восстановится самостоятельно)
# Но если нужно:
docker exec metateks_redis redis-cli BGSAVE
docker cp metateks_redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

#### 1.4. Бэкап статических файлов

```bash
# Статика собрана в volume, создадим tar архив
docker run --rm \
  -v metateks_static_volume:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/static_backup.tar.gz -C /data .
```

#### 1.5. Бэкап медиа-файлов

```bash
# Просто упакуйте папку media
tar czf media_backup_$(date +%Y%m%d).tar.gz media/

# Или используя rsync для синхронизации:
rsync -avz media/ user@new-server:/path/to/project/media/
```

#### 1.6. Бэкап конфигурации

```bash
# Создайте архив конфигурации
tar czf config_backup_$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env.docker \
  docker/
```

#### 1.7. Соберите все файлы

```bash
mkdir -p migrate_$(date +%Y%m%d)
mv metateks_images.tar.gz migrate_*/
mv db_backup_*.backup migrate_*/
mv redis_backup_*.rdb migrate_*/
mv static_backup.tar.gz migrate_*/
mv media_backup.tar.gz migrate_*/
mv config_backup.tar.gz migrate_*/

ls -lh migrate_*/
```

---

### Шаг 2: Передача файлов на новый сервер

#### 2.1. Через SCP

```bash
# Копирование на новый сервер
scp -r migrate_20241225/ user@new-server:/tmp/
```

#### 2.2. Через rsync (быстрее для больших файлов)

```bash
rsync -avz --progress migrate_20241225/ user@new-server:/tmp/
```

#### 2.3. Если исходный сервер недоступен

Используйте созданные архивы с предыдущего места.

---

### Шаг 3: Развертывание на новом сервере

#### 3.1. Установите зависимости

```bash
# На новом сервере
apt update
apt install -y docker.io docker-compose

# Проверьте версии
docker --version
docker-compose --version
```

#### 3.2. Создайте структуру проекта

```bash
# Распакуйте конфигурацию
cd /opt/metateks  # или любая другая директория
tar xzf /tmp/migrate_20241225/config_backup.tar.gz

# Создайте необходимые папки
mkdir -p media logs static
chmod 755 media logs static
```

#### 3.3. Загрузите Docker образы

```bash
# Загрузите образы
docker load < /tmp/migrate_20241225/metateks_images.tar.gz

# Проверьте
docker images | grep metateks
```

#### 3.4. Создайте volumes

```bash
docker volume create metateks_postgres_data
docker volume create metateks_redis_data
docker volume create metateks_static_volume
```

#### 3.5. Восстановите статику

```bash
docker run --rm \
  -v metateks_static_volume:/data \
  -v /tmp/migrate_20241225:/backup \
  alpine sh -c "cd /data && tar xzf /backup/static_backup.tar.gz"
```

#### 3.6. Восстановите медиа

```bash
tar xzf /tmp/migrate_20241225/media_backup.tar.gz
```

#### 3.7. Запустите контейнеры

```bash
# Сначала БД
docker-compose up -d db redis

# Дождитесь запуска
sleep 10
docker-compose ps

# Восстановите БД
docker cp /tmp/migrate_20241225/db_backup_*.backup metateks_db:/tmp/
docker exec metateks_db pg_restore \
  -U metateks \
  -d metateks \
  --clean \
  --if-exists \
  /tmp/db_backup.backup

# Запустите все сервисы
docker-compose up -d
```

#### 3.8. Проверьте работоспособность

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs -f web

# Тестовый запрос
curl http://localhost/
curl http://localhost/admin/
```

---

## 🔄 Способ 2: Перенос через Git (рекомендуется для разработки)

Этот способ подходит, если вы хотите перенести **код + конфигурацию**, но данные (БД, медиа) перенесете отдельно.

### Шаг 1: На новом сервере клонируйте репозиторий

```bash
git clone <repository-url> metateks
cd metateks
```

### Шаг 2: Настройте переменные окружения

```bash
# Скопируйте пример
cp .env.docker .env

# Отредактируйте при необходимости
nano .env
```

### Шаг 3: Соберите Docker образы

```bash
docker-compose build
```

### Шаг 4: Запустите контейнеры

```bash
docker-compose up -d
```

### Шаг 5: Перенесите данные (из Способа 1, шаги 1.2-1.5)

---

## 💻 Способ 3: Локальный компьютер → Сервер (деплой)

### Подготовка на локальном компьютере

```bash
# 1. Убедитесь, что все работает
docker-compose ps

# 2. Создайте .env для продакшена
cp .env.docker .env.production
nano .env.production
# Измените:
# - SECRET_KEY (сгенерируйте новый)
# - DEBUG=False
# - ALLOWED_HOSTS=ваш-домен.ru
# - DATABASE_URL (если используете внешний PostgreSQL)

# 3. Соберите образы для продакшена
docker-compose -f docker-compose.yml build
```

### Передача на сервер

```bash
# Сохраните образы
docker save metatecks-web metateks-celery | gzip > metateks_images.tar.gz

# Отправьте на сервер
scp metateks_images.tar.gz .env.production user@server:/opt/metateks/
scp -r docker/ docker-compose.yml user@server:/opt/metateks/
```

### На сервере

```bash
# Загрузите образы
docker load < metateks_images.tar.gz

# Переименуйте .env
mv .env.production .env.docker

# Запустите
docker-compose up -d
```

---

## 🌐 Способ 4: Server → Локальный компьютер (для разработки)

Это подходит, если вы хотите локально продублировать продакшн среду.

### На сервере

```bash
# 1. Создайте дамп данных
docker exec metateks_db pg_dump -U metateks -d metateks -F c > db_backup.backup

# 2. Скачайте медиа
tar czf media_backup.tar.gz media/

# 3. Скачайте конфигурацию
tar czf config.tar.gz docker-compose.yml .env.docker docker/

# 4. Отправьте все на локальный компьютер
scp db_backup.backup media_backup.tar.gz config.tar.gz user@local:~/metateks/
```

### На локальном компьютере

```bash
cd ~/metateks

# 1. Распакуйте конфигурацию
tar xzf config.tar.gz

# 2. Распакуйте медиа
tar xzf media_backup.tar.gz

# 3. Соберите образы
docker-compose build

# 4. Запустите БД
docker-compose up -d db redis
sleep 10

# 5. Восстановите БД
docker cp db_backup.backup metateks_db:/tmp/
docker exec metateks_db pg_restore -U metateks -d metateks --clean /tmp/db_backup.backup

# 6. Запустите все
docker-compose up -d

# 7. Проверьте
docker-compose ps
curl http://localhost/
```

---

## 🔧 Способ 5: Только данные (миграция)

Используется, когда Docker образы уже есть на новом сервере.

```bash
# На исходном сервере
docker exec metateks_db pg_dump -U metateks -d metateks -F c > db.backup
tar czf media.tar.gz media/

# Передача
scp db.backup media.tar.gz user@new-server:/tmp/

# На новом сервере
docker cp /tmp/db.backup metateks_db:/tmp/
docker exec metateks_db pg_restore -U metateks -d metateks --clean /tmp/db.backup
tar xzf /tmp/media.tar.gz -C /opt/metateks/

# Перезапустите контейнеры
docker-compose restart web celery
```

---

## 📝 Проверочный список после переезда

- [ ] Все контейнеры запущены (`docker-compose ps`)
- [ ] Сайт доступен (`curl http://domain/`)
- [ ] Админка работает (`curl http://domain/admin/`)
- [ ] Медиа-файлы отображаются
- [ ] База данных содержит данные
- [ ] Логи пишутся (`ls logs/`)
- [ ] Celery работает (`docker-compose logs celery`)
- [ ] 1С интеграция настроена (если нужно)

---

## ⚠️ Распространенные проблемы

### Проблема: Порт уже занят

```bash
# Проверьте что занимает порт
netstat -tulpn | grep :80

# Измените порт в docker-compose.yml
ports:
  - "8080:80"  # вместо "80:80"
```

### Проблема: Неверные права доступа

```bash
# На папку media
chown -R www-data:www-data media/
chmod -R 755 media/

# На .env файл
chmod 600 .env.docker
```

### Проблема: Контейнеры не видят друг друга

```bash
# Проверьте сеть
docker network ls
docker network inspect metateks_metateks_network

# Пересоздайте сеть
docker-compose down
docker-compose up -d
```

### Проблема: База данных не восстанавливается

```bash
# Очистите и начните заново
docker-compose down
docker volume rm metateks_postgres_data
docker-compose up -d db redis
# Затем восстановите снова
```

---

## 🎯 Рекомендации

### Для продакшена

1. **Используйте Docker Registry** вместо передачи образов:
   ```bash
   # На сервере сборки
   docker tag metateks-web registry.example.com/metateks-web:latest
   docker push registry.example.com/metateks-web:latest

   # на целевом сервере
   docker pull registry.example.com/metateks-web:latest
   ```

2. **Автоматизируйте бэкапы**:
   ```bash
   # В cron
   0 2 * * * /opt/metatecks/scripts/backup.sh
   ```

3. **Используйте docker-compose.override.yml** для локальных настроек

### Для разработки

1. **Используйте Git** для синхронизации кода
2. **Не переносите** данные между средами (используйте fixtures)
3. **Разные .env файлы**: `.env.local` и `.env.production`

---

## 📚 Полезные команды

```bash
# Посмотреть volumes
docker volume ls | grep metateks

# Резервный volume
docker run --rm \
  -v metateks_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Восстановить volume
docker run --rm \
  -v metateks_postgres_data:/data \
  -v $(pwd):/backup \
  alpine sh -c "rm -rf /data/* && tar xzf /backup/postgres_backup.tar.gz -C /data"

# Размер volumes
docker system df -v | grep metateks

# Очистка неиспользуемых образов
docker image prune -a

# Полная очистка (осторожно!)
docker-compose down -v
docker system prune -a --volumes
```

---

## 🚀 Быстрый чек-лист переезда

### Исходный сервер:
```bash
1. docker save ... > images.tar.gz
2. docker exec ... pg_dump ... > db.backup
3. tar czf media.tar.gz media/
4. tar czf config.tar.gz docker-compose.yml .env docker/
5. scp * user@new-server:/tmp/
```

### Новый сервер:
```bash
1. apt install docker.io docker-compose
2. mkdir /opt/metateks && cd /opt/metateks
3. docker load < /tmp/images.tar.gz
4. tar xzf /tmp/config.tar.gz
5. tar xzf /tmp/media.tar.gz
6. docker-compose up -d db redis
7. docker cp /tmp/db.backup metateks_db:/tmp/
8. docker exec metateks_db pg_restore ...
9. docker-compose up -d
10. curl http://localhost/
```

---

## 📞 Дополнительная документация

- [MIGRATION_FROM_VPS.md](MIGRATION_FROM_VPS.md) - Миграция данных
- [STORAGE_ARCHITECTURE.md](STORAGE_ARCHITECTURE.md) - Архитектура хранения
- [1C_INTEGRATION.md](1C_INTEGRATION.md) - Настройка 1С
