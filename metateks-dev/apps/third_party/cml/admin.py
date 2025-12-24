from django.db.models import Sum
from django.contrib import admin
from django.utils.safestring import mark_safe

from treenode.admin import TreeNodeModelAdmin
from treenode.forms import TreeNodeForm

from apps.utils.admin_mixins import (
    DontAddOrEditMixin, DontDoNothingMixin, SelectPrefetchRelatedMixin, SlowListEditableMixin
)
from apps.utils.common import bool_to_icon
from .models import (
    Exchange, ExchangeParsing,
    ImportedGroup, ImportedProperty, ImportedBrand,
    ImportedProduct, ImportedWarehouse, ImportedStockBalance,
)


# @admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):

    list_display = ('exchange_type', 'timestamp', 'user', 'filename')
    readonly_fields = ('exchange_type', 'timestamp', 'user', 'filename')

    def has_add_permission(self, request):
        return False


@admin.register(ExchangeParsing)
class ExchangeParsingAdmin(DontAddOrEditMixin, admin.ModelAdmin):
    list_display = (
        'id', 'created_at', 'show_is_full',
        'import_filename', 'offers_filename',
        'import_was_imported', 'import_imported_at',
        'offers_was_imported', 'offers_imported_at',
        'was_synced', 'synced_at',
    )
    list_display_links = ('id', 'created_at',)
    list_filter = ('is_full', 'was_synced',)

    @admin.display(description='Is full')
    def show_is_full(self, obj):
        return bool_to_icon(obj.is_full) if obj.is_full else ''


@admin.register(ImportedGroup)
class ImportedGroupAdmin(DontDoNothingMixin, SlowListEditableMixin, SelectPrefetchRelatedMixin, TreeNodeModelAdmin):

    def get_slow_list_editable(self):
        return (
            'category_obj',
            'subcategory_obj',
        )

    treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_BREADCRUMBS
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_ACCORDION
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_INDENTATION
    list_display = (
        'name',
        'do_not_sync',
        'category_obj',
        'subcategory_obj',
        'id',
        # 'is_new',
        # 'has_changed',
        # 'has_removed',
        # 'fields_changed',
        'tn_priority',
    )
    list_display_links = None
    list_editable = (
        'do_not_sync',
        'category_obj',
        'subcategory_obj',
        'tn_priority',
    )
    list_filter = ('parent',)
    suit_list_filter_horizontal = ('parent',)
    form = TreeNodeForm
    select_related = (
        'category_obj', 'subcategory_obj',
        'parent', 'tn_parent',
    )
    search_fields = ('name', 'id',)


@admin.register(ImportedProperty)
class ImportedPropertyAdmin(DontDoNothingMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = (
        'name',
        'name_clean',
        'unit_name',
        'value_type',
        'dont_show_in_lists',
        'do_not_sync',
        'variants_count',
        'show_attribute_obj',
        'id',
    )
    list_display_links = None
    list_editable = (
        'name_clean',
        'unit_name',
        'dont_show_in_lists',
        'do_not_sync',
    )
    list_filter = ('value_type', 'dont_show_in_lists', 'do_not_sync',)
    suit_list_filter_horizontal = ('value_type', 'dont_show_in_lists', 'do_not_sync',)
    list_per_page = 200
    select_related = ('attribute_obj',)
    prefetch_related = ('variants',)
    search_fields = ('name', 'id',)
    ordering = ['name']

    @admin.display(description='Кол-во вариантов')
    def variants_count(self, obj):
        count = obj.variants.count()
        return count or '-'

    @admin.display(description='Характеристика (сайт)')
    def show_attribute_obj(self, obj):
        attr = obj.attribute_obj
        return mark_safe(attr.__str__()) if attr else '-'


@admin.register(ImportedBrand)
class ImportedBrandAdmin(DontDoNothingMixin, admin.ModelAdmin):
    list_display = (
        'name',
        'name_clean',
        'is_name_good',
        'is_name_partial',
        'is_name_bad',
        'do_not_sync',
        'brand_obj',
    )
    list_display_links = None
    list_editable = (
        'name_clean',
        'is_name_good',
        'is_name_partial',
        'is_name_bad',
        'do_not_sync',
        'brand_obj',
    )
    list_filter = (
        'is_name_good',
        'is_name_partial',
        'is_name_bad',
        'do_not_sync',
    )
    suit_list_filter_horizontal = (
        'is_name_good',
        'is_name_partial',
        'is_name_bad',
        'do_not_sync',
    )
    list_per_page = 200
    search_fields = ('name', 'name_clean',)
    ordering = ['name']


@admin.register(ImportedWarehouse)
class ImportedWarehouseAdmin(DontDoNothingMixin, admin.ModelAdmin):
    list_display = (
        'name',
        'address',
        'phone',
        'warehouse_obj',
        'warehouse_address',
        'warehouse_phone',
        'products_count',
        'id',
    )
    list_display_links = None
    list_editable = (
        'warehouse_obj',
    )
    search_fields = ('id', 'name', 'address', 'phone',)
    ordering = ['name']

    @admin.display(description='Кол-во товара')
    def products_count(self, obj):
        qs = ImportedProduct.objects.filter(group__do_not_sync=False)
        product_ids = qs.values_list('id', flat=True)
        balance_qs = ImportedStockBalance.objects.filter(warehouse_id=obj.id, product_id__in=product_ids)
        return balance_qs.aggregate(count=Sum('number'))['count'] or 0

    @admin.display(description='Склад: адрес')
    def warehouse_address(self, obj):
        return mark_safe(obj.warehouse_obj.address) if obj.warehouse_obj else '-'

    @admin.display(description='Склад: телефон')
    def warehouse_phone(self, obj):
        return mark_safe(obj.warehouse_obj.phone) if obj.warehouse_obj else '-'
