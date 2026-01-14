@echo off
REM Скрипт быстрой настройки для локальной разработки

echo ========================================
echo Настройка локального окружения Django
echo ========================================

REM Создать директорию для логов
if not exist logs mkdir logs
echo [OK] Создана директория logs

REM Создать директорию для медиа файлов
if not exist media mkdir media
echo [OK] Создана директория media

REM Создать .env если его нет
if not exist .env (
    echo SECRET_KEY=local-dev-secret-key-change-in-production > .env
    echo DEBUG=True >> .env
    echo ALLOWED_HOSTS=localhost 127.0.0.1 >> .env
    echo DEFAULT_SITENAME=localhost:8000 >> .env
    echo DATABASE_URL= >> .env
    echo REDIS_URL=redis://localhost:6379/1 >> .env
    echo [OK] Создан файл .env
) else (
    echo [INFO] Файл .env уже существует
)

echo.
echo ========================================
echo Готово! Теперь выполните:
echo   python manage.py migrate
echo   python manage.py createsuperuser
echo   python manage.py runserver
echo ========================================
pause
