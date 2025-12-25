# Интеграция с 1С (CommerceML)

## 📋 Обзор

Проект **Метатэкс** имеет полную двустороннюю интеграцию с 1С через протокол **CommerceML 2.0**.

### ✅ Что синхронизируется из 1С → Django:

1. **Группы товаров (категории)**
   - Иерархическая структура категорий
   - Привязка к категориям и подкатегориям сайта

2. **Свойства (характеристики)**
   - Название свойства
   - Единица измерения
   - Тип значения (текст, число, справочник)
   - Варианты значений

3. **Бренды**
   - Автоматическое извлечение из названия товара
   - Привязка к брендам сайта

4. **Товары и модели**
   - Название товара
   - Артикул (vendor_code)
   - Штрихкод (bar_code)
   - Описание
   - Цена
   - **Изображения товаров** 📸
   - Характеристики (свойства)
   - Привязка к группам/категориям

5. **Склады**
   - Название склада
   - Адрес
   - Телефон
   - Привязка к складам сайта

6. **Остатки на складах**
   - Количество товара на каждом складе
   - Автоматический расчет общего количества

### ✅ Что синхронизируется из Django → 1С:

1. **Заказы**
   - Информация о заказе
   - Товары в заказе
   - Контактные данные клиента
   - Адрес доставки
   - Способ оплаты

---

## 🖼️ Синхронизация изображений

### Как это работает:

#### Шаг 1: 1С отправляет файлы на сайт

1С отправляет изображения вместе с XML файлами на endpoint:
```
POST /1c_exchange.php?type=catalog&mode=file&filename=picture.jpg
```

#### Шаг 2: Изображения сохраняются во временную директорию

Файл сохраняется в:
```
media/cml/tmp/picture.jpg
```

Исходный код: `apps/third_party/cml/views.py:43-60`

#### Шаг 3: XML содержит ссылку на изображение

В XML файле `import.xml` указывается путь к изображению:

```xml
<Товар>
    <Ид>00000001#00000001</Ид>
    <Наименование>Товар название</Наименование>
    <Картинка>picture.jpg</Картинка>
    ...
</Товар>
```

Исходный код: `apps/third_party/cml/utils.py:167-175`

#### Шаг 4: При синхронизации изображения копируются

Celery задача обрабатывает импорт и копирует изображения:

```python
# Из media/cml/tmp/picture.jpg
# В   media/models/photos_1c/picture.jpg
```

Процесс:
1. Проверяется, является ли файл изображением
2. Копируется в постоянную директорию `media/models/photos_1c/`
3. Привязывается к модели товара (`ProductModel.photo`)

Исходный код: `apps/third_party/cml/sync.py:116-125`

---

## 🔄 Процесс синхронизации каталога

### 1. Инициализация обмена

**Запрос от 1С:**
```
GET /1c_exchange.php?type=catalog&mode=checkauth
```

**Ответ Django:**
```
success
PHPSESSID
<session_id>
```

**Запрос от 1С:**
```
GET /1c_exchange.php?type=catalog&mode=init
```

**Ответ Django:**
```
zip=no
file_limit=0
```

### 2. Загрузка файлов

**1С отправляет файлы:**
```
POST /1c_exchange.php?type=catalog&mode=file&filename=import.xml
POST /1c_exchange.php?type=catalog&mode=file&filename=offers.xml
POST /1c_exchange.php?type=catalog&mode=file&filename=picture1.jpg
POST /1c_exchange.php?type=catalog&mode=file&filename=picture2.jpg
...
```

Файлы сохраняются в `media/cml/tmp/`

### 3. Импорт данных

**Запрос от 1С:**
```
GET /1c_exchange.php?type=catalog&mode=import&filename=import.xml
```

**Django создает асинхронную задачу Celery:**

```python
# apps/third_party/cml/views.py:81-85
exchange_obj = Exchange.log('import', request.user, filename)
parsing_obj = ExchangeParsing.log(exchange_obj, filename, file_path)
make_import.delay(parsing_obj_id=parsing_obj.id)
```

**Celery task выполняет:**

1. Парсинг XML файла (`import.xml`)
   - Извлечение групп товаров
   - Извлечение свойств
   - Извлечение товаров
   - **Извлечение путей к изображениям**

2. Сохранение в промежуточные таблицы (`ImportedProduct`, `ImportedGroup`, и т.д.)

3. Синхронизация с основными таблицами:
   ```python
   # apps/third_party/cml/tasks.py
   start_sync(modules=['properties', 'products', 'stock_balance', 'products_in_stock'])
   ```

4. Копирование изображений в постоянную директорию

### 4. Импорт цен и остатков

**Запрос от 1С:**
```
GET /1c_exchange.php?type=catalog&mode=import&filename=offers.xml
```

**Django обрабатывает:**
- Цены товаров
- Остатки на складах
- Обновление количества в наличии

---

## 📊 Структура данных

