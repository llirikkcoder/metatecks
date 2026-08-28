import logging
import re

from django.conf import settings
from django.urls import NoReverseMatch, reverse

from apps.orders.constants import PaymentMethods
from apps.utils.common import absolute

from .client import Bitrix24Client
from .exceptions import Bitrix24Error


l = logging.getLogger('bitrix24.services')


def _stage_id(order):
    """
    STATUS_ID стадии для текущего состояния заказа. Настраивается через
    settings.BITRIX24_STAGE_NEW / BITRIX24_STAGE_PAID (см. conf.py).
    """
    return settings.BITRIX24_STAGE_PAID if order.is_paid else settings.BITRIX24_STAGE_NEW


def _normalize_phone(phone):
    """Телефон в формате +7XXXXXXXXXX — в таком виде его хранит Битрикс24."""
    digits = re.sub(r'\D', '', phone or '')
    if len(digits) == 11 and digits[0] in '78':
        return f'+7{digits[1:]}'
    if len(digits) == 10:
        return f'+7{digits}'
    return f'+{digits}' if digits else None


def _find_contact_id(client, phone):
    """
    ID существующего контакта с таким телефоном, иначе None. Ищем по
    нормализованному и по исходному написанию — менеджеры заводят номера
    как придётся.
    """
    values = [v for v in {_normalize_phone(phone), phone} if v]
    if not values:
        return None

    payload = client.call('crm.duplicate.findbycomm', {
        'entity_type': 'CONTACT',
        'type': 'PHONE',
        'values': values,
    })
    if not payload:
        return None

    found = (payload.get('result') or {}).get('CONTACT') or []
    return found[0] if found else None


def _create_contact(client, contacts, order):
    fields = {
        'NAME': contacts.first_name,
        'LAST_NAME': contacts.last_name,
        'OPENED': 'Y',
        'PHONE': [{'VALUE': _normalize_phone(contacts.phone) or contacts.phone, 'VALUE_TYPE': 'MOBILE'}],
    }
    if contacts.patronymic_name:
        fields['SECOND_NAME'] = contacts.patronymic_name
    if settings.BITRIX24_SOURCE_ID:
        fields['SOURCE_ID'] = settings.BITRIX24_SOURCE_ID

    email = getattr(getattr(order, 'user', None), 'email', None)
    if email:
        fields['EMAIL'] = [{'VALUE': email, 'VALUE_TYPE': 'HOME'}]

    payload = client.call('crm.contact.add', {'fields': fields})
    return payload.get('result') if payload else None


def _resolve_contact_id(client, order):
    """
    ID контакта покупателя: находим существующий по телефону или создаём
    нового. Битрикс не умеет создавать контакт из полей сделки — поля
    CONTACT_NAME/CONTACT_PHONE в crm.deal.add он молча игнорирует.

    Проблемы с контактом не должны ронять синхронизацию заказа: в худшем
    случае сделка уедет без привязанного контакта, о чём будет запись в логе.
    """
    contacts = getattr(order, 'contacts_data', None)
    if not contacts:
        return None

    try:
        contact_id = _find_contact_id(client, contacts.phone)
        if contact_id:
            l.info('[bitrix24] existing contact #%s matched for order #%d', contact_id, order.id)
            return contact_id

        contact_id = _create_contact(client, contacts, order)
        if contact_id:
            l.info('[bitrix24] contact #%s created for order #%d', contact_id, order.id)
        return contact_id
    except Bitrix24Error as exc:
        l.error('[bitrix24] contact sync failed for order #%d: %s', order.id, exc.message)
        return None


def _admin_url(order):
    """Ссылка на заказ в админке сайта — менеджеру открыть карточку одним кликом."""
    try:
        return absolute(reverse('admin:orders_order_change', args=(order.id,)))
    except NoReverseMatch:
        return None


def _build_comments(order):
    """
    Данные заказа — в комментарий сделки: название сделки на портале
    перезаписывает автонумерация, а комментарий остаётся как есть.
    """
    lines = [f'Заказ с сайта № {order.number}']

    payment = getattr(order, 'active_payment', None)
    if order.is_paid:
        lines.append('Статус оплаты: оплачен')
        if order.paid_at:
            lines.append(f'Дата оплаты: {order.paid_at.strftime("%d.%m.%Y %H:%M")}')
        if payment and payment.alfa_order_id:
            lines.append(f'ID платежа в банке: {payment.alfa_order_id}')
    elif order.payment_method == PaymentMethods.ONLINE:
        lines.append('Статус оплаты: не оплачен')

    admin_url = _admin_url(order)
    if admin_url:
        lines.append(f'Заказ в админке: {admin_url}')

    if order.comment:
        lines += ['', f'Комментарий покупателя: {order.comment}']

    return '\n'.join(lines)


