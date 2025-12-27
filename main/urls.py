from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.urls import include, path, register_converter
from django.views.generic import TemplateView, RedirectView

from apps.cart.views import CartPageView
from apps.content.views import HomeView, PageView
from apps.promotions.views import PromotionsView
from apps.utils.urls_converters import DateConverter
from apps.search.views import SearchPageView


register_converter(DateConverter, 'post_date')

admin.site.site_header = 'Метатэкс'


def health_check(request):
    """Health check endpoint for Docker"""
    return HttpResponse("OK", content_type="text/plain")


urlpatterns = [
    # health check
    path('health/', health_check, name='health'),

    # api
    path('api/', include(('apps.api.urls', 'api'))),

    # разделы
    path('catalog/', include(('apps.catalog.urls.catalog', 'catalog'))),
    path('brands/', include(('apps.catalog.urls.brands', 'brands'))),
    path('about/', include(('apps.content.urls.about', 'about'))),
    path('news/', include(('apps.content.urls.news', 'news'))),
    path('articles/', include(('apps.content.urls.articles', 'articles'))),
    path('account/', include(('apps.users.urls', 'account'))),

    # страницы
    path('', HomeView.as_view(), name='home'),
    path('cart/', CartPageView.as_view(), name='cart'),
    path('promotions/', PromotionsView.as_view(), name='promotions'),
    path('search/', SearchPageView.as_view(), name='search'),

    # страницы: статика
    path('pages/', TemplateView.as_view(template_name='html/pages.html'), name='pages'),
    path('pages/home/', TemplateView.as_view(template_name='html/home.html'), name='pages_home'),
    path('pages/catalog/', TemplateView.as_view(template_name='html/catalog.html'), name='pages_catalog'),
    path('pages/category/', TemplateView.as_view(template_name='html/category.html'), name='pages_category'),
    path('pages/model/', TemplateView.as_view(template_name='html/model.html'), name='pages_model'),
    path('pages/model_filter/', TemplateView.as_view(template_name='html/model_filter.html'), name='pages_model_filter'),
    path('pages/product/', TemplateView.as_view(template_name='html/product.html'), name='pages_product'),
    path('pages/brands/', TemplateView.as_view(template_name='html/brand_list.html'), name='pages_brands'),
    path('pages/brands_item/', TemplateView.as_view(template_name='html/brand_page.html'), name='pages_brand_page'),
    path('pages/promotions/', TemplateView.as_view(template_name='html/promotions.html'), name='pages_promotions'),
    path('pages/about/', TemplateView.as_view(template_name='html/about.html'), name='pages_about'),
    path('pages/photo/', TemplateView.as_view(template_name='html/photo.html'), name='pages_photo'),
    path('pages/video/', TemplateView.as_view(template_name='html/video.html'), name='pages_video'),
    path('pages/news/', TemplateView.as_view(template_name='html/news.html'), name='pages_news'),
    path('pages/news-item/', TemplateView.as_view(template_name='html/news-item.html'), name='pages_news-item'),
    path('pages/articles/', TemplateView.as_view(template_name='html/articles.html'), name='pages_articles'),
    path('pages/search/', TemplateView.as_view(template_name='html/search.html'), name='pages_search'),
    path('pages/cart/', TemplateView.as_view(template_name='html/cart.html'), name='pages_cart'),
    path('pages/account_home/', TemplateView.as_view(template_name='html/account_home.html'), name='pages_account_home'),
    path('pages/account_orders/', TemplateView.as_view(template_name='html/account_orders.html'), name='pages_account_orders'),
    path('pages/account_addresses/', TemplateView.as_view(template_name='html/account_addresses.html'), name='pages_account_addresses'),
    path('pages/account_favorites/', TemplateView.as_view(template_name='html/account_favorites.html'), name='pages_account_favorites'),
    path('pages/account_profile/', TemplateView.as_view(template_name='html/account_profile.html'), name='pages_account_profile'),

    # страница для тестов
    path('test/', TemplateView.as_view(template_name='test.html'), name='test'),

    # админка
    path('admin/', admin.site.urls),

    # сторонние приложения
    path('images-handler/', include('galleryfield.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('cml/', include('apps.third_party.cml.urls')),

    # страницы
    path('<path:slug>/', PageView.as_view(), name='page'),
]


# static/media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
    for url, root in settings.INNER_STATIC_URLPATTERNS:
        urlpatterns += static(url, document_root=root)
