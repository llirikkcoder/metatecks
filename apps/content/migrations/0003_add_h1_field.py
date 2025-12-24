from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_load_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='h1',
            field=models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1'),
        ),
        migrations.AddField(
            model_name='news',
            name='h1',
            field=models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1'),
        ),
        migrations.AddField(
            model_name='page',
            name='h1',
            field=models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1'),
        ),
        migrations.AlterField(
            model_name='article',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)'),
        ),
        migrations.AlterField(
            model_name='article',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)'),
        ),
        migrations.AlterField(
            model_name='article',
            name='meta_title',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)'),
        ),
        migrations.AlterField(
            model_name='news',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)'),
        ),
        migrations.AlterField(
            model_name='news',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)'),
        ),
        migrations.AlterField(
            model_name='news',
            name='meta_title',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)'),
        ),
        migrations.AlterField(
            model_name='page',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)'),
        ),
        migrations.AlterField(
            model_name='page',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)'),
        ),
        migrations.AlterField(
            model_name='page',
            name='meta_title',
            field=models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)'),
        ),
    ]
