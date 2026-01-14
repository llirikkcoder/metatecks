#!/bin/bash
# ==============================================
# Скрипт автоматической настройки для WSL/Linux
# ==============================================

set -e  # Остановить выполнение при ошибке

echo "========================================"
echo "Настройка локального окружения Django"
echo "========================================"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода успешного сообщения
success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Функция для вывода предупреждения
warning() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Функция для вывода ошибки
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Проверка Python3
echo "1. Проверка Python..."
if ! command -v python3 &> /dev/null; then
    error "Python3 не установлен!"
    echo "Установите Python3:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
success "Python установлен: $PYTHON_VERSION"
echo ""

# 2. Проверка pip
echo "2. Проверка pip..."
if ! command -v pip3 &> /dev/null; then
    warning "pip3 не найден, устанавливаю..."
    sudo apt update
    sudo apt install -y python3-pip
fi
success "pip установлен: $(pip3 --version)"
echo ""

# 3. Удаление старого venv если он из Windows
echo "3. Проверка виртуального окружения..."
if [ -d "venv" ]; then
    # Проверяем, не из Windows ли это venv
    if [ -f "venv/Scripts/activate" ]; then
        warning "Обнаружено виртуальное окружение Windows, удаляю..."
        rm -rf venv
        success "Старое окружение удалено"
    else
        warning "Виртуальное окружение уже существует"
        read -p "Удалить и создать заново? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            success "Старое окружение удалено"
        fi
    fi
fi
echo ""

# 4. Создание виртуального окружения
echo "4. Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Виртуальное окружение создано"
else
    warning "Виртуальное окружение уже существует"
fi
echo ""

# 5. Активация виртуального окружения
echo "5. Активация виртуального окружения..."
source venv/bin/activate
success "Виртуальное окружение активировано"
echo ""

# 6. Обновление pip
echo "6. Обновление pip..."
pip install --upgrade pip --quiet
success "pip обновлен: $(pip --version)"
echo ""

# 7. Установка зависимостей
echo "7. Установка зависимостей проекта..."
echo "   Это может занять несколько минут..."

# Сначала устанавливаем базовые зависимости
if [ -f "requirements-conda.txt" ]; then
    echo "   - Устанавливаю requirements-conda.txt..."
    pip install -r requirements-conda.txt --quiet
    success "requirements-conda.txt установлен"
fi

if [ -f "requirements-pip.txt" ]; then
    echo "   - Устанавливаю requirements-pip.txt..."
    # Устанавливаем построчно, пропуская строки с git+https
    while IFS= read -r line || [ -n "$line" ]; do
        # Пропускаем пустые строки и комментарии
        if [[ -z "$line" ]] || [[ "$line" =~ ^# ]]; then
            continue
        fi

        # Пропускаем git+https строки (установим их отдельно)
        if [[ "$line" =~ ^git\+https ]]; then
            continue
        fi

        # Устанавливаем пакет
        pip install "$line" --quiet || warning "Не удалось установить: $line"
    done < requirements-pip.txt
    success "requirements-pip.txt установлен"
fi

# Пытаемся установить django-watson
echo "   - Устанавливаю django-watson..."
pip install "git+https://github.com/etianen/django-watson.git@refs/pull/309/head" --quiet 2>/dev/null && success "django-watson установлен" || warning "django-watson пропущен (не критично)"
echo ""

# 8. Создание необходимых директорий
echo "8. Создание директорий..."
mkdir -p logs
success "Создана директория logs"

mkdir -p media
success "Создана директория media"

mkdir -p static
success "Создана директория static"
echo ""

# 9. Проверка .env файла
echo "9. Проверка .env файла..."
if [ -f ".env" ]; then
    success ".env файл существует"
else
    warning ".env файл не найден - убедитесь, что он настроен"
fi
echo ""

# 10. Применение миграций
echo "10. Применение миграций базы данных..."
python manage.py migrate
success "Миграции применены"
echo ""

# 11. Сбор статики
echo "11. Сбор статических файлов..."
python manage.py collectstatic --noinput --clear
success "Статические файлы собраны"
echo ""

# 12. Предложение создать суперпользователя
echo "========================================"
echo "Настройка завершена успешно!"
echo "========================================"
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Создать суперпользователя (администратора):"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Запустить сервер разработки:"
echo "   python manage.py runserver"
echo ""
echo "3. Открыть в браузере:"
echo "   http://localhost:8000/admin/"
echo ""
echo "Для работы с виртуальным окружением в следующий раз:"
echo "   source venv/bin/activate"
echo ""

# Спросить, создать ли суперпользователя сейчас
read -p "Создать суперпользователя сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
    echo ""
    success "Суперпользователь создан"
fi

echo ""
echo "========================================"
echo "Готово! Запустите сервер:"
echo "  python manage.py runserver"
echo "========================================"
