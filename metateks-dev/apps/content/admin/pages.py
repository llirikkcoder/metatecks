from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.content.models import Page
from apps.utils.admin_mixins import ImageThumbnailsAdminMixin


@admin.register(Page)
class PageAdmin(ImageThumbnailsAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'show_cover', 'created_at', 'updated_at',)
    list_editable = ('slug',)
    suit_form_tabs = (
        ('default', 'Страница'),
        ('seo', 'SEO'),
    )
    fieldsets = (
        ('Страница', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('title', 'slug', 'cover', 'description', 'text', 'created_at', 'updated_at',),
        }),
        ('SEO', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1', 'show_instruction',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'show_instruction',)
    search_fields = ('title', 'slug', 'text',)

    @admin.display(description='Обложка')
    def show_cover(self, obj):
        if obj.cover:
            html = f'<a href="{obj.cover_url}" target="_blank"><img src="{obj.cover_admin_url}"></a>'
            return mark_safe(html)
        return ''
