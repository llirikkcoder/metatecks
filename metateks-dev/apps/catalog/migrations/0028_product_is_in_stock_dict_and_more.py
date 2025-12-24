from django.db import migrations, models


def fill_in_stock_dicts(apps, schema_editor):
    City = apps.get_model('addresses', 'City')
    city_ids = City.objects.values_list('id', flat=True)
    Warehouse = apps.get_model('addresses', 'Warehouse')
    warehouse_ids = Warehouse.objects.values_list('id', flat=True)

    _ids = [f'c{_id}' for _id in city_ids]
    _ids.extend([f'wh{_id}' for _id in warehouse_ids])

    warehouse_to_city = {}
    for wh in Warehouse.objects.all():
        warehouse_to_city[wh.id] = wh.city_id

    Product = apps.get_model('catalog', 'Product')
    products = Product.objects.prefetch_related('stock_balance')
    for obj in products:
        number_in_stock = {_id: 0 for _id in _ids}
        is_in_stock = {_id: False for _id in _ids}

        for balance in obj.stock_balance.all():
            if balance.number:
                number = balance.number
                _wh_id = f'wh{balance.warehouse_id}'
                _city_id = f'c{warehouse_to_city[balance.warehouse_id]}'

                number_in_stock[_wh_id] = number
                is_in_stock[_wh_id] = True

                if number_in_stock[_city_id] < number:
                    number_in_stock[_city_id] = number
                if is_in_stock[_city_id] is False:
                    is_in_stock[_city_id] = True

        obj.number_in_stock_dict = number_in_stock
        obj.is_in_stock_dict = is_in_stock
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0027_extra_products_rename'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_in_stock_dict',
            field=models.JSONField(default=dict, help_text='по городам и складам', verbose_name='Есть на складах?'),
        ),
        migrations.AddField(
            model_name='product',
            name='number_in_stock_dict',
            field=models.JSONField(default=dict, help_text='по городам и складам', verbose_name='Максимальное количество на складах'),
        ),
        migrations.RunPython(fill_in_stock_dicts, reverse_code=migrations.RunPython.noop),
    ]