def _build_deal_fields(order):
    fields = {
        'TITLE': f'Заказ № {order.number}',
        'OPPORTUNITY': str(order.total_cost),
        'CURRENCY_ID': 'RUB',
        'COMMENTS': _build_comments(order),
    }
    stage_id = _stage_id(order)
    if stage_id:
        fields['STAGE_ID'] = stage_id
    if settings.BITRIX24_SOURCE_ID:
        fields['SOURCE_ID'] = settings.BITRIX24_SOURCE_ID

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

    contact_id = _resolve_contact_id(client, order)
    if contact_id:
        fields['CONTACT_ID'] = contact_id

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


def create_lead_from_callback(callback):
    """
    Лид «Обратный звонок» по заявке с сайта. Каждая заявка — отдельный лид
    (портал в классическом режиме CRM, лиды включены): дедупликацию по
    телефону менеджер делает средствами Битрикса при конвертации лида.
    No-op без настроенного вебхука — как и остальные вызовы клиента.
    """
    client = Bitrix24Client()

    phone = _normalize_phone(callback.phone) or callback.phone
    lines = [f'Заявка № {callback.id} от {callback.created_at.strftime("%d.%m.%Y %H:%M")}']
    if callback.user:
        lines.append(f'Пользователь сайта: {callback.user.email}')
    try:
        lines.append(
            'Заявка в админке: '
            + absolute(reverse('admin:feedback_callbackrequest_change', args=(callback.id,)))
        )
    except NoReverseMatch:
        pass

    fields = {
        'TITLE': f'Обратный звонок с сайта: {callback.name or phone}',
        'PHONE': [{'VALUE': phone, 'VALUE_TYPE': 'MOBILE'}],
        'OPENED': 'Y',
        'COMMENTS': '\n'.join(lines),
    }
    if callback.name:
        fields['NAME'] = callback.name
    if settings.BITRIX24_SOURCE_CALLBACK_ID:
        fields['SOURCE_ID'] = settings.BITRIX24_SOURCE_CALLBACK_ID

    result = client.call('crm.lead.add', {'fields': fields})
    if result is not None:
        callback.is_synced_with_b24 = True
        callback.save(update_fields=['is_synced_with_b24'])
        l.info('[bitrix24] lead #%s created for callback #%d', result.get('result'), callback.id)


def _find_contact_id_by_email(client, email):
    """ID существующего контакта с таким email, иначе None."""
    if not email:
        return None

    payload = client.call('crm.duplicate.findbycomm', {
        'entity_type': 'CONTACT',
        'type': 'EMAIL',
        'values': [email],
    })
    if not payload:
        return None

    found = (payload.get('result') or {}).get('CONTACT') or []
    return found[0] if found else None


def create_contact_for_user(user):
    """
    Контакт в Битрикс24 по зарегистрировавшемуся пользователю. Если контакт
    с таким телефоном или email уже существует — новый не создаём, только
    помечаем пользователя синхронизированным.
    """
    client = Bitrix24Client()

    contact_id = _find_contact_id(client, user.phone) if user.phone else None
    if not contact_id:
        contact_id = _find_contact_id_by_email(client, user.email)
    if contact_id:
        l.info('[bitrix24] existing contact #%s matched for user #%d', contact_id, user.id)
        _mark_user_synced(user)
        return contact_id

    fields = {
        'NAME': user.first_name or user.email,
        'OPENED': 'Y',
        'EMAIL': [{'VALUE': user.email, 'VALUE_TYPE': 'HOME'}],
    }
    if user.last_name:
        fields['LAST_NAME'] = user.last_name
    if user.patronymic_name:
        fields['SECOND_NAME'] = user.patronymic_name
    if user.phone:
        fields['PHONE'] = [{'VALUE': _normalize_phone(user.phone) or user.phone, 'VALUE_TYPE': 'MOBILE'}]
    if settings.BITRIX24_SOURCE_ID:
        fields['SOURCE_ID'] = settings.BITRIX24_SOURCE_ID

    payload = client.call('crm.contact.add', {'fields': fields})
    contact_id = payload.get('result') if payload else None
    if contact_id:
        _mark_user_synced(user)
        l.info('[bitrix24] contact #%s created for user #%d', contact_id, user.id)
    return contact_id


def _mark_user_synced(user):
    user.is_synced_with_b24 = True
    user.save(update_fields=['is_synced_with_b24'])
