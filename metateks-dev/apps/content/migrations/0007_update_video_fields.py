from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_load_homepage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aboutadvantage',
            name='video_id',
        ),
        migrations.AlterField(
            model_name='aboutadvantage',
            name='video',
            field=models.TextField(blank=True, null=True, verbose_name='Видео (код для вставки на сайт)'),
        ),
        migrations.DeleteModel(
            name='AboutBrand',
        ),
    ]
