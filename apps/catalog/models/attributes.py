from django import forms
from django.db import models
from django.utils.safestring import mark_safe

from apps.content.templatetags.base_tags import lowfirst
from apps.utils.model_mixins import DatesBaseModel
from apps.utils.tokens import get_a_token


ICON_CHOICES = (
    ('kg', 'вес'),
    ('gear', 'другое'),
)
DEFAULT_ICON = 'met-ico-gear'


class AttributeUnit(DatesBaseModel):
    name = models.CharField('Название', max_length=31)
    name_html = models.CharField('Отображение на сайте', max_length=31, blank=True)
    icon = models.CharField('Иконка', max_length=7, choices=ICON_CHOICES, default='gear')
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'единица измерения'
        verbose_name_plural = 'характеристики: единицы измерения'

    def __str__(self):
        return self.name

    def get_name_html(self):
        return mark_safe(self.name_html or self.name)

    def get_icon(self):
        return f'met-ico-{self.icon}'


class Attribute(DatesBaseModel):
    ATTR_TYPES = (
        ('string', 'строка'),
        ('int', 'целое число'),
        ('float', 'дробное число'),
        ('number', 'число (1C)'),
    )
    name = models.CharField('Название', max_length=255)
    name_admin = models.CharField('Название в админке', max_length=255, blank=True)
    name_short = models.CharField(
        'Краткое название',
        max_length=255, blank=True,
        help_text='для списка товаров; например, «Г/п машины»',
    )
    name_filter = models.CharField(
        'Название в фильтре',
        max_length=255, blank=True,
        help_text='для фильтра товаров; например, «Грузоподъемность погрузчика»',
    )
    attr_type = models.CharField('Тип значения', max_length=7, choices=ATTR_TYPES, default='string')
    unit_str = models.CharField('Единица измерения (текстом)', max_length=31, blank=True, default='')
    unit = models.ForeignKey(AttributeUnit, models.SET_NULL, verbose_name='Единица измерения', null=True, blank=True)
    slug = models.SlugField(
        'В URL',
        help_text='''уникальное поле; принимаются английские буквы, цифры и символ "_"
            <br><br>примеры:<br>- weight<br>- teeth<br>- load_capacity''',
        unique=True, blank=True, null=True,
    )
    with_options = models.BooleanField('Выбор из вариантов', default=False)
    id_1c = models.UUIDField('ID в 1C', null=True, blank=True, db_index=True)
    is_synced_with_1c = models.BooleanField('Синхронизовано с 1C', default=False)
    dont_show_in_lists = models.BooleanField('Не выводить в списке товаров', default=False)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'характеристика'
        verbose_name_plural = 'характеристики товаров'

    def __str__(self):
        return mark_safe(f'{self.get_name_admin()} (id&nbsp;{self.id})')

    def save(self, *args, **kwargs):
        if self.id:
            self.slug = (self.slug or f'attr{self.id}').replace('-', '_')
        return super().save(*args, **kwargs)

    def get_name_admin(self):
        # return self.name_admin or self.name
        name = self.name_admin or self.name
        if self.unit_str:
            name = f'{name}, {self.unit_str}'
        return name

    def get_name_short(self):
        return self.name_short or self.name

    def get_name_filter(self):
        return self.name_filter or self.name

    @property
    def attrs_slug(self):
        return f'a{self.id}'

    def get_options_json(self):
        return {x.id: x.get_value(attr_type=self.attr_type) for x in self.options.all()}

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'name_short': self.get_name_short(),
            'name_filter': self.get_name_filter(),
            'attr_type': self.attr_type,
            'unit_name': self.unit_name,
            'unit_html': self.unit_html,
            'unit': self.unit_html,
            'slug': self.slug,
            'attrs_slug': self.attrs_slug,
            'with_options': self.with_options,
            'dont_show_in_lists': self.dont_show_in_lists,
        }
        if self.with_options:
            data['options'] = self.get_options_json()
        return data

    @classmethod
    def get_attributes_dict(cls):
        return {x.id: x.to_dict() for x in cls.objects.select_related('unit').prefetch_related('options')}

    @property
    def unit_name(self):
        return self.unit.name if self.unit else self.unit_str

    @property
    def unit_html(self):
        return self.unit.get_name_html() if self.unit else self.unit_str

    @property
    def icon_html(self):
        return self.unit.get_icon() if self.unit else DEFAULT_ICON

    def get_form_fieldname(self):
        return f'attrs__a{self.id}'

    def get_form_field(self):
        field = None

        if self.with_options:
            choices = [(o.id, o.get_value(self.attr_type)) for o in self.options.all()]
            choices.insert(0, (None, '---'))
            field = forms.ChoiceField(choices=choices, required=False, label=self.__str__())
        else:
            field_class = {
                'string': forms.CharField,
                'int': forms.IntegerField,
                'float': forms.FloatField,
                'number': forms.FloatField,
            }.get(self.attr_type)
            field = field_class(required=False, label=self.__str__())
        if self.unit:
            field.help_text = mark_safe(f'единица измерения: {self.unit_name}')
        return field


