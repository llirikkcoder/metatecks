from django.contrib.admin.utils import quote
from django.db import models
from django.urls import reverse

from tinymce.models import HTMLField

from apps.settings.models import Settings
from apps.utils.common import absolute, bool_to_icon
from apps.utils.manager import IsPublishedQueryset, IsPublishedManager
from apps.utils.seo import SEO_INSTRUCTION, seo_replace


class IsPublishedModel(models.Model):
    objects = IsPublishedManager.from_queryset(IsPublishedQueryset)()

    class Meta:
        abstract = True


class SearchResultModelMixin(object):

    @property
    def search_result_title(self):
        return self.__str__()


class DatesBaseModel(models.Model):
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        abstract = True

    @property
    def add_dt(self):
        return self.created_at

    @property
    def added_at(self):
        return self.created_at

    @property
    def create_dt(self):
        return self.created_at

    @property
    def update_dt(self):
        return self.updated_at

    @property
    def created_at_str(self):
        return (
            self.created_at.strftime('%d.%m.%Y') if self.created_at else '-'
        )

    @property
    def created_at_str_full(self):
        return (
            self.created_at.strftime('%d.%m.%Y %H:%M') if self.created_at else '-'
        )

    @property
    def add_datetime_str(self):
        return (
            self.created_at.strftime('%d.%m.%Y %H:%M') if self.created_at else '-'
        )

    @property
    def add_datetime_str2(self):
        return (
            self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '-'
        )

    @property
    def updated_at_str(self):
        return (
            self.updated_at.strftime('%d.%m.%Y') if self.updated_at else '-'
        )

    @property
    def update_datetime_str(self):
        return (
            self.updated_at.strftime('%d.%m.%Y %H:%M') if self.updated_at else '-'
        )


class AdminURLMixin(object):

    @property
    def opts(self):
        return self.__class__._meta

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self.opts.app_label, model_name), args=(quote(self.pk),))

    @property
    def admin_url(self):
        return self.get_admin_url()

    @property
    def absolute_admin_url(self):
        return absolute(self.admin_url)


class MetatagModel(models.Model):
    meta_title = models.CharField(
        'Meta title (заголовок страницы)',
        max_length=255, blank=True,
        help_text='Оставьте пустым, чтобы использовать название объекта',
    )
    meta_description = models.CharField(
        'Meta description (описание страницы)',
        max_length=255, blank=True,
        help_text='Оставьте пустым, чтобы использовать название объекта',
    )
    meta_keywords = models.CharField(
        'Meta keywords (ключевые слова через запятую)',
        max_length=255, blank=True,
        help_text='Оставьте пустым, чтобы использовать название объекта',
    )
    h1 = models.TextField(
        'Заголовок H1',
        max_length=255, blank=True, default='',
        help_text='Оставьте пустым, чтобы использовать название объекта',
    )
    seo_text = HTMLField('SEO-текст', blank=True)

    class Meta:
        abstract = True

    # методы для переопределения в классах

    def get_title(self):
        return self.title

    def get_h1_title(self):
        return self.get_title()

    # seo-методы

    def _get_meta_title(self):
        meta_title = self.meta_title
        if meta_title:
            return meta_title
        title_suffix = Settings.get_seo_title_suffix()
        return '{} — {}'.format(self.get_title(), title_suffix)

    def get_meta_title(self):
        return seo_replace(self._get_meta_title())

    def get_meta_desc(self):
        return seo_replace(self.meta_description or self.get_title())

    def get_meta_keyw(self):
        return seo_replace(self.meta_keywords or self.get_title())

    def get_h1(self):
        return seo_replace(self.h1 or self.get_h1_title())

    # админка

    def has_seo_text(self):
        return bool_to_icon(self.seo_text)
    has_seo_text.allow_tags = True
    has_seo_text.short_description = 'Есть SEO-текст?'

    def show_instruction(self):
        return SEO_INSTRUCTION
    show_instruction.allow_tags = True
    show_instruction.short_description = 'Инструкция'
