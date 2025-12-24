from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_content', '0002_update_video_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediatag',
            name='slug',
            field=models.SlugField(default='', unique=True, verbose_name='Адрес в url'),
            preserve_default=False,
        ),
    ]
