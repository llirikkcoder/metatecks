import os

from appconf import AppConf


class Bitrix24AppConf(AppConf):

    # входящий вебхук вида https://<портал>.bitrix24.ru/rest/<user_id>/<token>
    WEBHOOK_URL = os.getenv('BITRIX24_WEBHOOK_URL', '')

    REQUEST_TIMEOUT = 15

    # ID воронки сделок. На портале metateks одна воронка «Продажи» = 0
    # (crm.category.list?entityTypeId=2)
    CATEGORY_ID = os.getenv('BITRIX24_CATEGORY_ID', '0')

    # Стадии сделки. Меняются через .env без правок кода — список STATUS_ID
    # своего портала: crm.status.list?filter[ENTITY_ID]=DEAL_STAGE
    # Пустое значение = не передавать стадию (Битрикс поставит начальную).
    #
    # заказ создан на сайте, оплата ещё не прошла
    STAGE_NEW = os.getenv('BITRIX24_STAGE_NEW', 'NEW')
    # заказ оплачен онлайн
    STAGE_PAID = os.getenv('BITRIX24_STAGE_PAID', 'PREPARATION')

    # Источник сделки и контакта (crm.status.list?filter[ENTITY_ID]=SOURCE).
    # STORE = «Интернет-магазин». Пустое значение = не передавать источник.
    SOURCE_ID = os.getenv('BITRIX24_SOURCE_ID', 'STORE')

    # Источник лида «Заказ обратного звонка». CALLBACK = «Обратный звонок»,
    # на портале metateks есть (проверено 28.08.2026 по crm.status.list).
    SOURCE_CALLBACK_ID = os.getenv('BITRIX24_SOURCE_CALLBACK_ID', 'CALLBACK')

    # маппинг полей сделки -> уточняется пользователем после получения вебхука
    # (кастомные UF_CRM_* поля зависят от конкретного портала)
    DEAL_FIELD_MAP = {}

    class Meta:
        prefix = 'BITRIX24'
