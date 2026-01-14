# Deployment Contract: Docker Services

**Feature**: 002-fix-docker-deployment
**Version**: 1.0
**Date**: 2026-01-14

## Overview

This document defines the contracts between Docker services, health checks, and deployment expectations.

---

## Service Health Contracts

### PostgreSQL (db) Contract

**Health Check Endpoint**: `pg_isready -U metateks`

**Expected Behavior**:
| State | Exit Code | Meaning |
|-------|-----------|---------|
| Ready | 0 | Accepting connections |
| Not Ready | 1 | Not accepting connections yet |
| Error | 2 | Connection error |

**Dependencies**: None

**Dependents**: web, celery

**Contract Guarantee**:
- Returns exit code 0 when database is ready to accept connections
- Responds within 5 seconds timeout
- Retries every 10 seconds until ready

---

### Redis (redis) Contract

**Health Check Endpoint**: `redis-cli ping`

**Expected Behavior**:
| Response | Meaning |
|----------|---------|
| PONG | Ready |
| (no response) | Not ready or error |

**Dependencies**: None

**Dependents**: web, celery

**Contract Guarantee**:
- Returns "PONG" when Redis is operational
- Responds within 3 seconds timeout
- Retries every 10 seconds until ready

---

### Django Web (web) Contract

**Health Check Endpoint**: `curl -f http://localhost:8000/admin/login/`

**Expected Behavior**:
| HTTP Code | Meaning |
|-----------|---------|
| 200 | Application ready |
| 000 | Connection failed |
| 500 | Application error |

**Dependencies**: db (healthy), redis (healthy)

**Dependents**: nginx

**Initialization Sequence** (must complete within start_period: 40s):
1. Wait for PostgreSQL (Python script, 30 retries × 2s = 60s max)
2. Run migrations: `python manage.py migrate --noinput`
3. Collect static: `python manage.py collectstatic --noinput`
4. Load fixtures (if first run)
5. Build search index: `python manage.py buildwatson`
6. Start Gunicorn: `gunicorn --bind 0.0.0.0:8000`

**Contract Guarantee**:
- HTTP 200 response on /admin/login/ within 40 seconds of container start
- All migrations applied before Gunicorn starts
- Database connections established before web server starts

---

### Celery Worker Contract (Proposed)

**Health Check Endpoint**: `celery -A main inspect ping`

**Expected Behavior**:
| Response | Meaning |
|----------|---------|
| pong | Worker responding |
| (no response) | Worker not ready |

**Dependencies**: db (healthy), redis (healthy)

**Dependents**: None (background worker)

**Contract Guarantee**:
- Worker responds to ping within 10 seconds
- Worker is connected to Redis broker
- Worker can reach database

---

### Nginx Contract

**Health Check**: Implicit (container running = healthy)

**Dependencies**: web (healthy)

**Reverse Proxy Configuration**:
```nginx
upstream web {
    server web:8000;
}

server {
    listen 80;
    server_name localhost;

    location /static/ {
        alias /app/static/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Contract Guarantee**:
- Proxies requests to web:8000
- Serves static files from static_volume
- Serves media files from ./media mount

---

## Database Migration Contract

### Idempotency Requirement

**Contract**: All migrations must be safe to run multiple times

**Current Issue**: `orders_deliverycompany` type may persist

**Guarantee After Fix**:
```python
# Each migration with CreateModel must:
1. Check if type exists
2. Drop type if exists (CASCADE)
3. Create model
4. Log any type cleanup
```

**Expected Behavior**:
| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| First run | ✅ Success | ✅ Success |
| Re-run migrations | ❌ IntegrityError | ✅ Success |
| Downgrade + Upgrade | ❌ IntegrityError | ✅ Success |
| Fresh volume | ✅ Success | ✅ Success |

---

## Volume Persistence Contract

### postgres_data Volume

**Contains**: All PostgreSQL data files, including composite types

**Lifecycle**:
- Created on first `docker compose up -d`
- Persists across `docker compose down`
- Removed only with `docker compose down -v`

**Contract**:
- Database state fully persisted
- Composite types included in volume
- Safe to remove volume for fresh start (dev environment)

### redis_data Volume

**Contains**: Redis AOF (Append Only File)

**Contract**:
- Redis commands persisted to disk
- Survives container restarts
- Safe to remove for cache reset

### static_volume Volume

**Contains**: Collected static files

**Lifecycle**:
- Populated by `python manage.py collectstatic`
- Read-only mounted to nginx
- Regenerated on each web container start

**Contract**:
- Static files available to nginx
- Synchronized with Django static files
- No manual intervention required

---

## Startup Ordering Contract

### Required Startup Sequence

```
Time 0s:
    db starting → healthcheck starts (pg_isready every 10s)
    redis starting → healthcheck starts (ping every 10s)

Time ~10-30s:
    db healthy → condition satisfied
    redis healthy → condition satisfied

Time ~30s:
    web starts → entrypoint script runs
    celery starts → worker initializes

Time ~30-70s:
    web entrypoint:
      - Wait for DB (up to 60s)
      - Run migrations (expected < 10s)
      - Collect static (expected < 5s)
      - Load fixtures if needed (expected < 5s)
      - Start Gunicorn

