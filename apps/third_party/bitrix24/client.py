import logging

import requests
from django.conf import settings

from .exceptions import Bitrix24Error


l = logging.getLogger('bitrix24.client')


class Bitrix24Client:
    """Тонкая обёртка над REST API входящего вебхука Битрикс24."""

    def __init__(self):
        self.webhook_url = settings.BITRIX24_WEBHOOK_URL.rstrip('/') if settings.BITRIX24_WEBHOOK_URL else ''
        self.timeout = settings.BITRIX24_REQUEST_TIMEOUT

    @property
    def is_configured(self):
        return bool(self.webhook_url)

    def call(self, method, params):
        if not self.is_configured:
            l.info('[bitrix24] webhook not configured, would call %s with %s', method, params)
            return None

        url = f'{self.webhook_url}/{method}.json'
        try:
            response = requests.post(url, json=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            l.error('[bitrix24] %s request failed: %s', method, repr(exc))
            raise Bitrix24Error(f'Ошибка соединения с Битрикс24: {exc}') from exc
        except ValueError as exc:
            l.error('[bitrix24] %s returned non-JSON response: %s', method, response.text[:500])
            raise Bitrix24Error('Битрикс24 вернул некорректный ответ') from exc

        if 'error' in payload:
            l.error('[bitrix24] %s error: %s', method, payload.get('error_description', payload['error']))
            raise Bitrix24Error(payload.get('error_description', payload['error']), raw_response=payload)

        return payload