### Промежуточные таблицы (staging)

1С данные сначала сохраняются в промежуточные таблицы:

- `cml_importedgroup` - Группы товаров из 1С
- `cml_importedproperty` - Свойства товаров
- `cml_importedbrand` - Бренды
- `cml_importedproduct` - **Товары с путями к изображениям**
- `cml_importedwarehouse` - Склады
- `cml_importedstockbalance` - Остатки

### Основные таблицы сайта

После парсинга данные синхронизируются с основными таблицами:

- `catalog_category` / `catalog_subcategory` ← `cml_importedgroup`
- `catalog_attribute` ← `cml_importedproperty`
- `catalog_brand` ← `cml_importedbrand`
- `catalog_productmodel` ← `cml_importedproduct` (**с изображениями**)
- `catalog_product` ← `cml_importedproduct`
- `addresses_warehouse` ← `cml_importedwarehouse`
- `catalog_productstockbalance` ← `cml_importedstockbalance`

---

## 🔧 Настройка интеграции

### Шаг 1: Создание пользователя для 1С

```bash
# В Docker
docker-compose exec web python manage.py createsuperuser

# Или без Docker
python manage.py createsuperuser
```

Введите:
- Username: `1c_user` (или любое другое)
- Email: `1c@example.com`
- Password: (надежный пароль)

### Шаг 2: Настройка прав доступа

В Django Admin (`/admin/`) найдите пользователя и дайте ему право:
- **cml | exchange | Can add exchange**

Или через Django shell:

```python
from django.contrib.auth.models import User, Permission

user = User.objects.get(username='1c_user')
perm = Permission.objects.get(codename='add_exchange', content_type__app_label='cml')
user.user_permissions.add(perm)
```

### Шаг 3: Настройка в 1С

В 1С Управление Торговлей откройте настройки обмена:

**Основные настройки:**
- URL: `http://your-domain.com/1c_exchange.php`
- Логин: `1c_user`
- Пароль: (пароль пользователя Django)

**Дополнительные настройки:**
- Формат обмена: **CommerceML 2.0**
- Выгружать: ✅ Каталог товаров, ✅ Цены, ✅ Остатки
- Загружать: ✅ Заказы

### Шаг 4: Создание директорий для изображений

```bash
# В Docker
docker-compose exec web mkdir -p /app/media/models/photos_1c
docker-compose exec web mkdir -p /app/media/cml/tmp

# Или без Docker
mkdir -p media/models/photos_1c
mkdir -p media/cml/tmp
```

### Шаг 5: Первый запуск синхронизации

В 1С нажмите **"Выполнить обмен"**

Проверьте логи:

```bash
# В Docker
docker-compose logs -f celery

# Или локально
tail -f logs/cml_sync.log
tail -f logs/cml_tasks.log
```

---

## 📁 Структура файлов

```
media/
├── cml/
│   └── tmp/                    # Временные файлы от 1С
│       ├── import.xml          # XML с каталогом
│       ├── offers.xml          # XML с ценами/остатками
│       ├── picture1.jpg        # Изображения (временно)
│       └── picture2.jpg
│
└── models/
    └── photos_1c/              # Постоянное хранилище изображений
        ├── picture1.jpg        # Скопированные изображения
        └── picture2.jpg        # Привязаны к ProductModel.photo

logs/
├── cml_sync.log                # Логи синхронизации
├── cml_tasks.log               # Логи Celery задач
└── cml_utils.log               # Логи парсинга XML
```

---

## 🔍 Проверка синхронизации

### 1. Проверка через Admin

Откройте Django Admin:
- `/admin/cml/importedproduct/` - Импортированные товары
- `/admin/cml/exchange/` - История обменов
- `/admin/catalog/productmodel/` - Модели товаров (с изображениями)
- `/admin/catalog/product/` - Товары

### 2. Проверка через Django Shell

```python
docker-compose exec web python manage.py shell

# Проверка импортированных товаров
from apps.third_party.cml.models import ImportedProduct
ImportedProduct.objects.count()  # Должно быть > 0
ImportedProduct.objects.filter(image_path__isnull=False).count()  # Товары с изображениями

# Проверка синхронизированных товаров
from apps.catalog.models import ProductModel, Product
ProductModel.objects.filter(is_synced_with_1c=True).count()
ProductModel.objects.filter(photo__isnull=False).count()  # Модели с фото

# Проверка остатков
from apps.catalog.models import ProductStockBalance
ProductStockBalance.objects.count()

# Пример товара с изображением
product = ProductModel.objects.filter(photo__isnull=False).first()
print(f"Название: {product.name}")
print(f"Фото: {product.photo.url}")
print(f"ID из 1С: {product.id_1c}")
```

### 3. Проверка через Celery логи

```bash
docker-compose logs celery | grep "sync"
docker-compose logs celery | grep "ImportedProduct"
```

### 4. Проверка изображений

