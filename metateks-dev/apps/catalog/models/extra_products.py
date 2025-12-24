from django.db import models

from apps.utils.model_mixins import DatesBaseModel
from .categories import SubCategory


class ExtraProduct(DatesBaseModel):
    sub_category = models.ForeignKey(
        SubCategory, models.CASCADE, verbose_name='Подкатегория',
        blank=True, null=True,
        related_name='extra_products',
    )
    name = models.CharField('Название', max_length=255)
    price = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    is_active = models.BooleanField('Активен?', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['-is_active', 'order']
        verbose_name = 'дополнительный товар'
        verbose_name_plural = 'дополнительные товары'

    def __str__(self):
        return self.name
