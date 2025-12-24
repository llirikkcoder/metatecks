from decimal import Decimal
import math
import re
from urllib.parse import quote

from django import template
from django.utils.safestring import mark_safe

from pytils.numeral import choose_plural


register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_str(dictionary, key):
    return dictionary.get(key, '')


def _get_attr(obj, attr_name):
    attr = getattr(obj, attr_name)
    if callable(attr):
        attr = attr()
    return attr


@register.simple_tag
def get_obj_attr(obj, attr_name):
    return _get_attr(obj, attr_name)


@register.filter
def get_attr(obj, attr_name):
    return _get_attr(obj, attr_name)


@register.simple_tag
def get_form_field(form, field_name):
    return form[field_name]


@register.simple_tag
def pytils_plural(value, *labels):
    return choose_plural(value, labels)


@register.filter
def lowfirst(s):
    return f'{s[0].lower()}{s[1:]}'


@register.filter
def format_number(value, delimeter='&nbsp;'):
    """
    format int number with SPACES
    """
    if hasattr(value, '__round__'):
        # avoiding TypeError for strings
        value = int(round(value)) or 0
        return mark_safe('{:,}'.format(value).replace(',', delimeter).replace('.', ','))
    return value


@register.filter
def is_odd(number):
    return bool(number % 2)


@register.filter
def to_bool(value):
    return bool(value)


@register.filter
def to_bool_js(value):
    return str(bool(value)).lower()


@register.filter
def clean_html(str):
    return str.replace('&nbsp;', ' ').replace('<br/>', ' ')


@register.filter
def format_phone(phone):
    return re.sub(r'[ ()-]', '', phone)


@register.filter
def remove_p(str):
    return str.replace('<p>', '').replace('</p>', '')


@register.filter
def nbsp(value):
    return mark_safe(str(value).replace(' ', '&nbsp;'))
