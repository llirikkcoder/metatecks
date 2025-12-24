import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0004_load_cities'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='names_en',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=31), blank=True, default=list, size=None, verbose_name='Названия (англ.)'),
        ),
        migrations.AddField(
            model_name='city',
            name='region_names_en',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=31), blank=True, default=list, size=None, verbose_name='Названия региона (англ.)'),
        ),
    ]
