from django.contrib import admin
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from apps.utils.admin_mixins import ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin
from .models import MediaTag, MediaVideo, MediaPhoto, MediaFile


@admin.register(MediaTag)
class MediaTagAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug',)
    list_editable = ('slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug',)


@admin.register(MediaVideo)
class MediaVideoAdmin(SortableAdminMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = (
        'id', 'title', 'video', 'is_published', 'show_tags',
        'published_at', 'created_at', 'updated_at',
    )
    list_display_links = ('id', 'title',)
    list_editable = ('is_published',)
    list_filter = ('tags', 'is_published', 'published_at',)
    suit_list_filter_horizontal = ('tags', 'is_published', 'published_at',)
    suit_form_tabs = (
        ('default', 'Видео'),
        ('publication', 'Публикация'),
    )
    fieldsets = (
        ('Видео', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'title', 'video', 'tags',),
        }),
        ('Публикация', {
            'classes': ('suit-tab', 'suit-tab-publication',),
            'fields': ('is_published', 'published_at', 'created_at', 'updated_at',),
        }),
    )
    filter_vertical = ('tags',)
    readonly_fields = ('id', 'created_at', 'updated_at',)
    search_fields = ('title',)
    prefetch_related = ('tags',)


@admin.register(MediaPhoto)
class MediaPhotoAdmin(SortableAdminMixin, ImageThumbnailsAdminMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = (
        'id', 'title', 'show_photo', 'is_published', 'show_tags',
        'published_at', 'created_at', 'updated_at',
    )
    list_display_links = ('id', 'title',)
    list_editable = ('is_published',)
    list_filter = ('tags', 'is_published', 'published_at',)
    suit_list_filter_horizontal = ('tags', 'is_published', 'published_at',)
    suit_form_tabs = (
        ('default', 'Фото'),
        ('publication', 'Публикация'),
    )
    fieldsets = (
        ('Фото', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'title', 'photo', 'tags',),
        }),
        ('Публикация', {
            'classes': ('suit-tab', 'suit-tab-publication',),
            'fields': ('is_published', 'published_at', 'created_at', 'updated_at',),
        }),
    )
    filter_vertical = ('tags',)
    readonly_fields = ('id', 'created_at', 'updated_at',)
    search_fields = ('title',)
    prefetch_related = ('tags',)

    @admin.display(description='Фото')
    def show_photo(self, obj):
        html = f'<a href="{obj.photo_big_url}" target="_blank"><img src="{obj.photo_admin_url}"></a>'
        return mark_safe(html)



@admin.register(MediaFile)
class MediaFileAdmin(SortableAdminMixin, SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = (
        'id', 'title', 'file', 'is_published', 'show_tags',
        'published_at', 'created_at', 'updated_at',
    )
    list_display_links = ('id', 'title',)
    list_editable = ('is_published',)
    list_filter = ('tags', 'is_published', 'published_at',)
    suit_list_filter_horizontal = ('tags', 'is_published', 'published_at',)
    suit_form_tabs = (
        ('default', 'Файл'),
        ('publication', 'Публикация'),
    )
    fieldsets = (
        ('Файл', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'title', 'file', 'tags',),
        }),
        ('Публикация', {
            'classes': ('suit-tab', 'suit-tab-publication',),
            'fields': ('is_published', 'published_at', 'created_at', 'updated_at',),
        }),
    )
    filter_vertical = ('tags',)
    readonly_fields = ('id', 'created_at', 'updated_at',)
    search_fields = ('title',)
    prefetch_related = ('tags',)
