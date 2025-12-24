from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0022_update_attribute_fields'),
        ('addresses', '0002_load_data'),
        ('cml', '0011_importedproperty_dont_show_in_lists'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='importedbrand',
            options={'ordering': ['name'], 'verbose_name': 'бренд', 'verbose_name_plural': 'бренды'},
        ),
        migrations.AlterModelOptions(
            name='importedgroup',
            options={'ordering': ['-tn_priority', 'name'], 'verbose_name': 'группа', 'verbose_name_plural': 'группы'},
        ),
        migrations.AlterModelOptions(
            name='importedproduct',
            options={'verbose_name': 'товар', 'verbose_name_plural': 'товары'},
        ),
        migrations.AlterModelOptions(
            name='importedproperty',
            options={'verbose_name': 'свойство', 'verbose_name_plural': 'свойства товаров'},
        ),
        migrations.AlterModelOptions(
            name='importedpropertyvariant',
            options={'verbose_name': 'вариант', 'verbose_name_plural': 'свойства: варианты'},
        ),
        migrations.AlterModelOptions(
            name='importedstockbalance',
            options={'ordering': ['updated_at'], 'verbose_name': 'количество на складе', 'verbose_name_plural': 'товары: количество на складе'},
        ),
        migrations.AlterModelOptions(
            name='importedwarehouse',
            options={'verbose_name': 'склад', 'verbose_name_plural': 'склады'},
        ),
        migrations.AddField(
            model_name='importedwarehouse',
            name='address',
            field=models.CharField(blank=True, max_length=127, null=True, verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='importedwarehouse',
            name='phone',
            field=models.CharField(blank=True, max_length=127, null=True, verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('import', 'import'), ('export', 'export')], max_length=50),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='brand_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_brands', to='catalog.brand', verbose_name='Бренд'),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='do_not_sync',
            field=models.BooleanField(default=True, verbose_name='Не синхронизировать с сайтом'),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='is_name_bad',
            field=models.BooleanField(default=False, verbose_name='Плохое'),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='is_name_good',
            field=models.BooleanField(default=False, verbose_name='Хорошее'),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='is_name_partial',
            field=models.BooleanField(default=False, verbose_name='Частичное'),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='name',
            field=models.CharField(max_length=127, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='name_clean',
            field=models.CharField(max_length=127, verbose_name='Наименование (чистое)'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='category_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_groups', to='catalog.category', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='fields_changed',
            field=models.JSONField(default=list, verbose_name='Измененные поля'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='has_changed',
            field=models.BooleanField(default=False, verbose_name='Изменялся?'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='has_removed',
            field=models.BooleanField(default=False, verbose_name='Удален?'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='id',
            field=models.CharField(max_length=127, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Новый?'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='name',
            field=models.CharField(max_length=127, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='name_clean',
            field=models.CharField(blank=True, default='', max_length=127, verbose_name='Наименование (чистое)'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='parent',
            field=models.ForeignKey(blank=True, limit_choices_to={'parent': None}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cml.importedgroup', verbose_name='Основная группа'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='subcategory_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_groups', to='catalog.subcategory', verbose_name='Подкатегория'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='additional_fields',
            field=models.JSONField(default=dict, verbose_name='Реквизиты'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='bar_code',
            field=models.CharField(blank=True, max_length=63, verbose_name='Штрихкод'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='cml.importedbrand', verbose_name='Бренд (1С)'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='brand_name',
            field=models.CharField(blank=True, default='', max_length=127, verbose_name='Наименование бренда'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='brand_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.brand', verbose_name='Бренд (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='fields_changed',
            field=models.JSONField(default=list, verbose_name='Измененные поля'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='cml.importedgroup', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='group_ids',
            field=models.JSONField(default=list, verbose_name='ID групп'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='has_changed',
            field=models.BooleanField(default=False, verbose_name='Изменялся?'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='has_removed',
            field=models.BooleanField(default=False, verbose_name='Удален?'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='id',
            field=models.CharField(max_length=127, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='image_path',
            field=models.CharField(blank=True, max_length=511, verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Новый?'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='model_id',
            field=models.CharField(blank=True, db_index=True, max_length=127, null=True, verbose_name='ID модели'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='model_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.productmodel', verbose_name='Модель'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='name',
            field=models.CharField(max_length=127, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='name_clean',
            field=models.CharField(blank=True, default='', max_length=127, verbose_name='Наименование (чистое)'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='product_id',
            field=models.CharField(blank=True, db_index=True, max_length=127, null=True, verbose_name='ID товара'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='product_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.product', verbose_name='Товар'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='properties',
            field=models.JSONField(default=dict, verbose_name='Свойства'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='vendor_code',
            field=models.CharField(blank=True, max_length=63, verbose_name='Артикул'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='attribute_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_properties', to='catalog.attribute', verbose_name='Характеристика (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='dont_show_in_lists',
            field=models.BooleanField(default=False, verbose_name='Не показывать в списке товаров'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='fields_changed',
            field=models.JSONField(default=list, verbose_name='Измененные поля'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='has_changed',
            field=models.BooleanField(default=False, verbose_name='Изменялся?'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='has_removed',
            field=models.BooleanField(default=False, verbose_name='Удален?'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='id',
            field=models.CharField(max_length=127, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Новый?'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='name',
            field=models.CharField(max_length=127, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='name_clean',
            field=models.CharField(blank=True, default='', max_length=127, verbose_name='Наименование (чистое)'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='unit_name',
            field=models.CharField(blank=True, default='', max_length=31, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='value_type',
            field=models.CharField(max_length=63, verbose_name='Тип значения'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='fields_changed',
            field=models.JSONField(default=list, verbose_name='Измененные поля'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='has_changed',
            field=models.BooleanField(default=False, verbose_name='Изменялся?'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='has_removed',
            field=models.BooleanField(default=False, verbose_name='Удален?'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='id',
            field=models.CharField(max_length=127, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Новый?'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='option_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_variants', to='catalog.attributeoption', verbose_name='Вариант'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='cml.importedproperty', verbose_name='Свойство'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='value',
            field=models.CharField(max_length=127, verbose_name='Значение'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='balance_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_balance', to='catalog.productstockbalance', verbose_name='Остаток (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='fields_changed',
            field=models.JSONField(default=list, verbose_name='Измененные поля'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='has_changed',
            field=models.BooleanField(default=False, verbose_name='Изменялся?'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='has_removed',
            field=models.BooleanField(default=False, verbose_name='Удален?'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Новый?'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='number',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во на складе'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='product_id',
            field=models.CharField(db_index=True, max_length=127, verbose_name='ID товара'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='warehouse_id',
            field=models.CharField(db_index=True, max_length=127, verbose_name='ID склада'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='fields_changed',
            field=models.JSONField(default=list, verbose_name='Измененные поля'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='has_changed',
            field=models.BooleanField(default=False, verbose_name='Изменялся?'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='has_removed',
            field=models.BooleanField(default=False, verbose_name='Удален?'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='id',
            field=models.CharField(max_length=127, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Новый?'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='name',
            field=models.CharField(max_length=127, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='warehouse_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_warehouses', to='addresses.warehouse', verbose_name='Склад'),
        ),
    ]
