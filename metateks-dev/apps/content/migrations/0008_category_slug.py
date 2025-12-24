from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_update_video_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlescategory',
            name='slug',
            field=models.SlugField(default='', unique=True, verbose_name='Адрес в url'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='newscategory',
            name='slug',
            field=models.SlugField(default='', unique=True, verbose_name='Адрес в url'),
            preserve_default=False,
        ),
    ]
