# Руководство: Production vs Development режимы Docker

## Золотое правило: Stateless контейнеры

Docker следует принципу **Stateless** (без сохранения состояния внутри контейнера). Это значит, что контейнер должен быть "расходным материалом" - вы можете удалить его в любой момент и создать новый, и приложение продолжит работу с того же места.

---

## Что должно быть где?

### ✅ В Docker Image (Образе)
Все, что является частью "движка" приложения:
- ✅ Исходный код Python (`.py` файлы)
- ✅ Шаблоны Django (`templates/`)
- ✅ Библиотеки и зависимости (`requirements.txt`)
- ✅ Статические файлы CSS/JS (`assets/`)
- ✅ Системные утилиты и Python пакеты

### ✅ В Docker Volumes (Томах)
Только данные, которые изменяются в процессе работы:
- ✅ База данных PostgreSQL (`postgres_data`)
- ✅ Данные Redis (`redis_data`)
- ✅ Загрузки пользователей (`./media/`)
- ✅ Собранная статика (`static_volume`)
- ✅ Логи приложения (`./logs/`)
- ✅ Конфигурационные файлы (если нужно менять без пересборки)

---

## Production режим (docker-compose.yml)

### Характеристики
- Код **внутри образа** (не монтируется)
- Контейнер полностью автономный
- Используется Gunicorn вместо runserver
- Порты баз данных закрыты (безопасность)
- Healthcheck включен

### Запуск Production

```bash
# Сборка образа
docker-compose build

# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f web

# Остановка
docker-compose down
```

### Обновление кода в Production
После изменения кода нужно **пересобрать образ**:

```bash
# Пересборка образа
docker-compose build web celery

# Перезапуск контейнеров
docker-compose up -d
```

### Преимущества Production режима
- ✅ Контейнер самодостаточный и переносимый
- ✅ Можно удалить/создать в любой момент
- ✅ Легко масштабируется (несколько реплик)
- ✅ Безопасность (нет доступа к хостовой системе)

---

## Development режим (docker-compose.dev.yml)

### Характеристики
- Код **монтируется с хоста** (hot-reload)
- Используется Django runserver (автоматическая перезагрузка)
- Порты баз данных открыты для отладки
- Дополнительные инструменты (ipdb, django-debug-toolbar)
- Healthcheck отключен (быстрый старт)

### Запуск Development

```bash
# Сборка dev образа
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# Запуск dev окружения
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Короткая команда (создайте alias)
alias dc-dev="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"
dc-dev up
```

### Преимущества Development режима
- ✅ Изменения кода видны сразу (hot-reload)
- ✅ Не нужно пересобирать образ при каждом изменении
- ✅ Доступ к базе данных для отладки
- ✅ Дополнительные инструменты разработки

---

## Сравнительная таблица

| Характеристика | Production | Development |
|----------------|-----------|-------------|
| Код | В образе | Монтируется с хоста |
| Web сервер | Gunicorn | Django runserver |
| Hot-reload | ❌ Нет | ✅ Да |
| Порты БД | Закрыты | Открыты (5432, 6379) |
| Healthcheck | ✅ Включен | ❌ Отключен |
| Debug инструменты | Минимум | ✅ Полный набор |
| Безопасность | ✅ Высокая | ⚠️ Низкая |
| Скорость запуска | Средняя | Быстрая |
| Размер образа | Оптимизирован | Больше (dev tools) |

---

## Переключение между режимами

### Из Dev в Prod
```bash
# Остановить dev окружение
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Запустить production
docker-compose up -d
```

### Из Prod в Dev
```bash
# Остановить production
docker-compose down

# Запустить dev
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## Частые вопросы

### Вопрос: Нужно ли пересобирать образ при каждом изменении кода в Production?
**Ответ:** Да! В production код находится внутри образа, поэтому:
```bash
docker-compose build web celery
docker-compose up -d
```

### Вопрос: Почему в dev режиме изменения видны сразу?
**Ответ:** Потому что код монтируется с хоста через volume:
```yaml
volumes:
  - .:/app  # Код берется с хоста
```

### Вопрос: Можно ли использовать dev режим в production?
**Ответ:** Нет! Dev режим небезопасен:
- Открыты порты баз данных
- Монтируется весь проект (доступ к хосту)
- Используется runserver (не предназначен для production)
- DEBUG=True (раскрывает конфиденциальную информацию)

### Вопрос: Что делать, если нужно изменить настройки в production?
**Ответ:** Есть два варианта:
1. **Переменные окружения** (`.env.docker`) - меняются без пересборки
2. **Код/конфигурация** - требует пересборки образа

---

## Проверка текущего режима

### Проверить, что код в образе (Production)
```bash
# Войти в контейнер
docker exec -it metateks_web bash

# Изменить любой файл
echo "# test" >> manage.py

# Перезапустить контейнер
docker-compose restart web

# Проверить - изменения НЕ должны сохраниться
docker exec -it metateks_web cat manage.py
```

### Проверить hot-reload (Development)
```bash
# В отдельном терминале запустить логи
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f web

# Измените любой .py файл на хосте
# Вы должны увидеть в логах автоматическую перезагрузку Django
```

---

## Best Practices

### Production
1. ✅ Всегда используйте `.env.docker` для секретов
2. ✅ Создавайте резервные копии volumes перед обновлением
3. ✅ Используйте конкретные версии зависимостей (`==1.2.3`)
4. ✅ Тестируйте образ локально перед деплоем
5. ✅ Используйте health checks для автоматического восстановления

### Development
1. ✅ Не коммитьте `.env` файлы в Git
2. ✅ Используйте docker-compose.dev.yml для локальных переопределений
3. ✅ Регулярно чистите volumes: `docker-compose down -v` (осторожно!)
4. ✅ Используйте `docker-compose logs -f` для отладки
5. ✅ Создайте alias для удобства: `alias dc-dev="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"`

---

## Дополнительные команды

### Полная очистка (⚠️ удалит ВСЕ данные)
```bash
docker-compose down -v
docker system prune -a
```

### Пересборка без кеша
```bash
docker-compose build --no-cache
```

### Создание резервной копии базы данных
```bash
docker exec metateks_db pg_dump -U metateks metateks > backup_$(date +%Y%m%d).sql
```

### Восстановление базы данных
```bash
docker exec -i metateks_db psql -U metateks metateks < backup_20250126.sql
```

---

## Заключение

**Production режим** - для боевого окружения, где важна стабильность и безопасность.
**Development режим** - для разработки, где важна скорость итераций.

Используйте правильный режим для правильной задачи!
