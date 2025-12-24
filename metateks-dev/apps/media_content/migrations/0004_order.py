from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_content', '0003_mediatag_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mediafile',
            options={'ordering': ['order'], 'verbose_name': 'файл', 'verbose_name_plural': '3) Файлы'},
        ),
        migrations.AlterModelOptions(
            name='mediaphoto',
            options={'ordering': ['order'], 'verbose_name': 'фото', 'verbose_name_plural': '2) Фото'},
        ),
        migrations.AlterModelOptions(
            name='mediavideo',
            options={'ordering': ['order'], 'verbose_name': 'видео', 'verbose_name_plural': '1) Видео'},
        ),
        migrations.AddField(
            model_name='mediafile',
            name='order',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Порядок'),
        ),
        migrations.AddField(
            model_name='mediaphoto',
            name='order',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Порядок'),
        ),
        migrations.AddField(
            model_name='mediavideo',
            name='order',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Порядок'),
        ),
    ]
