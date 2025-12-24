from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0002_update_promotion_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='banner_695',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='p/', verbose_name='Баннер (695x522px)'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='banner',
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to='p/', verbose_name='Баннер (1920x720px)'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='new_price',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Новая цена на баннере, руб.'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='old_price',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Старая цена на баннере, руб.'),
        ),
    ]
