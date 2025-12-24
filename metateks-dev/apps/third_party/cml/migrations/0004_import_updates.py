import dirtyfields.dirtyfields
from django.db import migrations, models
import django.db.models.deletion


def set_default_values(apps, schema_editor):
    ImportedGroup = apps.get_model('cml', 'ImportedGroup')
    ImportedGroup.objects.update(name_clean=models.F('name'))
    ImportedProperty = apps.get_model('cml', 'ImportedProperty')
    ImportedProperty.objects.update(name_clean=models.F('name'))
    ImportedProduct = apps.get_model('cml', 'ImportedProduct')
    ImportedProduct.objects.update(product_id=models.F('id'), name_clean=models.F('name'))


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_update_video_fields'),
        ('cml', '0003_update_video_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedWarehouse',
            fields=[
                ('is_new', models.BooleanField(default=False)),
                ('has_changed', models.BooleanField(default=False)),
                ('has_removed', models.BooleanField(default=False)),
                ('fields_changed', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=127, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=127)),
            ],
            options={
                'ordering': ['updated_at'],
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.AddField(
            model_name='importedgroup',
            name='category_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_groups', to='catalog.category'),
        ),
        migrations.AddField(
            model_name='importedgroup',
            name='name_clean',
            field=models.CharField(blank=True, default='', max_length=127),
        ),
        migrations.AddField(
            model_name='importedgroup',
            name='subcategory_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_groups', to='catalog.subcategory'),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='brand_name',
            field=models.CharField(blank=True, default='', max_length=127),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='model_id',
            field=models.CharField(blank=True, db_index=True, max_length=127, null=True),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='model_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.productmodel'),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='name_clean',
            field=models.CharField(blank=True, default='', max_length=127),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='product_id',
            field=models.CharField(blank=True, db_index=True, max_length=127, null=True),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='product_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.product'),
        ),
        migrations.AddField(
            model_name='importedproperty',
            name='attribute_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_properties', to='catalog.attribute'),
        ),
        migrations.AddField(
            model_name='importedproperty',
            name='name_clean',
            field=models.CharField(blank=True, default='', max_length=127),
        ),
        migrations.AddField(
            model_name='importedpropertyvariant',
            name='option_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_variants', to='catalog.attributeoption'),
        ),
        migrations.CreateModel(
            name='ImportedStockBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_new', models.BooleanField(default=False)),
                ('has_changed', models.BooleanField(default=False)),
                ('has_removed', models.BooleanField(default=False)),
                ('fields_changed', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('warehouse_id', models.CharField(db_index=True, max_length=127)),
                ('product_id', models.CharField(db_index=True, max_length=127)),
                ('number', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['updated_at'],
                'unique_together': {('warehouse_id', 'product_id')},
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.RunPython(set_default_values, reverse_code=migrations.RunPython.noop),
    ]
