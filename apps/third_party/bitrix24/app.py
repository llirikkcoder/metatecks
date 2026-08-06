from django.apps import AppConfig


class Bitrix24Config(AppConfig):
    name = 'apps.third_party.bitrix24'
    verbose_name = 'Битрикс24: CRM'

    def ready(self):
        from . import conf  # noqa: F401 -- регистрирует Bitrix24AppConf в django.conf.settings
