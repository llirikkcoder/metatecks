# Базовый образ Python
FROM python:3.11-slim

# Метаданные
LABEL maintainer="metateks@example.com"
LABEL description="Metateks E-commerce Platform"

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Рабочая директория
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Для Pillow (обработка изображений)
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    # Для PostgreSQL
    libpq-dev \
    # Утилиты
    gcc \
    g++ \
    make \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements-conda.txt requirements-pip.txt ./

# Установка Python зависимостей
RUN pip install --upgrade pip && \
    pip install -r requirements-conda.txt && \
    pip install -r requirements-pip.txt && \
    pip install gunicorn psycopg2-binary

# Копирование кода приложения
COPY . .

# Создание директорий для media, static, logs
RUN mkdir -p /app/media /app/static /app/logs

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 metateks && \
    chown -R metateks:metateks /app

# Переключение на непривилегированного пользователя
USER metateks

# Сбор статических файлов (будет выполнено в entrypoint)
# RUN python manage.py collectstatic --noinput

# Открытие порта
EXPOSE 8000

# Entrypoint скрипт
COPY --chown=metateks:metateks docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

# Команда по умолчанию
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "main.wsgi:application"]
