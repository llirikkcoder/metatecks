from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView

from apps.catalog.models import Category, SubCategory, Product, Brand


class BrandListView(TemplateView):
    template_name = 'brand_list.html'

    def get_data(self):
        """
        Метод для получения сгруппированного и отсортированного списка категорий и брендов
        """
        # - получаем пары категория/бренд
        PAIRS = Product.objects.select_related('category').filter(
            is_shown=True, category__is_shown=True, brand_id__gt=0
        ).values_list('category_id', 'brand_id')
        PAIRS = set(PAIRS)

        # - подготавливаем хранилища данных
        CATS = {c.id: {'obj': c, 'brands': []} for c in Category.objects.filter(is_shown=True)}
        BRANDS = {b.id: b for b in Brand.objects.all()}
        BRANDS_ORDER = list(BRANDS.keys())

        # - заполняем список брендов в каждой категории
        for cat_id, brand_id in PAIRS:
            CATS[cat_id]['brands'].append(brand_id)

        # - сортируем их
        for cat_id, cat_dict in CATS.items():
            _brands = cat_dict['brands']
            if _brands:
                cat_dict['brands'] = sorted(_brands, key=lambda x: BRANDS_ORDER.index(x))
        return {
            'categories': CATS,
            'brands': BRANDS,
        }

    def get_context_data(self, **kwargs):
        data = self.get_data()
        data.update(super().get_context_data(**kwargs))
        return data


class BrandPageView(DetailView):
    template_name = 'brand_page.html'
    context_object_name = 'brand'

    def get_object(self, **kwargs):
        return get_object_or_404(Brand, slug=self.kwargs['brand'])

    def get_data(self):
        """
        Метод для получения сгруппированного и отсортированного списка категорий и подкатегорий
        """
        # - получаем пары категория/подкатегория
        PAIRS = Product.objects.select_related('category', 'sub_category').filter(
            is_shown=True, category__is_shown=True, sub_category__is_shown=True, brand_id=self.object.id
        ).values_list('category_id', 'sub_category_id')
        PAIRS = set(PAIRS)

        # - подготавливаем хранилища данных
        CATS = {c.id: {'obj': c, 'models': []} for c in Category.objects.filter(is_shown=True)}
        MODELS = {s.id: s for s in SubCategory.objects.filter(is_shown=True)}
        MODELS_ORDER = list(MODELS.keys())

        # - заполняем список подкатегории в каждой категории
        for cat_id, model_id in PAIRS:
            CATS[cat_id]['models'].append(model_id)

        # - сортируем их
        for cat_id, cat_dict in CATS.items():
            _models = cat_dict['models']
            if _models:
                cat_dict['models'] = sorted(_models, key=lambda x: MODELS_ORDER.index(x))
        return {
            'categories': CATS,
            'models': MODELS,
        }

    def get_context_data(self, **kwargs):
        data = self.get_data()
        data.update(super().get_context_data(**kwargs))
        return data
