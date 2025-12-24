from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, verbose_name='Название')),
                ('subdomain', models.CharField(blank=True, help_text='<город>.metateks.ru', max_length=31, null=True, verbose_name='Поддомен')),
                ('is_default', models.BooleanField(default=False, verbose_name='Город по умолчанию?')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'город',
                'verbose_name_plural': 'города',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Офис Метатэкс', max_length=31, verbose_name='Заголовок')),
                ('address', models.TextField(default='г. Москва, ул. Гиляровского, дом 57', verbose_name='Адрес')),
                ('address_on_map', models.CharField(default='улица Гиляровского, 57с1', max_length=63, verbose_name='Адрес на карте')),
                ('latitude', models.FloatField(default=0.0, verbose_name='Адрес: широта')),
                ('longitude', models.FloatField(default=0.0, verbose_name='Адрес: долгота')),
                ('schedule', models.TextField(default='Пн-Пт 09:00-18:00\n(по московскому времени)', verbose_name='Режим работы')),
            ],
            options={
                'verbose_name': 'Офис',
            },
        ),
        migrations.CreateModel(
            name='ProductionAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=63, verbose_name='Название')),
                ('address', models.TextField(blank=True, verbose_name='Адрес (текстом)')),
                ('address_on_map', models.CharField(blank=True, max_length=63, verbose_name='Адрес на карте')),
                ('latitude', models.FloatField(default=0.0, verbose_name='Адрес: широта')),
                ('longitude', models.FloatField(default=0.0, verbose_name='Адрес: долгота')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'адрес производства',
                'verbose_name_plural': 'адреса производства',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127, verbose_name='Полное название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('address', models.TextField(blank=True, verbose_name='Адрес (текстом)')),
                ('address_on_map', models.CharField(blank=True, max_length=63, verbose_name='Адрес на карте')),
                ('latitude', models.FloatField(default=0.0, verbose_name='Адрес: широта')),
                ('longitude', models.FloatField(default=0.0, verbose_name='Адрес: долгота')),
                ('schedule', models.TextField(blank=True, verbose_name='Режим работы')),
                ('phone', models.CharField(blank=True, max_length=31, verbose_name='Телефон')),
                ('contact_email', models.EmailField(blank=True, max_length=254, verbose_name='Почта (email)')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouses', to='addresses.city', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'склад',
                'verbose_name_plural': 'склады',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='OfficeSocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(choices=[('whatsapp', 'whatsapp'), ('telegram', 'telegram'), ('viber', 'viber'), ('youtube', 'youtube')], max_length=15, verbose_name='Иконка')),
                ('link', models.URLField(max_length=255, verbose_name='Ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='socials', to='addresses.office', verbose_name='Офис')),
            ],
            options={
                'verbose_name': 'ссылка на соц.сеть',
                'verbose_name_plural': 'Офис: ссылки на соц.сети',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='OfficePhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=31, verbose_name='Телефон')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='addresses.office', verbose_name='Офис')),
            ],
            options={
                'verbose_name': 'номер телефона',
                'verbose_name_plural': 'Офис: телефоны',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='OfficeEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='addresses.office', verbose_name='Офис')),
            ],
            options={
                'verbose_name': 'email-адрес',
                'verbose_name_plural': 'Офис: email-адреса',
                'ordering': ['order'],
            },
        ),
    ]
