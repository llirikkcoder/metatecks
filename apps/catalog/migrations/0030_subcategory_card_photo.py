# Generated manually for task _metatecks-26j
from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0029_seo_templates'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='card_photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(
                blank=True,
                help_text='Необязательно. Если не загружено, будет использоваться обрезанная версия основного изображения',
                null=True,
                upload_to='sub_categories/card_photos/',
                verbose_name='Изображение для карточки анонса'
            ),
        ),
    ]
