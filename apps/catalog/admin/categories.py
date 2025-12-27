from django.contrib import admin
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from apps.catalog.models import ExtraProduct, Category, SubCategory
from apps.utils.admin_mixins import ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin
from apps.utils.common import bool_to_icon


class ExtraProductInline(admin.TabularInline):
    model = ExtraProduct
    fields = ('name', 'price', 'is_active', 'order',)
    suit_classes = 'suit-tab suit-tab-extra-products'
    extra = 0


@admin.register(Category)
class CategoryAdmin(ImageThumbnailsAdminMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'cover', 'is_shown', 'is_synced_with_1c', 'has_price_list',)
    list_editable = ('slug',)
    list_filter = ('is_shown', 'is_synced_with_1c',)
    suit_list_filter_horizontal = ('is_shown', 'is_synced_with_1c',)
    suit_form_tabs = (
        ('default', 'Категория'),
        ('seo', 'SEO'),
        ('seo-templates', 'SEO Шаблоны'),
        ('1с', 'Синхронизация с 1C'),
    )
    fieldsets = (
        ('Категория', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'name', 'slug', 'icon', 'cover',),
        }),
        ('Варианты названия', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('name_plural', 'name_single', 'name_product',),
        }),
        ('Прайс-лист', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('price_list',),
        }),
        ('Настройки показа', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('is_shown', 'created_at', 'updated_at',),
        }),
        ('SEO', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1', 'show_instruction',),
        }),
        ('SEO Шаблоны', {
            'classes': ('suit-tab', 'suit-tab-seo-templates',),
            'description': '''
                <div style="padding: 10px; background: #f0f8ff; border-left: 4px solid #4CAF50; margin-bottom: 15px;">
                    <h3 style="margin-top: 0;">Доступные плейсхолдеры:</h3>
                    <ul style="columns: 2;">
                        <li><code>{name}</code> - название объекта</li>
                        <li><code>{category}</code> - название категории</li>
                        <li><code>{category_lower}</code> - категория в нижнем регистре</li>
                        <li><code>{city}</code> - название города</li>
                        <li><code>{city_loct}</code> - город в предложном падеже</li>
                        <li><code>{region}</code> - название региона</li>
                        <li><code>{region_loct}</code> - регион в предложном падеже</li>
                    </ul>
                    <p><strong>Примеры:</strong></p>
                    <ul>
                        <li>Title: <code>{category} в {city_loct} — Метатэкс</code></li>
                        <li>Description: <code>Продажа {category_lower} в {region}. Доставка по {city}</code></li>
                    </ul>
                </div>
            ''',
            'fields': (
                'meta_title_template',
                'meta_desc_template',
                'h1_template',
                'meta_keywords_template',
            ),
        }),
        ('Синхронизация с 1C', {
            'classes': ('suit-tab', 'suit-tab-1с',),
            'fields': ('is_synced_with_1c',),
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'created_at', 'updated_at', 'is_synced_with_1c', 'show_instruction',)
    search_fields = ('name', 'slug', 'name_plural', 'name_single', 'name_product',)

    @admin.display(description='Есть прайс-лист?')
    def has_price_list(self, obj):
        html = bool_to_icon(obj.price_list)
        return mark_safe(html)


@admin.register(SubCategory)
class SubCategoryAdmin(ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ('category', 'name', 'slug', 'photo', 'is_shown', 'is_popular', 'is_synced_with_1c', 'attribute_in_filter',)
    list_display_links = ('category', 'name',)
    list_editable = ('slug', 'attribute_in_filter',)
    list_filter = ('category', 'is_shown', 'is_popular', 'is_synced_with_1c',)
    list_per_page = 100
    suit_list_filter_horizontal = ('category', 'is_shown', 'is_popular', 'is_synced_with_1c',)
    suit_form_tabs = (
        ('default', 'Подкатегория'),
        ('description', 'Описание'),
        ('attributes', 'Характеристики'),
        ('extra-products', 'Дополнительные товары'),
        ('settings', 'Настройки показа'),
        ('seo', 'SEO'),
        ('seo-templates', 'SEO Шаблоны'),
        ('1с', 'Синхронизация с 1C'),
    )
    fieldsets = (
        ('Подкатегория', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'category', 'name', 'slug', 'name_single', 'photo',),
        }),
        ('Описание', {
            'classes': ('suit-tab', 'suit-tab-description',),
            'fields': (
                'purpose', 'description', 'design_features_title',
                'design_features', 'construction_features',
            ),
        }),
        ('Характеристики', {
            'classes': ('suit-tab', 'suit-tab-attributes',),
            # 'fields': ('attributes', 'attributes_in_products', 'attributes_in_filter', 'attributes_table',),
            'fields': ('attribute_in_filter', 'attributes_table',),
        }),
        ('Настройки показа', {
            'classes': ('suit-tab', 'suit-tab-settings',),
            'fields': ('is_shown', 'is_popular', 'created_at', 'updated_at',),
        }),
        ('SEO', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1', 'show_instruction',),
        }),
        ('SEO Шаблоны', {
            'classes': ('suit-tab', 'suit-tab-seo-templates',),
            'description': '''
                <div style="padding: 10px; background: #f0f8ff; border-left: 4px solid #4CAF50; margin-bottom: 15px;">
                    <h3 style="margin-top: 0;">Доступные плейсхолдеры:</h3>
                    <ul style="columns: 2;">
                        <li><code>{name}</code> - название подкатегории</li>
                        <li><code>{subcategory}</code> - название подкатегории</li>
                        <li><code>{subcategory_single}</code> - подкатегория в ед. числе</li>
                        <li><code>{category}</code> - название категории</li>
                        <li><code>{category_lower}</code> - категория в нижнем регистре</li>
                        <li><code>{city}</code>, <code>{city_loct}</code> - геолокация</li>
                        <li><code>{region}</code>, <code>{region_loct}</code> - регион</li>
                    </ul>
                    <p><strong>Примеры:</strong></p>
                    <ul>
                        <li>Title: <code>{subcategory} для {category_lower} — купить в {city_loct}</code></li>
                        <li>H1: <code>{subcategory} для {category_lower}</code></li>
                        <li>Description: <code>{subcategory_single} для {category_lower}. Выбирайте в фильтре свой бренд.</code></li>
                    </ul>
                    <p><em>Если шаблон не заполнен, наследуется от категории.</em></p>
                </div>
            ''',
            'fields': (
                'meta_title_template',
                'meta_desc_template',
                'h1_template',
                'meta_keywords_template',
            ),
        }),
        ('Синхронизация с 1C', {
            'classes': ('suit-tab', 'suit-tab-1с',),
            'fields': ('is_synced_with_1c',),
        }),
    )
    inlines = [ExtraProductInline]
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'created_at', 'updated_at', 'is_synced_with_1c', 'show_instruction',)
    search_fields = ('name', 'slug',)
    select_related = ('category', 'attribute_in_filter',)
