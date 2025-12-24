from django.contrib import admin

from solo.admin import SingletonModelAdmin

from apps.content.models import (
    FooterData, FooterFirstColumnLink, FooterSecondColumnLink,
    FooterThirdColumnLink, FooterFourthColumnLink, FooterSocialLink,
)


class FooterFirstColumnLinkInline(admin.TabularInline):
    model = FooterFirstColumnLink
    fields = ('title', 'link', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-first-col'
    extra = 0
    verbose_name_plural = 'ссылки'


class FooterSecondColumnLinkInline(admin.TabularInline):
    model = FooterSecondColumnLink
    fields = ('title', 'link', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-second-col'
    extra = 0
    verbose_name_plural = 'ссылки'


class FooterThirdColumnLinkInline(admin.TabularInline):
    model = FooterThirdColumnLink
    fields = ('title', 'link', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-third-col'
    extra = 0
    verbose_name_plural = 'ссылки'


class FooterFourthColumnLinkInline(admin.TabularInline):
    model = FooterFourthColumnLink
    fields = ('title', 'link', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-fourth-col'
    extra = 0
    verbose_name_plural = 'ссылки'


class FooterSocialLinkInline(admin.TabularInline):
    model = FooterSocialLink
    fields = ('icon', 'link', 'order', 'is_shown',)
    suit_classes = 'suit-tab suit-tab-socials'
    extra = 0


@admin.register(FooterData)
class FooterDataAdmin(SingletonModelAdmin):
    suit_form_tabs = (
        ('first-col', '1-й столбец'),
        ('second-col', '2-й столбец'),
        ('third-col', '3-й столбец'),
        ('fourth-col', '4-й столбец'),
        ('socials', 'Ссылки на соц.сети'),
        ('contacts', 'Контакты'),
    )
    fieldsets = (
        ('Заголовок', {
            'classes': ('suit-tab', 'suit-tab-first-col',),
            'fields': ('first_column_title',),
        }),
        ('Заголовок', {
            'classes': ('suit-tab', 'suit-tab-second-col',),
            'fields': ('second_column_title',),
        }),
        ('Заголовок', {
            'classes': ('suit-tab', 'suit-tab-third-col',),
            'fields': ('third_column_title',),
        }),
        ('Заголовок', {
            'classes': ('suit-tab', 'suit-tab-fourth-col',),
            'fields': ('fourth_column_title',),
        }),
        ('Контакты', {
            'classes': ('suit-tab', 'suit-tab-contacts',),
            'fields': ('contacts_phone', 'contacts_email',),
        }),
    )
    inlines = [
        FooterFirstColumnLinkInline,
        FooterSecondColumnLinkInline,
        FooterThirdColumnLinkInline,
        FooterFourthColumnLinkInline,
        FooterSocialLinkInline,
    ]
