from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_category_name_plural'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='h1',
            field=models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1'),
        ),
        migrations.AddField(
            model_name='category',
            name='h1',
            field=models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1'),
        ),
        migrations.AddField(
            model_name='product',
            name='h1',
            field=models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='h1',
            field=models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='meta_title',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)'),
        ),
        migrations.AlterField(
            model_name='category',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)'),
        ),
        migrations.AlterField(
            model_name='category',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)'),
        ),
        migrations.AlterField(
            model_name='category',
            name='meta_title',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_title',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='meta_title',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)'),
        ),
    ]
