from django.apps import AppConfig


class AlfaBankConfig(AppConfig):
    name = 'apps.third_party.alfabank'
    verbose_name = 'Альфа-Банк: эквайринг'

    def ready(self):
        from . import conf  # noqa: F401 -- регистрирует AlfaBankAppConf в django.conf.settings
