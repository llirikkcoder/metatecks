from django.db import migrations, models
import django.utils.timezone
import easy_thumbnails.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MediaTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'тег',
                'verbose_name_plural': '0) Теги',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='MediaVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('cover', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='media/video_covers/', verbose_name='Обложка')),
                ('video', models.URLField(verbose_name='Ссылка на YouTube')),
                ('video_id', models.CharField(blank=True, editable=False, max_length=31, null=True)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата публикации')),
                ('is_published', models.BooleanField(default=True, verbose_name='Видео опубликовано?')),
                ('tags', models.ManyToManyField(blank=True, related_name='videos', to='media_content.mediatag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'видео',
                'verbose_name_plural': '2) Видео',
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='MediaPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('photo', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='media/photos/', verbose_name='Фото')),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата публикации')),
                ('is_published', models.BooleanField(default=True, verbose_name='Фото опубликовано?')),
                ('tags', models.ManyToManyField(blank=True, related_name='photos', to='media_content.mediatag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'фото',
                'verbose_name_plural': '1) Фото',
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('file', models.FileField(upload_to='media/files/', verbose_name='Файл')),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата публикации')),
                ('is_published', models.BooleanField(default=True, verbose_name='Файл опубликован?')),
                ('tags', models.ManyToManyField(blank=True, related_name='files', to='media_content.mediatag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'файл',
                'verbose_name_plural': '3) Файлы',
                'ordering': ['-published_at'],
            },
        ),
    ]
