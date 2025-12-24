from .models import Settings, SEOSetting


def settings(request):
    if request.path.startswith('/admin/'):
        return {}

    settings = Settings.get_solo()
    seo_settings = {setting.key: setting for setting in SEOSetting.objects.all()}

    return {
        'settings': settings,
        'seo_settings': seo_settings,
    }
