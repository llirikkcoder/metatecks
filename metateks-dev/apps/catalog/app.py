from django.apps import AppConfig

from watson import search

from apps.search.adapters import (
    CategorySearchAdapter, SubCategorySearchAdapter, ProductSearchAdapter, BrandSearchAdapter
)


class CatalogConfig(AppConfig):
    name = 'apps.catalog'
    verbose_name = 'Каталог товаров'

    def ready(self):
        import apps.catalog.signals

        Category = self.get_model('Category')
        SubCategory = self.get_model('SubCategory')
        Product = self.get_model('Product')
        Brand = self.get_model('Brand')

        search.register(
            Category.objects.filter(is_shown=True),
            CategorySearchAdapter,
            store=('name',),
        )
        search.register(
            SubCategory.objects.filter(is_shown=True),
            SubCategorySearchAdapter,
            store=('name',),
        )
        search.register(
            Product.objects.filter(is_shown=True),
            ProductSearchAdapter,
            store=('name',),
        )
        search.register(Brand, BrandSearchAdapter, store=('name',))
