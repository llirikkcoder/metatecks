# Архитектура SEO в проекте Metateks

## Обзор системы

В проекте реализована двухуровневая система управления SEO:
1. **Статические страницы** - через модель `SEOSetting`
2. **Динамические объекты** - через миксин `MetatagModel`

---

## 1. SEO для статических страниц (SEOSetting)

### Местоположение
- **Модель:** `apps/settings/models.py` → `SEOSetting`
- **Админка:** Настройки → SEO-настройки: статические страницы

### Структура модели

```python
class SEOSetting(models.Model):
    key = models.SlugField('Код', max_length=255, unique=True)
    description = models.CharField('Страница', max_length=255)
    title = models.CharField('Title', max_length=511)
    meta_desc = models.TextField('Meta description')
    meta_keyw = models.TextField('Meta keywords')
    h1 = models.TextField('Заголовок H1')
    header_text = models.TextField('Описание страницы (рядом с заголовком)')
    url_pattern = models.CharField('URL pattern', max_length=31)
```

### Основные поля

| Поле | Описание | Обязательное |
|------|----------|--------------|
| `key` | Уникальный код страницы (slug) | ✅ Да |
| `description` | Название страницы (для админки) | ✅ Да |
| `title` | Meta title (заголовок в поисковиках) | ❌ Нет |
| `meta_desc` | Meta description (описание в поисковиках) | ❌ Нет |
| `meta_keyw` | Meta keywords (ключевые слова) | ❌ Нет |
| `h1` | Заголовок H1 на странице | ❌ Нет |
| `header_text` | Текст под заголовком страницы | ❌ Нет |
| `url_pattern` | Django URL pattern (для ссылок в админке) | ❌ Нет |

### Автоматические подстановки

Если поле оставить пустым:
- `title` → `"{description} — {title_suffix}"` (из Settings)
- `meta_desc` → берется из глобальной настройки `key='global'`
- `h1` → используется `description`

### Примеры использования

```python
# В view.py
from apps.settings.models import SEOSetting

def home(request):
    seo = SEOSetting.get_seo_dict('home')
    context = {
        'meta_title': seo.get('title', lambda: 'Главная')(),
        'meta_desc': seo.get('meta_desc', lambda: '')(),
        'h1': seo.get('h1', lambda: 'Главная')(),
    }
    return render(request, 'home.html', context)
```

---

## 2. SEO для динамических объектов (MetatagModel)

### Местоположение
- **Миксин:** `apps/utils/model_mixins.py` → `MetatagModel`

### Структура миксина

```python
class MetatagModel(models.Model):
    meta_title = models.CharField('Meta title', max_length=255, blank=True)
    meta_description = models.CharField('Meta description', max_length=255, blank=True)
    meta_keywords = models.CharField('Meta keywords', max_length=255, blank=True)
    h1 = models.TextField('Заголовок H1', max_length=255, blank=True)
    seo_text = HTMLField('SEO-текст', blank=True)
```

### Модели, использующие MetatagModel

- ✅ `Category` (Категории товаров)
- ✅ `SubCategory` (Подкатегории)
- ✅ `Brand` (Бренды)
- ✅ `Product` (Товары)
- ✅ `Article` (Статьи)
- ✅ `News` (Новости)

### Методы миксина

```python
# Получение meta title с суффиксом
obj.get_meta_title()  # "Погрузчики XCMG — Метатэкс"

# Получение meta description (с fallback на название)
obj.get_meta_desc()   # "Описание товара..." или obj.get_title()

# Получение meta keywords
obj.get_meta_keyw()   # "погрузчик, xcmg, купить"

# Получение H1
obj.get_h1()          # "Погрузчики XCMG"
```

### Автоподстановки

Если поле оставить пустым:
- `meta_title` → `"{obj.get_title()} — {Settings.title_suffix}"`
- `meta_description` → `obj.get_title()`
- `meta_keywords` → `obj.get_title()`
- `h1` → `obj.get_h1_title()` или `obj.get_title()`

---

## 3. Динамическая замена тегов (Геолокация)

### Доступные теги

| Тег | Описание | Пример |
|-----|----------|--------|
| `%city%` | Название города | "Москва" |
| `%city_loct%` | Город в предложном падеже | "Москве" |
| `%region%` | Название региона | "Московская область" |
| `%region_loct%` | Регион в предложном падеже | "Московской области" |

### Функция замены

