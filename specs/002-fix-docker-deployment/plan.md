# Implementation Plan: Исправление ошибок развертывания Docker

**Branch**: `002-fix-docker-deployment` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fix-docker-deployment/spec.md`

## Summary

Исправление критических проблем Docker развертывания, блокирующих разработчиков:
1. **PostgreSQL IntegrityError** - конфликт composite types при повторных миграциях
2. **WSL SIGBUS ошибки** - сбои сборки Docker образов на Windows filesystem

**Technical Approach**:
- Добавить безопасное удаление PostgreSQL types перед миграциями
- Оптимизировать Dockerfile для WSL (multi-stage build)
- Обновить документацию с instructions для WSL filesystem

---

## Technical Context

**Language/Version**: Python 3.11 (Django 4.2.13)
**Primary Dependencies**: Docker, Docker Compose v2+, PostgreSQL 15, Redis 7, Gunicorn
**Storage**: PostgreSQL 15 with persistent volumes
**Testing**: docker compose для интеграционного тестирования
**Target Platform**:
  - Linux (native)
  - macOS (native)
  - Windows via WSL2 (primary dev environment)
**Project Type**: web (Django e-commerce platform)
**Performance Goals**:
  - Startup time < 90 секунд до полной готовности системы
  - 100% успешных запусков docker-compose up -d
**Constraints**:
  - Минимизация изменений существующего кода
  - Обратная совместимость с production deployments
  - Нулевой простой для пользователей
**Scale/Scope**:
  - 5 Docker контейнеров (db, redis, web, celery, nginx)
  - ~100 миграций Django
  - ~30 таблиц PostgreSQL

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Current Constitution Status

**Project Constitution**: Not defined (template is empty)

**Gates**: No gates defined - N/A

**Result**: ✅ PASS (No constitution violations to check)

### Complexity Tracking

No violations to justify - straightforward infrastructure fix.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-fix-docker-deployment/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Research findings (Phase 0)
├── data-model.md        # Docker entities and state machines
├── quickstart.md        # Deployment guide
├── contracts/           # Service contracts
│   └── deployment-contract.md
├── checklists/
│   └── requirements.md  # Spec validation checklist
└── tasks.md             # To be created by /speckit.tasks
```

### Source Code (repository root)

```text
# Modified files (planned changes)
docker-compose.yml          # Add celery healthcheck, optimize dependencies
docker-entrypoint.sh        # Add migration safety check
Dockerfile                  # Optimize with multi-stage build
apps/orders/migrations/     # Add type cleanup migration
docs/DOCKER_DEPLOYMENT.md   # Update with WSL instructions
README_WSL.md               # Already created, may update

# New files (planned additions)
scripts/docker-migration-safety.py    # Utility for safe migrations
.wslconfig.example                    # WSL configuration template
docs/SIGBUS_TROUBLESHOOTING.md        # SIGBUS error guide
```

**Structure Decision**: Web application structure with Django backend, Nginx reverse proxy, and background workers. No structure changes required - only optimization of existing Docker configuration.

---

## Architecture Design

### Current Architecture Issues

```
┌─────────────────────────────────────────────────────────────────┐
│                        PROBLEM AREAS                            │
└─────────────────────────────────────────────────────────────────┘

1. PostgreSQL Type Conflicts:
   Django Migration (CreateModel) → PostgreSQL Table + Composite Type
   ↓ Migration re-run or fresh DB
   Type already exists → IntegrityError ⚠️

2. WSL Filesystem Issues:
   /mnt/c/ (Windows NTFS) → 9P/virtiofs mount → SIGBUS on build ⚠️
```

### Proposed Architecture Changes

```
┌─────────────────────────────────────────────────────────────────┐
│                     SOLUTION ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

1. Migration Safety Wrapper:
   docker-entrypoint.sh
   ↓
   NEW: Pre-migration type cleanup
   ↓
   python manage.py migrate (idempotent)

2. WSL Best Practices:
   ~/projects/metateks (WSL ext4) → Native filesystem → No SIGBUS ✅
   ↓
   Multi-stage Dockerfile → Smaller layers → Faster builds ✅

3. Enhanced Health Checks:
   celery: Add celery inspect ping healthcheck
   ↓
   All services have proper health status ✅
```

---

## Implementation Phases

### Phase 1: Migration Safety (P1 - Critical)

**Goal**: Eliminate IntegrityError on orders_deliverycompany type

**Files to Modify**:
1. `docker-entrypoint.sh` - Add pre-migration cleanup
2. `apps/orders/migrations/` - Add type fix migration

**Implementation**:

```python
# NEW: apps/orders/migrations/0008_fix_delivery_company_type.py

from django.db import migrations, connection


def drop_delivery_company_type_if_exists(apps, schema_editor):
    """Drop orders_deliverycompany composite type if exists"""
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
        ('orders', '0007_load_delivery_companies'),
    ]

    operations = [
        migrations.RunPython(drop_delivery_company_type_if_exists),
    ]
```

**Testing**:
```bash
# Test fresh volume
docker compose down -v
docker compose up -d
# Should succeed without IntegrityError

# Test re-run
docker compose down
docker compose up -d
# Should succeed without IntegrityError
```

---

### Phase 2: WSL Optimization (P2 - High Priority)

