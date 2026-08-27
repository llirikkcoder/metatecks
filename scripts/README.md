# Скрипты миграции и выгрузки данных

Эта директория содержит автоматизированные скрипты для миграции и выгрузки данных с VPS.

## Доступные скрипты

### 1. `full_vps_download.sh` - ПОЛНАЯ выгрузка всех данных ⭐ НОВОЕ

Самый полный скрипт - выгружает ВСЁ: БД, медиа, статику, конфиги, логи.

**Использование:**

```bash
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"
export VPS_PATH="/home/mt/metateks-dev"

./scripts/full_vps_download.sh
```

**Что делает:**
1. ✅ Проверяет доступ к VPS
2. ✅ Анализирует структуру проекта и размеры
3. ✅ Создает дамп БД (Django dumpdata)
4. ✅ Скачивает дамп
5. ✅ Синхронизирует все медиа-файлы
6. ✅ Предлагает скачать static/, assets/, конфиги, логи
7. ✅ Создает папку `vps_backup_YYYYMMDD_HHMMSS/` со всем
8. ✅ Генерирует README с инструкциями

**Когда использовать:**
- 🎯 Первая миграция с VPS
- 🎯 Нужен полный бэкап
- 🎯 Не уверены что именно нужно
- 🎯 Хотите сохранить всё

---

### 2. `migrate_from_vps.sh` - PostgreSQL миграция

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

### 3. `migrate_django_json.sh` - Универсальная миграция через Django

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

### 4. `check_vps_data.sh` - Проверка данных на VPS

Проверяет что есть на VPS без загрузки.

```bash
export VPS_USER="your_username"
export VPS_HOST="your_vps_ip"
./scripts/check_vps_data.sh
```

---

### 5. `monitor_1c.sh` - Мониторинг 1С интеграции

Интерактивный мониторинг обмена с 1С.

```bash
./scripts/monitor_1c.sh
```

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
export VPS_HOST="metateks-admin.vinodesign.ru"
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

## Какой скрипт использовать?

| Ситуация | Скрипт | Описание |
|----------|--------|----------|
| **Первая миграция, нужно всё** | `full_vps_download.sh` | Выгрузит всё подряд |
| **Быстрая миграция PostgreSQL** | `migrate_from_vps.sh` | PostgreSQL → PostgreSQL |
| **Универсальная миграция** | `migrate_django_json.sh` | Через Django (любая БД) |
| **Проверить что есть на VPS** | `check_vps_data.sh` | Только проверка |
| **Мониторинг 1С** | `monitor_1c.sh` | После миграции |

**Рекомендация:** Начните с `full_vps_download.sh` - он выгрузит всё и создаст структурированный бэкап.

---

## Дополнительная информация

**Документация:**
- [VPS_FULL_BACKUP.md](../docs/VPS_FULL_BACKUP.md) - Полная инструкция по выгрузке
- [VPS_QUICK_DOWNLOAD.md](../docs/VPS_QUICK_DOWNLOAD.md) - Быстрая шпаргалка
- [MIGRATION_FROM_VPS.md](../docs/MIGRATION_FROM_VPS.md) - Подробная миграция