```python
# apps/utils/seo.py
def seo_replace(s, city=None):
    city = city or get_current_city()
    return s.replace('%city%', city.get_name())\
            .replace('%city_loct%', city.get_name_loct())\
            .replace('%region%', city.get_region_name())\
            .replace('%region_loct%', city.get_region_name_loct())
```

### Примеры использования

```
Входные данные:
meta_title = "Купить погрузчик в %city_loct%"
meta_desc = "Продажа погрузчиков в %region_loct%. Доставка по %city%"

Результат (для Москвы):
meta_title = "Купить погрузчик в Москве"
meta_desc = "Продажа погрузчиков в Московской области. Доставка по Москва"
```

---

## 4. Настройка SEO в админке

### Для статических страниц (SEOSetting)

**Путь:** Django Admin → Настройки → SEO-настройки: статические страницы

**Fieldsets в админке:**
```python
fields = (
    'id', 'key', 'description',     # Идентификация
    'title', 'h1',                  # Заголовки
    'meta_desc', 'meta_keyw',       # Мета-теги
    'header_text',                  # Доп. текст
    'show_instruction',             # Подсказка о тегах
    'url_pattern',                  # URL для превью
)
```

**Особенности:**
- Поля `key`, `description`, `url_pattern` - read-only при редактировании
- Нельзя удалить запись (защита от случайного удаления)
- В списке показывается наличие `header_text`

### Для динамических объектов (через MetatagModel)

**Пример для Category:**

**Путь:** Django Admin → Каталог → Категории → [Выбрать категорию] → Вкладка "SEO"

**Fieldsets:**
```python
('SEO', {
    'classes': ('suit-tab', 'suit-tab-seo',),
    'fields': (
        'meta_title',
        'meta_description',
        'meta_keywords',
        'h1',
        'show_instruction',  # Подсказка о доступных тегах
    ),
})
```

**Пример для Article (со вкладкой):**

```python
suit_form_tabs = (
    ('default', 'Статья'),
    ('publication', 'Публикация'),
    ('seo', 'SEO'),  # ← Отдельная вкладка для SEO
)
```

---

## 5. Глобальные настройки SEO

### Settings (Singleton модель)

**Путь:** Django Admin → Настройки → Общие настройки

**SEO-поля:**
```python
class Settings(SingletonModel):
    title_suffix = models.CharField(
        'Хвост title у страниц',
        max_length=255,
        default='Метатэкс'
    )
    robots_txt = models.TextField(
        'Содержимое файла /robots.txt',
        default='User-agent: *\nDisallow: \nHost: metateks.ru...'
    )
```

**Использование:**
```python
# Получить суффикс для title
Settings.get_seo_title_suffix()  # → "Метатэкс"

# Получить robots.txt
Settings.get_robots_txt()
```

---

## 6. Интеграция в шаблонах

### Пример базового шаблона

```django
{# templates/_base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{{ meta_title }}</title>
    <meta name="description" content="{{ meta_desc }}">
    <meta name="keywords" content="{{ meta_keyw }}">
</head>
<body>
    {% if h1 %}
        <h1>{{ h1 }}</h1>
    {% endif %}

    {% if header_text %}
        <p class="header-description">{{ header_text|safe }}</p>
    {% endif %}

    {% block content %}{% endblock %}
</body>
</html>
```

### Пример для объекта с MetatagModel

```django
{# templates/product.html #}
{% extends "_base.html" %}

{% block title %}{{ product.get_meta_title }}{% endblock %}
{% block meta_description %}{{ product.get_meta_desc }}{% endblock %}

{% block content %}
    <h1>{{ product.get_h1 }}</h1>

    {# SEO-текст в конце страницы #}
    {% if product.seo_text %}
        <div class="seo-text">
            {{ product.seo_text|safe }}
        </div>
    {% endif %}
{% endblock %}
```

---

## 7. Архитектура кода

### Структура файлов

```
apps/
├── settings/
│   ├── models.py          # Settings, SEOSetting
│   └── admin.py           # Админка для SEO настроек
├── utils/
│   ├── seo.py             # SEO утилиты (seo_replace, теги)
│   ├── model_mixins.py    # MetatagModel миксин
│   └── admin_mixins.py    # Миксины для админки
└── catalog/
    ├── models/
    │   └── categories.py  # Category(MetatagModel)
    └── admin/
        └── categories.py  # CategoryAdmin с SEO вкладкой
```

### Диаграмма наследования

```
┌─────────────────┐
│ MetatagModel    │  (Abstract Model)
│ - meta_title    │
│ - meta_desc     │
│ - h1            │
│ - seo_text      │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
    ┌────▼─────┐      ┌────▼──────┐
    │ Category │      │  Article  │
    │ SubCat   │      │  News     │
    │ Brand    │      │  Product  │
    └──────────┘      └───────────┘
```

