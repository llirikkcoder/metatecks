import json
from html.parser import HTMLParser
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


_VOID_ELEMENTS = frozenset([
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
])


class _TagTracker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in _VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            self.stack.remove(tag)


@register.filter
def fix_html(value):
    """Закрывает незакрытые HTML-теги в строке."""
    if not value:
        return value
    tracker = _TagTracker()
    tracker.feed(value)
    closing = ''.join(f'</{tag}>' for tag in reversed(tracker.stack))
    return mark_safe(value + closing)


@register.filter
def with_video(videos):
    """Фильтрует список видео, оставляя только те, у которых есть реальный контент."""
    return [v for v in videos if v.video and v.video.strip()]
