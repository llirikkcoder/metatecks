import os

from appconf import AppConf


class Bitrix24AppConf(AppConf):

    # входящий вебхук вида https://<портал>.bitrix24.ru/rest/<user_id>/<token>
    WEBHOOK_URL = os.getenv('BITRIX24_WEBHOOK_URL', '')

    REQUEST_TIMEOUT = 15

    # маппинг полей сделки -> уточняется пользователем после получения вебхука
    # (кастомные UF_CRM_* поля зависят от конкретного портала)
    DEAL_FIELD_MAP = {}

    class Meta:
        prefix = 'BITRIX24'
