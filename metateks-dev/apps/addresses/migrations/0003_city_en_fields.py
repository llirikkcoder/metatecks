from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_load_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='name_en',
            field=models.CharField(blank=True, max_length=31, verbose_name='Название (англ.)'),
        ),
        migrations.AddField(
            model_name='city',
            name='region_en',
            field=models.CharField(blank=True, max_length=31, verbose_name='Название региона (англ.)'),
        ),
        migrations.AlterField(
            model_name='city',
            name='subdomain',
            field=models.CharField(blank=True, default='', help_text='<город>.metateks.ru', max_length=31, unique=True, verbose_name='Поддомен'),
        ),
    ]
