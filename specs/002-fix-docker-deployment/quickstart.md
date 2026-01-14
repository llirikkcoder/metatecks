# Quickstart: Docker Развертывание

**Feature**: 002-fix-docker-deployment
**Last Updated**: 2026-01-14

## Prerequisites

### Required Software
| Software | Minimum Version | Installation Check |
|----------|----------------|-------------------|
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.0+ | `docker compose version` |
| Python (for local) | 3.11+ | `python3 --version` |
| Git | Any | `git --version` |

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

---

## Installation Guide

### Option 1: WSL2 (Windows) - Recommended for Devs

#### Step 1: Configure WSL2

Create/Edit `C:\Users\<YourUser>\.wslconfig`:
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
```

Restart WSL2:
```powershell
wsl --shutdown
wsl
```

#### Step 2: Move Project to WSL Filesystem (Critical!)

**Why**: Prevents SIGBUS errors during Docker build

```bash
# In WSL terminal
cd ~
mkdir -p projects
cp -r /mnt/c/_KIPOL/_WORK/_metateks ~/projects/metateks
cd ~/projects/metateks
```

#### Step 3: Start Docker

```bash
# Verify Docker is running
docker ps

# Start all services
docker compose up -d

# Check logs
docker compose logs -f web
```

---

### Option 2: Native Linux / macOS

```bash
# Clone or navigate to project
cd /path/to/metateks

# Start services
docker compose up -d

# Check status
docker compose ps
```

---

### Option 3: Local Development (without Docker)

See `README_WSL.md` for detailed instructions.

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## Troubleshooting

### Issue 1: IntegrityError "orders_deliverycompany" already exists

**Symptom**:
```
django.db.utils.IntegrityError: duplicate key value violates unique constraint
Key (typname, typnamespace)=(orders_deliverycompany, 2200) already exists.
```

**Cause**: PostgreSQL composite type persists after table drop

**Solutions**:

#### Option A: Clean Restart (Recommended for Dev)
```bash
# Stop and remove all containers, volumes
docker compose down -v

# Start fresh
docker compose up -d
```

#### Option B: Manual Type Cleanup
```bash
# Connect to database
docker exec -it metateks_db psql -U metateks -d metateks

# Drop the type manually
DROP TYPE IF EXISTS orders_deliverycompany CASCADE;

# Exit psql
\q

# Restart web container
docker compose restart web
```

#### Option C: Run Fix Migration
```bash
# Apply the fix migration (after implementation)
docker exec metateks_web python manage.py migrate orders 0008_fix_delivery_company_type
```

---

### Issue 2: SIGBUS Error During Docker Build

**Symptom**:
```
fatal error: fault [signal SIGBUS: bus error code=0x2 addr=0x387405c pc=0x466a49]
```

**Cause**: Building on Windows filesystem from WSL2

**Solutions**:

#### Option A: Move to WSL Filesystem (Best Fix)
```bash
# Copy project to WSL home
cp -r /mnt/c/_KIPOL/_WORK/_metatecks ~/projects/metateks
cd ~/projects/metateks

# Rebuild
docker compose build --no-cache
```

#### Option B: Increase WSL Memory
```ini
# C:\Users\<You>\.wslconfig
[wsl2]
memory=8GB
processors=4
```

```powershell
wsl --shutdown
# Wait 10 seconds, restart WSL
```

---

### Issue 3: Containers Not Starting

**Check Services**:
```bash
# See all containers
docker compose ps

# Check logs for specific service
docker compose logs web
docker compose logs db
```

**Common Fixes**:
```bash
# Rebuild if Dockerfile changed
docker compose build --no-cache

# Remove stuck containers
docker compose down --remove-orphans

# Restart Docker Desktop (Windows/macOS)
```

---

### Issue 4: Database Connection Errors

**Symptom**: `could not connect to server: Connection refused`

**Check**:
```bash
# Verify db is healthy
docker compose ps db

# Check db logs
docker compose logs db

# Wait for db to be ready
docker exec metateks_db pg_isready -U metateks
```

**Fix**: Ensure web container waits for db health check (already configured)

---

### Issue 5: Permissions on mounted volumes

**Symptom**: `Permission denied: /app/media` or `/app/logs`

**Fix**:
```bash
# On host, fix ownership
sudo chown -R $USER:$USER media logs

# Or run container with correct user (already configured in Dockerfile)
```

---

## Common Commands

### Viewing Logs
```bash
# Follow logs for all services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f db

# Last 100 lines
docker compose logs --tail=100 web
```

### Database Management
```bash
# Access PostgreSQL shell
docker exec -it metateks_db psql -U metateks -d metateks

# Run migrations manually
docker exec metateks_web python manage.py migrate

# Create superuser
docker exec -it metateks_web python manage.py createsuperuser

# Load fixtures manually
docker exec metateks_web python manage.py loaddata fixtures/20240902_brands.json
```

### Maintenance
```bash
# Rebuild images
docker compose build

# Clean restart (keeps volumes)
docker compose down && docker compose up -d

# Fresh start (removes database!)
docker compose down -v && docker compose up -d

# Clean up unused resources
docker system prune -a
```

---

## Verification Steps

After deployment, verify the system is working:

### 1. Check Container Health
```bash
docker compose ps
```
Expected output: All services show "Up" and "healthy"

### 2. Check Application URL
```bash
curl http://localhost:8080/
# Should return HTML response
```

### 3. Access Django Admin
```
URL: http://localhost:8080/admin/
Login: Use your superuser credentials
```

### 4. Verify Database Connectivity
```bash
docker exec metateks_web python manage.py dbshell
# Should enter psql shell
```

---

## Production Deployment Notes

### For VPS/Server Deployment

1. **Update Environment Variables**:
   ```bash
   # Edit .env.docker
   DEBUG=False
   SECRET_KEY=<generate secure key>
   DATABASE_URL=postgresql://user:pass@localhost/db
   ```

2. **Configure Nginx**:
   - Update `docker/nginx/conf.d/default.conf`
   - Set proper server_name and SSL

3. **Firewall Rules**:
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ```

4. **Run behind System Nginx** (optional):
   ```bash
   # docker-compose.yml already binds to 127.0.0.1:8080
   # Configure system nginx to proxy_pass to localhost:8080
   ```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start all services | `docker compose up -d` |
| Stop all services | `docker compose down` |
| View logs | `docker compose logs -f` |
| Rebuild images | `docker compose build --no-cache` |
| Fresh restart | `docker compose down -v && docker compose up -d` |
| Access DB shell | `docker exec -it metateks_db psql -U metateks -d metateks` |
| Run migrations | `docker exec metateks_web python manage.py migrate` |
| Create superuser | `docker exec -it metateks_web python manage.py createsuperuser` |
| Access Django shell | `docker exec -it metateks_web python manage.py shell` |

---

## Getting Help

If issues persist:

1. **Check logs**: `docker compose logs <service>`
2. **Verify configuration**: Check `docker-compose.yml` and `.env.docker`
3. **Consult documentation**: `docs/DOCKER_DEPLOYMENT.md`
4. **Check issues**: Known issues documented in research.md

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (8080)                          │
│                    Reverse Proxy / Static                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Web (8001)   │
                    │  Django + Gunicorn│
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────┐
│  PostgreSQL    │  │     Redis      │  │  Celery    │
│  (5432 internal)│ │ (6379 internal) │  │  Worker    │
└────────────────┘  └────────────────┘  └────────────┘
```