Time ~70s:
    web healthcheck starts (curl every 30s, start_period 40s)

Time ~110s:
    web healthy → condition satisfied

Time ~110s:
    nginx starts
```

### Contract Violations

| Violation | Symptom | Impact |
|-----------|---------|--------|
| DB never healthy | web hangs forever | System unavailable |
| Migration fails | web container exits | System unavailable |
| Migration IntegrityError | web container exits | System unavailable |
| Web never healthy | nginx never starts | System unavailable |

---

## Environment Variable Contract

### Required Variables (.env.docker)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DEBUG | Yes | False | Django debug mode |
| SECRET_KEY | Yes | N/A | Django secret key |
| DATABASE_URL | No | postgresql://... | PostgreSQL connection |
| POSTGRES_DB | No | metateks | Database name |
| POSTGRES_USER | No | metateks | Database user |
| POSTGRES_PASSWORD | No | metateks_password | Database password |
| REDIS_URL | No | redis://redis:6379/1 | Redis connection |
| DJANGO_LOG_DIR | No | logs | Log directory |

**Contract**:
- All required variables must be set or have defaults
- Missing required variable causes container exit
- Variable changes require container restart

---

## Network Contract

### Service Discovery

**Network Name**: metateks_network

**DNS Resolution**:
| Service | Hostname | Internal Port |
|---------|----------|---------------|
| db | db | 5432 |
| redis | redis | 6379 |
| web | web | 8000 |
| celery | celery | N/A |
| nginx | nginx | 80 |

**Contract Guarantee**:
- All services can reach each other by hostname
- Services outside network cannot reach internal ports
- Web port 8001 exposed only to localhost (127.0.0.1)

---

## Performance Contract

### Startup Time SLA

| Phase | Expected Max Time |
|-------|-------------------|
| DB + Redis ready | 30s |
| Web migrations | 15s |
| Web health check | 40s (start_period) |
| **Total system ready** | **90s** |

### Resource Limits

| Service | Expected RAM | Expected CPU |
|---------|-------------|--------------|
| db | 256MB | 0.5 core |
| redis | 64MB | 0.1 core |
| web | 512MB | 1-4 cores |
| celery | 256MB | 2 cores |
| nginx | 32MB | 0.1 core |
| **Total** | **~1.1GB** | **~4 cores** |

---

## Error Handling Contract

### Container Restart Policy

**Policy**: `restart: unless-stopped`

**Behavior**:
| Scenario | Action |
|----------|--------|
| Container exits (code 0) | No restart |
| Container exits (code != 0) | Restart immediately |
| Manual stop | No restart |
| Daemon restart | Restart all containers |

### Log Output Contract

**Stdout/Stderr**:
- All application logs to stdout
- Errors to stderr
- Structured logging preferred

**Log Locations**:
- Container logs: `docker compose logs <service>`
- Host logs: `./logs/` directory (mounted)

---

## Security Contract

### Minimal Exposure

| Service | Ports Exposed | To |
|---------|---------------|-----|
| db | None | Internal only |
| redis | None | Internal only |
| web | 8001 → localhost only | Host machine |
| celery | None | Internal only |
| nginx | 8080 → localhost | Host machine |

### Trust Boundaries

**Trusted**: Internal Docker network (metateks_network)
**Untrusted**: External network traffic

**Contract**:
- No database access from external network
- No Redis access from external network
- Web server behind nginx reverse proxy
- All inter-service communication via internal network

---

## Monitoring Contract

### Health Check Status

**Query health**:
```bash
docker compose ps
```

**Expected Output**:
```
NAME              STATUS
metateks_db       Up (healthy)
metateks_redis    Up (healthy)
metateks_web      Up (healthy)
metateks_celery   Up
metateks_nginx    Up
```

### Log Monitoring

**Key log patterns to monitor**:
| Pattern | Severity | Action |
|---------|----------|--------|
| IntegrityError | CRITICAL | Investigate immediately |
| SIGBUS | CRITICAL | Check WSL configuration |
| OperationalError | ERROR | Check database connectivity |
| "healthy" | INFO | Expected (health check passed) |

---

## Version Contract

### Component Versions

| Component | Version | Contract |
|-----------|---------|----------|
| PostgreSQL | 15-alpine | Fixed in docker-compose.yml |
| Redis | 7-alpine | Fixed in docker-compose.yml |
| Python | 3.11-slim | Fixed in Dockerfile |
| Django | 4.2.13 | Fixed in requirements |
| Docker Compose | 2.0+ | Minimum version |

**Contract**:
- Image versions pinned in docker-compose.yml
- Python version pinned in Dockerfile
- Requirements versions pinned in requirements*.txt
- Updates require explicit version change

---

## Rollback Contract

### Deployment Rollback

**Scenario**: New deployment fails

**Rollback Steps**:
```bash
# Stop new deployment
docker compose down

# Revert docker-compose.yml to previous version
git checkout HEAD~1 docker-compose.yml

# Restart with previous configuration
docker compose up -d
```

**Contract**:
- Volumes persist across rollback
- Database state maintained
- No data loss in rollback scenario
