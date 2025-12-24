from django.contrib import admin
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from apps.utils.admin_mixins import ImageThumbnailsAdminMixin, ShortTextFieldAdminMixin
from .admin_forms import BannerForm
from .admin_utils import IsPublishedNowFilter, BaseBannerAdmin
from .models import Banner


@admin.register(Banner)
class BannerAdmin(ImageThumbnailsAdminMixin, ShortTextFieldAdminMixin, SortableAdminMixin, BaseBannerAdmin):
    list_display = (
        '__str__', 'banner_place', 'is_published', 'show_is_shown',
        'show_image_1200', 'show_image_670', 'link',
        'start_dt', 'end_dt',
        # 'shows',
    )
    list_display_links = ('__str__', 'banner_place',)
    list_filter = (IsPublishedNowFilter, 'is_published', 'banner_place',)
    suit_list_filter_horizontal = (IsPublishedNowFilter, 'is_published', 'banner_place',)
    suit_form_tabs = (
        ('default', 'Баннер'),
        ('data', 'Данные на баннере'),
        ('settings', 'Настройки показа'),
    )
    form = BannerForm
    fieldsets = (
        ('Баннер', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'title', 'banner_place', 'design', 'image_1200', 'image_670', 'link',)
        }),
        ('Данные на баннере', {
            'classes': ('suit-tab', 'suit-tab-data',),
            'fields': ('text', 'button_text', 'old_price', 'new_price', 'description',)
        }),
        ('Настройки показа', {
            'classes': ('suit-tab', 'suit-tab-settings',),
            # 'fields': ('created_at', 'start_dt', 'end_dt', 'is_published', 'show_is_shown', 'shows',)
            'fields': ('created_at', 'start_dt', 'end_dt', 'is_published', 'show_is_shown',)
        }),
    )
    readonly_fields = ('id', 'created_at', 'show_is_shown', 'shows',)
    search_fields = ('title', 'link', 'text', 'description',)

    @admin.display(description='Изображение 1200х570px')
    def show_image_1200(self, obj):
        html = f'<a href="{obj.image_1200_url}" target="_blank"><img src="{obj.image_1200_admin_url}"></a>'
        return mark_safe(html)

    @admin.display(description='Изображение 670х950px')
    def show_image_670(self, obj):
        html = f'<a href="{obj.image_1200_url}" target="_blank"><img src="{obj.image_670_admin_url}"></a>'
        return mark_safe(html)
