import logging

from celery import shared_task

from .exceptions import Bitrix24Error
from .services import create_or_update_deal


l = logging.getLogger('bitrix24.tasks')


@shared_task
def sync_order_with_bitrix24(order_id, event='created'):
    from apps.orders.models import Order

    try:
        order = Order.objects.get(id=order_id)
        create_or_update_deal(order)
        l.info('[bitrix24] sync (%s) done for order #%d', event, order_id)
    except Bitrix24Error as exc:
        l.error('[bitrix24] sync (%s) error for order #%s: %s', event, order_id, exc.message)
    except Exception as exc:
        l.error('[bitrix24] sync (%s) unexpected error for order #%s: %s', event, order_id, repr(exc))
