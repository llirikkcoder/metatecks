import copy

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from apps.catalog.admin_forms import ProductModelForm, ProductForm
from apps.catalog.models import ProductModel, Product, ProductPhoto, ProductVideo, ProductStockBalance, ProductProperty
from apps.catalog.models.categories import Category, SubCategory
from apps.utils.admin_mixins import (
    ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin, ShortTextFieldAdminMixin, DontDoNothingMixin
)
from apps.utils.common import get_admin_url


class SubCategoryRelatedFilter(SimpleListFilter):
    """
    МТ-13: При выборе категории показываем только подкатегории этой категории.
    """
    title = 'Подкатегория'
    parameter_name = 'sub_category'

    def lookups(self, request, model_admin):
        category_id = request.GET.get('category__id__exact') or request.GET.get('category')
        qs = SubCategory.objects.select_related('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        return [(sc.pk, str(sc)) for sc in qs.order_by('category__order', 'order')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sub_category_id=self.value())
        return queryset


class ModelRelatedFilter(SimpleListFilter):
    """
    МТ-13: При выборе подкатегории показываем только модели этой подкатегории.
    """
    title = 'Модель'
    parameter_name = 'model'

    def lookups(self, request, model_admin):
        from apps.catalog.models import ProductModel
        sub_category_id = request.GET.get('sub_category')
        category_id = request.GET.get('category__id__exact') or request.GET.get('category')
        qs = ProductModel.objects.select_related('sub_category')
        if sub_category_id:
            qs = qs.filter(sub_category_id=sub_category_id)
        elif category_id:
            qs = qs.filter(category_id=category_id)
        return [(m.pk, m.name) for m in qs.order_by('name')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(model_id=self.value())
        return queryset


def make_visible(modeladmin, request, queryset):
    """Массовое включение отображения товаров"""
    updated = queryset.update(is_shown=True)
    modeladmin.message_user(request, f'Включено отображение для {updated} товара(ов)')


make_visible.short_description = 'Включить отображение'


def make_hidden(modeladmin, request, queryset):
    """Массовое отключение отображения товаров"""
    updated = queryset.update(is_shown=False)
    modeladmin.message_user(request, f'Отключено отображение для {updated} товара(ов)')


make_hidden.short_description = 'Отключить отображение'


class ProductPhotoInline(ImageThumbnailsAdminMixin, admin.TabularInline):
    model = ProductPhoto
    fields = ('photo', 'is_shown', 'show_on_subcategory', 'order',)
    suit_classes = 'suit-tab suit-tab-media'
    extra = 0
    verbose_name_plural = 'фото'


class ProductVideoInline(ShortTextFieldAdminMixin, admin.TabularInline):
    model = ProductVideo
    fields = ('video', 'description', 'is_shown', 'show_on_subcategory', 'order',)
    suit_classes = 'suit-tab suit-tab-media'
    extra = 0
    verbose_name_plural = 'видео'


# class ProductPropertyInline(admin.TabularInline):
#     model = ProductProperty
#     fields = ('name', 'value', 'order',)
#     suit_classes = 'suit-tab suit-tab-1c'
#     extra = 0
#     verbose_name_plural = 'реквизиты'


@admin.register(ProductModel)
class ProductModelAdmin(
    ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin, SortableAdminMixin, ShortTextFieldAdminMixin, admin.ModelAdmin
):
    list_display = (
        'name', 'category', 'sub_category', 'photo', 'price', 'is_shown', 'is_popular', 'is_synced_with_1c',
    )
    list_filter = ('category', SubCategoryRelatedFilter, 'is_shown', 'is_popular', 'is_synced_with_1c',)
    list_per_page = 100
    actions = [make_visible, make_hidden, 'delete_selected']
    suit_list_filter_horizontal = (
        'category', 'sub_category', 'is_shown', 'is_popular', 'is_synced_with_1c',
    )
    suit_form_tabs = (
        ('default', 'Модель'),
        ('galleries', 'Фото- и 3D-галереи'),
        ('media', 'Медиа-файлы'),
        ('attributes', 'Характеристики'),
        ('settings', 'Настройки показа'),
        ('seo', 'SEO'),
        ('seo-templates', 'SEO Шаблоны'),
        ('1с', 'Данные из 1C'),
    )
    form = ProductModelForm
    fieldsets = (
        ('Модель', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'name', 'category', 'sub_category', 'photo', 'price',),
        }),
        ('Описание', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('description', 'tech_description',),
        }),
        ('Фото- и 3D-галереи', {
            'classes': ('suit-tab', 'suit-tab-galleries',),
            'fields': ('gallery', 'gallery_3d',),
        }),
        ('Характеристики', {
            'classes': ('suit-tab', 'suit-tab-attributes',),
            'fields': ('attrs_empty',),
        }),
        ('Настройки показа', {
            'classes': ('suit-tab', 'suit-tab-settings',),
            'fields': ('is_shown', 'is_popular', 'created_at', 'updated_at',),
        }),
        ('SEO (явные значения)', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'description': '''
                <p style="background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">
                    <strong>Внимание:</strong> Если заполните поля ниже, они будут использоваться вместо шаблонов.
                    <br>Для массового управления используйте вкладку "SEO Шаблоны".
                </p>
            ''',
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
                'h1',
                'seo_text',
                'show_instruction',
            ),
        }),
        ('SEO Шаблоны (автогенерация)', {
            'classes': ('suit-tab', 'suit-tab-seo-templates',),
            'description': '''
                <div style="padding: 10px; background: #f0f8ff; border-left: 4px solid #4CAF50; margin-bottom: 15px;">
                    <h3 style="margin-top: 0;">Доступные плейсхолдеры:</h3>
                    <ul style="columns: 2;">
                        <li><code>{name}</code> - название модели</li>
                        <li><code>{vendor_code}</code> - артикул</li>
                        <li><code>{price}</code> - цена (число)</li>
                        <li><code>{price_formatted}</code> - цена форматированная</li>
                        <li><code>{category}</code> - название категории</li>
                        <li><code>{subcategory}</code> - название подкатегории</li>
                        <li><code>{attr:название}</code> - значение атрибута</li>
                        <li><code>{city}</code>, <code>{city_loct}</code> - геолокация</li>
                    </ul>
                    <p><strong>Примеры атрибутов:</strong></p>
                    <ul>
                        <li><code>{attr:грузоподъемность}</code> - по имени</li>
                        <li><code>{attr:load_capacity}</code> - по slug</li>
                    </ul>
                    <p><strong>Примеры шаблонов:</strong></p>
                    <ul>
                        <li>Title: <code>{name} - купить в {city_loct} — Метатэкс</code></li>
                        <li>Description: <code>Продажа {name}. Цена: {price_formatted}. Артикул: {vendor_code}</code></li>
                    </ul>
                    <p><em>Если не заполнено, наследуется от подкатегории или категории.</em></p>
                </div>
            ''',
            'fields': (
                'meta_title_template',
                'meta_desc_template',
                'h1_template',
                'meta_keywords_template',
            ),
        }),
        ('Данные из 1C', {
            'classes': ('suit-tab', 'suit-tab-1с',),
            'fields': ('is_synced_with_1c', 'bar_code', 'vendor_code',),
        }),
    )
    inlines = [ProductPhotoInline, ProductVideoInline]
    readonly_fields = ('id', 'created_at', 'updated_at', 'attrs_empty', 'is_synced_with_1c', 'bar_code', 'vendor_code', 'show_instruction',)
    search_fields = ('name',)
    select_related = ('category', 'sub_category',)

    @admin.display(description='Характеристики модели')
    def attrs_empty(self, obj):
        if not obj:
            return '—'
        _sub_category = obj.sub_category
        _link = f'<a href="{get_admin_url(_sub_category)}#attributes" target="_blank">подкатегории</a>'
        return mark_safe(f'Сначала заполните поле "характеристики" у {_link} модели')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets = copy.deepcopy(fieldsets)
        fieldsets = list(fieldsets)

        if not obj:
            fieldsets[3][1]['fields'] = ['attrs_empty']
            return fieldsets

        # # получаем список атрибутов у подкатегории модели
        # sub_category = obj.sub_category
        # attrs = sub_category.attributes.all()

        # если они есть, добавляем их во вкладку вместо поля "attrs_empty"
        # (+ обновляем form.declared_fields, чтобы не вызывать ошибку FieldError)
        # if sub_category.attributes.count():
        if obj and obj.attrs:
            # fields_dict = sub_category.get_attrs_fields()
            fields_dict = obj.get_attrs_fields()

            fields = list(fields_dict.keys())
            fieldsets[3][1]['fields'] = fields

            # FROM: https://stackoverflow.com/a/62719818
            self.form.declared_fields = {}
            for name, field in fields_dict.items():
                self.form.declared_fields.update({name: field})

        # иначе - возвращаем attrs_empty
        else:
            fieldsets[3][1]['fields'] = ['attrs_empty']

        return fieldsets


