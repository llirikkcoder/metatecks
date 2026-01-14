# Research: Исправление ошибок развертывания Docker

**Feature**: 002-fix-docker-deployment
**Date**: 2026-01-14
**Status**: Complete

## Overview

Данный документ содержит результаты исследования проблем Docker развертывания и предложенные решения для:
1. **IntegrityError: duplicate key value violates unique constraint "pg_type_typname_nsp_index"**
2. **SIGBUS ошибки при сборке Docker образов в WSL**

---

## Problem 1: PostgreSQL IntegrityError - orders_deliverycompany

### Root Cause Analysis

**Symptom**:
```
django.db.utils.IntegrityError: duplicate key value violates unique constraint "pg_type_typname_nsp_index"
DETAIL: Key (typname, typnamespace)=(orders_deliverycompany, 2200) already exists.
```

**Root Cause**:
При создании таблицы `orders_deliverycompany` PostgreSQL автоматически создает composite type с тем же именем. При повторных миграциях или при `DROP TABLE` без `DROP TYPE`, type остается в базе данных.

**Why it happens**:
1. PostgreSQL автоматически создает composite type для каждой таблицы (ROW type)
2. Django миграции при `migrations.CreateModel` создают таблицу → PostgreSQL создает type
3. Если таблица удаляется и создается повторно (или при повторной миграции), тип может не удалиться
4. При повторном создании таблицы PostgreSQL пытается создать type с тем же именем → IntegrityError

**Reproduction**:
- Запуск `docker-compose down -v` (удаление volume)
- Запуск `docker-compose up -d` (создание новой базы)
- Повторный запуск `docker-compose up -d` может вызвать ошибку

### Research: Solutions Evaluated

| Solution | Pros | Cons | Verdict |
|----------|------|------|---------|
| **A. Check if type exists before migration** | Simple, explicit | Requires custom migration code | ✅ Recommended |
| **B. DROP TYPE IF EXISTS in migration** | Direct fix | May break if type has dependencies | ⚠️ Risky |
| **C. Use RunSQL for conditional drop** | PostgreSQL native | Complex, SQL-specific | ⚠️ Backup |
| **D. Ensure CASCADE drops in migrations** | Clean state | Dangerous if not careful | ❌ Too risky |
| **E. Add idempotency to migration system** | Prevents all future issues | Requires Django monkey-patching | ❌ Over-engineering |

### Decision: Solution A + Migration Safety Wrapper

**Approach**:
1. Создать утилиту `safe_migration.py` для безопасного создания моделей
2. Добавить проверку существования type перед `CreateModel`
3. Обернуть рискованные миграции в try-except с `DROP TYPE IF EXISTS`

**Implementation**:
```python
# apps/orders/migrations/xxxx_delivery_company_type_fix.py

from django.db import migrations, connection


def drop_delivery_company_type_if_exists(apps, schema_editor):
    """Удаляет composite type orders_deliverycompany если существует"""
    with connection.cursor() as cursor:
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_type
                    WHERE typname = 'orders_deliverycompany'
                    AND typtype = 'c'
                ) THEN
                    DROP TYPE IF EXISTS orders_deliverycompany CASCADE;
                RAISE NOTICE 'Dropped existing type: orders_deliverycompany';
                END IF;
            END $$;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0006_order_updated_at'),
    ]

    operations = [
        migrations.RunPython(drop_delivery_company_type_if_exists),
        # ... rest of migration operations
    ]
```

**Alternatives considered**:
- **C. RunSQL**: PostgreSQL-native но сложнее в поддержке
- **B. DROP TYPE напрямую**: Рисковано из-за возможных зависимостей

---

## Problem 2: SIGBUS Error in WSL During Docker Build

### Root Cause Analysis

**Symptom**:
```
fatal error: fault [signal SIGBUS: bus error code=0x2 addr=0x387405c pc=0x466a49]
```

