from django.contrib import admin

from solo.admin import SingletonModelAdmin
from suit import apps as suit_apps

from apps.content.admin_forms import AboutAdvantageForm
from apps.content.models import (
    AboutCompany, AboutFact, AboutAdvantage,
    AboutWarehouse, AboutTransportCompany,
)
from apps.utils.admin_mixins import ImageThumbnailsAdminMixin, ShortTextFieldAdminMixin


class AboutFactInline(admin.TabularInline):
    model = AboutFact
    fields = ('text1', 'number', 'text2', 'place', 'order',)
    suit_classes = 'suit-tab suit-tab-facts'
    extra = 0


class AboutAdvantageInline(ImageThumbnailsAdminMixin, ShortTextFieldAdminMixin, admin.StackedInline):
    model = AboutAdvantage
    form = AboutAdvantageForm
    fields = (
        'icon', 'list_title', 'block_type', 'title',
        'photo', 'video', 'gallery', 'text',
        'button_text', 'button_link',
        'order', 'is_shown',
    )
    suit_classes = 'suit-tab suit-tab-advantages'
    extra = 0


class AboutWarehouseInline(ShortTextFieldAdminMixin, admin.StackedInline):
    model = AboutWarehouse
    fields = (
        'name', 'description', 'address', 'schedule', 'phone',
        'order', 'is_shown',
    )
    suit_classes = 'suit-tab suit-tab-warehouses'
    extra = 0


class AboutTransportCompanyInline(admin.TabularInline):
    model = AboutTransportCompany
    fields = ('name', 'logo', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-transport'
    extra = 0


@admin.register(AboutCompany)
class AboutCompanyAdmin(ImageThumbnailsAdminMixin, SingletonModelAdmin):
    suit_form_tabs = (
        ('default', 'Страница'),
        ('facts', 'Блок с фактами'),
        ('advantages', 'Блоки «Наши преимущества»'),
        ('warehouses', 'Склады'),
        ('transport', 'Транспортные компании'),
        ('people', 'Блок «Люди»'),
        ('phone', 'Блок «Звонок в офис»'),
    )
    fieldsets = (
        ('Страница', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('about_title', 'about_text',),
        }),
        ('Блок «Люди»', {
            'classes': ('suit-tab', 'suit-tab-people',),
            'fields': ('people_title', 'people_photo',),
        }),
        ('Блок «Звонок в офис»', {
            'classes': ('suit-tab', 'suit-tab-phone',),
            'fields': ('phone_text', 'phone_number',),
        }),
    )
    inlines = [
        AboutFactInline,
        AboutAdvantageInline,
        AboutWarehouseInline,
        AboutTransportCompanyInline,
    ]