class ProductStockBalanceInline(admin.TabularInline):
    model = ProductStockBalance
    fields = ('warehouse', 'number',)
    suit_classes = 'suit-tab suit-tab-stock-balance'
    extra = 0
    verbose_name_plural = 'количество на складе'


@admin.register(Product)
class ProductAdmin(
    ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin, SortableAdminMixin, ShortTextFieldAdminMixin, admin.ModelAdmin
):
    list_display = (
        'name', 'category', 'sub_category', 'model', 'brand', 'brand_name', 'photo', 'is_shown', 'is_popular', 'is_synced_with_1c',
    )
    list_filter = (
        'category', SubCategoryRelatedFilter, ModelRelatedFilter, 'brand', 'brand_name', 'is_shown', 'is_popular', 'is_synced_with_1c',
    )
    list_per_page = 100
    actions = [make_visible, make_hidden, 'delete_selected']
    suit_list_filter_horizontal = (
        'category', 'sub_category', 'model', 'brand', 'brand_name', 'is_shown', 'is_popular', 'is_synced_with_1c',
    )
    suit_form_tabs = (
        ('default', 'Товар'),
        ('galleries', 'Фото- и 3D-галереи'),
        ('stock-balance', 'Количество на складе'),
        ('settings', 'Настройки показа'),
        ('1с', 'Данные из 1C'),
        ('seo', 'SEO'),
    )
    form = ProductForm
    fieldsets = (
        ('Товар', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'name', 'slug', 'category', 'sub_category', 'model', 'brand', 'brand_name', 'photo',),
        }),
        ('Фото- и 3D-галереи', {
            'classes': ('suit-tab', 'suit-tab-galleries',),
            'fields': ('gallery', 'gallery_3d',),
        }),
        ('Настройки показа', {
            'classes': ('suit-tab', 'suit-tab-settings',),
            'fields': ('is_shown', 'is_popular', 'created_at', 'updated_at',),
        }),
        ('SEO', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1', 'show_instruction',),
        }),
        ('Данные из 1C', {
            'classes': ('suit-tab', 'suit-tab-1с',),
            'fields': ('is_synced_with_1c', 'bar_code', 'vendor_code',),
        }),
    )
    inlines = [ProductStockBalanceInline]
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = (
        'id', 'brand_name', 'created_at', 'updated_at',
        'is_synced_with_1c', 'bar_code', 'vendor_code',
        'show_instruction',
    )
    search_fields = ('name', 'slug',)
    select_related = ('category', 'sub_category', 'model', 'brand',)


