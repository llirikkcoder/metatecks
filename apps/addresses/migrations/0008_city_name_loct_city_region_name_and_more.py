import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0007_warehouse_name_short'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='name_loct',
            field=models.CharField(blank=True, help_text='например, "Москве"', max_length=31, verbose_name='Название (предл. падеж)'),
        ),
        migrations.AddField(
            model_name='city',
            name='region_name',
            field=models.CharField(blank=True, help_text='например, "Московская область"', max_length=63, verbose_name='Название региона'),
        ),
        migrations.AddField(
            model_name='city',
            name='region_name_loct',
            field=models.CharField(blank=True, help_text='например, "Московской области"', max_length=63, verbose_name='Название региона (предл. падеж)'),
        ),
        migrations.AlterField(
            model_name='city',
            name='names_en',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=31), blank=True, default=list, help_text='для геолокации', size=None, verbose_name='Названия (англ.)'),
        ),
        migrations.AlterField(
            model_name='city',
            name='region_names_en',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=31), blank=True, default=list, help_text='для геолокации', size=None, verbose_name='Названия региона (англ.)'),
        ),
    ]
