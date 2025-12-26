# Docker - Быстрый старт

## 🚀 Для разработки (Development)

```bash
# Запуск dev окружения с hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Пересборка dev образа
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# Создать alias для удобства
echo 'alias dc-dev="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"' >> ~/.bashrc
source ~/.bashrc

# Теперь можно использовать короткую команду
dc-dev up
```

**Особенности dev режима:**
- ✅ Код монтируется с хоста (изменения видны сразу)
- ✅ Django runserver (автоматическая перезагрузка)
- ✅ Открыты порты БД для отладки (PostgreSQL:5432, Redis:6379)
- ✅ Debug инструменты (ipdb, django-debug-toolbar)

---

## 🏭 Для production

```bash
# Сборка production образа
docker-compose build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f web

# Перезапуск после изменения кода
docker-compose build web celery
docker-compose up -d

# Остановка
docker-compose down
```

**Особенности production режима:**
- ✅ Код внутри образа (Stateless)
- ✅ Gunicorn веб-сервер
- ✅ Порты БД закрыты (безопасность)
- ✅ Контейнер можно удалить/создать без потери данных

---

## 📊 Управление данными

```bash
# Выполнить команду Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Резервная копия БД
docker exec metateks_db pg_dump -U metateks metateks > backup.sql

# Восстановление БД
docker exec -i metateks_db psql -U metateks metateks < backup.sql
```

---

## 🔍 Отладка

```bash
# Просмотр логов
docker-compose logs -f web
docker-compose logs -f celery

# Войти в контейнер
docker exec -it metateks_web bash

# Перезапустить сервис
docker-compose restart web

# Проверить статус
docker-compose ps
```

---

## 🧹 Очистка

```bash
# Остановить и удалить контейнеры
docker-compose down

# Удалить контейнеры И volumes (⚠️ удалит БД!)
docker-compose down -v

# Полная очистка системы
docker system prune -a
```

---

## 📁 Что где находится?

### В образе (НЕ изменяется при перезапуске)
- Исходный код Python
- Зависимости (requirements)
- Шаблоны и assets

### В volumes (сохраняется при перезапуске)
- `postgres_data` - База данных PostgreSQL
- `redis_data` - Данные Redis
- `./media/` - Загрузки пользователей
- `./logs/` - Логи приложения
- `static_volume` - Собранная статика

---

## ⚙️ Переменные окружения

Используйте `.env.docker` для настройки:
```bash
# Скопировать пример
cp .env.example .env.docker

# Отредактировать настройки
nano .env.docker

# Перезапустить для применения
docker-compose up -d
```

---

## 📚 Подробная документация

Читайте полное руководство: [docs/DOCKER_PROD_VS_DEV.md](docs/DOCKER_PROD_VS_DEV.md)

---

## ❓ Частые проблемы

### Ошибка "port is already allocated"
```bash
# Найти процесс на порту 8000
sudo lsof -i :8000
# Убить процесс
sudo kill -9 <PID>
```

### Изменения кода не видны
```bash
# В production нужно пересобрать образ
docker-compose build web
docker-compose up -d

# В dev проверьте, что используете docker-compose.dev.yml
```

### База данных не сохраняется
```bash
# Проверьте volumes
docker volume ls

# Убедитесь, что не используете флаг -v при остановке
docker-compose down  # ✅ правильно
docker-compose down -v  # ❌ удалит данные!
```
