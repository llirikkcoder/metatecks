from functools import update_wrapper

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin
from django_object_actions import DjangoObjectActions

from apps.content.templatetags.base_tags import format_number
from apps.utils.admin_mixins import (
    DontAddOrDeleteMixin, InlineDontDoNothingMixin, SelectPrefetchRelatedMixin,
)
from apps.utils.common import get_error_message
from .models import (
    DeliveryCompany, Order, OrderItem, 
    OrderDeliveryAddressData, OrderContactsData,
    OrderPaymentCardData, OrderPaymentCashlessData,
)


@admin.register(DeliveryCompany)
class DeliveryCompanyAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'logo', 'is_shown',)
    fields = ('name', 'logo', 'is_shown',)
    search_fields = ('name',)


class OrderItemInline(InlineDontDoNothingMixin, admin.StackedInline):
    model = OrderItem
    fields = (
        'item_type', 'item_name', 'show_item_subtitle',
        'show_quantity', 'show_price', 'show_cost', 'warehouse',
    )
    readonly_fields = (
        'show_item_subtitle', 'show_quantity', 'show_price', 'show_cost',
    )
    suit_classes = 'suit-tab suit-tab-items'
    extra = 0
    verbose_name = 'товар'
    verbose_name_plural = 'товары в заказе'

    @admin.display(description='Кол-во')
    def show_quantity(self, obj):
        if not obj:
            return '—'
        return mark_safe(f'{obj.quantity}&nbsp;шт.')

    @admin.display(description='Цена')
    def show_price(self, obj):
        if not obj:
            return '—'
        return mark_safe(f'{format_number(obj.price)}&nbsp;₽')

    @admin.display(description='Стоимость')
    def show_cost(self, obj):
        if not obj:
            return '—'
        return mark_safe(f'{format_number(obj.cost)}&nbsp;₽')


class OrderDeliveryAddressDataInline(InlineDontDoNothingMixin, admin.StackedInline):
    model = OrderDeliveryAddressData
    fields = ('region', 'city', 'address',)
    suit_classes = 'suit-tab suit-tab-delivery'
    extra = 0
    verbose_name = 'адрес доставки'
    verbose_name_plural = 'адрес доставки'


class OrderContactsDataInline(InlineDontDoNothingMixin, admin.StackedInline):
    model = OrderContactsData
    fields = ('first_name', 'patronymic_name', 'last_name', 'phone',)
    suit_classes = 'suit-tab suit-tab-delivery'
    extra = 0
    verbose_name = 'контактные данные'
    verbose_name_plural = 'контактные данные'


class OrderPaymentCardDataInline(InlineDontDoNothingMixin, admin.StackedInline):
    model = OrderPaymentCardData
    fields = ('show_card_number', 'card_name', 'card_expire',)
    readonly_fields = ('show_card_number',)
    suit_classes = 'suit-tab suit-tab-payment'
    extra = 0
    verbose_name = 'данные карты'
    verbose_name_plural = 'данные карты'


class OrderPaymentCashlessDataInline(InlineDontDoNothingMixin, admin.StackedInline):
    model = OrderPaymentCashlessData
    fields = (
        'organization', 'jur_address', 'jur_phone', 'jur_email',
        'inn', 'kpp', 'ogrn', 'account',
        'bank', 'bik', 'director',
    )
    suit_classes = 'suit-tab suit-tab-payment'
    extra = 0
    verbose_name = 'данные безналичной оплаты'
    verbose_name_plural = 'данные безналичной оплаты'


