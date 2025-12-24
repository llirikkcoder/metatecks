from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.utils.admin_mixins import ImageThumbnailsAdminMixin
from .admin_forms import PromotionForm
from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(ImageThumbnailsAdminMixin, admin.ModelAdmin):
    list_display = (
        'id', 'name', 'discount_type', 'show_discount', 'show_banner', 'show_banner_695',
        'is_active', 'show_is_shown', 'start_dt', 'end_dt',
        'show_products_count',
    )
    list_display_links = ('id', 'name',)
    list_filter = ('discount_type', 'is_active',)
    suit_list_filter_horizontal = ('discount_type', 'is_active',)
    suit_form_tabs = (
        ('default', 'Акция'),
        ('discount', 'Скидка'),
        ('products', 'Товары в акции'),
        ('settings', 'Настройки показа'),
    )
    form = PromotionForm
    fieldsets = (
        ('Акция', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'name', 'banner_design', 'banner', 'banner_695', 'old_price', 'new_price', 'description',)
        }),
        ('Скидка', {
            'classes': ('suit-tab', 'suit-tab-discount',),
            'fields': ('discount_type', 'discount_percents', 'discount_amount', 'show_discount',)
        }),
        ('Товары в акции', {
            'classes': ('suit-tab', 'suit-tab-products',),
            'fields': ('model', 'product', 'show_products_count',)
        }),
        ('Настройки показа', {
            'classes': ('suit-tab', 'suit-tab-settings',),
            'fields': ('created_at', 'start_dt', 'end_dt', 'is_active', 'show_is_shown',)
        }),
    )
    raw_id_fields = ('model', 'product',)
    readonly_fields = ('id', 'show_discount', 'created_at', 'show_products_count', 'show_is_shown',)
    search_fields = ('name', 'description',)

    @admin.display(description='Баннер (1920x720px)')
    def show_banner(self, obj):
        html = f'<a href="{obj.banner.url}" target="_blank"><img src="{obj.banner_admin_url}"></a>'
        return mark_safe(html)

    @admin.display(description='Баннер (695x522px)')
    def show_banner_695(self, obj):
        if obj.banner_695:
            html = f'<a href="{obj.banner_695.url}" target="_blank"><img src="{obj.banner_695_admin_url}"></a>'
            return mark_safe(html)