---

## 8. Best Practices

### Для статических страниц

1. ✅ Создайте запись `key='global'` с дефолтным `meta_desc`
2. ✅ Используйте теги `%city%`, `%region%` для локализации
3. ✅ Заполняйте `description` понятным названием страницы
4. ✅ Указывайте `url_pattern` для быстрого перехода из админки

### Для динамических объектов

1. ✅ Используйте MetatagModel миксин
2. ✅ Переопределите `get_title()` в своей модели
3. ✅ Добавьте вкладку "SEO" в админку через `suit_form_tabs`
4. ✅ Используйте `show_instruction` в readonly_fields для подсказок
5. ✅ Заполняйте SEO-текст только на важных страницах

### Title оптимизация

```python
# ❌ Плохо - title слишком длинный
"Купить фронтальный погрузчик XCMG LW300FN в Москве с доставкой по всей России по низкой цене — Метатэкс"

# ✅ Хорошо - компактный и информативный
"Погрузчик XCMG LW300FN — Метатэкс"
```

### Meta description оптимизация

```python
# ❌ Плохо - слишком общее
"Купить в Москве"

# ✅ Хорошо - конкретное и полезное
"Продажа погрузчика XCMG LW300FN в Москве. Грузоподъемность 3т, мощность 162 л.с. Доставка по России. Гарантия 2 года."
```

---

## 9. Типичные задачи

### Добавить SEO для новой статической страницы

```python
# 1. Создать запись в админке
SEOSetting.objects.create(
    key='new-page',
    description='Новая страница',
    title='Новая страница — Метатэкс',
    meta_desc='Описание новой страницы в %city_loct%',
    h1='Новая страница',
    url_pattern='new_page'  # из urls.py
)

# 2. Использовать в view
def new_page(request):
    seo = SEOSetting.get_seo_dict('new-page')
    return render(request, 'new_page.html', seo)
```

### Добавить SEO для новой модели

```python
# 1. Добавить миксин к модели
from apps.utils.model_mixins import MetatagModel

class NewModel(MetatagModel, models.Model):
    title = models.CharField(max_length=255)

    def get_title(self):
        return self.title

# 2. Настроить админку
@admin.register(NewModel)
class NewModelAdmin(admin.ModelAdmin):
    suit_form_tabs = (
        ('default', 'Основное'),
        ('seo', 'SEO'),
    )
    fieldsets = (
        ('SEO', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
                'h1',
                'seo_text',
                'show_instruction',
            ),
        }),
    )
    readonly_fields = ('show_instruction',)
```

---

## 10. Частые вопросы

### Почему title дублируется?

**Проблема:** Title показывается как "Главная — Метатэкс — Метатэкс"

**Причина:** Суффикс добавляется дважды - в модели и в шаблоне

**Решение:** Использовать `get_meta_title()` вместо ручного добавления суффикса

### Как изменить глобальный суффикс title?

**Путь:** Django Admin → Настройки → Общие настройки → "Хвост title у страниц"

### Как отключить SEO-текст на странице?

Просто оставьте поле `seo_text` пустым. В шаблоне проверка:
```django
{% if product.seo_text %}
    {{ product.seo_text|safe }}
{% endif %}
```

### Теги %city% не работают

**Проблема:** Теги не заменяются на реальные значения

**Причины:**
1. Не вызван `seo_replace()` - убедитесь, что используете `get_meta_title()`, а не `meta_title`
2. Нет текущего города - проверьте middleware `apps.addresses.middleware.CityMiddleware`

---

## 11. Миграция и обновления

### При добавлении новой статической страницы

```python
# В fixtures или data migration
SEOSetting.objects.get_or_create(
    key='contacts',
    defaults={
        'description': 'Контакты',
        'title': 'Контакты — Метатэкс',
        'h1': 'Свяжитесь с нами',
        'meta_desc': 'Контакты компании Метатэкс в %city_loct%',
    }
)
```

### При изменении структуры SEO

```bash
# Создать миграцию
python manage.py makemigrations

# Применить
python manage.py migrate
```

---

## Заключение

Система SEO в проекте построена на трех столпах:
1. **SEOSetting** - для статических страниц
2. **MetatagModel** - для динамических объектов
3. **seo_replace()** - для геолокализации

Все вместе обеспечивает гибкое управление SEO прямо из админки Django без изменения кода.
