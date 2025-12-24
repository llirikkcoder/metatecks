from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import easy_thumbnails.fields
import galleryfield.fields
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about_title', models.CharField(default='О компании', max_length=255, verbose_name='Заголовок страницы')),
                ('about_text', tinymce.models.HTMLField(blank=True, default='<p>Метатэкс — лидер по производству навесного оборудования для спецтехники в России. Мы предоставляем проверенные и надежные решения, которые расширяют возможности вашей техники и повышают производительность.</p>', verbose_name='Текст в начале страницы')),
                ('people_title', models.CharField(default='Но главное в Метатэксе — это люди', max_length=255, verbose_name='Заголовок блока')),
                ('people_photo', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='about/people/', verbose_name='Фото с сотрудниками')),
                ('phone_text', models.CharField(default='Звонок в офис', max_length=63, verbose_name='Текст на кнопке')),
                ('phone_number', models.CharField(default='+7 499 964-41-12', max_length=31, verbose_name='Номер телефона')),
            ],
            options={
                'verbose_name': 'Страница «О компании»',
            },
        ),
        migrations.CreateModel(
            name='ArticlesCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на главной раздела?')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'раздел статей',
                'verbose_name_plural': 'статьи: разделы',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='FooterData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_column_title', models.CharField(blank=True, default='Компания', max_length=255, verbose_name='1-й столбец: заголовок')),
                ('second_column_title', models.CharField(blank=True, default='Продукция', max_length=255, verbose_name='2-й столбец: заголовок')),
                ('third_column_title', models.CharField(blank=True, default='Медиа', max_length=255, verbose_name='3-й столбец: заголовок')),
                ('fourth_column_title', models.CharField(blank=True, default='Личный кабинет', max_length=255, verbose_name='4-й столбец: заголовок')),
                ('contacts_phone', models.CharField(blank=True, default='+7 800 222-54-32', max_length=31, verbose_name='Номер телефона')),
                ('contacts_email', models.CharField(blank=True, default='metall@spmet.ru', max_length=31, verbose_name='Email')),
            ],
            options={
                'verbose_name': 'Данные в футере',
            },
        ),
        migrations.CreateModel(
            name='HeaderData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('working_days', models.CharField(blank=True, default='ПН - ПТ', max_length=31, verbose_name='Режим работы: дни')),
                ('working_time', models.CharField(blank=True, default='09:00 - 18:00', max_length=31, verbose_name='Режим работы: время')),
                ('contacts_phone', models.CharField(blank=True, default='+7 800 222-54-32', max_length=31, verbose_name='Контакты: номер телефона')),
                ('contacts_email', models.CharField(blank=True, default='info@metateks.ru', max_length=31, verbose_name='Контакты: email')),
            ],
            options={
                'verbose_name': 'Данные в шапке',
            },
        ),
        migrations.CreateModel(
            name='NewsCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на главной раздела?')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'раздел новостей',
                'verbose_name_plural': 'новости: разделы',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('meta_title', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta title (заголовок страницы)')),
                ('meta_description', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta description (описание страницы)')),
                ('meta_keywords', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)')),
                ('seo_text', tinymce.models.HTMLField(blank=True, verbose_name='SEO-текст')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('slug', models.SlugField(unique=True, verbose_name='Адрес в url')),
                ('cover', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='pages/covers/', verbose_name='Обложка')),
                ('text', tinymce.models.HTMLField(blank=True, verbose_name='Текст')),
            ],
            options={
                'verbose_name': 'страница',
                'verbose_name_plural': 'тексто-графические страницы',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('meta_title', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta title (заголовок страницы)')),
                ('meta_description', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta description (описание страницы)')),
                ('meta_keywords', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)')),
                ('seo_text', tinymce.models.HTMLField(blank=True, verbose_name='SEO-текст')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('slug', models.SlugField(verbose_name='Адрес в url')),
                ('short_description', models.TextField(blank=True, verbose_name='Краткое описание')),
                ('cover', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='news/covers/', verbose_name='Обложка')),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата публикации')),
                ('text', tinymce.models.HTMLField(blank=True, verbose_name='Текст')),
                ('is_published', models.BooleanField(default=True, verbose_name='Новость опубликована?')),
                ('categories', models.ManyToManyField(blank=True, related_name='news', to='content.newscategory', verbose_name='Разделы')),
            ],
            options={
                'verbose_name': 'новость',
                'verbose_name_plural': 'новости',
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='HeaderLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('link', models.CharField(max_length=127, verbose_name='Ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='content.headerdata')),
            ],
            options={
                'verbose_name': 'ссылка',
                'verbose_name_plural': 'ссылки в шапке',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='FooterThirdColumnLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('link', models.CharField(max_length=127, verbose_name='Ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='third_column_links', to='content.footerdata')),
            ],
            options={
                'verbose_name': 'ссылка',
                'verbose_name_plural': '3-й столбец: ссылки',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='FooterSocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(choices=[('vk', 'vk'), ('telegram', 'telegram'), ('youtube', 'youtube')], max_length=15, verbose_name='Иконка')),
                ('link', models.URLField(max_length=255, verbose_name='Ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_links', to='content.footerdata')),
            ],
            options={
                'verbose_name': 'ссылка',
                'verbose_name_plural': 'ссылки на соц.сети',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='FooterSecondColumnLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('link', models.CharField(max_length=127, verbose_name='Ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_column_links', to='content.footerdata')),
            ],
            options={
                'verbose_name': 'ссылка',
                'verbose_name_plural': '2-й столбец: ссылки',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='FooterFourthColumnLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('link', models.CharField(max_length=127, verbose_name='Ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fourth_column_links', to='content.footerdata')),
            ],
            options={
                'verbose_name': 'ссылка',
                'verbose_name_plural': '4-й столбец: ссылки',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='FooterFirstColumnLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('link', models.CharField(max_length=127, verbose_name='Ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_column_links', to='content.footerdata')),
            ],
            options={
                'verbose_name': 'ссылка',
                'verbose_name_plural': '1-й столбец: ссылки',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('meta_title', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta title (заголовок страницы)')),
                ('meta_description', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta description (описание страницы)')),
                ('meta_keywords', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать поле "Заголовок"', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)')),
                ('seo_text', tinymce.models.HTMLField(blank=True, verbose_name='SEO-текст')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('slug', models.SlugField(verbose_name='Адрес в url')),
                ('short_description', models.TextField(blank=True, verbose_name='Краткое описание')),
                ('cover', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='articles/covers/', verbose_name='Обложка')),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата публикации')),
                ('text', tinymce.models.HTMLField(blank=True, verbose_name='Текст')),
                ('is_published', models.BooleanField(default=True, verbose_name='Статья опубликована?')),
                ('categories', models.ManyToManyField(blank=True, related_name='articles', to='content.articlescategory', verbose_name='Разделы')),
            ],
            options={
                'verbose_name': 'статья',
                'verbose_name_plural': 'статьи',
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='AboutWarehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Краткое описание')),
                ('address', models.TextField(blank=True, verbose_name='Адрес')),
                ('schedule', models.TextField(blank=True, verbose_name='Режим работы')),
                ('phone', models.CharField(blank=True, max_length=31, verbose_name='Телефон')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на странице?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouses', to='content.aboutcompany')),
            ],
            options={
                'verbose_name': 'склад',
                'verbose_name_plural': 'склады',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='AboutTransportCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('logo', models.FileField(help_text='файл .svg', upload_to='about/delivery/', verbose_name='Логотип')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на странице?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transport_companies', to='content.aboutcompany')),
            ],
            options={
                'verbose_name': 'транспортная компания',
                'verbose_name_plural': 'транспортные компании',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='AboutFact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text1', models.CharField(blank=True, max_length=31, verbose_name='Текст №1')),
                ('number', models.CharField(blank=True, max_length=15, verbose_name='Число')),
                ('text2', models.CharField(blank=True, max_length=31, verbose_name='Текст №2')),
                ('place', models.PositiveSmallIntegerField(choices=[(1, 'сверху'), (2, 'снизу')], default=1, verbose_name='Расположение')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facts', to='content.aboutcompany')),
            ],
            options={
                'verbose_name': 'факт',
                'verbose_name_plural': 'факты',
                'ordering': ['place', 'order'],
            },
        ),
        migrations.CreateModel(
            name='AboutBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('logo', models.FileField(help_text='файл .svg', upload_to='about/brands/', verbose_name='Логотип')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на странице?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brands', to='content.aboutcompany')),
            ],
            options={
                'verbose_name': 'бренд',
                'verbose_name_plural': 'бренды оборудования',
                'ordering': ['-is_shown', 'order'],
            },
        ),
        migrations.CreateModel(
            name='AboutAdvantage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(choices=[('buro', 'конструкторское бюро'), ('testing', 'испытательная база'), ('production', 'собственное производство'), ('storage', 'продукция в наличии'), ('compatibility', 'совместимость с техникой'), ('delivery', 'доставка по России')], max_length=15, verbose_name='Иконка в списке')),
                ('list_title', models.TextField(verbose_name='Заголовок в списке')),
                ('block_type', models.CharField(choices=[('regular', 'обычный'), ('warehouses', 'склады'), ('brands', 'бренды'), ('delivery', 'доставка')], default='regular', max_length=15, verbose_name='Тип блока')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок блока')),
                ('photo', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='about/advantages/', verbose_name='Фото')),
                ('video', models.URLField(blank=True, help_text='ссылка на youtube.com', null=True, verbose_name='Видео')),
                ('video_id', models.CharField(blank=True, editable=False, max_length=31, null=True)),
                ('gallery', galleryfield.fields.GalleryField(blank=True, null=True, target_model='galleryfield.BuiltInGalleryImage', verbose_name='Галерея')),
                ('text', tinymce.models.HTMLField(blank=True, verbose_name='Текст')),
                ('button_text', models.CharField(blank=True, max_length=63, verbose_name='Кнопка: текст')),
                ('button_link', models.CharField(blank=True, max_length=255, verbose_name='Кнопка: ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на странице?')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advantages', to='content.aboutcompany')),
            ],
            options={
                'verbose_name': 'преимущество',
                'verbose_name_plural': 'преимущества',
                'ordering': ['-is_shown', 'order'],
            },
        ),
    ]
