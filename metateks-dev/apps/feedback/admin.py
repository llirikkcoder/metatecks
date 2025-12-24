from django.contrib import admin

from apps.utils.admin_mixins import SelectPrefetchRelatedMixin
from .models import CallbackRequest


@admin.register(CallbackRequest)
class CallbackRequestAdmin(SelectPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = ('id', 'created_at', 'name', 'phone', 'user', 'ip_address', 'is_synced_with_b24',)
    list_display_links = ('id', 'created_at', 'name', 'phone',)
    list_filter = ('is_synced_with_b24',)
    suit_list_filter_horizontal = ('is_synced_with_b24',)
    fields = ('id', 'created_at', 'name', 'phone', 'user', 'ip_address', 'is_synced_with_b24',)
    readonly_fields = ('id', 'created_at', 'is_synced_with_b24',)
    search_fields = (
        'name', 'phone', 'ip_address', 'profile__email',
        'profile__first_name', 'profile__patronymic_name', 'profile__last_name',
    )
    select_related = ('user',)
