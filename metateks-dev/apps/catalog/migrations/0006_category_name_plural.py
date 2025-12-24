from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_load_brands'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_plural',
            field=models.CharField(blank=True, help_text='пример: «фронтальные погрузчики»', max_length=255, verbose_name='Название (во множественном числе)'),
        ),
    ]
