from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import View, DetailView

from apps.addresses.models import City
from apps.catalog.models import Product
from apps.users.favorites_utils import is_in_favorites


# -- товары --

class ProductLinkView(View):

    def get_object(self, **kwargs):
        return get_object_or_404(Product, pk=self.kwargs['product_id'])

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        return HttpResponseRedirect(product.get_absolute_url())


class ProductView(DetailView):
    template_name = 'product.html'
    context_object_name = 'product'

    def get_object(self, **kwargs):
        return get_object_or_404(
            Product,
            pk=self.kwargs['product_id'],
            slug=self.kwargs['product'],
            sub_category__slug=self.kwargs['sub_category'],
            category__slug=self.kwargs['category'],
            is_shown=True,
        )

    def _get_attr_value(self, attrs_all, attr_name):
        value = None
        _attr = attrs_all.get(attr_name)
        if _attr:
            value = _attr['value']
        return value

    def get_data(self):
        """
        Получаем:
        - данные о товаре для вывода на странице
        - фото и видео
        - склады и кол-во товаров на них
        - дополнительные опции
        """
        # - модель и категория
        product = self.object
        model = product.model
        sub_category = product.sub_category
        category = product.category

        # - фото и видео
        photos = model.photos.filter(is_shown=True)
        videos = model.videos.filter(is_shown=True)

        # - в корзине или нет
        cart = self.request.session.get('cart', {})
        is_added = False
        added_warehouse_id = None
        added_extra_ids = []
        _product_id = str(product.id)

        if _product_id in cart:
            is_added = True
            item = cart[_product_id]
            added_warehouse_id = item.get('warehouse_id')
            added_extra_ids = [int(x) for x in item.get('extra', {}).keys()]

        # - склады и кол-во товаров на них
        in_stock_dict = {x.warehouse_id: x.number for x in product.stock_balance.all()}
        city_qs = City.objects.prefetch_related('warehouses').filter(warehouses__isnull=False).distinct()
        warehouses_by_city = []
        _selected = False

        # - атрибуты и специфические атрибуты
        attrs_all = {a['name']: a for a in product.get_attrs_list_v3(full=True)}
        _filtered_names = [
            'Срок изготовления',
            'Назначение',
            'Особенности конструкции',
            'Опции в базовой комплектации',
        ]
        attrs = {k: v for k, v in attrs_all.items() if k not in _filtered_names}

        # -- назначение
        purpose = self._get_attr_value(attrs_all, 'Назначение')
        # -- особенности конструкции
        design_features = self._get_attr_value(attrs_all, 'Особенности конструкции')
        # -- опции
        basic_options = self._get_attr_value(attrs_all, 'Опции в базовой комплектации')
        # -- срок изготовления
        making_days = self._get_attr_value(attrs_all, 'Срок изготовления')

        # -- список складов с группировкой по городу
        current_city = getattr(self.request, 'city', None)
        current_warehouse = getattr(self.request, 'warehouse', None)
        for city in city_qs:
            _warehouses = []
            _is_current = city == current_city

            for obj in city.warehouses.all():
                _in_stock = in_stock_dict.get(obj.id)
                obj_data = obj.to_dict()
                obj_data['in_stock'] = _in_stock
                if is_added is True:
                    if obj.id == added_warehouse_id:
                        obj_data['selected'] = True
                        _selected = True
                elif obj == current_warehouse:
                    obj_data['selected'] = True
                    _selected = True
                # elif _is_current and _in_stock and _selected is False:
                #     obj_data['selected'] = True
                #     _selected = True
                _warehouses.append(obj_data)

            if _is_current:
                warehouses_by_city.insert(0, _warehouses)
            else:
                warehouses_by_city.append(_warehouses)

        # if _selected is False:
        #     warehouses_by_city[0][0]['selected'] = True

        # - дополнительные опции
        extra_products = sub_category.extra_products.filter(is_active=True)

        # - в вишлисте?
        is_favorite = is_in_favorites(self.request, product.id)

        return {
            'model': model,
            'subcat': sub_category,
            'cat': category,
            'photos': photos,
            'videos': videos,
            'warehouses_by_city': warehouses_by_city,
            'attrs': attrs,
            'purpose': purpose,
            'design_features': design_features,
            'basic_options': basic_options,
            'has_texts': any([purpose, design_features, basic_options]),
            'making_days': making_days,
            'extra_products': extra_products,
            'is_added': is_added,
            'added_extra_ids': added_extra_ids,
            'is_favorite': is_favorite,
        }

    def get_context_data(self, **kwargs):
        data = self.get_data()
        data.update(super().get_context_data(**kwargs))
        return data
