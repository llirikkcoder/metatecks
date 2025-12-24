from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0019_add_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvideo',
            name='video_id',
        ),
        migrations.AlterField(
            model_name='productvideo',
            name='video',
            field=models.TextField(blank=True, null=True, verbose_name='Видео (код для вставки на сайт)'),
        ),
    ]
