import copy

from django.db import models
from django.urls import reverse

from galleryfield.fields import GalleryField
from easy_thumbnails.fields import ThumbnailerImageField
from tinymce.models import HTMLField

from apps.addresses.models import Warehouse
from apps.utils.common import get_current_request
from apps.utils.model_mixins import DatesBaseModel, MetatagModel
from apps.utils.thumbs import get_thumb_url
from .attributes import Attribute
from .brands import Brand
from .categories import Category, SubCategory


class ProductModel(DatesBaseModel, MetatagModel):
    # основные поля
    name = models.CharField('Название', max_length=255)
    category = models.ForeignKey(Category, models.PROTECT, verbose_name='Категория', related_name='models')
    sub_category = models.ForeignKey(SubCategory, models.PROTECT, verbose_name='Подкатегория', related_name='models')
    photo = ThumbnailerImageField('Фото', null=True, blank=True, upload_to='models/photos/')
    price = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)

    # описание
    description = HTMLField('Описание', blank=True)
    tech_description = models.FileField('Техническое описание', null=True, blank=True, upload_to='models/tech/')

    # фото- и 3d-галереи
    gallery = GalleryField(verbose_name='Фотогалерея', null=True, blank=True, help_text='до 5 фото')
    gallery_3d = GalleryField(verbose_name='3D-галерея', null=True, blank=True)

    # характеристики
    attrs = models.JSONField(default=dict)

    # настройки показа на сайте
    is_shown = models.BooleanField('Показывать на сайте', default=True)
    is_popular = models.BooleanField('Показывать в списке «Популярное»', default=False)

    # данные из 1C
    id_1c = models.UUIDField('ID в 1C', null=True, blank=True, db_index=True)
    is_synced_with_1c = models.BooleanField('Синхронизовано с 1C', default=False)
    bar_code = models.CharField('Штрихкод', max_length=15, blank=True)
    vendor_code = models.CharField('Артикул', max_length=31, null=True, blank=True, db_index=True)

    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'модель'
        verbose_name_plural = '3) Модели'

    def save(self, *args, **kwargs):
        self.category = self.sub_category.category
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:model', kwargs={
            'model_id': self.pk,
            'sub_category': self.sub_category.slug,
            'category': self.category.slug,
        })

    # миниатюры изображений

    @property
    def list_photo_url(self):
        return get_thumb_url(self.photo, 'product_list_photo')

    # редактирование атрибутов на странице модели в админке

    def get_attr_ids(self):
        return [k[1:] for k in self.attrs.keys()]

    def get_attrs_fields(self):
        # attrs = self.sub_category.attributes.select_related('unit').prefetch_related('options').all()
        attr_ids = self.get_attr_ids()
        attrs = Attribute.objects.filter(id__in=attr_ids)
        return {
            a.get_form_fieldname(): a.get_form_field()
            for a in attrs
        }

    # методы для карточки товара

    def get_attrs_list(self, attr_ids=None, attributes=None, in_filter=True):
        if not attr_ids:
            _name = 'attr_ids' if in_filter is False else 'attr_products_ids'
            attr_ids = getattr(self.sub_category, _name)
        if not attributes:
            attributes = Attribute.get_attributes_dict()
        attrs = self.attrs
        lst = []
        attr_name_field = 'name' if in_filter is False else 'name_short'
        for attr_id in attr_ids:
            attr = attributes.get(attr_id)
            value = attrs.get(f'{attr["attrs_slug"]}')
            if attr and value is not None:
                if attr['with_options']:
                    value = attr['options'].get(value)
                    if value is None:
                        continue
                lst.append({
                    'name': attr[attr_name_field],
                    'unit': attr['unit'],
                    'value': value,
                })
        return lst

    def get_attrs_list_v2(self, attributes=None, in_filter=False, full=False):
        if not attributes:
            attributes = Attribute.get_attributes_dict()
        attrs = self.attrs
        lst = []
        attr_name_field = 'name' if in_filter is False else 'name_short'
        for key, value in attrs.items():
            attr_id = int(key[1:])
            attr = attributes.get(attr_id)
            if not attr:
                continue
            if in_filter is True and attr['dont_show_in_lists'] is True:
                continue
            if value is not None:
                if attr['with_options']:
                    value = attr['options'].get(value)
                    if value is None:
                        continue
                _name = attr[attr_name_field]
                if full is False and _name == 'Срок изготовления':
                    continue
                lst.append({
                    'name': _name,
                    'unit': attr['unit'],
                    'value': value,
                })
        return lst

    def get_attrs_list_v3(self, attributes=None, in_filter=False, full=False):
        if not attributes:
            attributes = Attribute.get_attributes_dict()

        attrs = self.attrs
        attr_ids = self.get_attr_ids()
        attributes = copy.deepcopy(attributes)
        attributes = {k: v for k, v in attributes.items() if str(k) in attr_ids}

        lst = []
        attr_name_field = 'name' if in_filter is False else 'name_short'
        for attr_id, attr in attributes.items():
            value = attrs.get(f'a{attr_id}')
            if not value:
                continue
            if in_filter is True and attr['dont_show_in_lists'] is True:
                continue
            if value is not None:
                if attr['with_options']:
                    value = attr['options'].get(value)
                    if value is None:
                        continue
                _name = attr[attr_name_field]
                if full is False and _name == 'Срок изготовления':
                    continue
                lst.append({
                    'name': _name,
                    'unit': attr['unit'],
                    'value': value,
                })
        return lst

    # тексты на странице товара

    @property
    def has_description(self):
        text = self.description
        return bool(text and text != '<p>&nbsp;</p>')


