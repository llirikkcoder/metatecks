from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from solo.models import SingletonModel


def get_in_stock_ids():
    _ids = [f'c{_id}' for _id in City.objects.values_list('id', flat=True)]
    _ids.extend([f'wh{_id}' for _id in Warehouse.objects.values_list('id', flat=True)])
    return _ids


def get_warehouse_to_city():
    _dict = {}
    for wh in Warehouse.objects.all():
        _dict[wh.id] = wh.city_id
    return _dict


class City(models.Model):
    name = models.CharField('Название', max_length=31)
    subdomain = models.CharField(
        'Поддомен', max_length=31,
        unique=True, blank=True, null=True, default='',
        help_text='<город>.metateks.ru',
    )
    name_loct = models.CharField(
        'Название (предл. падеж)', max_length=31, blank=True, help_text='например, "Москве"'
    )
    region_name = models.CharField(
        'Название региона', max_length=63, blank=True, help_text='например, "Московская область"'
    )
    region_name_loct = models.CharField(
        'Название региона (предл. падеж)', max_length=63, blank=True,
        help_text='например, "Московской области"'
    )
    contacts_phone = models.CharField('Контактный номер', max_length=31, blank=True)
    is_default = models.BooleanField('Город по умолчанию?', default=False)
    names_en = ArrayField(
        models.CharField(max_length=31),
        verbose_name='Названия (англ.)',
        blank=True, default=list,
        help_text='для геолокации',
    )
    region_names_en = ArrayField(
        models.CharField(max_length=31),
        verbose_name='Названия региона (англ.)',
        blank=True, default=list,
        help_text='для геолокации',
    )
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'город'
        verbose_name_plural = 'города'

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        return cls.objects.order_by('-is_default', 'order').first()

    @classmethod
    def get_default_id(cls):
        _default = cls.get_default()
        return _default.id if _default else None

    @classmethod
    def get_by_id(cls, city_id, default_if_error=True):
        return (
            cls.objects.get(id=city_id)
            if default_if_error is False
            else (cls.objects.filter(id=city_id).first() or cls.get_default())
        )

    def get_redirect_to(self, path):
        _subdomain = f'{self.subdomain}.' if self.subdomain else ''
        return f'{settings.DEFAULT_SCHEME}://{_subdomain}{settings.DEFAULT_SITENAME}{path}'

    def get_name(self):
        return self.name

    def get_name_loct(self):
        return self.name_loct or self.name

    def get_region_name(self):
        return self.region_name or self.name

    def get_region_name_loct(self):
        return self.region_name_loct or self.region_name or self.get_name_loct()


class Warehouse(models.Model):
    city = models.ForeignKey(City, models.CASCADE, verbose_name='Город', related_name='warehouses')
    name = models.CharField('Полное название', max_length=127)
    name_short = models.CharField('Краткое название', max_length=127, blank=True)
    description = models.TextField('Описание', blank=True)

    address = models.TextField('Адрес (текстом)', blank=True)
    address_on_map = models.CharField('Адрес на карте', max_length=63, blank=True)
    latitude = models.FloatField('Адрес: широта', default=0.0)
    longitude = models.FloatField('Адрес: долгота', default=0.0)

    schedule = models.TextField('Режим работы', blank=True)
    phone = models.CharField('Телефон', blank=True, max_length=31)
    contact_email = models.EmailField('Почта (email)', blank=True)

    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'склад'
        verbose_name_plural = 'склады'

    def __str__(self):
        return f'({self.city.__str__()}) {self.show_name()}'

    def show_name(self):
        return self.name.replace('&nbsp;', ' ')
    show_name.allow_tags = True
    show_name.short_description = 'Название'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    @classmethod
    def get_default_id(cls):
        obj = cls.objects.first()
        return obj.id if obj else None

    def get_name_short(self):
        return self.name_short or self.name


class Office(SingletonModel):
    title = models.CharField('Заголовок', max_length=31, default='Офис Метатэкс')
    address = models.TextField('Адрес', default='г. Москва, ул. Гиляровского, дом 57')
    address_on_map = models.CharField('Адрес на карте', max_length=63, default='улица Гиляровского, 57с1')
    latitude = models.FloatField('Адрес: широта', default=0.0)
    longitude = models.FloatField('Адрес: долгота', default=0.0)
    schedule = models.TextField('Режим работы', default='Пн-Пт 09:00-18:00\n(по московскому времени)')

    class Meta:
        verbose_name = 'Офис'

    def __str__(self):
        return 'Офис'


class OfficeEmail(models.Model):
    office = models.ForeignKey(Office, models.CASCADE, verbose_name='Офис', related_name='emails')
    email = models.EmailField('Email')
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'email-адрес'
        verbose_name_plural = 'Офис: email-адреса'

    def __str__(self):
        return self.email


class OfficePhone(models.Model):
    office = models.ForeignKey(Office, models.CASCADE, verbose_name='Офис', related_name='phones')
    phone = models.CharField('Телефон', blank=True, max_length=31)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'номер телефона'
        verbose_name_plural = 'Офис: телефоны'

    def __str__(self):
        return self.phone


class OfficeSocialLink(models.Model):
    ICON_CHOICES = (
        ('whatsapp', 'whatsapp'),
        ('telegram', 'telegram'),
        ('viber', 'viber'),
        ('youtube', 'youtube'),
    )
    office = models.ForeignKey(Office, models.CASCADE, verbose_name='Офис', related_name='socials')
    icon = models.CharField('Иконка', max_length=15, choices=ICON_CHOICES)
    link = models.URLField('Ссылка', max_length=255)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'ссылка на соц.сеть'
        verbose_name_plural = 'Офис: ссылки на соц.сети'

    def __str__(self):
        return f'#{self.id}: {self.icon}'


class ProductionAddress(models.Model):
    name = models.CharField('Название', max_length=63)
    address = models.TextField('Адрес (текстом)', blank=True)
    address_on_map = models.CharField('Адрес на карте', max_length=63, blank=True)
    latitude = models.FloatField('Адрес: широта', default=0.0)
    longitude = models.FloatField('Адрес: долгота', default=0.0)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'адрес производства'
        verbose_name_plural = 'адреса производства'

    def __str__(self):
        return self.name
