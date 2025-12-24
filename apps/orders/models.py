from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from apps.addresses.models import Warehouse
from apps.catalog.models import Product, ExtraProduct
from .constants import DeliveryMethods, PaymentMethods, OrderStatuses
from .utils import get_order_number


# -- транспортные компании --

class DeliveryCompany(models.Model):
    name = models.CharField('Название', max_length=127)
    logo = models.FileField('Логотип', upload_to='delivery/', help_text='файл .svg')
    is_shown = models.BooleanField('Показывать на сайте?', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'транспортная компания'
        verbose_name_plural = 'транспортные компании'

    def __str__(self):
        return self.name

    @classmethod
    def shown(cls):
        return cls.objects.filter(is_shown=True)


# -- заказы --

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        verbose_name='Пользователь',
        blank=True, null=True, related_name='orders',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    status = models.CharField('Статус заказа', choices=OrderStatuses.choices, blank=True, null=True, max_length=15)
    comment = models.TextField('Комментарий', blank=True, null=True)

    total_quantity = models.PositiveSmallIntegerField('Кол-во товаров', default=0)

    has_discount = models.BooleanField('Есть скидка?', default=False)
    total_cost = models.DecimalField('Стоимость (₽)', max_digits=9, decimal_places=2, default=0)
    total_without_discount = models.DecimalField('Стоимость без скидки (₽)', max_digits=9, decimal_places=2, default=0)

    warehouse = models.ForeignKey(
        Warehouse, models.SET_NULL,
        verbose_name='Склад',
        blank=True, null=True, related_name='orders',
    )

    delivery_method = models.CharField('Способ доставки', choices=DeliveryMethods.choices, max_length=15)
    delivery_company = models.ForeignKey(
        DeliveryCompany, models.SET_NULL,
        verbose_name='Транспортная компания',
        blank=True, null=True, related_name='orders',
    )
    delivery_company_name = models.CharField('Транспортная компания', max_length=127, blank=True, null=True)

    payment_method = models.CharField('Метод оплаты', choices=PaymentMethods.choices, max_length=15)
    is_paid = models.BooleanField('Оплачен?', default=False)
    paid_at = models.DateTimeField('Дата оплаты', blank=True, null=True)

    is_canceled = models.BooleanField('Отменен?', default=False)
    is_canceled_by_user = models.BooleanField('Отменен пользователем?', null=True, default=None)
    canceled_at = models.DateTimeField('Дата отмены', blank=True, null=True)

    is_synced_with_b24 = models.BooleanField('Синхронизован с Битрикс24', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def save(self, *args, **kwargs):
        if self.is_paid and not self.paid_at:
            self.paid_at = timezone.now()
        if self.is_canceled is True:
            self.status = OrderStatuses.CANCELED
        elif self.status == OrderStatuses.CANCELED:
            self.is_canceled = True
        if self.is_canceled and not self.canceled_at:
            self.canceled_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'№ {self.number}'

    @property
    def number(self):
        return get_order_number(self.id)

    def get_absolute_url(self):
        url = reverse('account:orders')
        return f'{url}#order{self.id}'

    def get_created_url(self):
        url = reverse('account:orders')
        return f'{url}?p=created#order{self.id}'

    def get_canceled_url(self):
        url = reverse('account:orders')
        return f'{url}?p=canceled#order{self.id}'

    @property
    def first_product(self):
        item = self.items.filter(product_id__isnull=False).first()
        if item:
            return item.product

    @property
    def is_status_created(self):
        return self.status == OrderStatuses.CREATED

    @property
    def is_status_collecting(self):
        return self.status == OrderStatuses.COLLECTING

    @property
    def is_status_delivering(self):
        return self.status == OrderStatuses.DELIVERING

    @property
    def is_status_completed(self):
        return self.status == OrderStatuses.COMPLETED

    @property
    def is_status_canceled(self):
        return self.status == OrderStatuses.CANCELED

    @property
    def can_be_canceled(self):
        return self.is_status_created and not self.is_canceled

    @property
    def is_inactive(self):
        return self.status in [OrderStatuses.COMPLETED, OrderStatuses.CANCELED]


class OrderItem(models.Model):
    ITEM_TYPE_CHOICES = (
        ('product', 'товар'),
        ('extra', 'доп.товар'),
    )
    order = models.ForeignKey(Order, models.CASCADE, verbose_name='Заказ', related_name='items')
    item_type = models.CharField('Тип позиции', choices=ITEM_TYPE_CHOICES, default='product', max_length=7)

    base_item = models.ForeignKey(
        'self', models.SET_NULL,
        verbose_name='Основной товар',
        blank=True, null=True, related_name='extra_items',
    )
    product = models.ForeignKey(
        Product, models.SET_NULL,
        verbose_name='Товар',
        blank=True, null=True, related_name='order_items',
    )
    extra_product = models.ForeignKey(
        ExtraProduct, models.SET_NULL,
        verbose_name='Доп.товар',
        blank=True, null=True, related_name='order_items',
    )
    item_name = models.CharField('Название товара', max_length=255, blank=True, null=True)
    item_subtitle = models.CharField('Подзаголовок товара', max_length=255, blank=True, null=True)

    quantity = models.PositiveSmallIntegerField('Кол-во', default=0)

    has_discount = models.BooleanField('Есть скидка?', default=False)
    discount_percent = models.PositiveSmallIntegerField('Скидка за шт. (%)', default=0)
    discount_price = models.DecimalField('Скидка за шт. (₽)', max_digits=9, decimal_places=2, default=0)

    price = models.DecimalField('Цена (₽)', max_digits=9, decimal_places=2, default=0)
    price_without_discount = models.DecimalField('Цена без скидки (₽)', max_digits=9, decimal_places=2, default=0)
    cost = models.DecimalField('Стоимость (₽)', max_digits=9, decimal_places=2, default=0)
    cost_without_discount = models.DecimalField('Стоимость без скидки (₽)', max_digits=9, decimal_places=2, default=0)

    warehouse = models.ForeignKey(
        Warehouse, models.SET_NULL,
        verbose_name='Склад',
        blank=True, null=True, related_name='order_items',
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'товар'
        verbose_name_plural = 'товары в заказе'

    @property
    def is_product(self):
        return self.item_type == 'product'

    @property
    def is_extra(self):
        return self.item_type == 'extra'

    def get_object(self):
        return {
            'product': self.product,
            'extra': self.extra_product,
        }.get(self.item_type)
    # get_object.short_description = 'Товар'
    # get_object.allow_tags = True

    def show_item_subtitle(self):
        return mark_safe(self.item_subtitle or '')
    show_item_subtitle.short_description = 'Подзаголовок товара'
    show_item_subtitle.allow_tags = True

    def __str__(self):
        # obj = self.get_object()
        # return obj.__str__() if obj else f'#{self.id}'
        return mark_safe(f'{self.item_name} ({self.quantity} шт.)')


# -- адреса доставки и контактные данные --

class DeliveryAddressData(models.Model):
    region = models.CharField('Область', max_length=63)
    city = models.CharField('Город', max_length=63)
    address = models.TextField('Адрес')

    class Meta:
        abstract = True

    def get_address_data(self):
        return {
            'region': self.region,
            'city': self.city,
            'address': self.address,
        }


class ContactsData(models.Model):
    first_name = models.CharField('Имя', max_length=31)
    patronymic_name = models.CharField('Отчество', max_length=31, blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=31)
    phone = models.CharField('Телефон', max_length=31)

    class Meta:
        abstract = True

    @property
    def name(self):
        names = [self.first_name, self.patronymic_name, self.last_name]
        names = [x for x in names if x]
        return ' '.join(names)

    def get_contacts_data(self):
        return {
            'first_name': self.first_name,
            'patronymic_name': self.patronymic_name or '',
            'last_name': self.last_name,
            'phone': self.phone,
        }


class OrderDeliveryAddressData(DeliveryAddressData):
    order = models.OneToOneField(Order, models.CASCADE, related_name='address_data')

    class Meta:
        verbose_name = 'заказ: адрес доставки'
        verbose_name_plural = 'заказ: адреса доставки'

    def __str__(self):
        return f'{self.region}, {self.city}, {self.address}'


class OrderContactsData(ContactsData):
    order = models.OneToOneField(Order, models.CASCADE, related_name='contacts_data')

    class Meta:
        verbose_name = 'заказ: контактные данные'
        verbose_name_plural = 'заказ: контактные данные'

    def __str__(self):
        names = [self.first_name, self.patronymic_name, self.last_name]
        name = ' '.join(x for x in names if x)
        return f'{self.phone}, {name}'


class UserDeliveryAddress(DeliveryAddressData, ContactsData):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='addresses')
    is_selected = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_selected', 'id']
        verbose_name = 'пользователь: адрес доставки'
        verbose_name_plural = 'пользователь: адреса доставки'

    def get_contacts(self):
        return self.contacts_data.first()


# -- платежные данные: карты --

class PaymentCardData(models.Model):
    card_number = models.CharField('Номер карты', max_length=31)
    card_name = models.CharField('Имя на карте', max_length=255)
    card_expire = models.CharField('Срок действия', max_length=7)
    card_cvv = models.PositiveSmallIntegerField('CVV')

    class Meta:
        abstract = True

    @property
    def card_number_line(self):
        return f'**{self.card_number[-4:]} {self.card_expire}'

    def __str__(self):
        return self.card_number_line

    @property
    def card_type(self):
        card_number = self.card_number
        return (
            'МИР' if card_number.startswith('2')
            else 'VISA' if card_number.startswith('4')
            else 'MasterCard' if card_number.startswith('5')
            else 'American Express' if card_number.startswith('3')
            else ''
        )

    @property
    def card_logo_html(self):
        card_type = self.card_type
        logo_url = {
            'МИР': '/images/account/logo-mir.svg',
            'MasterCard': '/images/account/logo-masterard.svg',
        }.get(card_type)
        return (
            f'<img src="{logo_url}" alt="{card_type}"/>'
            if logo_url
            else f'<span class="card-type-text">{card_type}</span>'
        )

    def show_card_number(self):
        return f'**{self.card_number[-4:]}'
    show_card_number.short_description = 'Номер карты'
    show_card_number.allow_tags = True

    def get_data(self):
        return {
            'card_number': self.card_number,
            'card_name': self.card_name,
            'card_expire': self.card_expire,
            'card_cvv': self.card_cvv,
        }


class OrderPaymentCardData(PaymentCardData):
    order = models.OneToOneField(Order, models.CASCADE, related_name='payment_card_data')

    class Meta:
        verbose_name = 'заказ: данные карты'
        verbose_name_plural = 'заказ: данные карты'


class UserPaymentCard(PaymentCardData):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='payment_cards')
    is_selected = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_selected', 'id']
        verbose_name = 'пользователь: данные карты'
        verbose_name_plural = 'пользователь: данные карты'


# -- платежные данные: безналичный расчет --

class PaymentCashlessData(models.Model):
    organization = models.CharField('Название организации', max_length=63)
    jur_address = models.TextField('Юридический адрес')
    jur_phone = models.CharField('Телефон', max_length=31)
    jur_email = models.CharField('E-mail', max_length=31)
    inn = models.CharField('ИНН организации', max_length=31)
    kpp = models.CharField('КПП', max_length=31)
    ogrn = models.CharField('ОГРН', max_length=31)
    account = models.CharField('Р/С', max_length=31)
    bank = models.CharField('Банк', max_length=31)
    bik = models.CharField('БИК', max_length=31)
    director = models.CharField('Генеральный директор', max_length=63)

    class Meta:
        abstract = True

    def __str__(self):
        return self.organization

    def get_data(self):
        return {
            'organization': self.organization,
            'jur_address': self.jur_address,
            'jur_phone': self.jur_phone,
            'jur_email': self.jur_email,
            'inn': self.inn,
            'kpp': self.kpp,
            'ogrn': self.ogrn,
            'account': self.account,
            'bank': self.bank,
            'bik': self.bik,
            'director': self.director,
        }


class OrderPaymentCashlessData(PaymentCashlessData):
    order = models.OneToOneField(Order, models.CASCADE, related_name='payment_cashless_data')

    class Meta:
        verbose_name = 'заказ: данные безналичной оплаты'
        verbose_name_plural = 'заказ: данные безналичной оплаты'


class UserPaymentCashlessData(PaymentCashlessData):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE, related_name='payment_cashless_data')

    class Meta:
        verbose_name = 'пользователь: данные безналичной оплаты'
        verbose_name_plural = 'пользователь: данные безналичной оплаты'
