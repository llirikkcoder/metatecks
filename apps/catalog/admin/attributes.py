from django.contrib import admin
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from apps.catalog.models import AttributeUnit, Attribute, AttributeOption, AttributeFilterOption
from apps.utils.admin_mixins import SelectPrefetchRelatedMixin
from apps.utils.common import bool_to_icon


@admin.register(AttributeUnit)
class AttributeUnitAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'name_html', 'icon')
    list_editable = ('name_html', 'icon',)
    search_fields = ('name', 'name_html',)


class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption
    fields = ('value_string', 'value_int', 'value_float', 'order',)
    suit_classes = 'suit-tab suit-tab-options'
    extra = 0
    verbose_name_plural = 'Варианты'


class AttributeFilterOptionInline(admin.TabularInline):
    model = AttributeFilterOption
    fields = ('filter_type', 'value_int', 'value_float', 'value_string', 'order',)
    suit_classes = 'suit-tab suit-tab-filter-options'
    extra = 0
    verbose_name_plural = 'Варианты в фильтре'


@admin.register(Attribute)
class AttributeAdmin(SortableAdminMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = (
        'name', 'attr_type', 'unit', 'unit_str', 'id_site', 'ids_1c',
        'slug', 'name_admin', 'name_short', 'name_filter',
        'with_options', 'with_filter_options',
        'dont_show_in_lists', 'is_synced_with_1c',
    )
    list_display_links = ('name', 'attr_type',)
    list_editable = ('name_admin', 'name_short', 'name_filter', 'slug', 'dont_show_in_lists',)
    list_filter = ('attr_type', 'unit', 'unit_str', 'with_options', 'dont_show_in_lists',)
    suit_list_filter_horizontal = ('attr_type', 'unit', 'unit_str', 'with_options', 'dont_show_in_lists',)
    list_per_page = 200
    suit_form_tabs = (
        ('default', 'Характеристика'),
        ('options', 'Варианты'),
        ('filter-options', 'Варианты в фильтре'),
        ('1с', 'Синхронизация с 1C'),
    )
    fieldsets = (
        ('Характеристика', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': (
                'name', 'name_admin', 'name_short', 'name_filter',
                'slug', 'attr_type', 'unit', 'unit_str',
                'with_options', 'dont_show_in_lists', 'created_at', 'updated_at',
            ),
        }),
        ('Синхронизация с 1C', {
            'classes': ('suit-tab', 'suit-tab-1с',),
            'fields': ('is_synced_with_1c',),
        }),
    )
    inlines = [AttributeOptionInline, AttributeFilterOptionInline]
    readonly_fields = ('created_at', 'updated_at', 'is_synced_with_1c',)
    search_fields = ('name',)
    select_related = ('unit',)

    @admin.display(description='ID на сайте')
    def id_site(self, obj):
        return mark_safe(f'id&nbsp;{obj.id}')

    @admin.display(description='ID в 1C')
    def ids_1c(self, obj):
        ids = obj.cml_properties.all().values_list('id', flat=True)
        return mark_safe(';\r\n'.join(ids))

    @admin.display(description='Варианты в фильтре')
    def with_filter_options(self, obj):
        return bool_to_icon(obj.filter_options.count())
