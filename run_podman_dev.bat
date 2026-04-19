@echo off
chcp 65001 >nul
REM Metateks Podman dev environment

echo ========================================
echo   Metateks - Podman Dev Environment
echo ========================================
echo.

REM Check podman-compose is available
where podman-compose >nul 2>&1
if errorlevel 1 (
    echo [ERROR] podman-compose not found. Run: pip install podman-compose
    pause
    exit /b 1
)

echo ==^> Starting containers...
podman-compose -p metateks -f docker-compose.yml -f docker-compose.dev.yml up -d
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers. Check Podman machine is running:
    echo   podman machine start
    pause
    exit /b 1
)

echo.
echo ==^> Container status:
podman-compose -p metateks -f docker-compose.yml -f docker-compose.dev.yml ps

echo.
echo ========================================
echo   URLs
echo ========================================
echo   Site (via nginx):    http://localhost
echo   Django direct:       http://localhost:9000
echo   PostgreSQL:          localhost:5432
echo   Redis:               localhost:6379
echo ========================================
echo.
echo ==^> Following web logs (Ctrl+C to stop watching, containers keep running)
echo.
podman-compose -p metateks -f docker-compose.yml -f docker-compose.dev.yml logs -f web
