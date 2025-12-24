from django.contrib import admin

from solo.admin import SingletonModelAdmin
from suit import apps as suit_apps

from apps.content.models import (
    Homepage, HomepageFact, HomepageAdvantage, HomepageWarehouse, HomepageSalesPhone, HomepageSalesManager
)
from apps.utils.admin_mixins import ImageThumbnailsAdminMixin, ShortTextFieldAdminMixin


class HomepageFactInline(ShortTextFieldAdminMixin, admin.TabularInline):
    model = HomepageFact
    fields = ('icon', 'text_large', 'text', 'order',)
    suit_classes = 'suit-tab suit-tab-default'
    extra = 0


class HomepageAdvantageInline(ShortTextFieldAdminMixin, admin.StackedInline):
    model = HomepageAdvantage
    fields = ('icon', 'text', 'order',)
    suit_classes = 'suit-tab suit-tab-advantages'
    extra = 0


class HomepageWarehouseInline(ShortTextFieldAdminMixin, admin.StackedInline):
    model = HomepageWarehouse
    fields = ('photo', 'name', 'subtitle', 'address', 'schedule', 'phone', 'order',)
    suit_classes = 'suit-tab suit-tab-warehouses'
    extra = 0


class HomepageSalesPhoneInline(admin.TabularInline):
    model = HomepageSalesPhone
    fields = ('phone', 'is_free', 'order',)
    suit_classes = 'suit-tab suit-tab-sales'
    extra = 0


class HomepageSalesManagerInline(admin.TabularInline):
    model = HomepageSalesManager
    fields = ('name', 'name_dative', 'photo', 'phone', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-sales'
    extra = 0


@admin.register(Homepage)
class HomepageAdmin(ImageThumbnailsAdminMixin, SingletonModelAdmin):
    suit_form_tabs = (
        ('default', 'Страница'),
        ('about-company', 'О компании'),
        ('advantages', 'Наши преимущества'),
        ('media', 'Медиа'),
        ('warehouses', 'Склады оборудования'),
        ('sales', 'Отдел продаж'),
    )
    fieldsets = (
        ('Шапка страницы', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('page_title',),
        }),
        ('О компании', {
            'classes': ('suit-tab', 'suit-tab-about-company',),
            'fields': ('about_title', 'about_photo', 'about_text',),
        }),
        ('Наши преимущества', {
            'classes': ('suit-tab', 'suit-tab-advantages',),
            'fields': ('advantages_title',),
        }),
        ('Медиа', {
            'classes': ('suit-tab', 'suit-tab-media',),
            'fields': (
                'news_title', 'news_text', 'articles_title', 'articles_text',
                'photo_title', 'photo_text', 'video_title', 'video_text',
            ),
        }),
        ('Отдел продаж', {
            'classes': ('suit-tab', 'suit-tab-sales',),
            'fields': ('sales_title', 'sales_text',),
        }),
    )
    inlines = [
        HomepageFactInline,
        HomepageAdvantageInline,
        HomepageWarehouseInline,
        HomepageSalesPhoneInline,
        HomepageSalesManagerInline,
    ]
