from django.views.generic import ListView

from apps.catalog.models import Category


# -- главная страница каталога --

class CatalogHomeView(ListView):
    template_name = 'catalog.html'
    context_object_name = 'categories'

    def get_queryset(self, **kwargs):
        return Category.objects.filter(is_shown=True).prefetch_related('sub_categories')
