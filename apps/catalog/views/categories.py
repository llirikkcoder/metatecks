from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import ListView, DetailView

from apps.catalog.models import (
    Attribute, Brand, Category, SubCategory, ProductModel, Product, ProductPhoto, ProductVideo
)
from apps.utils.common import absolute


PRODUCTS_PAGINATE_BY = 8


# -- категории и подкатегории --

class CatalogHomeView(ListView):
    template_name = 'catalog.html'
    context_object_name = 'categories'

    def get_queryset(self, **kwargs):
        return Category.objects.filter(is_shown=True).prefetch_related('sub_categories')


class CategoryView(DetailView):
    template_name = 'category.html'
    context_object_name = 'cat'

    def get_object(self, **kwargs):
        return get_object_or_404(Category, slug=self.kwargs['category'], is_shown=True)

    def get_data(self):
        """
        Получаем:
        - список моделей и минимальных цен
        - список популярных товаров
        """
        # 1) список моделей и минимальных цен
        category = self.object
        subcat_prices = {}
        subcat_hits = {}
        subcat_attrs = {}

        SUB_CATEGORIES = list(category.shown_children)
        for m in SUB_CATEGORIES:
            subcat_attrs[m.id] = m.attr_products_ids
            _models = m.shown_models.filter(price__gt=0)
            if _models.exists():
                _cheap = _models.order_by('price').first()
                if _cheap:
                    subcat_prices[m.id] = _cheap.price
            _products = m.shown_products.all()
            if _products.exists():
                subcat_hits[m.id] = _products.filter(is_popular=True).exists()

        SUB_CATEGORIES = sorted(SUB_CATEGORIES, key=lambda x: x.id in subcat_prices, reverse=True)

        # 2) список популярных товаров
        ATTRIBUTES = Attribute.get_attributes_dict()
        popular_products = Product.objects.filter(is_shown=True, is_popular=True, category=category)
        with_popular = popular_products.exists()
        if with_popular:
            popular_products = popular_products.select_related('model').prefetch_related('stock_balance').order_by('?')[:7]

        return {
            'sub_categories': SUB_CATEGORIES,
            'subcat_prices': subcat_prices,
            'subcat_hits': subcat_hits,
            'subcat_attrs': subcat_attrs,
            'attributes': ATTRIBUTES,
            'popular_products': popular_products,
            'with_popular_products': with_popular,
        }

    def get_context_data(self, **kwargs):
        data = self.get_data()
        data.update(super().get_context_data(**kwargs))
        return data


