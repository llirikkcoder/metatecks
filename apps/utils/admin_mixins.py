from django.db import models
from django.forms import TextInput
from django.contrib.admin.widgets import AdminTextareaWidget

from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.widgets import ImageClearableFileInput


class CustomExtraMixin(object):
    related_name = None

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj and getattr(obj, self.related_name).count() else 1


class DontAddMixin(object):

    def has_add_permission(self, request):
        return False


class InlineDontAddMixin(object):
    max_num = 0


class DontEditMixin(object):

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(DontEditMixin, self).get_readonly_fields(request, obj))
        exclude = list(getattr(self, 'exclude', []) or [])
        exclude.extend(getattr(self, 'exclude_readonly', []))
        readonly_fields.extend([f.name for f in self.model._meta.fields if f.name not in exclude])
        return list(set(readonly_fields))


class DontDeleteMixin(object):

    def has_delete_permission(self, request, obj=None):
        return None


class DontAddOrEditMixin(DontAddMixin, DontEditMixin):
    pass


class InlineDontAddOrEditMixin(InlineDontAddMixin, DontEditMixin):
    pass


class DontAddOrDeleteMixin(DontAddMixin, DontDeleteMixin):
    pass


class InlineDontAddOrDeleteMixin(InlineDontAddMixin, DontDeleteMixin):
    pass


class DontDoNothingMixin(DontAddMixin, DontEditMixin, DontDeleteMixin):
    pass


class InlineDontDoNothingMixin(InlineDontAddMixin, DontEditMixin, DontDeleteMixin):
    pass


class SelectPrefetchRelatedMixin(object):

    def _update_qs_with_related(self, qs):
        select_related = getattr(self, 'select_related', []) or []
        prefetch_related = getattr(self, 'prefetch_related', []) or []
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)
        return qs

    def get_queryset(self, request, *args, **kwargs):
        qs = super(SelectPrefetchRelatedMixin, self).get_queryset(request, *args, **kwargs)
        qs = self._update_qs_with_related(qs)
        return qs


class DifferentAddChangeAdminMixin(object):
    """
    FROM: django.contrib.auth.admin.UserAdmin
    """
    IS_POPUP_VAR = '_popup'

    def response_add(self, request, obj, post_url_continue=None):
        if '_addanother' not in request.POST and self.IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj,
                                                                      post_url_continue)

    def get_fields(self, request, obj=None):
        if obj is None and getattr(self, 'add_fields', None):
            return self.add_fields
        return super().get_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if obj is None and getattr(self, 'add_fieldsets', None):
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None and getattr(self, 'add_form', None):
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_readonly_fields(self, request, obj=None):
        if obj is None and getattr(self, 'add_readonly_fields', None) is not None:
            return self.add_readonly_fields
        return super().get_readonly_fields(request, obj)

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


class ImageThumbnailsAdminMixin(object):
    # TODO: fix
    # 1) ошибка при отсутствии изображения на сервере
    # 2) ошибка при кириллице в имени файла
    pass
    # formfield_overrides = {ThumbnailerImageField: {'widget': ImageClearableFileInput},}


class CompactTextFieldAdminMixin(object):
    formfield_overrides = {models.TextField: {'widget': TextInput(attrs={'size': '40'})},}


class ShortTextFieldAdminMixin(object):
    formfield_overrides = {
        models.TextField: {
            'widget': AdminTextareaWidget(attrs={'cols': '40', 'rows': '4', 'class': 'vLargeTextField'}),
        },
    }


class SlowListEditableMixin(object):

    def get_slow_list_editable(self):
        return []

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        FROM: https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/#use-annotations-if-possible-for-function-entries-list-display-instead-of-making-additional-queries
        Сокращаем кол-во запросов к базе
        """
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        _slow_fields = self.get_slow_list_editable()
        if db_field.name in _slow_fields:
            cache_key = f'_{db_field.name}_choices_cache'
            choices = getattr(request, cache_key, None)
            if choices is None:
                choices = list(formfield.choices)
                setattr(request, cache_key, choices)
            formfield.choices = choices
        return formfield


# def MetatagModelAdmin(cls=None):

#     def decorator(cls):
#         cls.fieldsets += (
#             ('SEO', {
#                 'classes': ('collapse',),
#                 'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1', 'seo_text',)
#             }),
#         )
#         cls.search_fields += ['meta_title', 'meta_description', 'meta_keywords', 'h1', 'seo_text',]
#         return cls

#     if cls is None:
#         return decorator
#     else:
#         return decorator(cls)
