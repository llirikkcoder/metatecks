from django.db import models
from django.utils import timezone
from django.urls import reverse

from easy_thumbnails.fields import ThumbnailerImageField

from apps.utils.model_mixins import IsPublishedModel, DatesBaseModel
from apps.utils.thumbs import get_thumb_url


class MediaTag(models.Model):
    name = models.CharField('Название', max_length=255, unique=True)
    slug = models.SlugField('Адрес в url', unique=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'тег'
        verbose_name_plural = '0) Теги'

    def __str__(self):
        return self.name

    def get_url(self, model_name):
        return reverse(f'about:{model_name}_tag', kwargs={'tag': self.slug})


class MediaVideo(IsPublishedModel, DatesBaseModel):
    title = models.CharField('Заголовок', max_length=255)
    video = models.TextField('Видео (код для вставки на сайт)', null=True, blank=True)
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    tags = models.ManyToManyField(MediaTag, verbose_name='Теги', blank=True, related_name='videos')
    is_published = models.BooleanField('Видео опубликовано?', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    cover = ThumbnailerImageField('Обложка', null=True, blank=True, upload_to='media/video_covers/')

    class Meta:
        ordering = ['order']
        verbose_name = 'видео'
        verbose_name_plural = '1) Видео'

    def __str__(self):
        return self.title

    @property
    def has_video(self):
        return self.video and not self.video.startswith('http')

    def show_tags(self):
        tag_names = self.tags.values_list('name', flat=True)
        return ', '.join(tag_names) or '-'
    show_tags.allow_tags = True
    show_tags.short_description = 'Теги'


class MediaPhoto(IsPublishedModel, DatesBaseModel):
    title = models.CharField('Заголовок', max_length=255)
    photo = ThumbnailerImageField('Фото', null=True, blank=True, upload_to='media/photos/')
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    tags = models.ManyToManyField(MediaTag, verbose_name='Теги', blank=True, related_name='photos')
    is_published = models.BooleanField('Фото опубликовано?', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'фото'
        verbose_name_plural = '2) Фото'

    def __str__(self):
        return self.title

    def show_tags(self):
        tag_names = self.tags.values_list('name', flat=True)
        return ', '.join(tag_names) or '-'
    show_tags.allow_tags = True
    show_tags.short_description = 'Теги'

    @property
    def homepage_photo_thumb(self):
        return get_thumb_url(self.photo, 'homepage_photo_thumb')

    @property
    def homepage_photo_big(self):
        return get_thumb_url(self.photo, 'homepage_photo_big')

    @property
    def photo_big_url(self):
        return get_thumb_url(self.photo, 'about_photos_big')

    @property
    def photo_thumb_url(self):
        return get_thumb_url(self.photo, 'about_photos_thumb')

    @property
    def photo_admin_url(self):
        return get_thumb_url(self.photo, 'admin_list_image')


class MediaFile(IsPublishedModel, DatesBaseModel):
    title = models.CharField('Заголовок', max_length=255)
    file = models.FileField('Файл', upload_to='media/files/')
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    tags = models.ManyToManyField(MediaTag, verbose_name='Теги', blank=True, related_name='files')
    is_published = models.BooleanField('Файл опубликован?', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'файл'
        verbose_name_plural = '3) Файлы'

    def __str__(self):
        return self.title

    def show_tags(self):
        tag_names = self.tags.values_list('name', flat=True)
        return ', '.join(tag_names) or '-'
    show_tags.allow_tags = True
    show_tags.short_description = 'Теги'
