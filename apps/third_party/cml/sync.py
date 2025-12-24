import logging
import os
import shutil

import filetype
from pytils.translit import slugify

from apps.catalog.models import Attribute, Brand, ProductModel, Product, ProductStockBalance
from .models import (
    ImportedGroup, ImportedProperty, ImportedBrand,
    ImportedProduct, ImportedWarehouse, ImportedStockBalance,
)


l = logging.getLogger('cml.sync')


def sync_groups():
    pass


def sync_properties():
    l.info('  sync_properties() start')

    for p in ImportedProperty.objects.filter(do_not_sync=False, attribute_obj__isnull=True).exclude(value_type='Справочник'):
        attr_type = p.attr_type
        attr, _created = Attribute.objects.get_or_create(
            name=p.name_clean, unit_str=p.unit_name, attr_type=p.attr_type, is_synced_with_1c=True,
            defaults={'dont_show_in_lists': p.dont_show_in_lists},
        )
        if _created:
            attr.save()  # чтобы заполнить slug
        p.attribute_obj = attr
        p.save()

    # for i, a in enumerate(Attribute.objects.all().order_by('-is_synced_with_1c', 'name')):
    for i, a in enumerate(Attribute.objects.all().order_by('-is_synced_with_1c', 'order')):
        a.order = i+1
        a.save()

    l.info('  sync_properties() done')


def sync_brands():
    pass


def sync_products():
    l.info('  sync_products() start')

    props_qs = ImportedProperty.objects.filter(do_not_sync=False, attribute_obj__isnull=False)
    PROPERTIES = {p.id: p for p in props_qs}
    brands_qs = ImportedBrand.objects.filter(brand_obj__isnull=False)
    BRANDS = {b.id: b for b in brands_qs}

    qs = ImportedProduct.for_sync()
    count = qs.count()
    l.info('    ImportedProduct.for_sync() count: %d', count)

    for i, p in enumerate(qs):
        # == 1) модель ==
        model = None
        _created = False

        # - получаем id модели
        model_id = p.model_id
        if not model_id:
            model_id = p.id

        # - получаем характеристики
        attrs = {}
        for k, v in p.properties.items():
            prop = PROPERTIES.get(k)
            if not prop:
                continue
            attr_id = prop.attribute_obj_id
            if prop.attr_type == 'number':
                v = v.replace(' ', '').replace(',', '.')
                if '.' in v:
                    try:
                        v = float(v)
                    except ValueError:
                        continue
                else:
                    try:
                        v = int(v)
                    except ValueError:
                        continue
            attrs[f'a{attr_id}'] = v

        # - собираем dict
        model_kw = {
            'name': p.model_name,
            'sub_category_id': p.group.subcategory_obj_id,
            'price': p.price,
            'description': p.description,
            'attrs': attrs,
            'is_synced_with_1c': True,
            'vendor_code': p.vendor_code,
        }

        # - создаем/апдейтим модель
        model = p.model_obj
        if not model:
            model, _created = ProductModel.objects.get_or_create(id_1c=model_id, defaults=model_kw)
            p.model_obj = model
            p.save()
        if _created is False:
            for k, v in model_kw.items():
                if k == 'price' and not v:
                    continue
                setattr(model, k, v)
            model.save()

        # - фото
        if p.image_path:
            try:
                if filetype.is_image(p.image_path):
                    image_name = os.path.basename(p.image_path)
                    if (not model.photo or image_name != os.path.basename(model.photo.path)):
                        shutil.copy(p.image_path, 'media/models/photos_1c/')
                        model.photo = f'models/photos_1c/{image_name}'
                        model.save()
            except FileNotFoundError:
                pass

        # == 2) товар ==
        product = None
        _created = False

        # - получаем id товара
        product_id = p.product_id
        if not product_id:
            product_id = p.id

        # - получаем бренд
        brand_name = p.brand_name
        brand_id = None
        brand = BRANDS.get(p.brand_id)
        if brand:
            brand_name = brand.name_clean
            brand_id = brand.brand_obj_id

        # - собираем dict
        product_kw = {
            'name': p.name,
            'slug': slugify(p.name)[:255],
            'brand_name': brand_name,
            'brand_id': brand_id,
            'is_synced_with_1c': True,
            'bar_code': p.bar_code,
            'vendor_code': p.vendor_code,
        }

        # - создаем/апдейтим товар
        product = p.product_obj
        if not product:
            product, _created = Product.objects.get_or_create(model_id=model.id, id_1c=product_id, defaults=product_kw)
            p.product_obj = product
            p.save()
        if _created is False:
            del product_kw['slug']
            for k, v in product_kw.items():
                setattr(product, k, v)
            product.save()

        if i == 0:
            l.info('    pervyi poshel!')
        if not (i+1) % 100:
            l.info('    done: %d/%d', i+1, count)

        # + заполнить реквизиты (ProductProperty)?

    l.info('  sync_products() done')