```bash
# Проверка временных файлов
docker-compose exec web ls -lh /app/media/cml/tmp/

# Проверка постоянных изображений
docker-compose exec web ls -lh /app/media/models/photos_1c/

# Размер директории
docker-compose exec web du -sh /app/media/models/photos_1c/
```

---

## 🐛 Решение проблем

### Проблема: Изображения не синхронизируются

**Возможные причины:**

1. **Нет прав на запись**
   ```bash
   docker-compose exec web chmod -R 777 /app/media/cml/tmp
   docker-compose exec web chmod -R 777 /app/media/models/photos_1c
   ```

2. **Celery worker не запущен**
   ```bash
   docker-compose ps celery  # Должен быть Up
   docker-compose logs celery
   ```

3. **Путь к изображению неверный**
   ```python
   # Проверьте в ImportedProduct
   from apps.third_party.cml.models import ImportedProduct
   p = ImportedProduct.objects.filter(image_path__isnull=False).first()
   print(p.image_path)

   # Проверьте, существует ли файл
   import os
   os.path.exists(p.image_path)
   ```

### Проблема: Товары не синхронизируются

**Решение:**

1. Проверьте флаг `do_not_sync`:
   ```python
   from apps.third_party.cml.models import ImportedProduct, ImportedGroup
   ImportedProduct.objects.filter(do_not_sync=True).update(do_not_sync=False)
   ImportedGroup.objects.filter(do_not_sync=True).update(do_not_sync=False)
   ```

2. Запустите синхронизацию вручную:
   ```bash
   docker-compose exec web python manage.py shell
   ```
   ```python
   from apps.third_party.cml.sync import start_sync
   start_sync(modules=['products'], is_full=True)
   ```

### Проблема: Ошибка аутентификации от 1С

**Решение:**

1. Проверьте права пользователя:
   ```python
   from django.contrib.auth.models import User
   user = User.objects.get(username='1c_user')
   user.has_perm('cml.add_exchange')  # Должно быть True
   ```

2. Проверьте логи:
   ```bash
   docker-compose logs web | grep "1c_exchange"
   ```

---

## 🚀 Ручная синхронизация

### Полная синхронизация

```bash
docker-compose exec web python manage.py shell
```

```python
from apps.third_party.cml.sync import start_sync

# Полная синхронизация всех модулей
start_sync(modules=['properties', 'products', 'stock_balance', 'products_in_stock'], is_full=True)
```

### Частичная синхронизация

```python
# Только товары
start_sync(modules=['products'])

# Только остатки
start_sync(modules=['stock_balance', 'products_in_stock'])

# Только свойства
start_sync(modules=['properties'])
```

---

## 📊 Мониторинг

### Celery задачи

```bash
# Активные задачи
docker-compose exec celery celery -A main inspect active

# Статистика
docker-compose exec celery celery -A main inspect stats
```

### Логи в реальном времени

```bash
# Все логи Celery
docker-compose logs -f celery

# Только ошибки
docker-compose logs -f celery | grep ERROR

# Только синхронизация
docker-compose logs -f celery | grep sync
```

---

## 🔐 Безопасность

### Рекомендации:

1. **Используйте HTTPS** для обмена с 1С
2. **Создайте отдельного пользователя** только для 1С
3. **Дайте минимальные права** (только `cml.add_exchange`)
4. **Используйте сложный пароль**
5. **Ограничьте доступ по IP** (в Nginx)

### Ограничение доступа в Nginx:

```nginx
location ~* ^/(1c_exchange\.php|exchange) {
    # Разрешить только с IP адреса 1С сервера
    allow 192.168.1.100;
    deny all;

    proxy_pass http://django;
    # ...
}
```

---

## 📚 Дополнительные команды

### Очистка старых файлов

```bash
# Удалить временные файлы старше 7 дней
docker-compose exec web find /app/media/cml/tmp -type f -mtime +7 -delete

# Очистить все временные файлы
docker-compose exec web rm -rf /app/media/cml/tmp/*
```

### Резервное копирование изображений

```bash
# Создать архив изображений
docker-compose exec web tar -czf /tmp/photos_backup.tar.gz /app/media/models/photos_1c/

# Скопировать на хост
docker cp metateks_web:/tmp/photos_backup.tar.gz ./
```

---

## ✅ Итого: Что синхронизируется

| Компонент | Из 1С | В 1С | Изображения |
|-----------|-------|------|-------------|
| Категории товаров | ✅ | ❌ | - |
| Характеристики | ✅ | ❌ | - |
| Бренды | ✅ | ❌ | - |
| Товары | ✅ | ❌ | ✅ Да |
| Цены | ✅ | ❌ | - |
| Склады | ✅ | ❌ | - |
| Остатки | ✅ | ❌ | - |
| Заказы | ❌ | ✅ | - |

**Изображения товаров полностью синхронизируются автоматически!** 📸
