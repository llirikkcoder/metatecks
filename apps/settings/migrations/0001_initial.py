from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SEOSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.SlugField(max_length=255, unique=True, verbose_name='Код')),
                ('description', models.CharField(max_length=255, verbose_name='Страница')),
                ('title', models.CharField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название страницы (выше)', max_length=511, verbose_name='Title')),
                ('meta_desc', models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать глобальный meta_desc', verbose_name='Meta description (описание)')),
                ('meta_keyw', models.TextField(blank=True, default='', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)')),
                ('h1', models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название страницы', max_length=255, verbose_name='Заголовок H1')),
            ],
            options={
                'verbose_name': 'SEO-настройка',
                'verbose_name_plural': 'SEO-настройки: статические страницы',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_email', models.TextField(default='email1@example.com\r\nemail2@example.com', help_text='можно несколько; каждый на новой строке', verbose_name='Email для отправки уведомлений с сайта')),
                ('orders_email', models.TextField(default='email1@example.com\r\nemail2@example.com', help_text='можно несколько; каждый на новой строке', verbose_name='Email для отправки писем о новых заказах')),
                ('title_suffix', models.CharField(default='Метатэкс', max_length=255, verbose_name='Хвост title у страниц')),
                ('robots_txt', models.TextField(default='User-agent: *\r\nDisallow: \r\nHost: metateks.ru\r\nSitemap: https://metateks.ru/sitemap.xml', verbose_name='Содержимое файла /robots.txt')),
            ],
            options={
                'verbose_name': 'Общие настройки',
            },
        ),
    ]
