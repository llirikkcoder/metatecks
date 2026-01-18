# Локальный запуск приложения (без Docker)

## Состояние базы данных

База данных успешно заполнена фикстурами:
- ✅ **12 категорий**
- ✅ **185 подкатегорий**
- ✅ **24 бренда**
- ✅ **Баннеры, атрибуты, настройки, контент**

## Быстрый старт

1. **Запустите приложение:**
   ```bash
   run_local.bat
   ```

2. **Откройте в браузере:**
   http://localhost:8000

## Что было исправлено

### 1. База данных
- Изменен `DATABASE_URL` в `.env` с Docker-хоста `db` на локальный `127.0.0.1`
- Подключение к PostgreSQL: `postgresql://postgres:postgres@127.0.0.1:5432/metateks`

### 2. Логирование
- Изменен `DJANGO_LOG_DIR` в `.env` с `/app/logs` (Docker) на `logs` (локальный путь)

### 3. Виртуальное окружение
- Пересоздан `.venv` для правильной изоляции зависимостей
- Установлены все зависимости из requirements

### 4. Фикстуры
- Обновлены фикстуры для совместимости с текущими моделями:
  - Удалено устаревшее поле `id_1c` (удалено в миграции 0021)
  - Переименована модель `AdditionalProduct` → `ExtraProduct` (миграция 0026)
  - Удалены устаревшие поля `video_id`, `video_url`, `video_file`
- Загружены те же фикстуры, что и в Docker (см. `docker-entrypoint.sh`)

## Структура фикстур

Загружаются следующие фикстуры (как в Docker):
1. `20240722_addresses.json` - Адреса складов
2. `20240722_settings.json` - Настройки сайта
3. `20240722_content.json` - Контент страниц (частично - некоторые модели устарели)
4. `20240901_categories_and_models.json` - **Основной каталог** (категории, подкатегории, модели)
5. `20240902_brands.json` - Бренды
6. `20241105_attributes.json` - Атрибуты товаров
7. `20241201_banners.json` - Баннеры
8. `20241201_homepage.json` - Главная страница
9. `20250607_delivery_companies.json` - Транспортные компании
10. `20250820_cities.json` - Города

## Управление данными

### Пересоздать базу с нуля
```bash
# Удалить маркер загрузки фикстур
del .fixtures_loaded

# Очистить базу (опционально)
.venv\Scripts\python.exe manage.py flush --noinput

# Запустить run_local.bat - фикстуры загрузятся заново
run_local.bat
```

### Проверить количество данных
```bash
.venv\Scripts\python.exe manage.py shell -c "from apps.catalog.models import Category, SubCategory, Brand; print('Categories:', Category.objects.count(), '| SubCategories:', SubCategory.objects.count(), '| Brands:', Brand.objects.count())"
```

## Требования

- PostgreSQL 15+ запущен локально на порту 5432
- База данных `metateks` создана
- Пользователь PostgreSQL: `postgres` / пароль: `postgres`

## Примечания

- Фикстуры загружаются только при первом запуске (маркер `.fixtures_loaded`)
- Продукты (товары) не включены в фикстуры - они синхронизируются из 1C
- Некоторые модели из `20240722_content.json` устарели и пропускаются (например, `aboutbrand`)
