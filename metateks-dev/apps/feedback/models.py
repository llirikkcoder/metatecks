from django.conf import settings
from django.db import models

from apps.utils.model_mixins import DatesBaseModel


class CallbackRequest(DatesBaseModel):
    name = models.CharField('Имя', blank=True, null=True, max_length=63)
    phone = models.CharField('Телефон', max_length=63)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL, verbose_name='Пользователь', null=True, blank=True
    )
    ip_address = models.CharField('IP-адрес', max_length=40, null=True, blank=True)
    is_synced_with_b24 = models.BooleanField('Синхронизирован с Битрикс24?', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'заказ обратного звонка'
        verbose_name_plural = 'заказы обратного звонка'

    def save(self, *args, **kwargs):
        if not self.name and self.user:
            self.name = self.user.get_name()
        return super().save(*args, **kwargs)

    def __str__(self):
        _str = self.name or self.phone
        return f'#{self.id}/ {_str} ({self.created_at_str})'
