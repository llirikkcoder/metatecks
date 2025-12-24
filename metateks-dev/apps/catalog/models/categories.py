from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import capfirst

from easy_thumbnails.fields import ThumbnailerImageField
from sortedm2m.fields import SortedManyToManyField
from tinymce.models import HTMLField

from apps.utils.common import get_current_request
from apps.utils.model_mixins import SearchResultModelMixin, DatesBaseModel, MetatagModel
from apps.utils.thumbs import get_thumb_url
from .attributes import Attribute


def get_shown_products(category_or_subcategory):
    obj = category_or_subcategory
    request = get_current_request()
    city_id = getattr(request, 'city_id', None)
    return obj.products.filter(is_shown=True).order_by(f'-is_in_stock_dict__c{city_id}')


class Category(SearchResultModelMixin, DatesBaseModel, MetatagModel):
    name = models.CharField('Название', max_length=255, help_text='пример: «Для фронтальных погрузчиков»')
    slug = models.SlugField('Адрес в url', max_length=255)
    icon = ThumbnailerImageField('Иконка', null=True, blank=True, upload_to='categories/icons/', help_text='файл .png')
    cover = ThumbnailerImageField('Обложка', null=True, blank=True, upload_to='categories/covers/')

    name_plural = models.CharField(
        'Название (во множественном числе)', max_length=255, blank=True,
        help_text='пример: «фронтальные погрузчики»',
    )
    name_single = models.CharField(
        'Название (в единственном числе)', max_length=255, blank=True,
        help_text='пример: «для фронтального погрузчика»',
    )
    name_product = models.CharField(
        'Название (на странице товара)', max_length=255, blank=True,
        help_text='пример: «на фронтальный погрузчик»',
    )
    price_list = models.FileField('Файл с прайсом', null=True, blank=True, upload_to='categories/price_lists/')

    is_shown = models.BooleanField('Показывать на сайте', default=True)
    is_synced_with_1c = models.BooleanField('Синхронизовано с 1C', default=False)

    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'категория'
        verbose_name_plural = '1) Категории'

    # def save(self, *args, **kwargs):
    #     self.name_full = f'Навесное оборудование {self.name.lower()}'
    #     return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        # return f'{self.name} (id {self.id})'

    def get_absolute_url(self):
        return reverse('catalog:category', kwargs={'category': self.slug})

    @property
    def shown_children(self):
        return self.sub_categories.filter(is_shown=True)

    @property
    def shown_models(self):
        return self.models.filter(is_shown=True)

    @property
    def shown_products(self):
        return get_shown_products(self)

    def get_children(self):
        return self.sub_categories.filter(is_shown=True)

    # разные варианты названия

    def get_name_lower(self):
        return '{}{}'.format(self.name[0].lower(), self.name[1:])

    @property
    def name_lower(self):
        return self.get_name_lower()

    def get_name_plural(self):
        return self.name_plural or self.name

    def get_name_single(self):
        return self.name_single or self.name

    def get_name_product(self):
        name = self.name_product or self.name
        return name.replace(' ', '&nbsp;', 1)

    def get_homepage_name(self, with_nbsp=False):
        name = self.name
        if name.startswith('Для '):
            name = capfirst(name.replace('Для ', '', 1))
        if with_nbsp is True:
            name = name.replace(' для ', ' для&nbsp;').replace(' и ', ' и&nbsp;')
        return name

    @property
    def homepage_name(self):
        return self.get_homepage_name(with_nbsp=False)

    @property
    def homepage_name_nbsp(self):
        return self.get_homepage_name(with_nbsp=True)

    # миниатюры изображений

    @property
    def icon_url(self):
        return get_thumb_url(self.icon, 'category_icon')

    @property
    def cover_url(self):
        return get_thumb_url(self.cover, 'category_cover')

    # seo и тексты на странице

    def get_title(self):
        return f'Навесное оборудование {self.name_lower}'

    def get_h1_title(self):
        _name = self.name_lower.replace(' ', '&nbsp;', 1)
        return mark_safe(f'Навесное оборудование {_name}')


