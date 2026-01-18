import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def to_json(value):
    """Convert value to JSON string for use in data attributes."""
    return mark_safe(json.dumps(value, ensure_ascii=False))
