from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from easy_thumbnails.fields import ThumbnailerImageField

from apps.catalog.models import ProductModel, Product
from apps.utils.common import bool_to_icon
from apps.utils.math import get_decimal_percent_fixed
from apps.utils.model_mixins import DatesBaseModel
from apps.utils.thumbs import get_thumb_url
from .manager import PromotionQueryset, PromotionManager


DISCOUNT_PERCENTS = 1
DISCOUNT_AMOUNT = 2
DISCOUNT_TYPES = (
    (DISCOUNT_PERCENTS, 'проценты'),
    (DISCOUNT_AMOUNT, 'рубли'),
)
DESIGN_CHOICES = (
    ('light', 'светлый фон, черный текст'),
    ('dark', 'темный фон, светлый текст'),
)


class Promotion(DatesBaseModel):
    name = models.CharField('Название', max_length=255)

    banner_design = models.CharField('Оформление баннера', max_length=7, choices=DESIGN_CHOICES, default='light')
    banner = ThumbnailerImageField('Баннер (1920x720px)', upload_to='p/')
    banner_695 = ThumbnailerImageField('Баннер (695x522px)', upload_to='p/', null=True, blank=True)
    old_price = models.PositiveIntegerField('Старая цена на баннере, руб.', null=True, blank=True)
    new_price = models.PositiveIntegerField('Новая цена на баннере, руб.', null=True, blank=True)
    description = models.TextField('Описание акции', blank=True)

    discount_type = models.PositiveSmallIntegerField(
        'Тип скидки', choices=DISCOUNT_TYPES, default=DISCOUNT_PERCENTS
    )
    discount_percents = models.PositiveSmallIntegerField('Размер скидки (%)', null=True, blank=True)
    discount_amount = models.PositiveSmallIntegerField('Размер скидки (руб)', null=True, blank=True)

    model = models.ForeignKey(
        ProductModel, models.SET_NULL, null=True, blank=True, verbose_name='Модель по акции', related_name='promotions'
    )
    product = models.ForeignKey(
        Product, models.SET_NULL, null=True, blank=True, verbose_name='Товар по акции', related_name='promotions',
        help_text='в случае, если не выбрана модель'
    )

    start_dt = models.DateField('Дата начала акции', default=timezone.now)
    end_dt = models.DateField(
        'Дата окончания акции', null=True, blank=True, help_text='оставьте пустым для бессрочной акции'
    )
    is_active = models.BooleanField('Активна?', default=True)

    objects = PromotionManager.from_queryset(PromotionQueryset)()

    class Meta:
        ordering = ['start_dt', 'end_dt']
        verbose_name = 'акция'
        verbose_name_plural = 'акции'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '{}#promo{}'.format(reverse('promotions'), self.id)

    # скидка

    def show_discount(self):
        _type = self.discount_type
        value = {
            DISCOUNT_PERCENTS: self.discount_percents or 0,
            DISCOUNT_AMOUNT: self.discount_amount or 0,
        }[_type]
        label = {
            DISCOUNT_PERCENTS: '%',
            DISCOUNT_AMOUNT: 'руб.',
        }[_type]
        return f'{value} {label}'
    show_discount.allow_tags = True
    show_discount.short_description = 'Скидка'

    #TODO: optimize

    @classmethod
    def get_product_promotion(cls, model=None, product=None):
        if not (model or product):
            return None
        qs = cls.objects.active()
        obj = None
        if model:
            obj = qs.filter(model_id=model.id).first()
        elif product:
            obj = qs.filter(Q(model_id=product.model_id) | Q(product_id=product.id)).first()
        return obj

    def get_new_price(self, old_price):
        price = (
            get_decimal_percent_fixed(old_price, 100-self.discount_percents)
            if self.discount_type == DISCOUNT_PERCENTS
            else old_price - self.discount_amount
        )
        if price < 0:
            price = 0
        return price

    # методы для показа в админке

    @property
    def is_shown(self):
        now_date = timezone.now().date()
        if not (self.id and self.start_dt):
            return None
        is_shown = self.is_active and self.start_dt <= now_date
        if self.end_dt:
            is_shown = is_shown and self.end_dt >= now_date
        return is_shown

    def show_is_shown(self):
        return bool_to_icon(self.is_shown)
    show_is_shown.allow_tags = True
    show_is_shown.short_description = 'Активна сейчас?'

    def show_products_count(self):
        return (
            self.model.products.count()
            if self.model
            else 1
            if self.product
            else 0
        )
    show_products_count.allow_tags = True
    show_products_count.short_description = 'Кол-во товаров в акции'

    # тексты на странице

    MONTHS = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
        5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
        9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря',
    }

    @property
    def dates_str(self):
        start_dt = self.start_dt
        _day = start_dt.day
        _month = self.MONTHS[start_dt.month]

        dates = f'с&nbsp;{_day}&nbsp;{_month}'

        end_dt = self.end_dt
        if end_dt:
            _day = end_dt.day
            _month = self.MONTHS[end_dt.month]
            dates = f'{dates} до&nbsp;{_day}&nbsp;{_month}'
        return dates

    # миниатюры изображений

    @property
    def banner_url(self):
        return get_thumb_url(self.banner, 'promo_1920')

    @property
    def banner_695_url(self):
        banner = self.banner_695 or self.banner
        return get_thumb_url(banner, 'promo_695')

    @property
    def banner_admin_url(self):
        return get_thumb_url(self.banner, 'admin_list_image')

    @property
    def banner_695_admin_url(self):
        return get_thumb_url(self.banner_695, 'admin_list_image')
