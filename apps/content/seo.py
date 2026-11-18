from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.urls import reverse

from apps.catalog.models import Brand, Category, Product, ProductModel, SubCategory
from apps.content.models import Article, News, Page


ROBOTS_DISALLOW = (
    '/admin/',
    '/api/',
    '/account/',
    '/cart/',
    '/search/',
    '/pages/',
    '/test/',
    '/cml/',
    '/tinymce/',
    '/images-handler/',
    '/*?',
)


def robots_txt(request):
    host = request.get_host().split(':')[0]
    lines = ['User-agent: *']
    lines += [f'Disallow: {path}' for path in ROBOTS_DISALLOW]
    lines += [
        '',
        f'Host: https://{host}',
        f'Sitemap: https://{host}{reverse("sitemap")}',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


class BaseSitemap(Sitemap):
    protocol = 'https'

    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None)


class StaticSitemap(BaseSitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['home', 'catalog:home', 'brands:home', 'about:home', 'promotions', 'news:home', 'articles:home']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return None


class CategorySitemap(BaseSitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Category.objects.filter(is_shown=True)


class SubCategorySitemap(BaseSitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return SubCategory.objects.filter(is_shown=True, category__is_shown=True).select_related('category')


class ModelSitemap(BaseSitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return (ProductModel.objects
                .filter(is_shown=True, sub_category__is_shown=True, category__is_shown=True)
                .select_related('sub_category', 'category'))


class ProductSitemap(BaseSitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return (Product.objects
                .filter(is_shown=True, model__is_shown=True,
                        sub_category__is_shown=True, category__is_shown=True)
                .select_related('sub_category', 'category'))


class BrandSitemap(BaseSitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        brand_ids = Product.objects.filter(is_shown=True).values_list('brand_id', flat=True)
        return Brand.objects.filter(id__in=set(brand_ids))


class NewsSitemap(BaseSitemap):
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return News.objects.published()


class ArticleSitemap(BaseSitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Article.objects.published()


class PageSitemap(BaseSitemap):
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return Page.objects.all()


sitemaps = {
    'static': StaticSitemap,
    'categories': CategorySitemap,
    'subcategories': SubCategorySitemap,
    'models': ModelSitemap,
    'products': ProductSitemap,
    'brands': BrandSitemap,
    'news': NewsSitemap,
    'articles': ArticleSitemap,
    'pages': PageSitemap,
}