class SubCategoryView(DetailView):
    TEMPLATES = {
        'default': 'sub_category.html',
        'ajax': 'include/products_container.html',
        'ajax_offset': 'include/products_list.html',
    }
    context_object_name = 'subcat'
    force_filter = False
    paginate_by = PRODUCTS_PAGINATE_BY
    with_model = False
    with_brand = False

    def _get_offset(self):
        self.offset = None
        _offset = self.request.GET.get('offset')
        if _offset:
            try:
                self.offset = int(_offset)
            except ValueError:
                pass

    def _get_ajax_response(self, response):
        _paginator = self.paginator
        res = {
            'html': response.rendered_content,
            'offset': self.offset,
            'has_more': _paginator.get('has_more', False),
            'new_offset': _paginator.get('new_offset', None),
        }
        return JsonResponse(res)

    def get(self, request, *args, **kwargs):
        self._get_offset()
        self.with_offset = bool(self.offset)
        response = super().get(request, *args, **kwargs)
        if request.is_ajax:
            return self._get_ajax_response(response)
        return response

    def get_template_names(self):
        TEMPLATES = self.TEMPLATES
        return (
            TEMPLATES['default']
            if not self.request.is_ajax
            else TEMPLATES['ajax_offset']
            if self.with_offset
            else TEMPLATES['ajax']
        )

    def get_object(self, **kwargs):
        subcat = get_object_or_404(
            SubCategory, slug=self.kwargs['sub_category'], category__slug=self.kwargs['category'], is_shown=True
        )
        self.model = None
        if self.with_model:
            self.model = get_object_or_404(ProductModel, sub_category=subcat, id=self.kwargs['model_id'], is_shown=True)
        return subcat

    def _get_attr_filter(self, attr_values):
        lookups = []
        values = []

        attr = self.attr
        attr_slug = attr.attrs_slug
        attr_type = attr.attr_type

        # - фильтр по вариантам атрибута
        if attr.with_options:
            option_ids = attr.options.values_list('id', flat=True)
            for value in [x for x in attr_values if x.startswith('o')]:
                try:
                    v = int(value[1:])
                    if v in option_ids:
                        q = f'Q(model__attrs__{attr_slug}={v})'
                        lookups.append(eval(q))
                        values.append(v)
                except ValueError:
                    pass

        # - фильтр по вариантам для фильтра
        elif attr.filter_options.count():
            options = {o.id: o for o in attr.filter_options.all()}
            option_ids = options.keys()
            for value in [x for x in attr_values if x.startswith('f')]:
                try:
                    v = int(value[1:])
                    if v in option_ids:
                        _option = options[v]
                        _filter = _option.get_filter_str(attr_slug, attr_type)
                        q = f'Q(model__attrs__{_filter})'
                        lookups.append(eval(q))
                        values.append(v)
                except ValueError:
                    pass

        # - фильтр по значениям
        else:
            for value in attr_values:
                try:
                    v = (
                        int(value)
                        if attr_type == 'int'
                        else float(value.replace(',', '.'))
                        if attr_type == 'float'
                        else value
                    )
                    q = f'Q(model__attrs__{attr_slug}={v})'
                    lookups.append(eval(q))
                    values.append(v)
                except ValueError:
                    pass

        query = None
        if lookups:
            query = lookups[0]
            for q in lookups[1:]:
                query |= q

        return query, values

    def filter(self, qs):
        self.f = {}
        self.brand = None
        GET = self.request.GET

        # фильтр по бренду
        brand_ids = []
        if self.with_brand:
            self.brand = get_object_or_404(Brand, slug=self.kwargs['brand'])
            brand_ids = [self.brand.id]
        if 'brand' in GET:
            brand_ids.extend(GET.get('brand', '').split('_'))
        if brand_ids:
            try:
                brand_ids = [int(x) for x in brand_ids]
                qs = qs.filter(brand_id__in=brand_ids)
                self.f['brand'] = brand_ids
                if not self.with_brand and len(brand_ids) == 1:
                    self.brand = Brand.objects.get(id=brand_ids[0])
            except BaseException:
                pass

        # фильтр по атрибуту
        if self.attr:
            attr_slug = self.attr.slug
            if attr_slug in GET:
                attr_values = GET.get(attr_slug, '').split('_')
                attr_filter, attr_values = self._get_attr_filter(attr_values)
                if attr_filter:
                    try:
                        qs = qs.select_related('model').filter(attr_filter)
                        self.f['attr'] = attr_values
                    except BaseException:
                        pass

        return qs

    def paginate_products(self, products, products_count):
        # if self.with_filter is False:
        #     return {}

        offset = self.offset or 0
        _page_size = self.paginate_by

        _next_index = offset + _page_size
        self.products = products[offset:_next_index]
        has_more = products_count > _next_index
        new_offset = offset + _page_size

        return {
            'offset': offset,
            'has_more': has_more,
            'new_offset': new_offset,
        }

    def get_data(self):
        """
        Получаем:
        - включен фильтр или нет
        - данные о подкатегории для вывода на странице
        - список товаров
        - список популярных товаров
        """
        # - список атрибутов
        ATTRIBUTES = Attribute.get_attributes_dict()

        # - категория, подкатегория, модель
        subcat = self.object
        category = subcat.category
        model = self.model

        # - атрибут в фильтре
        # self.attr = attr = subcat.attributes_in_filter.first()
        self.attr = attr = subcat.attribute_in_filter

        # - список моделей и товаров
        self.all_models = subcat.shown_models
        self.all_products = all_products = subcat.shown_products
        if self.with_model:
            self.all_products = all_products = all_products.filter(model=model)

        # - фильтрация товаров
        self.products = self.filter(all_products)
        self.with_filter = bool(self.with_model or self.f)
        products_count = self.products.count()

        # - пагинация товаров
        self.paginator = self.paginate_products(self.products, products_count)

        # - список популярных товаров
        popular_products = None
        with_popular = False

        if self.with_filter is False:
            popular_products = all_products.filter(is_popular=True)
            with_popular = popular_products.exists()
            if with_popular:
                popular_products = popular_products.select_related('model').prefetch_related('stock_balance').order_by('?')[:7]

        return {
            'with_filter': self.with_filter,
            'attributes': ATTRIBUTES,
            'cat': category,
            'with_model': self.with_model,
            'model': model,
            'attr': attr,
            'products_count': products_count,
            'products': self.products,
            'brand': self.brand,
            'paginator': self.paginator,
            'popular_products': popular_products,
            'with_popular_products': with_popular,
        }

    def _get_is_chosen(self, attr_name, value):
        values = self.f.get(attr_name, [])
        return value in values or str(value) in values

    def get_extra_data(self):
        """
        Получаем:
        - варианты атрибутов для фильтра
        - список фото и видео
        - абсолютный путь к странице
        """
        all_models = self.all_models
        all_products = self.all_products
        attr = self.attr

        # - товары: минимальная цена
        price = None
        _cheap = all_models.filter(price__gt=0).order_by('price').first()
        if _cheap:
            price = _cheap.price

        # - варианты в фильтре: бренд
        brands = Brand.objects.filter(id__in=all_products.values_list('brand_id', flat=True))
        brand_options = [
            {
                'value': b.id,
                'name': b.name,
                'is_chosen': self._get_is_chosen('brand', b.id),
            }
            for b in brands
        ]
        BRAND_ATTR_SLUG = Brand.get_attr_slug()

        # - варианты в фильтре: атрибут
        attr_options = []
        if attr:
            _options = (
                attr.options.all()
                if attr.with_options
                else attr.filter_options.all()
            )
            if _options:
                attr_options = [
                    {
                        'value': f'o{o.id}' if attr.with_options else f'f{o.id}',
                        'name': o.name,
                        'is_chosen': self._get_is_chosen('attr', o.id),
                    }
                    for o in _options
                ]
            else:
                _values = all_models.values_list(f'attrs__{attr.attrs_slug}', flat=True)
                _values = set(_values) - {None}
                _values = sorted(_values)
                _unit = f' {attr.unit_html}' if attr.unit else ''
                attr_options = [
                    {
                        'value': v,
                        'name': mark_safe(f'{v}{_unit}'),
                        'is_chosen': self._get_is_chosen('attr', v),
                    }
                    for v in _values
                ]

        # - список фото и видео
        photos = ProductPhoto.objects.filter(
            photo__gt='', is_shown=True, show_on_subcategory=True, model__in=all_models
        ).order_by('model', 'order', 'id')
        videos = ProductVideo.objects.filter(
            video__gt='', is_shown=True, show_on_subcategory=True, model__in=all_models
        ).exclude(video__startswith='http').order_by('model', 'order', 'id')

        # - путь до страницы (для передачи в filter.js)
        # absolute_path = absolute(self.request.path)
        absolute_path = absolute(self.object.get_absolute_url())

        # - список slug у брендов (для передачи в filter.js)
        brand_slugs = {b.id: b.slug for b in brands}

        return {
            'price': price,
            'attr_options': attr_options,
            'brand_options': brand_options,
            'BRAND_ATTR_SLUG': BRAND_ATTR_SLUG,
            'photos': photos,
            'videos': videos,
            'absolute_path': absolute_path,
            'brand_slugs': brand_slugs,
        }

    def get_context_data(self, **kwargs):
        data = self.get_data()
        if not self.request.is_ajax:
            data.update(self.get_extra_data())
        data.update(super().get_context_data(**kwargs))
        return data
