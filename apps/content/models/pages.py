from django.db import models
from django.urls import reverse

from easy_thumbnails.fields import ThumbnailerImageField
from tinymce.models import HTMLField

from apps.utils.model_mixins import DatesBaseModel, MetatagModel
from apps.utils.thumbs import get_thumb_url


class Page(DatesBaseModel, MetatagModel):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.CharField('Адрес в url', max_length=255, unique=True)
    cover = ThumbnailerImageField('Обложка', null=True, blank=True, upload_to='pages/covers/')
    description = models.TextField('Описание страницы', blank=True, help_text='рядом с заголовком')
    text = HTMLField('Текст', blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'страница'
        verbose_name_plural = 'тексто-графические страницы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page', kwargs={'slug': self.slug})

    @property
    def cover_url(self):
        return get_thumb_url(self.cover, 'page_cover')

    @property
    def cover_admin_url(self):
        return get_thumb_url(self.cover, 'admin_list_image')