class ProductPhoto(DatesBaseModel):
    model = models.ForeignKey(ProductModel, models.PROTECT, verbose_name='Модель', related_name='photos')
    photo = ThumbnailerImageField('Фото', null=True, blank=True, upload_to='products/photos/')
    is_shown = models.BooleanField('Показывать на сайте', default=True)
    show_on_subcategory = models.BooleanField('Показывать на странице подкатегории', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'фото'
        verbose_name_plural = 'товары: фото'

    def __str__(self):
        return f'#{self.id}'

    @property
    def photo_big_url(self):
        return get_thumb_url(self.photo, 'product_photos_big')

    @property
    def photo_thumb_url(self):
        return get_thumb_url(self.photo, 'product_photos_thumb')

    @property
    def photo_admin_url(self):
        return get_thumb_url(self.photo, 'admin_list_image')


class ProductVideo(DatesBaseModel):
    model = models.ForeignKey(ProductModel, models.PROTECT, verbose_name='Модель', related_name='videos')
    video = models.TextField('Видео (код для вставки на сайт)', null=True, blank=True)
    description = models.TextField('Описание (необязательно)', blank=True)
    is_shown = models.BooleanField('Показывать на сайте', default=True)
    show_on_subcategory = models.BooleanField('Показывать на странице подкатегории', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'видео'
        verbose_name_plural = 'товары: видео'

    def __str__(self):
        return f'#{self.id}'

    @property
    def has_video(self):
        return self.video and not self.video.startswith('http')


class Product(DatesBaseModel, MetatagModel):
    # основные поля
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Адрес в url', max_length=255)
    category = models.ForeignKey(Category, models.PROTECT, verbose_name='Категория', related_name='products')
    sub_category = models.ForeignKey(SubCategory, models.PROTECT, verbose_name='Подкатегория', related_name='products')
    model = models.ForeignKey(ProductModel, models.PROTECT, verbose_name='Модель', related_name='products')
    brand_name = models.CharField('Название бренда (автомат.)', max_length=127, default='')
    brand = models.ForeignKey(Brand, models.PROTECT, verbose_name='Бренд', null=True, blank=True, related_name='products')
    photo = ThumbnailerImageField('Фото', null=True, blank=True, upload_to='products/photos/')

    # фото- и 3d-галереи
    gallery = GalleryField(verbose_name='Фотогалерея', null=True, blank=True, help_text='до 5 фото')
    gallery_3d = GalleryField(verbose_name='3D-галерея', null=True, blank=True)

    # настройки показа на сайте
    is_shown = models.BooleanField('Показывать на сайте', default=True)
    is_popular = models.BooleanField('Показывать в списке «Популярное»', default=False)

    # данные из 1C
    id_1c = models.UUIDField('ID в 1C', null=True, blank=True, db_index=True)
    is_synced_with_1c = models.BooleanField('Синхронизовано с 1C', default=False)
    bar_code = models.CharField('Штрихкод', max_length=15, blank=True)
    vendor_code = models.CharField('Артикул', max_length=31, blank=True)

    # кэш
    number_in_stock = models.PositiveSmallIntegerField('Максимальное количество на складе', default=0)
    is_in_stock = models.BooleanField('Есть на складе?', default=False)
    number_in_stock_dict = models.JSONField(
        'Максимальное количество на складах', default=dict, help_text='по городам и складам'
    )
    is_in_stock_dict = models.JSONField(
        'Есть на складах?', default=dict, help_text='по городам и складам'
    )

    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'товар'
        verbose_name_plural = '4) Товары'

    def save(self, *args, **kwargs):
        self.sub_category = self.model.sub_category
        self.category = self.sub_category.category
        self.is_in_stock = bool(self.number_in_stock)
        for k, v in self.number_in_stock_dict.items():
            self.is_in_stock_dict[k] = bool(v)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product', kwargs={
            'product_id': self.pk,
            'product': self.slug,
            'sub_category': self.sub_category.slug,
            'category': self.category.slug,
        })

    def get_link_url(self):
        return reverse('catalog:product-link', kwargs={
            'product_id': self.pk,
        })

    @property
    def price(self):
        return self.model.price

    # миниатюры изображений

    def get_photo(self):
        return self.photo or self.model.photo

    @property
    def list_photo_url(self):
        return get_thumb_url(self.get_photo(), 'product_list_photo')

    @property
    def micro_photo_url(self):
        return get_thumb_url(self.get_photo(), 'product_micro_photo')

    # seo и тексты на странице

    def get_title(self):
        return self.name

    @property
    def has_description(self):
        text = self.description
        return bool(text and text != '<p>&nbsp;</p>')

    # методы для карточки товара

    def get_gallery(self):
        return self.gallery or self.model.gallery

    def get_gallery_3d(self):
        return self.gallery_3d or self.model.gallery_3d

    def count_in_stock_old(self, warehouse_ids=None):
        if not warehouse_ids:
            request = get_current_request()
            warehouse_ids = getattr(request, 'city_warehouses', None)
        balances = self.stock_balance.all()
        if warehouse_ids:
            balances = balances.filter(warehouse__in=warehouse_ids)
        in_stock_list = [x.number for x in balances]
        return max(in_stock_list) if in_stock_list else 0

    @property
    def in_stock(self):
        request = get_current_request()
        city_id = getattr(request, 'city_id', None)
        return self.number_in_stock_dict.get(f'c{city_id}', 0)

    def get_attrs_list(self, attr_ids=None, attributes=None, in_filter=True):
        return self.model.get_attrs_list(attr_ids, attributes, in_filter)

    def get_attrs_list_v2(self, attributes=None, in_filter=False, full=False):
        return self.model.get_attrs_list_v2(attributes, in_filter, full)

    def get_attrs_list_v3(self, attributes=None, in_filter=False, full=False):
        return self.model.get_attrs_list_v3(attributes, in_filter, full)


class ProductStockBalance(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, verbose_name='Товар', related_name='stock_balance')
    warehouse = models.ForeignKey(Warehouse, models.CASCADE, verbose_name='Склад', related_name='stock_balance')
    number = models.PositiveSmallIntegerField('Количество', default=0)

    class Meta:
        unique_together = ('product', 'warehouse')
        ordering = ['warehouse']
        verbose_name = 'количество на складе'
        verbose_name_plural = 'товары: количество на складе'

    def __str__(self):
        return self.warehouse.show_name()


class ProductProperty(models.Model):
    model = models.ForeignKey(ProductModel, models.PROTECT, verbose_name='Модель', related_name='properties', null=True, blank=True)
    product = models.ForeignKey(Product, models.CASCADE, verbose_name='Товар', related_name='properties', null=True, blank=True)
    name = models.CharField('Название', max_length=127)
    value = models.CharField('Значение', max_length=127)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'реквизит'
        verbose_name_plural = 'товары: реквизиты'

    def __str__(self):
        return self.name
