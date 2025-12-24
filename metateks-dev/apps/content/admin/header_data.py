from django.contrib import admin

from solo.admin import SingletonModelAdmin

from apps.content.models import HeaderData, HeaderLink


class HeaderLinkInline(admin.TabularInline):
    model = HeaderLink
    fields = ('title', 'link', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-links'
    extra = 0


@admin.register(HeaderData)
class HeaderDataAdmin(SingletonModelAdmin):
    suit_form_tabs = (
        ('default', 'Данные'),
        ('links', 'Ссылки'),
    )
    fieldsets = (
        ('Режим работы', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('working_days', 'working_time',),
        }),
        ('Контакты', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('contacts_phone', 'contacts_email',),
        }),
    )
    inlines = [HeaderLinkInline]
