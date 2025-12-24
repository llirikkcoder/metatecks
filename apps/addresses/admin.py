from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin
from solo.admin import SingletonModelAdmin

from apps.utils.admin_mixins import SelectPrefetchRelatedMixin, ShortTextFieldAdminMixin
from .models import City, Warehouse, Office, OfficeEmail, OfficePhone, OfficeSocialLink, ProductionAddress


@admin.register(City)
class CityAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        'name', 'subdomain', 'contacts_phone', 'is_default', 'name_loct', 'region_name', 'region_name_loct',
    )
    list_editable = (
        'subdomain', 'contacts_phone', 'is_default', 'name_loct', 'region_name', 'region_name_loct',
    )
    fields = (
        'name', 'subdomain',
        'name_loct', 'region_name', 'region_name_loct',
        'contacts_phone', 'is_default',
        'names_en', 'region_names_en',
    )
    search_fields = ('name', 'subdomain', 'name_loct', 'region_name', 'region_name_loct',)


@admin.register(Warehouse)
class WarehouseAdmin(ShortTextFieldAdminMixin, SortableAdminMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = ('city', 'show_name', 'name_short', 'description',)
    list_display_links = ('city', 'show_name',)
    list_editable = ('name_short',)
    list_filter = ('city',)
    suit_list_filter_horizontal = ('city',)
    suit_form_tabs = (
        ('default', 'Склад'),
        ('address', 'Адрес'),
        ('contacts', 'Контакты'),
    )
    fieldsets = (
        ('Склад', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('city', 'name', 'name_short', 'description',),
        }),
        ('Адрес', {
            'classes': ('suit-tab', 'suit-tab-address',),
            'fields': ('address', 'address_on_map', 'latitude', 'longitude',),
        }),
        ('Контакты', {
            'classes': ('suit-tab', 'suit-tab-contacts',),
            'fields': ('schedule', 'phone', 'contact_email',),
        }),
    )
    search_fields = ('name', 'description', 'address', 'address_on_map',)
    select_related = ('city',)


class OfficeEmailInline(admin.TabularInline):
    model = OfficeEmail
    fields = ('email', 'order',)
    suit_classes = 'suit-tab suit-tab-contacts'
    extra = 0
    verbose_name_plural = 'email-адреса'


class OfficePhoneInline(admin.TabularInline):
    model = OfficePhone
    fields = ('phone', 'order',)
    suit_classes = 'suit-tab suit-tab-contacts'
    extra = 0
    verbose_name_plural = 'телефоны'


class OfficeSocialLinkInline(admin.TabularInline):
    model = OfficeSocialLink
    fields = ('icon', 'link', 'order',)
    suit_classes = 'suit-tab suit-tab-socials'
    extra = 0
    verbose_name_plural = 'ссылки на соц.сети'


@admin.register(Office)
class OfficeAdmin(ShortTextFieldAdminMixin, SingletonModelAdmin):
    suit_form_tabs = (
        ('default', 'Адрес'),
        ('contacts', 'Контакты'),
        ('socials', 'Соц.сети'),
    )
    fieldsets = (
        ('Офис', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('title',),
        }),
        ('Адрес', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('address', 'address_on_map', 'latitude', 'longitude',),
        }),
        ('Контакты', {
            'classes': ('suit-tab', 'suit-tab-contacts',),
            'fields': ('schedule',),
        }),
    )
    inlines = [OfficeEmailInline, OfficePhoneInline, OfficeSocialLinkInline]


@admin.register(ProductionAddress)
class ProductionAddressAdmin(ShortTextFieldAdminMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name', 'address', 'address_on_map', 'latitude', 'longitude',)
    search_fields = ('name', 'address', 'address_on_map',)
