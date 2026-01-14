# Запуск проекта на WSL/Linux

## Быстрый старт (автоматическая установка)

```bash
# 1. Перейдите в директорию проекта
cd /mnt/c/_KIPOL/_WORK/_metatecks

# 2. Запустите скрипт автоматической настройки
./setup_local.sh

# 3. После завершения скрипта запустите сервер
source venv/bin/activate
python manage.py runserver
```

Откройте в браузере: http://localhost:8000/admin/

---

## Ручная установка (если нужно)

### 1. Установите Python3 и pip

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

### 2. Удалите старое виртуальное окружение (если было создано в Windows)

```bash
rm -rf venv
```

### 3. Создайте новое виртуальное окружение

```bash
python3 -m venv venv
```

### 4. Активируйте виртуальное окружение

```bash
source venv/bin/activate
```

### 5. Обновите pip

```bash
pip install --upgrade pip
```

### 6. Установите зависимости

```bash
# Установите зависимости из requirements
pip install -r requirements-conda.txt
pip install -r requirements-pip.txt

# Если django-watson не установился, установите вручную:
pip install "git+https://github.com/etianen/django-watson.git@refs/pull/309/head"
```

### 7. Создайте необходимые директории

```bash
mkdir -p logs media static
```

### 8. Примените миграции

```bash
python manage.py migrate
```

### 9. Соберите статические файлы

```bash
python manage.py collectstatic --noinput
```

### 10. Создайте суперпользователя

```bash
python manage.py createsuperuser
```

### 11. Запустите сервер

```bash
python manage.py runserver
```

---

## Дополнительные команды

### Celery (опционально)

Если нужны фоновые задачи:

```bash
# Установите Redis
sudo apt install redis-server

# Запустите Redis
sudo service redis-server start

# В отдельных терминалах:

# Terminal 1: Celery Worker
celery -A main worker --loglevel=info

# Terminal 2: Celery Beat
celery -A main beat --loglevel=info
```

### Полезные команды Django

```bash
# Создать новое приложение
python manage.py startapp app_name

# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Запустить shell Django
python manage.py shell

# Собрать статику
python manage.py collectstatic

# Запустить тесты
python manage.py test
```

---

## Устранение проблем

### Проблема: `python: command not found`

**Решение:**
```bash
# Python3 должен быть установлен
sudo apt install python3 python3-pip python3-venv

# Используйте python3 вместо python
python3 manage.py runserver
```

### Проблема: Ошибка с логами `FileNotFoundError: logs/`

**Решение:**
```bash
mkdir -p logs
```

### Проблема: `No module named 'dotenv'`

**Решение:**
```bash
pip install python-dotenv
```

### Проблема: Конфликт портов `Address already in use`

**Решение:**
```bash
# Запустите на другом порту
python manage.py runserver 8001

# Или найдите и остановите процесс на порту 8000
sudo lsof -ti:8000 | xargs kill -9
```

---

## Различия WSL vs Windows

| Параметр | Windows (CMD/PowerShell) | WSL/Linux |
|----------|--------------------------|-----------|
| **Команда Python** | `python` | `python3` |
| **Активация venv** | `venv\Scripts\activate` | `source venv/bin/activate` |
| **Путь к проекту** | `C:\_KIPOL\_WORK\_metatecks` | `/mnt/c/_KIPOL/_WORK/_metatecks` |
| **Разделитель путей** | `\` (обратный слеш) | `/` (прямой слеш) |
| **Установка пакетов** | `pip install` | `pip install` или `sudo apt install` |

---

## Структура проекта

```
metatecks/
├── apps/                 # Django приложения
├── main/                 # Настройки проекта
│   ├── settings/        # Конфигурация
│   └── urls.py          # URL маршруты
├── templates/           # HTML шаблоны
├── static/              # Статические файлы (CSS, JS, images)
├── media/               # Загруженные файлы
├── logs/                # Лог-файлы
├── venv/                # Виртуальное окружение (создается)
├── .env                 # Переменные окружения (для локальной разработки)
├── .env.docker          # Переменные окружения (для Docker)
├── manage.py            # Утилита управления Django
├── requirements.txt     # Зависимости Python
└── docker-compose.yml   # Конфигурация Docker
```

---

## Контакты и помощь

Если возникли проблемы:
1. Проверьте, что виртуальное окружение активировано
2. Убедитесь, что `.env` файл настроен правильно
3. Проверьте логи в директории `logs/`
