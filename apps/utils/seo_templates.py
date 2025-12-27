import re
from decimal import Decimal
from typing import Dict, Any, Optional

from apps.utils.seo import seo_replace


class SEOTemplatePlaceholders:
    """
    Класс для управления плейсхолдерами SEO-шаблонов
    """

    # Регулярка для поиска всех плейсхолдеров
    PLACEHOLDER_PATTERN = re.compile(r'\{([^}]+)\}')

    # Регулярка для атрибутов: {attr:название} или {attr:slug} или {attr:12}
    ATTR_PATTERN = re.compile(r'^attr:(.+)$')

    @staticmethod
    def format_price(price: Decimal) -> str:
        """
        Форматирование цены: 3500000 -> "3 500 000 руб."

        Args:
            price: цена в формате Decimal

        Returns:
            Отформатированная строка с ценой
        """
        if not price:
            return ''
        price_int = int(price)
        price_str = f'{price_int:,}'.replace(',', ' ')
        return f'{price_str} руб.'

    @classmethod
    def get_attribute_value(cls, obj, attr_key: str) -> str:
        """
        Получение значения атрибута по ключу (имя/slug/id)

        Args:
            obj: ProductModel или Product объект
            attr_key: ключ атрибута ("грузоподъемность" или "load_capacity" или "12")

        Returns:
            Значение атрибута с единицей измерения или пустая строка
        """
        # Получаем все атрибуты объекта
        attrs_list = []
        if hasattr(obj, 'get_attrs_list_v3'):
            try:
                attrs_list = obj.get_attrs_list_v3(full=True)
            except Exception:
                pass

        # Пробуем найти атрибут по разным критериям
        for attr in attrs_list:
            # По имени (case-insensitive)
            if attr.get('name', '').lower() == attr_key.lower():
                value = attr.get('value', '')
                unit = attr.get('unit', '')
                return f"{value} {unit}".strip() if unit else str(value)

            # По ID (формат: "12" или "a12")
            attr_id_str = str(attr.get('id', ''))
            if attr_key == attr_id_str or attr_key == f'a{attr_id_str}':
                value = attr.get('value', '')
                unit = attr.get('unit', '')
                return f"{value} {unit}".strip() if unit else str(value)

        # Пробуем по slug через базу данных
        try:
            from apps.catalog.models import Attribute
            attribute = Attribute.objects.filter(slug=attr_key).first()
            if attribute and hasattr(obj, 'attrs'):
                attr_slug = f'a{attribute.id}'
                value = obj.attrs.get(attr_slug)
                if value is not None:
                    # Если атрибут с опциями
                    if attribute.with_options:
                        option = attribute.options.filter(id=value).first()
                        value = option.get_value(attribute.attr_type) if option else value
                    unit = attribute.unit.get_name_html() if attribute.unit else ''
                    return f"{value} {unit}".strip() if unit else str(value)
        except Exception:
            pass

        return ''

    @classmethod
    def get_context(cls, obj) -> Dict[str, Any]:
        """
        Получение контекста для замены плейсхолдеров

        Args:
            obj: Category, SubCategory, ProductModel или Product

        Returns:
            Словарь с доступными переменными
        """
        context = {}

        # Базовые поля
        context['name'] = getattr(obj, 'name', '')
        context['vendor_code'] = getattr(obj, 'vendor_code', '')
        context['bar_code'] = getattr(obj, 'bar_code', '')

        # Цена
        if hasattr(obj, 'price'):
            price = obj.price
            context['price'] = str(price) if price else ''
            context['price_formatted'] = cls.format_price(price)

        # Для Product - берем связанные объекты
        if obj.__class__.__name__ == 'Product':
            context['category'] = obj.category.name if obj.category else ''
            context['subcategory'] = obj.sub_category.name if obj.sub_category else ''
            context['brand'] = obj.brand.name if obj.brand else obj.brand_name
            context['model_name'] = obj.model.name if obj.model else ''

            # Дополнительные варианты
            if obj.category:
                context['category_lower'] = obj.category.get_name_lower()
            if obj.sub_category:
                context['subcategory_single'] = obj.sub_category.get_name_single()

        # Для ProductModel
        elif obj.__class__.__name__ == 'ProductModel':
            context['category'] = obj.category.name if obj.category else ''
            context['subcategory'] = obj.sub_category.name if obj.sub_category else ''
            context['brand'] = ''  # У модели нет бренда

            if obj.category:
                context['category_lower'] = obj.category.get_name_lower()
            if obj.sub_category:
                context['subcategory_single'] = obj.sub_category.get_name_single()

        # Для SubCategory
        elif obj.__class__.__name__ == 'SubCategory':
            context['subcategory'] = obj.name
            context['subcategory_single'] = obj.get_name_single()
            context['category'] = obj.category.name if obj.category else ''
            context['category_lower'] = obj.category.get_name_lower() if obj.category else ''

        # Для Category
        elif obj.__class__.__name__ == 'Category':
            context['category'] = obj.name
            context['category_lower'] = obj.get_name_lower()

        # Добавляем пустые значения для недоступных полей
        context.setdefault('brand', '')
        context.setdefault('category', '')
        context.setdefault('subcategory', '')
        context.setdefault('price', '')
        context.setdefault('price_formatted', '')
        context.setdefault('vendor_code', '')
        context.setdefault('bar_code', '')

        return context

    @classmethod
    def replace_placeholders(cls, template: str, obj, city=None) -> str:
        """
        Замена всех плейсхолдеров в шаблоне

        Args:
            template: строка с плейсхолдерами
            obj: объект для получения данных
            city: объект City для геолокации (опционально)

        Returns:
            Строка с замененными плейсхолдерами
        """
        if not template:
            return ''

        # Получаем базовый контекст
        context = cls.get_context(obj)

        # Функция для замены каждого плейсхолдера
        def replace_match(match):
            placeholder = match.group(1)  # без фигурных скобок

            # Проверяем, это атрибут?
            attr_match = cls.ATTR_PATTERN.match(placeholder)
            if attr_match:
                attr_key = attr_match.group(1)
                return cls.get_attribute_value(obj, attr_key)

            # Обычный плейсхолдер
            return str(context.get(placeholder, f'{{{placeholder}}}'))

        # Заменяем все плейсхолдеры
        result = cls.PLACEHOLDER_PATTERN.sub(replace_match, template)

        # Удаляем лишние пробелы
        result = re.sub(r'\s+', ' ', result).strip()

        # Применяем геолокационные замены (%city%, %region% и т.д.)
        result = seo_replace(result, city=city)

        return result


def apply_seo_template(obj, template: str, city=None) -> str:
    """
    Вспомогательная функция для применения шаблона

    Args:
        obj: объект Category/SubCategory/ProductModel/Product
        template: шаблон с плейсхолдерами
        city: объект City для геолокации

    Returns:
        Обработанная строка
    """
    return SEOTemplatePlaceholders.replace_placeholders(template, obj, city=city)
