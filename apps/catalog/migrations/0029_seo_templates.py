from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0028_product_is_in_stock_dict_and_more'),
    ]

    operations = [
        # Category
        migrations.AddField(
            model_name='category',
            name='meta_title_template',
            field=models.CharField(
                blank=True,
                help_text='Используйте плейсхолдеры: {name}, {category}, {city}, {region}',
                max_length=511,
                verbose_name='Шаблон Meta Title'
            ),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_desc_template',
            field=models.TextField(
                blank=True,
                help_text='Используйте плейсхолдеры: {name}, {category}, {city}, {region}',
                verbose_name='Шаблон Meta Description'
            ),
        ),
        migrations.AddField(
            model_name='category',
            name='h1_template',
            field=models.CharField(
                blank=True,
                help_text='Используйте плейсхолдеры для динамической генерации заголовка',
                max_length=511,
                verbose_name='Шаблон H1'
            ),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_keywords_template',
            field=models.TextField(
                blank=True,
                help_text='(опционально) Используйте плейсхолдеры',
                verbose_name='Шаблон Meta Keywords'
            ),
        ),

        # SubCategory
        migrations.AddField(
            model_name='subcategory',
            name='meta_title_template',
            field=models.CharField(
                blank=True,
                help_text='Используйте плейсхолдеры: {name}, {category}, {subcategory}, {city}, {region}',
                max_length=511,
                verbose_name='Шаблон Meta Title'
            ),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='meta_desc_template',
            field=models.TextField(
                blank=True,
                help_text='Используйте плейсхолдеры: {name}, {subcategory}, {city}, {region}',
                verbose_name='Шаблон Meta Description'
            ),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='h1_template',
            field=models.CharField(
                blank=True,
                help_text='Используйте плейсхолдеры для динамической генерации заголовка',
                max_length=511,
                verbose_name='Шаблон H1'
            ),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='meta_keywords_template',
            field=models.TextField(
                blank=True,
                help_text='(опционально) Используйте плейсхолдеры',
                verbose_name='Шаблон Meta Keywords'
            ),
        ),

        # ProductModel
        migrations.AddField(
            model_name='productmodel',
            name='meta_title_template',
            field=models.CharField(
                blank=True,
                help_text='Используйте плейсхолдеры: {name}, {brand}, {price}, {attr:название}',
                max_length=511,
                verbose_name='Шаблон Meta Title'
            ),
        ),
        migrations.AddField(
            model_name='productmodel',
            name='meta_desc_template',
            field=models.TextField(
                blank=True,
                help_text='Используйте плейсхолдеры: {name}, {price}, {vendor_code}, {city}, {region}, {attr:грузоподъемность}',
                verbose_name='Шаблон Meta Description'
            ),
        ),
        migrations.AddField(
            model_name='productmodel',
            name='h1_template',
            field=models.CharField(
                blank=True,
                help_text='Используйте плейсхолдеры для динамической генерации заголовка',
                max_length=511,
                verbose_name='Шаблон H1'
            ),
        ),
        migrations.AddField(
            model_name='productmodel',
            name='meta_keywords_template',
            field=models.TextField(
                blank=True,
                help_text='(опционально) Используйте плейсхолдеры',
                verbose_name='Шаблон Meta Keywords'
            ),
        ),
    ]
