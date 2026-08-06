import logging

import requests
from django.conf import settings

from .constants import ALFA_STATUS_MAP
from .exceptions import AlfaBankError


l = logging.getLogger('alfabank.client')


class AlfaBankClient:
    """
    Клиент REST API Интернет-эквайринга Альфа-Банка.
    Документация метода: register.do / getOrderStatusExtended.do (общий для банков движок).
    """

    def __init__(self):
        self.base_url = settings.ALFA_API_BASE_URL.rstrip('/')
        self.login = settings.ALFA_MERCHANT_LOGIN
        self.password = settings.ALFA_MERCHANT_PASSWORD
        self.timeout = settings.ALFA_REQUEST_TIMEOUT

    def _post(self, method, params):
        url = f'{self.base_url}/{method}'
        data = {'userName': self.login, 'password': self.password, **params}
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            l.error('[alfabank] %s request failed: %s', method, repr(exc))
            raise AlfaBankError(f'Ошибка соединения с банком: {exc}') from exc
        except ValueError as exc:
            l.error('[alfabank] %s returned non-JSON response: %s', method, response.text[:500])
            raise AlfaBankError('Банк вернул некорректный ответ') from exc

        error_code = payload.get('errorCode')
        if error_code and error_code != '0':
            error_message = payload.get('errorMessage', '')
            l.error('[alfabank] %s error %s: %s', method, error_code, error_message)
            raise AlfaBankError(error_message or 'Ошибка банка', code=error_code, raw_response=payload)

        return payload

    def register_order(self, order_number, amount_rub, return_url, fail_url, description=''):
        amount_kopecks = int(amount_rub * 100)
        payload = self._post('register.do', {
            'orderNumber': order_number,
            'amount': amount_kopecks,
            'returnUrl': return_url,
            'failUrl': fail_url,
            'description': description,
        })
        alfa_order_id = payload.get('orderId')
        form_url = payload.get('formUrl')
        if not alfa_order_id or not form_url:
            raise AlfaBankError('Банк не вернул orderId/formUrl', raw_response=payload)
        return alfa_order_id, form_url, payload

    def get_order_status(self, alfa_order_id):
        payload = self._post('getOrderStatusExtended.do', {'orderId': alfa_order_id})
        order_status = payload.get('orderStatus')
        payment_status = ALFA_STATUS_MAP.get(order_status)
        if payment_status is None:
            l.warning('[alfabank] unknown orderStatus=%r for orderId=%s', order_status, alfa_order_id)
        return payment_status, payload
