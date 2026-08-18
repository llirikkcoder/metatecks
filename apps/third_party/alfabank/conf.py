import os

from appconf import AppConf


class AlfaBankAppConf(AppConf):

    # тестовый контур: https://alfa.rbsuat.com/payment/rest
    # боевой контур:   https://payment.alfabank.ru/payment/rest
    API_BASE_URL = os.getenv('ALFA_API_BASE_URL', 'https://alfa.rbsuat.com/payment/rest')
    MERCHANT_LOGIN = os.getenv('ALFA_MERCHANT_LOGIN', '')
    MERCHANT_PASSWORD = os.getenv('ALFA_MERCHANT_PASSWORD', '')

    REQUEST_TIMEOUT = 15

    class Meta:
        prefix = 'ALFA'
