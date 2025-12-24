from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.banners.models import Banner
from apps.content.models.news import NewsCategory, News


class NewsView(TemplateView):
    with_year = False
    with_category = False
    template_name = 'news.html'

    def get_year(self):
        self.year = self.kwargs.get('year')
        return self.year

    def get_category(self):
        self.category = False
        if self.with_category:
            self.category = get_object_or_404(NewsCategory, slug=self.kwargs['category'])
        return self.category

    def get_queryset(self, **kwargs):
        self.base_qs = self.qs = News.objects.published().prefetch_related('categories')
        if self.with_year:
            self.qs = self.qs.filter(published_at__year=self.year)
        if self.with_category:
            self.qs = self.qs.filter(categories=self.category)
        return self.qs

    def get_years(self):
        self.years = self.base_qs.values_list('published_at__year', flat=True)
        return self.years

    def get_categories(self):
        self.categories = list(NewsCategory.objects.filter(is_shown=True))
        if self.with_category:
            cat = self.category
            if not cat.is_shown:
                self.categories.append(cat)
        return self.categories

    def get_banner(self):
        qs = Banner.objects.published().filter(banner_place='news')
        self.banner = qs.order_by('?').first()
        return self.banner

    def get_context_data(self, **kwargs):
        self.get_year()
        self.get_category()
        self.get_queryset()
        self.get_years()
        self.get_categories()
        self.get_banner()
        context = {
            'items': self.qs,
            'year': self.year,
            'active_category': self.category,
            'years': self.years,
            'categories': self.categories,
            'banner': self.banner,
        }
        context.update(super().get_context_data(**kwargs))
        return context


class NewsPostView(TemplateView):
    template_name = 'news-item.html'

    def get(self, *args, **kwargs):
        kw = self.kwargs
        _year, _month = kw['date']
        _slug = kw['slug']
        self.post = News.objects.published().filter(
            published_at__year=_year, published_at__month=_month, slug=_slug
        ).first()
        if not self.post:
            return HttpResponse(status=404)
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'post': self.post,
        }
        context.update(super().get_context_data(**kwargs))
        return context
