from apps.third_party.cml.models import (
    ImportedGroup, ImportedProperty, ImportedPropertyVariant,
    ImportedBrand, ImportedProduct, ImportedWarehouse, ImportedStockBalance,
)


class GroupPipeline(object):
    """
    Item fields:
    id
    name
    groups
    """
    def process_item(self, item):
        group, _created = ImportedGroup.save_item(
            {'id': item.id},
            name=item.name,
            name_clean=item.name,  # TODO
        )
        do_not_sync = group.do_not_sync

        for child in item.groups:
            ImportedGroup.save_item(
                {'id': child.id},
                name=child.name,
                name_clean=child.name,  # TODO
                do_not_sync=do_not_sync,
                parent=group,
                tn_parent=group,
            )


class PropertyPipeline(object):
    """
    Item fields:
    id
    name
    value_type
    for_products
    """
    def process_item(self, item):
        ImportedProperty.save_item(
            {'id': item.id},
            name=item.name,
            name_clean=item.name,  # TODO
            value_type=item.value_type,
        )


class PropertyVariantPipeline(object):
    """
    Item fields:
    id
    value
    property_id
    """
    def process_item(self, item):
        ImportedPropertyVariant.save_item({'id': item.id}, value=item.value, property_id=item.property_id)


class SkuPipeline(object):
    """
    Item fields:
    id
    name
    name_full
    international_abbr
    """
    def process_item(self, item):
        pass


class TaxPipeline(object):
    """
    Item fields:
    name
    value
    """
    def process_item(self, item):
        pass


class ProductPipeline(object):
    """
    Item fields:
    id
    name
    bar_code
    vendor_code
    description
    sku_id
    group_ids
    properties
    tax_name
    image_path
    additional_fields
    """
    def process_item(self, item):
        _id = item.id
        model_id, product_id = (
            _id.split('#', 1)
            if '#' in _id
            else (None, _id)
        )

        brand_name = ImportedProduct.get_brand_name(item.name)
        # brand, _ = ImportedBrand.objects.get_or_create(
        #     name=brand_name,
        #     defaults={'name_clean': brand_name, 'do_not_sync': True},
        # )
        brand = ImportedBrand.objects.filter(name__iexact=brand_name).first()

        _group_ids = item.group_ids
        _additional_fields = {}
        for f in item.additional_fields:
            _additional_fields[f.name] = f.value

        kw = {
            'model_id': model_id,
            'product_id': product_id,
            'name': item.name,
            'name_clean': item.name,
            'brand_name': brand_name,
            'brand': brand,
            'group_id': _group_ids[0] if _group_ids else None,
            'group_ids': _group_ids,
            'bar_code': item.bar_code,
            'vendor_code': item.vendor_code,
            'description': item.description,
            'properties': dict(item.properties),
            'image_path': item.image_path,
            'additional_fields': _additional_fields,
            'has_removed': False,
        }
        ImportedProduct.save_item({'id': item.id}, **kw)
        # product, _created = ImportedProduct.save_item({'id': item.id}, **kw)
        # if _created:
        #     if brand:
        #         product.brand = brand
        #         product.save(check_changes=False)


class PriceTypePipeline(object):
    """
    Item fields:
    id
    name
    currency
    tax_name
    tax_in_sum
    """
    def process_item(self, item):
        pass


class WarehousePipeline(object):
    """
    Item fields:
    id
    name
    address
    phone
    """
    def process_item(self, item):
        ImportedWarehouse.save_item(
            {'id': item.id},
            name=item.name,
            address=item.address,
            phone=item.phone,
        )


class OfferPipeline(object):
    """
    Item fields:
    id
    additional_id
    name
    sku_id
    prices
    stock_balances
    """
    def process_item(self, item):
        # - получаем id товара
        product_id = (
            f'{item.id}#{item.additional_id}'
            if item.additional_id
            else item.id
        )

        # - проставляем цену
        if item.prices:
            price = item.prices[0]
            price = price.price_for_sku
            if price:
                product = ImportedProduct.objects.filter(id=product_id).first()
                if product:
                    product.price = price
                    product.save(check_changes=False)

        # - проставляем остатки
        for balance_item in item.stock_balances:
            warehouse_id = balance_item.warehouse_id
            number = balance_item.number
            balance_obj, _created = ImportedStockBalance.objects.get_or_create(
                warehouse_id=warehouse_id, product_id=product_id, defaults={'number': number}
            )
            if _created is False:
                balance_obj.number = number
                balance_obj.save(check_changes=False)


class OrderPipeline(object):
    """
    Item fields:
    id
    number
    date
    currency_name
    currency_rate
    operation
    role
    sum
    client
    time
    comment
    items
    additional_fields
    """
    def process_item(self, item):
        pass

    def yield_item(self):
        pass

    def flush(self):
        pass
