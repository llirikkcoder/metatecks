from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_update_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='dont_show_in_lists',
            field=models.BooleanField(default=False, verbose_name='Не выводить в списке товаров'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='unit_str',
            field=models.CharField(blank=True, default='', max_length=31, verbose_name='Единица измерения (текстом)'),
        ),
        migrations.AlterField(
            model_name='attribute',
            name='attr_type',
            field=models.CharField(choices=[('string', 'строка'), ('int', 'целое число'), ('float', 'дробное число'), ('number', 'число (1C)')], default='string', max_length=7, verbose_name='Тип значения'),
        ),
    ]
