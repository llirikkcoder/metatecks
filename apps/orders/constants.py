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
    AWAITING_PAYMENT = 'awaiting_payment', 'Ожидает оплаты'
    CREATED = 'created', 'Оформлен'
    COLLECTING = 'collecting', 'Комплектуется'
    DELIVERING = 'delivering', 'Доставляется'
    COMPLETED = 'completed', 'Выполнен'
    CANCELED = 'canceled', 'Отменен'
    PAYMENT_FAILED = 'payment_failed', 'Ошибка оплаты'
    PAYMENT_CANCELED = 'payment_canceled', 'Оплата отменена'
    REFUNDED = 'refunded', 'Возврат'

ORDER_STATUSES = dict(OrderStatuses.choices).keys()


# -- статусы онлайн-платежа --

class PaymentStatuses(GetLabelMixin, models.TextChoices):
    REGISTERED = 'registered', 'Зарегистрирован в банке'
    PENDING = 'pending', 'Ожидает оплаты'
    AUTHORIZED = 'authorized', 'Авторизован'
    PAID = 'paid', 'Оплачен'
    DECLINED = 'declined', 'Отклонён'
    CANCELED = 'canceled', 'Отменён'
    REFUNDED = 'refunded', 'Возврат'
    ERROR = 'error', 'Ошибка'

PAYMENT_STATUSES = dict(PaymentStatuses.choices).keys()
