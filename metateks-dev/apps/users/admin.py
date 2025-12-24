from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from apps.utils.admin_mixins import ImageThumbnailsAdminMixin
from .admin_forms import UserCreationForm, UserChangeForm
from .models import User


admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(ImageThumbnailsAdminMixin, UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        'id', 'first_name', 'last_name', 'email', 'date_joined', 'is_active', 'is_admin', 'is_superuser',
    )
    list_display_links = ('id', 'first_name', 'last_name', 'email',)
    list_filter = ('is_active', 'is_admin', 'is_superuser',)
    suit_list_filter_horizontal = ('is_active', 'is_admin', 'is_superuser',)
    suit_form_tabs = (
        ('default', 'Пользователь'),
        ('permissions', 'Доступы к админ.панели'),
    )
    fieldsets = (
        ('Пользователь', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'email', 'is_active', 'date_joined',),
        }),
        ('Контакты', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('first_name', 'patronymic_name', 'last_name', 'phone', 'avatar',),
        }),
        ('Общие доступы', {
            'classes': ('suit-tab suit-tab-permissions',),
            'fields': ('is_admin', 'is_superuser',),
        }),
        ('Доступы к таблицам', {
            'classes': ('suit-tab suit-tab-permissions',),
            'fields': ('user_permissions',),
        }),
    )
    add_fieldsets = (
        ('Пользователь', {
            'fields': ('email', 'first_name', 'last_name', 'is_active',)
        }),
        ('Доступы', {
            'fields': ('is_admin', 'is_superuser', 'password', 'password_repeat',)
        }),
    )
    readonly_fields = ('id', 'date_joined',)
    search_fields = ('email', 'first_name', 'patronymic_name', 'last_name', 'phone',)
    ordering = ('id',)
