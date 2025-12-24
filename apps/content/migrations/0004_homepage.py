from django.db import migrations, models
import django.db.models.deletion
import easy_thumbnails.fields
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_add_h1_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='Homepage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_title', models.CharField(default='Производитель навесного оборудования для&nbsp;спецтехники', max_length=255, verbose_name='Заголовок страницы')),
                ('about_title', models.CharField(default='О компании', max_length=255, verbose_name='О компании: заголовок')),
                ('about_photo', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='homepage/about/', verbose_name='О компании: фото с сотрудниками')),
                ('about_text', tinymce.models.HTMLField(blank=True, default='<p>Основное направление деятельности компании Метатэкс&nbsp;&mdash; производство навесного оборудования для&nbsp;строительной и&nbsp;коммунальной техники. В&nbsp;наших цехах производится более 100&nbsp;модификаций навесного оборудования для&nbsp;более чем 3000&nbsp;моделей специальной техники.</p>', verbose_name='О компании: текст')),
                ('advantages_title', models.CharField(default='Наши преимущества', max_length=255, verbose_name='Наши преимущества: заголовок')),
                ('news_title', models.CharField(default='Новости', max_length=255, verbose_name='Новости: заголовок')),
                ('news_text', models.TextField(verbose_name='Новости: текст')),
                ('articles_title', models.CharField(default='Статьи', max_length=255, verbose_name='Статьи: заголовок')),
                ('articles_text', models.TextField(verbose_name='Статьи: текст')),
                ('photo_title', models.CharField(default='Фото', max_length=255, verbose_name='Фото: заголовок')),
                ('photo_text', models.TextField(verbose_name='Фото: текст')),
                ('video_title', models.CharField(default='Видео', max_length=255, verbose_name='Видео: заголовок')),
                ('video_text', models.TextField(verbose_name='Видео: текст')),
                ('delivery_title', models.TextField(default='Доставка по&nbsp;России со&nbsp;складов<br />Московской области', verbose_name='Доставка: заголовок')),
                ('sales_title', models.CharField(default='Отдел продаж', max_length=255, verbose_name='Отдел продаж: заголовок')),
                ('sales_text', models.TextField(blank=True, default='Чтобы заказать товар, свяжитесь с отделом продаж', null=True, verbose_name='Отдел продаж: текст')),
            ],
            options={
                'verbose_name': 'Главная страница',
            },
        ),
        migrations.CreateModel(
            name='HomepageWarehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', easy_thumbnails.fields.ThumbnailerImageField(upload_to='homepage/warehouses/', verbose_name='Фото')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('subtitle', models.TextField(blank=True, verbose_name='Подзаголовок')),
                ('address', models.TextField(blank=True, verbose_name='Адрес')),
                ('schedule', models.TextField(blank=True, verbose_name='Режим работы')),
                ('phone', models.CharField(blank=True, max_length=31, verbose_name='Телефон')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouses', to='content.homepage')),
            ],
            options={
                'verbose_name': 'склад',
                'verbose_name_plural': 'склады',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='HomepageSalesPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=31, verbose_name='Номер телефона')),
                ('is_free', models.BooleanField(default=False, verbose_name='Звонок по России бесплатный')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='content.homepage')),
            ],
            options={
                'verbose_name': 'номер',
                'verbose_name_plural': 'номера телефона',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='HomepageSalesManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, verbose_name='Имя')),
                ('photo', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='homepage/managers/', verbose_name='Фото')),
                ('phone', models.CharField(max_length=31, verbose_name='Номер телефона')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на странице?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managers', to='content.homepage')),
            ],
            options={
                'verbose_name': 'менеджер',
                'verbose_name_plural': 'менеджеры',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='HomepageFact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(choices=[('storage', 'продукция в наличии'), ('productions', 'напрямую с завода')], max_length=15, verbose_name='Иконка')),
                ('text_large', models.CharField(blank=True, max_length=31, verbose_name='Крупный текст (сверху)')),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facts', to='content.homepage')),
            ],
            options={
                'verbose_name': 'факт',
                'verbose_name_plural': 'факты',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='HomepageAdvantage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(choices=[('buro', 'конструкторское бюро'), ('testing', 'испытательная база'), ('production', 'собственное производство'), ('storage', 'продукция в наличии'), ('compatibility', 'совместимость с техникой'), ('delivery', 'доставка по России')], max_length=15, verbose_name='Иконка')),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advantages', to='content.homepage')),
            ],
            options={
                'verbose_name': 'преимущество',
                'verbose_name_plural': 'преимущества',
                'ordering': ['order'],
            },
        ),
    ]
