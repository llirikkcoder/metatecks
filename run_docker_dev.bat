@echo off
chcp 65001 >nul
REM Metateks Docker dev environment

echo ========================================
echo   Metateks - Docker Dev Environment
echo ========================================
echo.

echo ==^> Starting containers...
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers. Check Docker Desktop is running.
    pause
    exit /b 1
)

echo.
echo ==^> Container status:
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps

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
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f web
