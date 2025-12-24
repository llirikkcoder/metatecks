from django.db import migrations, models
import django.utils.timezone
import easy_thumbnails.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('banner', easy_thumbnails.fields.ThumbnailerImageField(upload_to='p/', verbose_name='Баннер')),
                ('old_price', models.CharField(blank=True, max_length=15, verbose_name='Старая цена на баннере, руб.')),
                ('new_price', models.CharField(blank=True, max_length=15, verbose_name='Новая цена на баннере, руб.')),
                ('description', models.TextField(blank=True, verbose_name='Описание акции')),
                ('discount_type', models.PositiveSmallIntegerField(choices=[(1, 'проценты'), (2, 'рубли')], default=1, verbose_name='Тип скидки')),
                ('discount_percents', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Размер скидки (%)')),
                ('discount_amount', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Размер скидки (руб)')),
                ('start_dt', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата начала акции')),
                ('end_dt', models.DateTimeField(blank=True, help_text='оставьте пустым для бессрочной акции', null=True, verbose_name='Дата окончания акции')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна?')),
                ('products', models.ManyToManyField(blank=True, related_name='promotions', to='catalog.product', verbose_name='Товары в акции')),
            ],
            options={
                'verbose_name': 'акция',
                'verbose_name_plural': 'акции',
                'ordering': ['-id'],
            },
        ),
    ]
