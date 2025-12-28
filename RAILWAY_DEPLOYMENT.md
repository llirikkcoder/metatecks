# Railway Deployment Guide

## Быстрый старт

### 1. Установить Railway CLI

```bash
curl -fsSL https://railway.com/install.sh | sh
```

### 2. Подключиться к проекту

```bash
railway login
railway link -p 6929e4b1-e4c9-406c-ab3b-3a38b775aed1
```

### 3. Задеплоить

```bash
railway up
```

## Настройка переменных окружения в Railway

### Вариант 1: С PostgreSQL (рекомендуется для продакшена)

**В Railway Dashboard:**

1. **Добавить PostgreSQL:**
   - `+ New` → `Database` → `Add PostgreSQL`

2. **Настроить Variables:**
   ```bash
   DATABASE_URL=${{Postgres.DATABASE_URL}}  # Автоматически из PostgreSQL
   DEBUG=0
   SECRET_KEY=your-random-secret-key-here
   ALLOWED_HOSTS=metatecks-production.up.railway.app,localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=https://metatecks-production.up.railway.app
   REDIS_URL=redis://localhost:6379/0
   ```

### Вариант 2: С SQLite (только для тестирования)

**В Railway Dashboard Variables:**

```bash
USE_SQLITE=1
DEBUG=0
SECRET_KEY=your-random-secret-key-here
ALLOWED_HOSTS=metatecks-production.up.railway.app,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://metatecks-production.up.railway.app
REDIS_URL=redis://localhost:6379/0
```

⚠️ **Важно:** SQLite в Railway ephemeral - данные удалятся при редеплое!

## Fallback на SQLite

Приложение автоматически использует SQLite если:
- Нет `DATABASE_URL`
- Или установлено `USE_SQLITE=1`

**Порядок приоритета:**
1. `USE_SQLITE=1` → SQLite (принудительно)
2. `DATABASE_URL` задан → PostgreSQL
3. Иначе → SQLite (fallback для локальной разработки)

## Стоимость

**Hobby Plan:**
- $5 бесплатных кредитов/месяц
- PostgreSQL < 500MB: входит в бесплатные $5
- Для теста SEO: **бесплатно**

**Starter Plan ($5/месяц):**
- $5 кредитов + дополнительные фичи
- PostgreSQL включен

## URL проекта

**Production:** https://metatecks-production.up.railway.app
**Admin:** https://metatecks-production.up.railway.app/admin/

## Полезные команды Railway CLI

```bash
# Статус проекта
railway status

# Логи
railway logs

# Логи билда
railway logs --build

# Переменные окружения
railway variables

# Открыть в браузере
railway open
```

## Troubleshooting

### 502 Bad Gateway

**Причины:**
1. Приложение еще запускается (подожди 1-2 минуты)
2. Ошибка при старте (проверь `railway logs`)
3. Неправильный порт (проверь Dockerfile expose 80)

### Миграции не применились

```bash
# Посмотреть логи
railway logs | grep migrate

# Если нужно вручную
railway run python manage.py migrate
```

### База данных не готова

**Если видишь "Database not ready":**
1. Убедись что PostgreSQL добавлен в проекте
2. Проверь что `DATABASE_URL` в Variables
3. Или установи `USE_SQLITE=1` для fallback

## Структура проекта

```
metatecks/
├── db.sqlite3              # SQLite база (в git для Railway)
├── main/settings/base.py   # Настройки с fallback на SQLite
├── .env.example            # Примеры переменных для Railway
├── docker-compose.yml      # Docker конфигурация
├── Dockerfile              # Railway использует это для билда
└── requirements-*.txt      # Python зависимости
```

## Git & Railway

Railway автоматически деплоит при push в GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin feature/seo-improve
```

Railway увидит push и автоматически запустит deploy.
