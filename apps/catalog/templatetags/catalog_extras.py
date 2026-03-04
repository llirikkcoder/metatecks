import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def to_json(value):
    """Convert value to JSON string for use in data attributes."""
    return mark_safe(json.dumps(value, ensure_ascii=False))


@register.filter
def with_photo(photos):
    """Фильтрует список фото, оставляя только те, у которых есть реальное изображение."""
    return [p for p in photos if p.photo_thumb_url]


@register.filter
def with_video(videos):
    """Фильтрует список видео, оставляя только те, у которых есть реальный контент."""
    return [v for v in videos if v.video and v.video.strip()]