**Root Cause**:
SIGBUS (Signal BUS error) в WSL2 возникает из-за проблем с памятью/диском при сборке Docker образов. Причины:
1. **Cross-platform filesystem issues**: WSL2 mounts Windows drives через 9P/virtiofs, что может вызывать memory alignment issues
2. **Memory pressure**: Сборка больших образов требует больше памяти чем доступно в WSL2
3. **Docker Desktop WSL2 backend limitations**: Известная проблема с большими builds в WSL2

**Why it happens**:
- Docker build context на Windows filesystem (WSL2 /mnt/c)
- Docker Desktop использует WSL2 backend с ограниченной памятью
- Large COPY operations или pip install могут вызывать SIGBUS

### Research: Solutions Evaluated

| Solution | Pros | Cons | Verdict |
|----------|------|------|---------|
| **A. Move project to WSL filesystem (~)** | Eliminates cross-FS issues | Requires project relocation | ✅ Most Effective |
| **B. Increase WSL memory in .wslconfig** | Easy, no code changes | Requires restart, may not fully fix | ✅ Recommended (with A) |
| **C. Use Docker buildx with different driver** | Modern approach | Still experimental for WSL | ⚠️ Try if A fails |
| **D. Multi-stage build optimization** | Good practice anyway | Doesn't address root cause | ✅ Always do |
| **E. Build in native Linux VM** | 100% reliable | Inconvenient for Windows devs | ❌ Last resort |

### Decision: Solution A + B + D (Combined)

**Approach**:
1. **Primary**: Переместить проект в WSL filesystem (`~/projects/` вместо `/mnt/c/...`)
2. **Secondary**: Настроить `.wslconfig` с увеличением памяти
3. **Optimization**: Multi-stage build для снижения размера образа

**Implementation - Step 1: Move to WSL filesystem**
```bash
# Копировать проект в WSL home
cp -r /mnt/c/_KIPOL/_WORK/_metatecks ~/projects/metateks
cd ~/projects/metateks

# Обновить .dockerignore для исключения лишних файлов
```

**Implementation - Step 2: Configure .wslconfig**
```ini
# C:\Users\<User>\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=2GB
swapFile=C:\\temp\\wsl-swap.vhdx
```

**Implementation - Step 3: Optimize Dockerfile**
```dockerfile
# Multi-stage build для уменьшения слоев
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-conda.txt requirements-pip.txt ./
RUN pip install --user --no-cache-dir -r requirements-conda.txt && \
    pip install --user --no-cache-dir -r requirements-pip.txt

# Final stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .
```

**Alternatives considered**:
- **C. buildx**: Может помочь, но не решает проблему cross-FS
- **E. Native Linux VM**: Надежно но неудобно для разработки

---

## Problem 3: Health Check and Dependency Issues

### Current State Analysis

**Health checks**:
- ✅ db: `pg_isready` - правильно настроен
- ✅ redis: `redis-cli ping` - правильно настроен
- ⚠️ web: checks `/admin/login/` - зависит от маршрутизации Django

**Dependencies**:
- ✅ web depends_on db + redis с condition: service_healthy
- ⚠️ celery depends_on db + redis - нет health check у celery
- ✅ nginx depends_on web с condition: service_healthy

### Research: Improvements Needed

| Issue | Current | Recommended | Priority |
|-------|---------|-------------|----------|
| Celery health check | None | Add celery-specific check | P2 |
| Migration idempotency | Run every time | Check if already applied | P1 |
| Entrypoint DB wait | Python script | Consider dockerize tool | P3 |

### Decision: Add Celery Health Check

**Implementation**:
```yaml
# docker-compose.yml
celery:
  # ... existing config
  healthcheck:
    test: ["CMD", "celery", "-A", "main", "inspect", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

---

## Summary of Decisions

| Problem | Solution | Complexity | Risk |
|---------|----------|------------|------|
| IntegrityError orders_deliverycompany | Migration wrapper with DROP TYPE IF EXISTS | Low | Low |
| SIGBUS in WSL | Move to ~ + .wslconfig + multi-stage build | Medium | Low |
| Health checks | Add celery health check | Low | Low |

## Next Steps

1. **Phase 1**: Design artifacts (data-model.md, contracts/)
2. **Phase 2**: Create implementation plan with tasks
3. **Phase 3**: Implement fixes in priority order
