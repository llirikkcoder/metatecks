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
    ca-certificates \
    git \
    # Для переключения пользователя
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Корневой сертификат «Минцифры» (Russian Trusted Root CA) — им подписаны
# платёжный шлюз Альфа-Банка (alfa.rbsuat.com, payment.alfabank.ru) и другие
# госресурсы РФ. В стандартном наборе CA его нет, без него requests падает
# с SSLError: certificate verify failed на любом обращении к шлюзу.
COPY conf/certs/russian_trusted_root_ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# requests проверяет сертификаты по своему набору certifi, а не по системному
# хранилищу, поэтому одного update-ca-certificates мало — явно указываем бандл
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

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

# НЕ переключаемся на пользователя здесь - делаем это в entrypoint
# USER metateks

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
