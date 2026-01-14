# SIGBUS Error Troubleshooting (WSL2)

**Last Updated**: 2026-01-14
**Issue**: SIGBUS errors during Docker build in WSL2

## Symptoms

```
fatal error: fault [signal SIGBUS: bus error code=0x2 addr=0x387405c pc=0x466a49]
```

Ошибка происходит во время `docker compose build` или `docker build` при работе в WSL2.

## Root Cause

SIGBUS (Signal BUS Error) в WSL2 возникает из-за проблем с cross-filesystem доступом:
- Docker build context находится на Windows filesystem (NTFS)
- WSL2 монтирует Windows диски через 9P/virtiofs протокол
- При больших операциях I/O (сборка образов) возникают memory alignment issues
- Ограниченная память в WSL2 может вызывать ошибки при тяжелых операциях

## Solutions

### Solution 1: Переместить проект в WSL Filesystem (РЕКОМЕНДУЕТСЯ)

**Почему это работает**: WSL filesystem (ext4) - native для Linux, нет cross-FS проблем

```bash
# 1. Скопируйте проект в WSL home
cd ~
mkdir -p projects
cp -r /mnt/c/_KIPOL/_WORK/_metateks ~/projects/metateks

# 2. Перейдите в новое расположение
cd ~/projects/metateks

# 3. Пересоберите образы (должно пройти без SIGBUS)
docker compose build --no-cache
```

### Solution 2: Увеличить память WSL2

**Файл**: `C:\Users\<YourUser>\.wslconfig`

```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
```

**Применить**:
```powershell
# В PowerShell или CMD
wsl --shutdown
# Подождите 10 секунд, затем запустите WSL снова
```

### Solution 3: Оптимизировать Dockerfile

Используйте multi-stage build для уменьшения нагрузки:

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
# Install build dependencies and Python packages
# ...

# Final stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
# Install only runtime dependencies
# ...
```

### Solution 4: Использовать BuildKit (экспериментально)

```bash
export DOCKER_BUILDKIT=1
docker compose build
```

## Verification

После применения решения:

```bash
# Тестовая сборка
docker compose build --no-cache

# Если успешно - запуск контейнеров
docker compose up -d

# Проверка статуса
docker compose ps
```

## Known Limitations

Даже после применения решений:
- Крупные сборки (>2GB образы) могут все равно вызывать проблемы
- Рекомендуется использовать Docker BuildKit для сложных проектов
- Для production лучше использовать нативный Linux или macOS

## Additional Resources

- [WSL2 Configuration](https://docs.microsoft.com/en-us/windows/wsl/wsl-config)
- [Docker Desktop WSL2 Backend](https://docs.docker.com/desktop/windows/wsl/)
- `.wslconfig.example` в корне проекта

## Quick Reference

| Problem | Solution | Command |
|---------|----------|---------|
| SIGBUS на сборке | Переместить в WSL FS | `cp -r /mnt/c/... ~/projects/...` |
| SIGBUS + малая память | Увеличить память | Edit `.wslconfig` |
| Медленная сборка | Multi-stage build | Оптимизировать Dockerfile |
