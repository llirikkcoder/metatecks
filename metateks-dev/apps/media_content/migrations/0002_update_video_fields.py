from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_content', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediavideo',
            name='video_id',
        ),
        migrations.AlterField(
            model_name='mediavideo',
            name='video',
            field=models.TextField(blank=True, null=True, verbose_name='Видео (код для вставки на сайт)'),
        ),
    ]
