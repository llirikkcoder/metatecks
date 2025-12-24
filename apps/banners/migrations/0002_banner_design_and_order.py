from django.db import migrations, models


def set_order(apps, schema_editor):
    Banner = apps.get_model('banners', 'Banner')
    Banner.objects.update(order=models.F('id'))


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ['order'], 'verbose_name': 'баннер', 'verbose_name_plural': 'баннеры'},
        ),
        migrations.AddField(
            model_name='banner',
            name='design',
            field=models.CharField(choices=[('light', 'светлый фон, черный текст'), ('dark', 'темный фон, светлый текст')], default='light', max_length=7, verbose_name='Оформление'),
        ),
        migrations.AddField(
            model_name='banner',
            name='order',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Порядок'),
        ),
        migrations.RunPython(set_order, reverse_code=migrations.RunPython.noop),
    ]