**Goal**: Eliminate SIGBUS errors during Docker build

**Files to Modify**:
1. `.wslconfig.example` - Create configuration template
2. `Dockerfile` - Optimize with multi-stage build
3. `docs/DOCKER_DEPLOYMENT.md` - Add WSL instructions

**Implementation**:

```dockerfile
# OPTIMIZED: Dockerfile (multi-stage build)

# Builder stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev libjpeg-dev libpng-dev libwebp-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-conda.txt requirements-pip.txt ./
RUN pip install --user --no-cache-dir -r requirements-conda.txt && \
    pip install --user --no-cache-dir -r requirements-pip.txt && \
    pip install --user --no-cache-dir gunicorn psycopg2-binary

# Final stage
FROM python:3.11-slim

# Copy installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libjpeg62-turbo libpng16-16 libwebp6 zlib1g \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
WORKDIR /app
COPY . .

# Create directories and user
RUN mkdir -p /app/media /app/static /app/logs && \
    useradd -m -u 1000 metateks && \
    chown -R metateks:metateks /app

USER metateks

# Copy entrypoint
COPY --chown=metateks:metateks docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "main.wsgi:application"]
```

```ini
# NEW: .wslconfig.example

[wsl2]
memory=8GB
processors=4
swap=2GB
swapFile=C:\\temp\\wsl-swap.vhdx
```

**Documentation Update**:
```markdown
# In DOCKER_DEPLOYMENT.md

## Windows/WSL2 Developers

### Critical: Use WSL Filesystem

To avoid SIGBUS errors during Docker build, project must be on WSL filesystem:

```bash
# ❌ WRONG - Windows filesystem
cd /mnt/c/_KIPOL/_WORK/_metatecks

# ✅ CORRECT - WSL filesystem
cd ~/projects/metateks
```

### Configure WSL Memory

Copy `.wslconfig.example` to `C:\Users\<You>\.wslconfig` and restart WSL.
```

---

### Phase 3: Health Check Enhancements (P3 - Medium)

**Goal**: Add health check for Celery worker

**Files to Modify**:
1. `docker-compose.yml` - Add celery healthcheck

**Implementation**:

```yaml
# MODIFIED: docker-compose.yml

celery:
  # ... existing config ...
  healthcheck:
    test: ["CMD", "celery", "-A", "main", "inspect", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

---

### Phase 4: Documentation & Troubleshooting (P3 - Medium)

**Goal**: Comprehensive troubleshooting guide

**Files to Create**:
1. `docs/SIGBUS_TROUBLESHOOTING.md` - SIGBUS error guide
2. Update `docs/DOCKER_DEPLOYMENT.md` - Add all troubleshooting steps

**Content**: Already covered in `quickstart.md` - copy to project docs

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Migration fix breaks production | Low | High | Test extensively in dev, add rollback plan |
| Multi-stage build increases complexity | Low | Low | Document changes, keep simple |
| WSL filesystem move confuses users | Medium | Medium | Clear documentation in quickstart |
| Health check adds false positives | Low | Low | Generous timeouts and retries |

---

## Rollback Plan

If Phase 1 (Migration Safety) causes issues:

```bash
# Revert migration
docker exec metateks_web python manage.py migrate orders 0007_load_delivery_companies

# Remove problematic migration
rm apps/orders/migrations/0008_fix_delivery_company_type.py

# Restart container
docker compose restart web
```

If Phase 2 (WSL Optimization) causes issues:

```bash
# Revert Dockerfile
git checkout HEAD -- Dockerfile

# Rebuild
docker compose build --no-cache
```

---

## Success Metrics

From spec.md success criteria:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| SC-001 | 100% successful docker-compose up -d | Run 10 times, count failures |
| SC-002 | All containers healthy in 60s | time docker compose up -d; watch status |
| SC-003 | No IntegrityError on migrations | Check logs after each run |
| SC-004 | No SIGBUS on builds in WSL | Build 5 times in WSL, count failures |
| SC-005 | Full system ready < 2 min | Time from docker compose up to nginx healthy |

---

## Dependencies

**External Dependencies**:
- Docker Desktop for WSL (must support WSL2 backend)
- PostgreSQL 15 (already in use)
- WSL2 configuration access (Windows users)

**Internal Dependencies**:
- Existing migrations must not conflict with new type cleanup
- Dockerfile changes must maintain compatibility with production

---

## Open Questions

None - all unknowns resolved in research.md

---

## Next Steps

After this plan is approved:

1. **Run `/speckit.tasks`** - Generate actionable tasks from this plan
2. **Implement Phase 1** - Migration safety (highest priority)
3. **Test Phase 1** - Verify IntegrityError is fixed
4. **Implement Phase 2** - WSL optimization
5. **Test Phase 2** - Verify no SIGBUS errors
6. **Implement Phase 3-4** - Health checks and documentation
7. **Final Testing** - Verify all success criteria met

---

## References

- [spec.md](./spec.md) - Feature specification with user stories
- [research.md](./research.md) - Technical research and solution evaluation
- [data-model.md](./data-model.md) - Docker entities and state machines
- [quickstart.md](./quickstart.md) - Deployment and troubleshooting guide
- [contracts/deployment-contract.md](./contracts/deployment-contract.md) - Service contracts and SLAs
