from django.apps import AppConfig

from watson import search

from apps.search.adapters import SEOSettingSearchAdapter


class SettingsConfig(AppConfig):
    name = 'apps.settings'
    verbose_name = 'Настройки'

    def ready(self):
        SEOSetting = self.get_model('SEOSetting')
        search.register(
            SEOSetting.objects.filter(url_pattern__gt=''),
            SEOSettingSearchAdapter,
            store=('description',),
        )
