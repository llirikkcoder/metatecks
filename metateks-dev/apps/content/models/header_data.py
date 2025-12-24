from django.db import models

from solo.models import SingletonModel


class HeaderData(SingletonModel):
    working_days = models.CharField('Режим работы: дни', max_length=31, blank=True, default='ПН - ПТ')
    working_time = models.CharField('Режим работы: время', max_length=31, blank=True, default='09:00 - 18:00')
    contacts_phone = models.CharField('Контакты: номер телефона', max_length=31, blank=True, default='+7 800 222-54-32')
    contacts_email = models.CharField('Контакты: email', max_length=31, blank=True, default='info@metateks.ru')

    class Meta:
        verbose_name = 'Данные в шапке'

    def __str__(self):
        return 'Данные в шапке'

    def get_links(self):
        return self.links.filter(is_shown=True)


class HeaderLink(models.Model):
    base = models.ForeignKey(HeaderData, models.CASCADE, related_name='links')
    title = models.CharField('Заголовок', max_length=255)
    link = models.CharField('Ссылка', max_length=127)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'ссылка'
        verbose_name_plural = 'ссылки в шапке'

    def __str__(self):
        return self.title
