from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from apps.catalog.models import Brand
from apps.utils.admin_mixins import ImageThumbnailsAdminMixin


@admin.register(Brand)
class BrandAdmin(ImageThumbnailsAdminMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'logo', 'photo', 'created_at', 'updated_at',)
    list_display_links = ('id', 'name',)
    list_editable = ('slug',)
    list_per_page = 100
    suit_form_tabs = (
        ('default', 'Бренд'),
        ('texts', 'Тексты на странице'),
        ('seo', 'SEO'),
    )
    fieldsets = (
        ('Бренд', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'name', 'slug', 'logo', 'photo', 'created_at', 'updated_at',),
        }),
        ('Тексты', {
            'classes': ('suit-tab', 'suit-tab-texts',),
            'fields': ('description', 'text',),
        }),
        ('SEO', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1', 'show_instruction',),
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'created_at', 'updated_at', 'show_instruction',)
    search_fields = ('name', 'slug',)
