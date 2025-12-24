from django.db import models


class GetLabelMixin(object):

    @classmethod
    def get_label(cls, key, default=''):
        try:
            return cls(key).label
        except ValueError:
            return default


# -- способы доставки --

class DeliveryMethods(GetLabelMixin, models.TextChoices):
    PICKUP = 'pickup', 'Самовывоз'
    METATEKS = 'metateks', 'Транспортом Метатэкс'
    COMPANY = 'company', 'Транспортной компанией'

DELIVERY_METHODS = dict(DeliveryMethods.choices).keys()


# -- методы оплаты --

class PaymentMethods(GetLabelMixin, models.TextChoices):
    ONLINE = 'online', 'Оплата онлайн'
    NON_CASH = 'non_cash', 'Безналичная оплата'
    ON_RECEIPT = 'on_receipt', 'Оплата при получении'

PAYMENT_METHODS = dict(PaymentMethods.choices).keys()


# -- статусы заказа --

class OrderStatuses(GetLabelMixin, models.TextChoices):
    CREATED = 'created', 'Оформлен'
    COLLECTING = 'collecting', 'Комплектуется'
    DELIVERING = 'delivering', 'Доставляется'
    COMPLETED = 'completed', 'Выполнен'
    CANCELED = 'canceled', 'Отменен'

ORDER_STATUSES = dict(OrderStatuses.choices).keys()
