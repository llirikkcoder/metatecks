import logging

from celery import shared_task

from .emails import send_order_paid_email, send_payment_failed_email


l = logging.getLogger('orders.tasks')


@shared_task
def notify_and_sync_paid_order(order_id):
    from apps.third_party.bitrix24.tasks import sync_order_with_bitrix24
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)
        send_order_paid_email(order)
    except Exception as exc:
        l.error('[orders] notify_and_sync_paid_order: error for order #%s: %s', order_id, repr(exc))

    sync_order_with_bitrix24.delay(order_id, event='paid')


@shared_task
def notify_payment_failed(order_id):
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)
        send_payment_failed_email(order)
    except Exception as exc:
        l.error('[orders] notify_payment_failed: error for order #%s: %s', order_id, repr(exc))
