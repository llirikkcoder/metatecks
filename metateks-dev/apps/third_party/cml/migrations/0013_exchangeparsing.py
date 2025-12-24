from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_load_data'),
        ('catalog', '0023_subcategory_attribute_in_filter'),
        ('cml', '0012_add_warehouse_address_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importedbrand',
            name='brand_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_brands', to='catalog.brand', verbose_name='Бренд (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedbrand',
            name='do_not_sync',
            field=models.BooleanField(default=True, verbose_name='Не синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='category_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_groups', to='catalog.category', verbose_name='Категория (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не&nbsp;синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='subcategory_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_groups', to='catalog.subcategory', verbose_name='Подкатегория (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не&nbsp;синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='cml.importedgroup', verbose_name='Группа (1C)'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='model_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.productmodel', verbose_name='Модель (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='product_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.product', verbose_name='Товар (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedproperty',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не&nbsp;синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не&nbsp;синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='option_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_variants', to='catalog.attributeoption', verbose_name='Вариант (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedpropertyvariant',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='cml.importedproperty', verbose_name='Свойство (сайт)'),
        ),
        migrations.AlterField(
            model_name='importedstockbalance',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не&nbsp;синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='do_not_sync',
            field=models.BooleanField(default=False, verbose_name='Не&nbsp;синхронизировать'),
        ),
        migrations.AlterField(
            model_name='importedwarehouse',
            name='warehouse_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_warehouses', to='addresses.warehouse', verbose_name='Склад (сайт)'),
        ),
        migrations.CreateModel(
            name='ExchangeParsing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('import_filename', models.CharField(max_length=255)),
                ('import_file_path', models.CharField(max_length=255)),
                ('import_was_imported', models.BooleanField(default=False)),
                ('import_imported_at', models.DateTimeField(blank=True, null=True)),
                ('import_error_message', models.TextField(blank=True)),
                ('offers_filename', models.CharField(max_length=255)),
                ('offers_file_path', models.CharField(max_length=255)),
                ('offers_was_imported', models.BooleanField(default=False)),
                ('offers_imported_at', models.DateTimeField(blank=True, null=True)),
                ('offers_error_message', models.TextField(blank=True)),
                ('is_full', models.BooleanField(default=False)),
                ('was_synced', models.BooleanField(default=False)),
                ('synced_at', models.DateTimeField(blank=True, null=True)),
                ('sync_error_message', models.TextField(blank=True)),
                ('stats_before', models.JSONField(default=dict)),
                ('stats_after', models.JSONField(default=dict)),
                ('import_xml_obj', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='import_xml_parsing', to='cml.exchange')),
                ('offers_xml_obj', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='offers_xml_parsing', to='cml.exchange')),
            ],
            options={
                'verbose_name': 'объекты парсинга',
                'verbose_name_plural': 'парсинг',
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
