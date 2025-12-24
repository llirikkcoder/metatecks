from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from easy_thumbnails.fields import ThumbnailerImageField
from tinymce.models import HTMLField

from apps.utils.model_mixins import DatesBaseModel, MetatagModel
from apps.utils.thumbs import get_thumb_url


class Brand(DatesBaseModel, MetatagModel):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Адрес в url', max_length=255)
    logo = models.FileField('Логотип', null=True, blank=True, upload_to='brands/logos/')
    photo = ThumbnailerImageField('Фото', null=True, blank=True, upload_to='brands/photos/')
    description = models.TextField(
        'Краткое описание', blank=True,
        help_text=mark_safe("""
            оставьте пустым, чтобы использовать стандартное описание:
            <br/>
            «Метатэкс изготавливает навесное оборудование, совместимое со спецтехникой марки <Название бренда>»
        """)
    )
    text = HTMLField('Текст', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'бренд техники'
        verbose_name_plural = 'бренды техники'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('brands:brand', kwargs={'brand': self.slug})

    # миниатюры изображений

    def get_logo_url(self, thumb_key='brand_logo'):
        return (
            None if not self.logo
            else self.logo.url if self.logo.url.lower().endswith('.svg')
            else get_thumb_url(self.logo, thumb_key)
        )

    @property
    def logo_url(self):
        return self.get_logo_url('brand_logo')

    @property
    def homepage_logo_url(self):
        return self.get_logo_url('homepage_brand')

    @property
    def about_logo_url(self):
        return self.get_logo_url('about_brand')

    @property
    def photo_url(self):
        return get_thumb_url(self.photo, 'brand_photo')

    # seo и тексты на странице

    def get_title(self):
        return f'Страница бренда техники {self.name}'

    def get_h1_title(self):
        return f'Бренды техники {self.name}'

    DESCRIPTION_TEXT = """
        Метатэкс изготавливает навесное оборудование совместимое со&nbsp;спецтехникой марки {}
    """

    def get_description(self):
        return self.description or mark_safe(self.DESCRIPTION_TEXT.format(self.name))

    @staticmethod
    def get_attr_slug():
        return 'brand'
