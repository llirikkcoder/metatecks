# Data Model: Исправление ошибок развертывания Docker

**Feature**: 002-fix-docker-deployment
**Date**: 2026-01-14

## Overview

Данный документ описывает сущности, вовлеченные в процесс Docker развертывания, и их взаимодействия.

---

## Docker Service Entities

### 1. PostgreSQL Database Service (db)

**Description**: Контейнер с базой данных PostgreSQL 15 Alpine

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| image | postgres:15-alpine | Базовый образ |
| container_name | metateks_db | Имя контейнера |
| environment | POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD | Переменные окружения |
| volumes | postgres_data:/var/lib/postgresql/data | Persistent storage |
| healthcheck.test | pg_isready -U metateks | Проверка готовности |
| healthcheck.interval | 10s | Частота проверок |
| healthcheck.retries | 5 | Количество попыток |

**State Transitions**:
```
starting → health: starting → health: healthy (ready)
                                    ↓
                               (accepts connections)
```

**Relationships**:
- web → depends_on: db (condition: service_healthy)
- celery → depends_on: db (condition: service_healthy)

**Critical Issues**:
- PostgreSQL composite types могут оставаться после DROP TABLE
- Нужно безопасное удаление types перед миграциями

---

### 2. Redis Service (redis)

**Description**: Контейнер с Redis 7 Alpine для Celery broker

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| image | redis:7-alpine | Базовый образ |
| container_name | metateks_redis | Имя контейнера |
| command | redis-server --appendonly yes | AOF persistence |
| volumes | redis_data:/data | Persistent storage |
| healthcheck.test | redis-cli ping | Проверка готовности |

**State Transitions**:
```
starting → health: starting → health: healthy (PING PONG)
```

---

### 3. Django Web Application (web)

**Description**: Контейнер с Django приложением (Gunicorn production server)

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| build.context | . | Контекст сборки |
| build.dockerfile | Dockerfile | Путь к Dockerfile |
| command | gunicorn --bind 0.0.0.0:8000 --workers 4 | Запуск сервера |
| volumes | static_volume, ./media, ./logs | Monitored directories |
| ports | 127.0.0.1:8001:8000 | localhost binding |
| healthcheck.test | curl -f http://localhost:8000/admin/login/ | Проверка приложения |
| healthcheck.start_period | 40s | Время на инициализацию |

**Entrypoint Flow**:
```
1. docker-entrypoint.sh starts
    ↓
2. Wait for PostgreSQL (Python script, 30 retries)
    ↓
3. Run migrations: python manage.py migrate --noinput
    ↓
4. Collect static: python manage.py collectstatic --noinput
    ↓
5. Load fixtures (if /app/logs/.fixtures_loaded not exists)
    ↓
6. Build search index: python manage.py buildwatson
    ↓
7. Execute CMD: gunicorn ...
```

**Dependencies**:
- db (health: healthy)
- redis (health: healthy)

---

### 4. Celery Worker (celery)

**Description**: Контейнер с Celery worker для фоновой обработки задач

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| command | celery -A main worker --loglevel=info --concurrency=2 | Worker config |
| volumes | ./media, ./logs | Shared directories |

**Health Check Status**: ⚠️ NOT CONFIGURED (needs implementation)

**Proposed Health Check**:
```yaml
healthcheck:
  test: ["CMD", "celery", "-A", "main", "inspect", "ping"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

### 5. Nginx Reverse Proxy (nginx)

**Description**: Nginx контейнер для reverse proxy и static files

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| image | nginx:alpine | Базовый образ |
| ports | 127.0.0.1:8080:80 | Reverse proxy port |
| volumes | ./docker/nginx, static_volume, ./media | Config and data |

**Dependencies**:
- web (health: healthy)

---

## Docker Volume Entities

### postgres_data
- **Type**: Named volume
- **Path in container**: /var/lib/postgresql/data
- **Purpose**: Persistent PostgreSQL storage
- **Issue**: Contains composite types that may cause IntegrityError

### redis_data
- **Type**: Named volume
- **Path in container**: /data
- **Purpose**: Redis AOF persistence

### static_volume
- **Type**: Named volume
- **Path in container**: /app/static
- **Purpose**: Shared static files between web and nginx
- **Population**: `python manage.py collectstatic --noinput`

---

## Django Migration Entities

### Migration Dependency Graph

```
addresses.0002_load_data
    ↓
catalog.0027_extra_products_rename
    ↓
orders.0001_initial ──→ Creates orders_deliverycompany table
    ↓                    └──→ PostgreSQL creates composite type
