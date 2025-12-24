from django.db import migrations, models
import sortedm2m.fields


def fill_subcategory_fields(apps, schema_editor):
    SubCategory = apps.get_model('catalog', 'SubCategory')
    for obj in SubCategory.objects.prefetch_related('attributes'):
        obj.attributes_in_products.set(obj.attributes.all())
        obj.attr_products_ids = obj.attr_ids
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_increase_attribute_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='name_admin',
            field=models.CharField(blank=True, max_length=255, verbose_name='Название в админке'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='name_short',
            field=models.CharField(blank=True, help_text='для списка товаров; например, «Г/п машины»', max_length=255, verbose_name='Краткое название'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='name_filter',
            field=models.CharField(blank=True, help_text='для фильтра товаров; например, «Грузоподъемность погрузчика»', max_length=255, verbose_name='Название в фильтре'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='attr_products_ids',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='attributes_in_products',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, related_name='products_sub_categories', to='catalog.attribute', verbose_name='Характеристики в списке товаров'),
        ),
        migrations.RunPython(fill_subcategory_fields, reverse_code=migrations.RunPython.noop),
    ]
