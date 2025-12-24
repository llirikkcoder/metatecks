from django.contrib import admin
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from apps.content.models import NewsCategory, News
from apps.utils.admin_mixins import ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin


@admin.register(NewsCategory)
class NewsCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_shown',)
    list_editable = ('slug', 'is_shown',)
    suit_form_tabs = (
        ('default', 'Раздел'),
    )
    fieldsets = (
        ('Раздел', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('name', 'slug', 'is_shown',),
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug',)


@admin.register(News)
class NewsAdmin(ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = (
        'id', 'title', 'slug', 'show_cover', 'short_description', 'is_published', 'show_categories',
        'published_at', 'created_at', 'updated_at',
    )
    list_display_links = ('id', 'title',)
    list_editable = ('slug', 'is_published',)
    list_filter = ('categories', 'is_published', 'published_at',)
    suit_list_filter_horizontal = ('categories', 'is_published', 'published_at',)
    suit_form_tabs = (
        ('default', 'Новость'),
        ('publication', 'Публикация'),
        ('seo', 'SEO'),
    )
    fieldsets = (
        ('Новость', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'title', 'slug', 'cover', 'short_description', 'categories', 'text',),
        }),
        ('Публикация', {
            'classes': ('suit-tab', 'suit-tab-publication',),
            'fields': ('is_published', 'published_at', 'created_at', 'updated_at',),
        }),
        ('SEO', {
            'classes': ('suit-tab', 'suit-tab-seo',),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1', 'show_instruction',),
        }),
    )
    # prepopulated_fields = {'slug': ('title',)}
    filter_vertical = ('categories',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'show_instruction',)
    search_fields = ('title', 'slug', 'text',)
    prefetch_related = ('categories',)

    @admin.display(description='Обложка')
    def show_cover(self, obj):
        if obj.cover:
            html = f'<a href="{obj.cover_url}" target="_blank"><img src="{obj.cover_admin_url}"></a>'
            return mark_safe(html)
        return ''
