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

    # методы для работы с шаблонами

    def get_template_field(self, field_name: str):
        """
        Получение шаблона с учетом наследования

        Args:
            field_name: имя поля ('meta_title_template', 'meta_desc_template' и т.д.)

        Returns:
            Шаблон или None
        """
        # 1. Проверяем собственный шаблон
        template = getattr(self, field_name, None)
        if template:
            return template

        # 2. Наследование для ProductModel от SubCategory
        if self.__class__.__name__ == 'ProductModel':
            if hasattr(self, 'sub_category') and self.sub_category:
                template = getattr(self.sub_category, field_name, None)
                if template:
                    return template
                # Проверяем Category через SubCategory
                if hasattr(self.sub_category, 'category') and self.sub_category.category:
                    template = getattr(self.sub_category.category, field_name, None)
                    if template:
                        return template

        # 3. Наследование для SubCategory от Category
        elif self.__class__.__name__ == 'SubCategory':
            if hasattr(self, 'category') and self.category:
                template = getattr(self.category, field_name, None)
                if template:
                    return template

        # 4. Наследование для Product от ProductModel
        elif self.__class__.__name__ == 'Product':
            if hasattr(self, 'model') and self.model:
                # Сначала проверяем у ProductModel
                template = getattr(self.model, field_name, None)
                if template:
                    return template
                # Потом проверяем у SubCategory через модель
                if hasattr(self.model, 'sub_category') and self.model.sub_category:
                    template = getattr(self.model.sub_category, field_name, None)
                    if template:
                        return template
                    # Наконец проверяем у Category
                    if hasattr(self.model.sub_category, 'category') and self.model.sub_category.category:
                        template = getattr(self.model.sub_category.category, field_name, None)
                        if template:
                            return template

        return None

    def apply_template(self, template: str, city=None) -> str:
        """
        Применение шаблона с заменой плейсхолдеров

        Args:
            template: шаблон с плейсхолдерами
            city: объект City для геолокации

        Returns:
            Обработанная строка
        """
        from apps.utils.seo_templates import apply_seo_template
        return apply_seo_template(self, template, city=city)

    # seo-методы

    def _get_meta_title(self):
        """Получение meta title с поддержкой шаблонов"""
        # 1. Приоритет: явно заполненное поле
        if self.meta_title:
            return self.meta_title

        # 2. Шаблон (с наследованием)
        template = self.get_template_field('meta_title_template')
        if template:
            return self.apply_template(template)

        # 3. Fallback - текущая логика
        title_suffix = Settings.get_seo_title_suffix()
        return '{} — {}'.format(self.get_title(), title_suffix)

    def get_meta_title(self):
        return seo_replace(self._get_meta_title())

    def _get_meta_desc(self):
        """Получение meta description с поддержкой шаблонов"""
        # 1. Приоритет: явно заполненное поле
        if self.meta_description:
            return self.meta_description

        # 2. Шаблон (с наследованием)
        template = self.get_template_field('meta_desc_template')
        if template:
            return self.apply_template(template)

        # 3. Fallback
        return self.get_title()

    def get_meta_desc(self):
        return seo_replace(self._get_meta_desc())

    def _get_meta_keyw(self):
        """Получение meta keywords с поддержкой шаблонов"""
        # 1. Приоритет: явно заполненное поле
        if self.meta_keywords:
            return self.meta_keywords

        # 2. Шаблон (с наследованием)
        template = self.get_template_field('meta_keywords_template')
        if template:
            return self.apply_template(template)

        # 3. Fallback
        return self.get_title()

    def get_meta_keyw(self):
        return seo_replace(self._get_meta_keyw())

    def _get_h1(self):
        """Получение H1 с поддержкой шаблонов"""
        # 1. Приоритет: явно заполненное поле
        if self.h1:
            return self.h1

        # 2. Шаблон (с наследованием)
        template = self.get_template_field('h1_template')
        if template:
            return self.apply_template(template)

        # 3. Fallback
        return self.get_h1_title()

    def get_h1(self):
        return seo_replace(self._get_h1())

    # админка

    def has_seo_text(self):
        return bool_to_icon(self.seo_text)
    has_seo_text.allow_tags = True
    has_seo_text.short_description = 'Есть SEO-текст?'

    def show_instruction(self):
        return SEO_INSTRUCTION
    show_instruction.allow_tags = True
    show_instruction.short_description = 'Инструкция'
