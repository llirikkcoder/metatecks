# Скрипты миграции базы данных

Эта директория содержит автоматизированные скрипты для миграции базы данных с VPS на локальный Docker.

## Доступные скрипты

### 1. `migrate_from_vps.sh` - PostgreSQL миграция (рекомендуется)

Полностью автоматизированный скрипт для миграции PostgreSQL базы данных.

**Использование:**

```bash
# Настройте переменные окружения
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"
export VPS_PATH="/home/mt/metateks-dev"

# Запустите скрипт
./scripts/migrate_from_vps.sh
```

**Что делает:**
1. ✅ Создает дамп PostgreSQL на VPS
2. ✅ Скачивает дамп на локальный компьютер
3. ✅ Синхронизирует медиа-файлы (опционально)
4. ✅ Пересоздает локальную базу данных
5. ✅ Восстанавливает дамп в Docker PostgreSQL
6. ✅ Запускает все сервисы
7. ✅ Проверяет результат

---

### 2. `migrate_django_json.sh` - Универсальная миграция через Django

Использует Django dumpdata/loaddata для миграции. Подходит для любых баз данных.

**Использование:**

```bash
# Настройте переменные окружения
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"
export VPS_PATH="/home/mt/metateks-dev"

# Запустите скрипт
./scripts/migrate_django_json.sh
```

**Когда использовать:**
- ✅ Миграция SQLite → PostgreSQL
- ✅ Когда нет прямого доступа к PostgreSQL на VPS
- ✅ Для выборочной миграции данных

**Что делает:**
1. ✅ Создает JSON дамп через Django на VPS
2. ✅ Скачивает дамп
3. ✅ Пересоздает локальную базу
4. ✅ Загружает данные через Django loaddata
5. ✅ Пересоздает поисковый индекс

---

## Настройка параметров

### Способ 1: Переменные окружения

```bash
export VPS_USER="your_username"
export VPS_HOST="192.168.1.100"
export VPS_PATH="/home/mt/metateks-dev"
export DB_NAME="metateks"
export DB_USER="metateks"

./scripts/migrate_from_vps.sh
```

### Способ 2: Редактирование скрипта

Откройте скрипт и измените значения в начале файла:

```bash
VPS_USER="your_username"
VPS_HOST="192.168.1.100"
VPS_PATH="/home/mt/metateks-dev"
```

---

## Требования

### На VPS:
- SSH доступ
- PostgreSQL установлен (для migrate_from_vps.sh)
- Python и Django настроены (для migrate_django_json.sh)

### На локальном компьютере:
- Docker и Docker Compose
- SSH клиент
- SCP/rsync (для копирования файлов)

---

## Пример полного процесса

```bash
# 1. Настройка переменных
export VPS_USER="kipol"
export VPS_HOST="metateks.vlch.dev"
export VPS_PATH="/home/mt/metateks-dev"

# 2. Запуск миграции
cd /mnt/c/_KIPOL/_WORK/_metatecks
./scripts/migrate_from_vps.sh

# 3. Проверка результата
docker-compose ps
curl http://localhost/

# 4. Вход в админку
# Откройте http://localhost/admin/
# Используйте учетные данные с VPS
```

---

## Решение проблем

### Ошибка: "Permission denied (publickey)"

Настройте SSH ключ или используйте пароль:

```bash
ssh-copy-id $VPS_USER@$VPS_HOST
```

### Ошибка: "pg_dump: command not found"

На VPS не установлен PostgreSQL. Используйте `migrate_django_json.sh`.

### Ошибка при восстановлении дампа

Попробуйте вручную с дополнительными флагами:

```bash
docker-compose exec db pg_restore \
  -U metateks \
  -d metateks \
  -v -c --clean --if-exists --no-owner --no-acl \
  /tmp/metateks_dump.backup
```

---

## Безопасность

⚠️ **ВАЖНО:**
- Дампы баз данных содержат конфиденциальные данные
- Файлы `*.backup`, `*.sql`, `*_dump.json` добавлены в `.gitignore`
- Удаляйте дампы после успешной миграции
- Не храните дампы в публичных местах

```bash
# Удаление дампов
rm -f *.backup *.sql *_dump.json
```

---

## Дополнительная информация

Подробная инструкция по миграции: [DATABASE_MIGRATION.md](../DATABASE_MIGRATION.md)
