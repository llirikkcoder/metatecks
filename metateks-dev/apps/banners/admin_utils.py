from django.contrib.admin.filters import SimpleListFilter
from django.contrib import admin, messages
from django.utils import timezone

from django_object_actions import DjangoObjectActions

from .publish_utils import make_banner_published, make_banner_unpublished


class IsPublishedNowFilter(SimpleListFilter):
    """
    Дополнительный фильтр для баннеров в админке
    """
    title = 'Размещены сейчас'
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()

        if self.value() == 'yes':
            return queryset.published()

        if self.value() == 'no':
            return queryset.not_published()


# class BaseBannerAdmin(DjangoObjectActions, admin.ModelAdmin):
class BaseBannerAdmin(admin.ModelAdmin):
    """
    Утилиты для публикации/распубликации
    """
    actions = ['make_qs_published', 'make_qs_unpublished', ]

    def make_qs_published(self, request, queryset):
        for banner in queryset:
            make_banner_published(banner)
        self.message_user(request, 'Опубликовано баннеров: {}'.format(queryset.count()), messages.SUCCESS)
    make_qs_published.short_description = 'Опубликовать'

    def make_qs_unpublished(self, request, queryset):
        for banner in queryset:
            make_banner_unpublished(banner)
        self.message_user(request, 'Снято с публикации баннеров: {}'.format(queryset.count()), messages.SUCCESS)
    make_qs_unpublished.short_description = 'Снять с публикации'

    change_actions = ('make_published', 'make_unpublished',)

    def make_published(self, request, obj):
        try:
            make_banner_published(obj)
        except Exception as e:
            self.message_user(
                request,
                'При публикации баннера "{}" произошла ошибка: {}'.format(obj.__unicode__(), repr(type(e))),
                messages.ERROR,
            )
        else:
            self.message_user(request, 'Баннер "{}" успешно опубликован.'.format(obj.__unicode__()), messages.SUCCESS)
    make_published.label = 'Опубликовать'
    make_published.short_description = 'Опубликовать баннер'

    def make_unpublished(self, request, obj):
        try:
            make_banner_unpublished(obj)
        except Exception as e:
            self.message_user(
                request,
                'При снятии баннера "{}" с публикации произошла ошибка: {}'.format(obj.__unicode__(), repr(type(e))),
                messages.ERROR,
            )
        else:
            self.message_user(request, 'Баннер "{}" был успешно снят с публикации.'.format(obj.__unicode__()), messages.SUCCESS)
    make_unpublished.label = 'Снять с публикации'
    make_unpublished.short_description = 'Снять баннер с публикации'

    def get_change_actions(self, request, object_id, form_url):
        actions = super(BaseBannerAdmin, self).get_change_actions(request, object_id, form_url)
        actions = list(actions)

        obj = self.model.objects.get(pk=object_id)
        if obj.is_published:
            actions.remove('make_published')
        else:
            actions.remove('make_unpublished')
        return actions