@admin.register(ProductPhoto)
class ProductPhotoAdmin(DontDoNothingMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = ('model', 'sub_category', 'show_photo', 'is_shown', 'show_on_subcategory', 'created_at', 'updated_at',)
    list_display_links = None
    list_editable = ('is_shown', 'show_on_subcategory',)
    list_filter = (
        'model', 'model__sub_category', 'model__category', 'is_shown', 'show_on_subcategory', 'created_at', 'updated_at',
    )
    suit_list_filter_horizontal = (
        'model', 'model__sub_category', 'model__category', 'is_shown', 'show_on_subcategory', 'created_at', 'updated_at',
    )
    list_per_page = 100
    search_fields = ('product__name', 'model__sub_category__name', 'model__category__name',)
    select_related = ('model', 'model__sub_category', 'model__category',)

    @admin.display(description='Подкатегория')
    def sub_category(self, obj):
        return obj.model.sub_category.__str__()

    @admin.display(description='Фото')
    def show_photo(self, obj):
        html = f'<a href="{obj.photo_big_url}" target="_blank"><img src="{obj.photo_admin_url}"></a>'
        return mark_safe(html)


@admin.register(ProductVideo)
class ProductVideoAdmin(DontDoNothingMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = (
        'model', 'sub_category', 'video', 'description', 'is_shown', 'show_on_subcategory', 'created_at', 'updated_at',
    )
    list_display_links = None
    list_editable = ('is_shown', 'show_on_subcategory',)
    list_filter = (
        'model', 'model__sub_category', 'model__category', 'is_shown', 'show_on_subcategory', 'created_at', 'updated_at',
    )
    suit_list_filter_horizontal = (
        'model', 'model__sub_category', 'model__category', 'is_shown', 'show_on_subcategory', 'created_at', 'updated_at',
    )
    list_per_page = 100
    search_fields = ('video', 'description', 'product__name', 'model__sub_category__name', 'model__category__name',)
    select_related = ('model', 'model__sub_category', 'model__category',)

    @admin.display(description='Подкатегория')
    def sub_category(self, obj):
        return obj.model.sub_category.__str__()
