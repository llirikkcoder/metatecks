import logging

from django.conf import settings

from .client import Bitrix24Client


l = logging.getLogger('bitrix24.services')


def _stage_id(order):
    """
    STATUS_ID стадии для текущего состояния заказа. Настраивается через
    settings.BITRIX24_STAGE_NEW / BITRIX24_STAGE_PAID (см. conf.py).
    """
    return settings.BITRIX24_STAGE_PAID if order.is_paid else settings.BITRIX24_STAGE_NEW


def _build_deal_fields(order):
    contacts = getattr(order, 'contacts_data', None)
    fields = {
        'TITLE': f'Заказ № {order.number}',
        'OPPORTUNITY': str(order.total_cost),
        'CURRENCY_ID': 'RUB',
        'COMMENTS': order.comment or '',
    }
    stage_id = _stage_id(order)
    if stage_id:
        fields['STAGE_ID'] = stage_id
    if contacts:
        fields['CONTACT_NAME'] = contacts.name
        fields['CONTACT_PHONE'] = contacts.phone

    # кастомные UF_CRM_* поля портала клиента — донастраиваются через
    # settings.BITRIX24_DEAL_FIELD_MAP, когда пользователь получит вебхук и
    # список полей своего портала (crm.deal.fields)
    for our_key, bitrix_key in settings.BITRIX24_DEAL_FIELD_MAP.items():
        value = getattr(order, our_key, None)
        if value is not None:
            fields[bitrix_key] = value

    return fields


def create_or_update_deal(order):
    """
    Создаёт/обновляет сделку в Битрикс24 по заказу. No-op (без исключения),
    если BITRIX24_WEBHOOK_URL не настроен — см. Bitrix24Client.is_configured.
    """
    client = Bitrix24Client()
    fields = _build_deal_fields(order)

    if order.is_synced_with_b24:
        deal_id = order.bitrix24_deal_id
        if deal_id:
            # стадию при обновлении двигаем только по факту оплаты, иначе
            # затирали бы ручные перемещения менеджера по воронке
            if not order.is_paid:
                fields.pop('STAGE_ID', None)
            client.call('crm.deal.update', {'id': deal_id, 'fields': fields})
            l.info('[bitrix24] deal #%s updated for order #%d', deal_id, order.id)
            return

    fields['CATEGORY_ID'] = settings.BITRIX24_CATEGORY_ID
    result = client.call('crm.deal.add', {'fields': fields})
    if result is not None:
        order.is_synced_with_b24 = True
        order.bitrix24_deal_id = result.get('result')
        order.save(update_fields=['is_synced_with_b24', 'bitrix24_deal_id'])
        l.info('[bitrix24] deal #%s created for order #%d', order.bitrix24_deal_id, order.id)