@admin.register(Order)
class OrderAdmin(DjangoObjectActions, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    def make_paid(self, request, obj=None):
        if not request.user.is_superuser:
            raise PermissionDenied
        if obj:
            obj.is_paid = True
            obj.save()
            messages.success(request, f'Заказ № {obj.number} отмечен как оплаченный.')

    def make_canceled(self, request, obj=None):
        if not request.user.is_superuser:
            raise PermissionDenied
        if obj:
            obj.is_canceled = True
            obj.save()
            messages.warning(request, f'Заказ № {obj.number} отменен.')

    make_paid.label = '✅ Заказ оплачен'
    make_canceled.label = '❌ Отменить заказ'

    def get_change_actions(self, request, object_id, form_url):
        actions = super().get_change_actions(request, object_id, form_url)
        actions = list(actions)
        if not request.user.is_superuser:
            return []
        obj = self.model.objects.get(pk=object_id)
        if obj.is_paid:
            actions.remove('make_paid')
        if obj.is_canceled:
            actions.remove('make_canceled')
        return actions

    change_actions = ('make_paid', 'make_canceled',)


    list_display = (
        'show_number',
        'user',
        'status',
        'comment',
        'show_quantity',
        'show_cost',
        'warehouse',
        'delivery_method',
        'show_delivery_company',
        'payment_method',
        'created_at',
        'updated_at',
        'is_paid',
        'paid_at',
        'is_canceled',
        'canceled_at',
    )
    list_display_links = ('show_number', 'user',)
    list_filter = (
        'status',
        'warehouse',
        'delivery_method',
        'delivery_company',
        'payment_method',
        'is_paid',
        'is_canceled',
        'created_at',
        'updated_at',
    )
    suit_list_filter_horizontal = (
        'status',
        'warehouse',
        'delivery_method',
        'delivery_company',
        'payment_method',
        'is_paid',
        'is_canceled',
        'created_at',
        'updated_at',
    )
    suit_form_tabs = (
        ('default', 'Заказ'),
        ('items', 'Товары в заказе'),
        ('delivery', 'Доставка и контакты'),
        ('payment', 'Оплата'),
        ('cancel', 'Отмена заказа'),
        ('sync', 'Синхронизация'),
    )
    fieldsets = (
        ('Заказ', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': (
                'show_number', 'user', 'status',
                'warehouse', 'show_quantity', 'show_cost',
                'comment',
                'created_at', 'updated_at',
            ),
        }),
        ('Доставка и контакты', {
            'classes': ('suit-tab', 'suit-tab-delivery',),
            'fields': ('delivery_method', 'show_delivery_company',),
        }),
        ('Оплата', {
            'classes': ('suit-tab', 'suit-tab-payment',),
            'fields': ('payment_method', 'is_paid', 'paid_at',),
        }),
        ('Отмена заказа', {
            'classes': ('suit-tab', 'suit-tab-cancel',),
            'fields': ('is_canceled', 'is_canceled_by_user', 'canceled_at',),
        }),
        ('Синхронизация', {
            'classes': ('suit-tab', 'suit-tab-sync',),
            'fields': ('is_synced_with_b24',),
        }),
    )
    not_readonly_fields = ('status', 'comment',)
    inlines = [
        OrderItemInline,
        OrderDeliveryAddressDataInline,
        OrderContactsDataInline,
        OrderPaymentCardDataInline,
        OrderPaymentCashlessDataInline,
    ]
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__phone',)
    select_related = ('user', 'delivery_company',)

    def get_readonly_fields(self, request, obj=None):
        not_readonly_fields = self.not_readonly_fields
        if obj and obj.is_canceled:
            try:
                not_readonly_fields = list(not_readonly_fields)
                not_readonly_fields.remove('status')
            except ValueError:
                pass
        return [
            f for x in self.fieldsets for f in x[1]['fields']
            if f not in not_readonly_fields
        ]

    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        return qs.filter(status__gt='')

    @admin.display(description='Номер заказа')
    def show_number(self, obj):
        if not obj:
            return '—'
        return f'№ {obj.number}'

    @admin.display(description='ТК')
    def show_delivery_company(self, obj):
        if not obj:
            return '—'
        return (
            obj.delivery_company if obj.delivery_company
            else obj.delivery_company_name if obj.delivery_company_name
            else '—'
        )

    @admin.display(description='Кол-во товаров')
    def show_quantity(self, obj):
        if not obj:
            return '—'
        return mark_safe(f'{obj.total_quantity}&nbsp;шт.')

    @admin.display(description='Стоимость')
    def show_cost(self, obj):
        if not obj:
            return '—'
        return mark_safe(f'{format_number(obj.total_cost)}&nbsp;₽')