orders.0002_orderitem_item_subtitle
    ↓
orders.0003_reorganize_address_models
    ↓
...
orders.0006_order_updated_at
    ↓
orders.0007_load_delivery_companies ──→ Loads fixture data
```

### Problematic Migration: orders.0001_initial

**Issue**: Creates `orders_deliverycompany` table → PostgreSQL creates `orders_deliverycompany` type

**If migration re-runs**:
1. Django detects model already exists (if table present)
2. Or tries to create table → PostgreSQL creates type → IntegrityError (if type exists)

**Resolution Strategy**:
```python
# Pre-migration operation: Drop type if exists
DROP TYPE IF EXISTS orders_deliverycompany CASCADE;
```

---

## Docker Build Artifacts

### Dockerfile Layers

```
1. python:3.11-slim (base image)
    ↓
2. Install system packages (apt-get)
    ↓
3. Copy requirements*.txt
    ↓
4. pip install (creates many layers)
    ↓
5. COPY . . (application code)
    ↓
6. Create directories (chown metateks)
    ↓
7. COPY docker-entrypoint.sh
    ↓
8. ENTRYPOINT + CMD
```

**Optimization Opportunities**:
- Multi-stage build for smaller image
- Combine pip install into single layer
- Use .dockerignore to exclude unnecessary files

---

## State Machine: Container Startup

```
┌─────────────────────────────────────────────────────────────┐
│                     docker-compose up                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │                                           │
   ┌────▼────┐                               ┌─────▼────┐
   │   db    │                               │  redis   │
   │ starting│                               │ starting │
   └────┬────┘                               └─────┬────┘
        │                                          │
        │ healthcheck: pg_isready                  │ healthcheck: ping
        │ (interval: 10s, retries: 5)             │ (interval: 10s)
        │                                          │
        ▼                                          ▼
   ┌─────┴─────┐                            ┌─────┴─────┐
   │ db:healthy│                            │redis:healthy│
   └─────┬─────┘                            └─────┬─────┘
        │                                         │
        └─────────────────┬───────────────────────┘
                         │
                         ↓ both healthy
              ┌────────────────────┐
              │  web entrypoint    │
              └─────────┬──────────┘
                        │
         ┌──────────────┴──────────────┐
         │   1. Wait for DB (Python)   │
         └──────────────┬──────────────┘
                        │ ready
         ┌──────────────┴──────────────┐
         │   2. Run migrations         │
         │   manage.py migrate         │
         └──────────────┬──────────────┘
                        │
         ┌──────────────┴──────────────┐
         │  ⚠️ IntegrityError possible │
         │  if type exists            │
         └──────────────┬──────────────┘
                        │
         ┌──────────────┴──────────────┐
         │   3. Collect static         │
         │   4. Load fixtures          │
         │   5. Build search index     │
         └──────────────┬──────────────┘
                        │
         ┌──────────────┴──────────────┐
         │   gunicorn starts          │
         └──────────────┬──────────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ web:health check    │
              │ curl /admin/login/  │
              │ (start_period: 40s) │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ nginx depends on   │
              │ web:healthy        │
              └────────────────────┘
```

---

## WSL Filesystem Architecture

### Current (Problematic)
```
Windows Filesystem (NTFS)
    └── C:\_KIPOL\_WORK\_metatecks
            └── Mounted via 9P/virtiofs
                └── /mnt/c/_KIPOL/_WORK/_metatecks (WSL)
                    └── Docker build context
                        └── SIGBUS risk ⚠️
```

### Recommended (Fixed)
```
WSL Filesystem (ext4)
    └── ~/projects/metateks
        └── Native filesystem access
            └── Docker build context
                └── No SIGBUS ✅
```

---

## Validation Rules

### Container Health Rules
| Service | Health Check | Healthy Condition |
|---------|--------------|-------------------|
| db | pg_isready | Exit code 0 |
| redis | redis-cli ping | Returns PONG |
| web | curl /admin/login/ | HTTP 200 |
| celery | celery inspect ping (proposed) | pong response |
| nginx | (implicit) | Running |

### Migration Idempotency Rules
1. Migration must be safe to run multiple times
2. Type conflicts must be resolved before CreateModel
3. Fixture loading must check `.fixtures_loaded` flag

### Volume Persistence Rules
1. `postgres_data`: Contains all database state including types
2. `redis_data`: Contains AOF file
3. `static_volume`: Populated from image, not host
4. `logs/`: Contains `.fixtures_loaded` flag on host