def get_number_value(value):
    value = value or 0.0
    int_value = int(value)
    if int_value == value:
        value = int_value
    return value


class AttributeOption(DatesBaseModel):
    attribute = models.ForeignKey(
        Attribute, models.CASCADE, verbose_name='Характеристика', related_name='options'
    )
    value_string = models.CharField('Значение (строка)', max_length=31, null=True, blank=True)
    value_int = models.PositiveSmallIntegerField('Значение (целое число)', null=True, blank=True)
    value_float = models.FloatField('Значение (дробное число)', null=True, blank=True)
    id_1c = models.UUIDField('ID в 1C', null=True, blank=True, db_index=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'вариант'
        verbose_name_plural = 'характеристики: варианты'

    @property
    def attr_type(self):
        return self.attribute.attr_type

    def get_value(self, attr_type=None):
        attr_type = attr_type or self.attr_type
        return {
            'string': self.value_string or '-',
            'int': str(self.value_int or 0),
            'float': str(self.value_float or 0.0),
            'number': get_number_value(self.value_float),
        }.get(attr_type, '-')

    @property
    def value(self):
        return self.get_value()

    def __str__(self):
        return self.value

    @property
    def name(self):
        return self.value


class AttributeFilterOption(DatesBaseModel):
    FILTER_TYPES = (
        ('eq', 'Равно'),
        ('gte', 'От'),
        ('lte', 'До'),
    )
    attribute = models.ForeignKey(
        Attribute, models.CASCADE, verbose_name='Характеристика', related_name='filter_options'
    )
    filter_type = models.CharField('Тип', max_length=3, choices=FILTER_TYPES, default='eq')
    value_int = models.PositiveSmallIntegerField('Значение (целое число)', null=True, blank=True)
    value_float = models.FloatField('Значение (дробное число)', null=True, blank=True)
    value_string = models.CharField('Значение (строка)', max_length=31, null=True, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'вариант'
        verbose_name_plural = 'характеристики: варианты в фильтре'

    @property
    def attr_type(self):
        return self.attribute.attr_type

    @property
    def unit(self):
        return self.attribute.unit

    @property
    def unit_name(self):
        return self.attribute.unit_name

    @property
    def unit_html(self):
        return self.attribute.unit_html

    def get_value(self, attr_type=None):
        attr_type = attr_type or self.attr_type
        return {
            'string': self.value_string or '-',
            'int': str(self.value_int or 0),
            'float': str(self.value_float or 0.0),
            'number': get_number_value(self.value_float),
        }.get(attr_type, '-')

    @property
    def value(self):
        return self.get_value()

    def get_name(self):
        type_str = self.get_filter_type_display() if self.filter_type != 'eq' else ''
        value = self.value
        unit = f' {self.unit_html}' if self.unit else ''
        return f'{type_str} {value}{unit}' if type_str else f'{value}{unit}'

    def __str__(self):
        return mark_safe(self.get_name())

    @property
    def name(self):
        return lowfirst(self.get_name())

    def get_filter_str(self, attr_slug, attr_type):
        filter_type = self.filter_type
        filter_type_str = '' if filter_type == 'eq' else f'__{filter_type}'
        value = self.get_value(attr_type)
        return f'{attr_slug}{filter_type_str}={value}'
