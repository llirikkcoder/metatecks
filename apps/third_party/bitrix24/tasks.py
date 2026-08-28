import logging

from celery import shared_task

from .exceptions import Bitrix24Error
from .services import create_contact_for_user, create_lead_from_callback, create_or_update_deal


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


@shared_task
def sync_callback_with_bitrix24(callback_id):
    from apps.feedback.models import CallbackRequest

    try:
        callback = CallbackRequest.objects.get(id=callback_id)
        create_lead_from_callback(callback)
        l.info('[bitrix24] sync (callback) done for callback #%d', callback_id)
    except Bitrix24Error as exc:
        l.error('[bitrix24] sync (callback) error for callback #%s: %s', callback_id, exc.message)
    except Exception as exc:
        l.error('[bitrix24] sync (callback) unexpected error for callback #%s: %s', callback_id, repr(exc))


@shared_task
def sync_user_with_bitrix24(user_id):
    from apps.users.models import User

    try:
        user = User.objects.get(id=user_id)
        create_contact_for_user(user)
        l.info('[bitrix24] sync (registration) done for user #%d', user_id)
    except Bitrix24Error as exc:
        l.error('[bitrix24] sync (registration) error for user #%s: %s', user_id, exc.message)
    except Exception as exc:
        l.error('[bitrix24] sync (registration) unexpected error for user #%s: %s', user_id, repr(exc))
