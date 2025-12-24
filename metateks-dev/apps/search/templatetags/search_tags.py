from django import template
from django.utils.safestring import mark_safe

from apps.utils.common import absolute


register = template.Library()

TITLE_FIELDS = {
    'категория': 'name',
    'подкатегория': 'name',
    'товар': 'name',
    'бренд техники': 'name',
    'новость': 'title',
    'статья': 'title',
    'страница': 'title',
    'SEO-настройка': 'description',
}
ITEM_TYPES = {
    'SEO-настройка': 'страница',
}


@register.simple_tag
def get_item_title(item):
    meta_name = TITLE_FIELDS.get(item.content_type.name)
    return item.meta[meta_name] if meta_name else item.title.split(', ')[0]


@register.simple_tag
def get_item_type(item):
    _name = item.content_type.name
    return ITEM_TYPES.get(_name, _name)


@register.simple_tag
def get_item_url(item):
    return absolute(item.url)