def sync_stock_balance():
    l.info('  sync_stock_balance() start')

    warehouses_qs = ImportedWarehouse.objects.filter(warehouse_obj__isnull=False)
    WAREHOUSES = {w.id: w.warehouse_obj_id for w in warehouses_qs}
    products_qs = ImportedProduct.objects.filter(product_obj__isnull=False)
    PRODUCTS = {p.id: p.product_obj_id for p in products_qs}

    qs = ImportedStockBalance.objects.filter(
        warehouse_id__in=WAREHOUSES.keys(), product_id__in=PRODUCTS.keys(),
    )
    count = qs.count()
    l.info('    ImportedStockBalance.for_sync() count: %d', count)

    for i, obj in enumerate(qs):
        _created = False
        balance = obj.balance_obj
        if not balance:
            balance, _created = ProductStockBalance.objects.get_or_create(
                warehouse_id=WAREHOUSES.get(obj.warehouse_id),
                product_id=PRODUCTS.get(obj.product_id),
                defaults={'number': obj.number},
            )
            obj.balance_obj = balance
            obj.save()
        if _created is False:
            balance.number = obj.number
            balance.save()

        if i == 0:
            l.info('    pervyi poshel!')
        if not (i+1) % 100:
            l.info('    done: %d/%d', i+1, count)

    l.info('  sync_stock_balance() done')


def sync_products_in_stock():
    l.info('  sync_products_in_stock() start')

    _products = Product.objects.prefetch_related('stock_balance')

    products1 = _products.filter(stock_balance__isnull=True)
    products1.update(number_in_stock=0)

    products2 = _products.filter(stock_balance__isnull=False)
    count = products2.count()
    l.info('    Products for update count: %d', count)

    for i, obj in enumerate(products2):
        obj.number_in_stock = obj.get_in_stock()
        obj.save()

        if i == 0:
            l.info('    pervyi poshel!')
        if not (i+1) % 100:
            l.info('    done: %d/%d', i+1, count)

    l.info('  sync_products_in_stock() done')


def start_sync(modules=None, is_full=False):
    l.info('[sync] is_full/%s: start...', is_full)

    try:
        modules = modules or ['groups', 'properties', 'brands', 'products', 'stock_balance', 'products_in_stock']
        # if 'groups' in modules:
        #     sync_groups()
        if 'properties' in modules:
            sync_properties()
        # if 'brands' in modules:
        #     sync_brands()
        if 'products' in modules:
            sync_products()
        if 'stock_balance' in modules:
            sync_stock_balance()
        if 'products_in_stock' in modules:
            sync_products_in_stock()

        l.info('[sync] is_full/%s: done!', is_full)

        if is_full is True:
            l.info('[sync] is_full/%s: hiding removed products...', is_full)

            removed_products = ImportedProduct.objects.filter(has_removed=True, product_obj__isnull=False)
            product_ids = removed_products.values_list('product_obj_id', flat=True)
            products = Product.objects.filter(id__in=product_ids, is_shown=True)
            l.info('[sync] is_full/%s:   products count: %d', is_full, products.count())

            products.update(is_shown=False)
            l.info('[sync] is_full/%s:   done!', is_full)

    except Exception as exc:
        err_message = repr(exc)
        l.error('[sync] is_full/%s: sync error: %s', is_full, err_message)
        raise exc