class SubCategory(SearchResultModelMixin, DatesBaseModel, MetatagModel):
    category = models.ForeignKey(Category, models.PROTECT, verbose_name='Категория', related_name='sub_categories')
    name = models.CharField('Название', max_length=255, help_text='пример: «Ковши общего назначения»')
    name_single = models.CharField(
        'Название (в единственном числе)', max_length=255, blank=True,
        help_text='пример: «ковш общего назначения»',
    )
    slug = models.SlugField('Адрес в url', max_length=255)
    photo = ThumbnailerImageField('Обложка', null=True, blank=True, upload_to='sub_categories/photos/')

    purpose = models.TextField('Назначение', blank=True)
    description = HTMLField('Описание', blank=True)
    design_features_title = models.CharField(
        'Конструктивные особенности: заголовок', max_length=255, default='Конструктивные особенности',
        help_text='пример: «Конструктивные особенности ковша общего назначения»'
    )
    design_features = HTMLField('Конструктивные особенности: текст', blank=True)
    construction_features = HTMLField('Особенности конструкции', blank=True)
    # attributes_table = HTMLField('Таблица с характеристиками', blank=True, config_name='extends')
    attributes_table = HTMLField('Таблица с характеристиками', blank=True)

    attributes = SortedManyToManyField(Attribute, verbose_name='Характеристики', related_name='sub_categories', blank=True)
    attributes_in_products = SortedManyToManyField(
        Attribute, verbose_name='Характеристики в списке товаров', related_name='products_sub_categories', blank=True
    )
    attributes_in_filter = SortedManyToManyField(
        Attribute, verbose_name='Характеристики в фильтре', related_name='filter_sub_categories', blank=True,
        help_text='не больше 1 характеристики',
    )
    attribute_in_filter = models.ForeignKey(
        Attribute, models.SET_NULL, verbose_name='Характеристика в фильтре',
        null=True, blank=True, related_name='filter_sub_category',
        limit_choices_to={'is_synced_with_1c': True},
    )
    attr_ids = models.JSONField(default=list)
    attr_products_ids = models.JSONField(default=list)
    attr_filter_ids = models.JSONField(default=list)

    is_shown = models.BooleanField('Показывать на сайте', default=True)
    is_popular = models.BooleanField('Показывать в списке «Популярное»', default=False)
    is_synced_with_1c = models.BooleanField('Синхронизовано с 1C', default=False)

    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'подкатегория'
        verbose_name_plural = '2) Подкатегории'

    def get_full_name(self, category=None, single=True, self_single=True, for_html=True):
        category = category or self.category
        cat_name = category.get_name_single() if single is True else category.name_lower
        self_name = self.get_name_single() if self_single is True else self.name
        name = capfirst(f'{self_name} {cat_name}')
        if for_html is True:
            name = name.replace(' с ', ' с&nbsp;').replace(' для ', ' для&nbsp;').replace('-', '&#8209;')
        return mark_safe(name)

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def full_name_plural(self):
        return self.get_full_name(self_single=False)

    def __str__(self):
        return self.get_full_name(for_html=False)
        # return f'{self.category.name} / {self.name} (id {self.id})'

    @property
    def name_html(self):
        name = self.name
        name = name.replace(' с ', ' с&nbsp;').replace(' для ', ' для&nbsp;').replace('-', '&#8209;')
        return name

    def get_absolute_url(self):
        return reverse('catalog:sub_category', kwargs={'category': self.category.slug, 'sub_category': self.slug})

    @property
    def shown_models(self):
        return self.models.filter(is_shown=True)

    @property
    def shown_products(self):
        return get_shown_products(self)

    # разные варианты названия

    def get_name_single(self):
        return self.name_single or self.name

    # миниатюры изображений

    @property
    def list_photo_url(self):
        return (
            get_thumb_url(self.photo, 'sub_category_list_photo')
            if self.photo
            else get_thumb_url(self.category.cover, 'sub_category_list_photo')
        )

    def get_photo(self):
        return self.photo or self.category.cover

    @property
    def product_photo_url(self):
        return (
            get_thumb_url(self.photo, 'product_list_photo')
            if self.photo
            else get_thumb_url(self.category.cover, 'product_list_photo')
        )

    @property
    def product_micro_url(self):
        return (
            get_thumb_url(self.photo, 'product_micro_photo')
            if self.photo
            else get_thumb_url(self.category.cover, 'product_micro_photo')
        )

    @property
    def photo_url(self):
        return (
            get_thumb_url(self.photo, 'sub_category_photo')
            if self.photo
            else get_thumb_url(self.category.cover, 'sub_category_photo')
        )

    # seo и тексты на странице

    def get_title(self):
        return self.get_full_name(for_html=False)

    def get_h1_title(self):
        return self.get_full_name(for_html=True)

    META_DESCRIPTION = '{}. Выбирайте в фильтре свой бренд и нужное вам оборудование Метатэкс'

    def get_meta_desc(self):
        return self.meta_description or self.META_DESCRIPTION.format(self.get_title())

    @property
    def has_description(self):
        text = self.description
        return bool(text and text != '<p>&nbsp;</p>')

    @property
    def has_design_features(self):
        text = self.design_features
        return bool(text and text != '<p>&nbsp;</p>')

    @property
    def has_construction_features(self):
        text = self.construction_features
        return bool(text and text != '<p>&nbsp;</p>')

    @property
    def has_description_content(self):
        return any([self.has_description, self.has_design_features, self.has_construction_features])

    @property
    def has_attributes_table(self):
        text = self.attributes_table
        return bool(text and text != '<p>&nbsp;</p>')

    # редактирование атрибутов на странице модели в админке

    def get_attrs_fields(self):
        attrs = self.attributes.select_related('unit').prefetch_related('options').all()
        return {
            a.get_form_fieldname(): a.get_form_field()
            for a in attrs
        }
