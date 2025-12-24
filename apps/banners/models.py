from django.db import models
from django.utils import timezone

from easy_thumbnails.fields import ThumbnailerImageField

from apps.utils.common import bool_to_icon
from apps.utils.model_mixins import DatesBaseModel
from apps.utils.thumbs import get_thumb_url
from .manager import BannerQueryset, BannerManager


BANNER_PLACES = (
    ('homepage', 'главная страница'),
    ('news', 'новости'),
    ('articles', 'статьи'),
)
DESIGN_CHOICES = (
    ('light', 'светлый фон, черный текст'),
    ('dark', 'темный фон, светлый текст'),
)


class Banner(DatesBaseModel):
    banner_place = models.CharField('Баннерное место', max_length=15, choices=BANNER_PLACES)
    title = models.CharField(
        'Короткое описание', max_length=255, null=True, blank=True, help_text='для отображения в админке'
    )

    design = models.CharField('Оформление', max_length=7, choices=DESIGN_CHOICES, default='light')
    image_1200 = ThumbnailerImageField('Изображение 1200х570px', upload_to='b/')
    image_670 = ThumbnailerImageField('Изображение 670х950px', upload_to='b/')
    # link = models.URLField('Ссылка', null=True, blank=True)
    link = models.CharField('Ссылка', max_length=512, null=True, blank=True)

    text = models.TextField('Основной текст', blank=True)
    button_text = models.CharField(
        'Текст на кнопке', max_length=31, blank=True,
        help_text='также используется в свойстве "title" у ссылки',
    )
    old_price = models.CharField('Старая цена', max_length=15, blank=True)
    new_price = models.CharField('Новая цена', max_length=15, blank=True)
    description = models.TextField('Описание внизу', blank=True)

    is_published = models.BooleanField('Опубликован?', default=True)
    start_dt = models.DateTimeField('Начало размещения', default=timezone.now)
    end_dt = models.DateTimeField(
        'Конец размещения', null=True, blank=True, help_text='оставьте пустым для бесконечной публикации'
    )
    shows = models.IntegerField('Кол-во показов', default=0)

    order = models.PositiveSmallIntegerField('Порядок', default=1)

    objects = BannerManager.from_queryset(BannerQueryset)()

    class Meta:
        ordering = ['order']
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'

    def __str__(self):
        return f'{self.title} (#{self.id})' if self.title else f'#{self.id}'

    @property
    def is_shown(self):
        now = timezone.now()
        is_shown = self.is_published and self.start_dt <= now
        if self.end_dt:
            is_shown = is_shown and self.end_dt >= now
        return is_shown

    def show_is_shown(self):
        return bool_to_icon(self.is_shown)
    show_is_shown.allow_tags = True
    show_is_shown.short_description = 'Размещен сейчас?'

    def get_button_text(self):
        return self.button_text or 'Перейти'

    # миниатюры изображений

    @property
    def image_1200_url(self):
        return get_thumb_url(self.image_1200, 'banner_1200')

    @property
    def image_670_url(self):
        return get_thumb_url(self.image_670, 'banner_670')

    @property
    def image_1200_admin_url(self):
        return get_thumb_url(self.image_1200, 'admin_list_image')

    @property
    def image_670_admin_url(self):
        return get_thumb_url(self.image_670, 'admin_list_image')

    @property
    def image_430_url(self):
        return get_thumb_url(self.image_670, 'banner_430')
