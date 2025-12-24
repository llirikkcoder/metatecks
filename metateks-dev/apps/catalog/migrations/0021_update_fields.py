from django.db import migrations, models


def set_vendor_code(apps, schema_editor):
    ProductModel = apps.get_model('catalog', 'ProductModel')
    ProductModel.objects.filter(vendor_code='').update(vendor_code=None)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_update_video_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='id_1c',
        ),
        migrations.RemoveField(
            model_name='subcategory',
            name='id_1c',
        ),
        migrations.AddField(
            model_name='product',
            name='brand_name',
            field=models.CharField(default='', max_length=127, verbose_name='Название бренда (автомат.)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='vendor_code',
            field=models.CharField(blank=True, max_length=31, verbose_name='Артикул'),
        ),
        migrations.AlterField(
            model_name='productmodel',
            name='vendor_code',
            field=models.CharField(blank=True, db_index=True, max_length=31, null=True, verbose_name='Артикул'),
        ),
        migrations.RunPython(set_vendor_code, reverse_code=migrations.RunPython.noop),
    ]
