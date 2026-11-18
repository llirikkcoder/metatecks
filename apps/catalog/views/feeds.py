from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from apps.catalog.feeds import build_feed, FEED_PRODUCTS, FEED_MODELS, FEED_MODELS_WORK

FEED_CACHE_TIMEOUT = 60 * 60  # 1 час
FEEDS = (FEED_PRODUCTS, FEED_MODELS, FEED_MODELS_WORK)


def get_feed_xml(kind, refresh=False):
    key = f'yandex_feed_v1:{kind}'
    data = None if refresh else cache.get(key)
    if data is None:
        data = build_feed(kind)
        cache.set(key, data, FEED_CACHE_TIMEOUT)
    return data


def _make_view(kind):
    @require_GET
    def view(request):
        if kind not in FEEDS:
            raise Http404
        response = HttpResponse(get_feed_xml(kind), content_type='application/xml; charset=utf-8')
        response['Cache-Control'] = 'public, max-age=900'
        return response
    return view


products_feed = _make_view(FEED_PRODUCTS)
models_feed = _make_view(FEED_MODELS)
models_work_feed = _make_view(FEED_MODELS_WORK)
