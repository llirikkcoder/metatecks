from django.contrib import admin
from django.utils.safestring import mark_safe

from solo.admin import SingletonModelAdmin

from apps.utils.admin_mixins import ShortTextFieldAdminMixin
from apps.utils.common import bool_to_icon
from .models import Settings, SEOSetting, SEO_INSTRUCTION


@admin.register(Settings)
class SettingsAdmin(ShortTextFieldAdminMixin, SingletonModelAdmin):
    fieldsets = (
        ('Email для обратной связи', {
            'fields': ('feedback_email', 'orders_email',)
        }),
        ('SEO и Robots.txt', {
            'fields': ('title_suffix', 'robots_txt',)
        }),
    )


@admin.register(SEOSetting)
class SEOSettingAdmin(ShortTextFieldAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'key', 'description', 'title', 'h1', 'meta_desc', 'meta_keyw', 'has_header_text', 'url_pattern',)
    list_display_links = ('id', 'key', 'description',)
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': (
                'id', 'key', 'description',
                'title', 'h1', 'meta_desc', 'meta_keyw', 'header_text',
                'show_instruction',
                'url_pattern',
            )
        }),
    )
    readonly_fields = ('id', 'show_instruction',)
    search_fields = ('key', 'description', 'title', 'h1', 'meta_desc', 'meta_keyw',)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj:
            fields.append('key')
            fields.append('description')
            if obj.url_pattern:
                fields.append('url_pattern')
        return fields

    @admin.display(description='Есть описание страницы?')
    def has_header_text(self, obj):
        return '+' if obj.header_text else ''

    def has_delete_permission(self, request, obj=None):
        return None
