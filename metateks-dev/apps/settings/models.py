from django.db import models
from django.urls import reverse

from solo.models import SingletonModel

from apps.utils.seo import SEO_FIELDS, SEO_INSTRUCTION, seo_replace


class Settings(SingletonModel):
    feedback_email = models.TextField(
        'Email для отправки уведомлений с сайта',
        default='email1@example.com\r\nemail2@example.com',
        help_text='можно несколько; каждый на новой строке',
    )
    orders_email = models.TextField(
        'Email для отправки писем о новых заказах',
        default='email1@example.com\r\nemail2@example.com',
        help_text='можно несколько; каждый на новой строке',
    )
    title_suffix = models.CharField('Хвост title у страниц', max_length=255, default='Метатэкс')
    robots_txt = models.TextField(
        'Содержимое файла /robots.txt',
        default='User-agent: *\r\nDisallow: \r\nHost: metateks.ru\r\nSitemap: https://metateks.ru/sitemap.xml',
    )

    class Meta:
        verbose_name = 'Общие настройки'

    def __str__(self):
        return 'Общие настройки'

    @classmethod
    def get_feedback_emails(cls):
        obj = cls.get_solo()
        return [e.strip() for e in (obj.feedback_email or '').split('\r\n')]

    @classmethod
    def get_orders_emails(cls):
        obj = cls.get_solo()
        return [e.strip() for e in (obj.orders_email or '').split('\r\n')]

    @classmethod
    def get_seo_title_suffix(cls):
        DEFAULT_PREFIX = 'Метатэкс'
        obj = cls.get_solo()
        return obj.title_suffix or DEFAULT_PREFIX

    @classmethod
    def get_robots_txt(cls):
        obj = cls.get_solo()
        return obj.robots_txt


class SEOSetting(models.Model):
    key = models.SlugField('Код', max_length=255, unique=True)
    description = models.CharField('Страница', max_length=255)
    title = models.CharField(
        'Title',
        max_length=511, blank=True, default='',
        help_text='Оставьте пустым, чтобы использовать название страницы (выше)',
    )
    meta_desc = models.TextField(
        'Meta description (описание)',
        blank=True, default='',
        help_text='Оставьте пустым, чтобы использовать глобальный meta_desc',
    )
    meta_keyw = models.TextField(
        'Meta keywords (ключевые слова через запятую)',
        max_length=255, blank=True, default='',
    )
    h1 = models.TextField(
        'Заголовок H1',
        max_length=255, blank=True, default='',
        help_text='Оставьте пустым, чтобы использовать название страницы',
    )
    header_text = models.TextField(
        'Описание страницы (рядом с заголовком)',
        blank=True, default='',
    )
    url_pattern = models.CharField('URL pattern', max_length=31, blank=True, default='')

    class Meta:
        ordering = ['id',]
        verbose_name = 'SEO-настройка'
        verbose_name_plural = 'SEO-настройки: статические страницы'

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        pattern = self.url_pattern or 'home'
        return reverse(pattern)

    def _get_meta_title(self):
        title = self.title
        if title:
            return title
        title_suffix = Settings.get_seo_title_suffix()
        return '{} — {}'.format(self.description, title_suffix)

    def get_meta_title(self):
        return seo_replace(self._get_meta_title())

    def get_meta_desc(self):
        return seo_replace(self.meta_desc or SEOSetting.objects.get(key='global').meta_desc)

    def get_meta_keyw(self, city=None):
        return seo_replace(self.meta_keyw or '')

    def get_h1(self, city=None):
        return seo_replace(self.h1 or self.description)

    def get_header_text(self):
        return seo_replace(self.header_text or '')

    @classmethod
    def get_seo_dict(cls, key):
        obj = cls.objects.filter(key=key).first()
        if not obj:
            return {}
        return obj.get_obj_seo_dict()

    def get_obj_seo_dict(self):
        seo_dict = {}
        for field_name in SEO_FIELDS:
            method_name = {
                'title': 'get_meta_title'
            }.get(field_name, 'get_{}'.format(field_name))
            seo_dict[field_name] = getattr(self, method_name)
        return seo_dict

    def show_instruction(self):
        return SEO_INSTRUCTION
    show_instruction.allow_tags = True
    show_instruction.short_description = 'Инструкция'
