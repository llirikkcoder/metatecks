from django.db import models
from django.utils import timezone
from django.urls import reverse

from easy_thumbnails.fields import ThumbnailerImageField
from tinymce.models import HTMLField

from apps.utils.model_mixins import IsPublishedModel, DatesBaseModel, MetatagModel
from apps.utils.thumbs import get_thumb_url


class NewsCategory(models.Model):
    name = models.CharField('Название', max_length=255, unique=True)
    slug = models.SlugField('Адрес в url', unique=True)
    is_shown = models.BooleanField('Показывать на главной раздела?', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'раздел новостей'
        verbose_name_plural = 'новости: разделы'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:category', kwargs={'category': self.slug})


class News(IsPublishedModel, DatesBaseModel, MetatagModel):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Адрес в url')
    short_description = models.TextField('Краткое описание', blank=True)
    cover = ThumbnailerImageField('Обложка', null=True, blank=True, upload_to='news/covers/')
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    text = HTMLField('Текст', blank=True)
    categories = models.ManyToManyField(NewsCategory, verbose_name='Разделы', blank=True, related_name='news')
    is_published = models.BooleanField('Новость опубликована?', default=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'новость'
        verbose_name_plural = 'новости'

    def __str__(self):
        return self.title

    @property
    def url_date(self):
        date = self.published_at
        return f'{date.year}/{date.month:02d}'

    def get_absolute_url(self):
        date_str = self.url_date
        return reverse('news:post', kwargs={'date': date_str, 'slug': self.slug})

    def show_categories(self):
        cat_names = self.categories.values_list('name', flat=True)
        return ', '.join(cat_names) or '-'
    show_categories.allow_tags = True
    show_categories.short_description = 'Разделы'

    def get_meta_title(self):
        title = super().get_meta_title()
        if not self.meta_title:
            title = f'Новость: {title}'
        return title

    @property
    def homepage_cover_url(self):
        return get_thumb_url(self.cover, 'homepage_news')

    @property
    def cover_url(self):
        return get_thumb_url(self.cover, 'page_cover')

    @property
    def cover_thumb_url(self):
        return get_thumb_url(self.cover, 'news_cover_thumb')

    @property
    def cover_admin_url(self):
        return get_thumb_url(self.cover, 'admin_list_image')
