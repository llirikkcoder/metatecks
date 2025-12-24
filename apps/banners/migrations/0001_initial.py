from django.db import migrations, models
import django.utils.timezone
import easy_thumbnails.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('banner_place', models.CharField(choices=[('homepage', 'главная страница'), ('news', 'новости'), ('articles', 'статьи')], max_length=15, verbose_name='Баннерное место')),
                ('title', models.CharField(blank=True, help_text='для отображения в админке', max_length=255, null=True, verbose_name='Короткое описание')),
                ('image_1200', easy_thumbnails.fields.ThumbnailerImageField(upload_to='b/', verbose_name='Изображение 1200х570px')),
                ('image_670', easy_thumbnails.fields.ThumbnailerImageField(upload_to='b/', verbose_name='Изображение 670х950px')),
                ('link', models.CharField(blank=True, max_length=512, null=True, verbose_name='Ссылка')),
                ('text', models.TextField(blank=True, verbose_name='Основной текст')),
                ('button_text', models.CharField(blank=True, help_text='также используется в свойстве "title" у ссылки', max_length=31, verbose_name='Текст на кнопке')),
                ('old_price', models.CharField(blank=True, max_length=15, verbose_name='Старая цена')),
                ('new_price', models.CharField(blank=True, max_length=15, verbose_name='Новая цена')),
                ('description', models.TextField(blank=True, verbose_name='Описание внизу')),
                ('is_published', models.BooleanField(default=True, verbose_name='Опубликован?')),
                ('start_dt', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Начало размещения')),
                ('end_dt', models.DateTimeField(blank=True, help_text='оставьте пустым для бесконечной публикации', null=True, verbose_name='Конец размещения')),
                ('shows', models.IntegerField(default=0, verbose_name='Кол-во показов')),
            ],
            options={
                'verbose_name': 'баннер',
                'verbose_name_plural': 'баннеры',
                'ordering': ['-id'],
            },
        ),
    ]
