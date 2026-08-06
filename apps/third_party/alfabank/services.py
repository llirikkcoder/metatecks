import logging

from django.urls import reverse

from apps.orders.constants import PaymentStatuses
from apps.orders.models import Payment
from apps.utils.common import absolute

from .client import AlfaBankClient


l = logging.getLogger('alfabank.services')


def register_payment(order):
    """
    Регистрирует заказ в Альфа-Банке и создаёт объект Payment.
    Бросает AlfaBankError при сбое — обрабатывается вызывающим кодом (view).
    """
    client = AlfaBankClient()
    return_url = absolute(f"{reverse('alfabank:payment-return')}?order_id={order.id}")
    fail_url = absolute(f"{reverse('alfabank:payment-fail')}?order_id={order.id}")

    alfa_order_id, form_url, raw = client.register_order(
        order_number=str(order.id),
        amount_rub=order.total_cost,
        return_url=return_url,
        fail_url=fail_url,
        description=f'Заказ № {order.number}',
    )
    payment = Payment.objects.create(
        order=order,
        amount=order.total_cost,
        alfa_order_id=alfa_order_id,
        form_url=form_url,
        status=PaymentStatuses.REGISTERED,
        raw_register_response=raw,
    )
    l.info('[alfabank] payment #%d registered for order #%d (alfa_order_id=%s)', payment.id, order.id, alfa_order_id)
    return payment


def sync_payment_status(payment):
    """
    Опрашивает банк и обновляет Payment/Order. Идемпотентна — повторный вызов
    при уже финальном статусе не переотправляет уведомления/Bitrix24-синк.
    """
    # локальный импорт — избегаем цикла orders -> alfabank.services -> orders.tasks
    from apps.orders.tasks import notify_and_sync_paid_order, notify_payment_failed

    client = AlfaBankClient()
    new_status, raw = client.get_order_status(payment.alfa_order_id)
    payment.raw_status_response = raw

    was_final = payment.status in (PaymentStatuses.PAID, PaymentStatuses.DECLINED, PaymentStatuses.CANCELED)

    if new_status == PaymentStatuses.PAID:
        if payment.status != PaymentStatuses.PAID:
            payment.mark_paid(raw_response=raw)
            notify_and_sync_paid_order.delay(payment.order_id)
        else:
            payment.save()
    elif new_status in (PaymentStatuses.DECLINED, PaymentStatuses.CANCELED):
        if not was_final:
            payment.mark_declined(raw_response=raw)
            notify_payment_failed.delay(payment.order_id)
        else:
            payment.save()
    elif new_status is not None:
        payment.status = new_status
        payment.save()
    else:
        payment.save()

    return payment
