from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models.categories import SubCategory


@receiver(m2m_changed, sender=SubCategory.attributes.through)
def update_model_attr_ids(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Подкатегории: обновляем поле attr_ids при изменении m2m-поля attributes
    """
    instance.attr_ids = [attr.id for attr in instance.attributes.all()]
    instance.save()


@receiver(m2m_changed, sender=SubCategory.attributes_in_products.through)
def update_model_attr_products_ids(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Подкатегории: обновляем поле attr_products_ids при изменении m2m-поля attributes_in_products
    """
    instance.attr_products_ids = [attr.id for attr in instance.attributes_in_products.all()]
    instance.save()


@receiver(m2m_changed, sender=SubCategory.attributes_in_filter.through)
def update_model_attr_filter_ids(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Подкатегории: обновляем поле attr_filter_ids при изменении m2m-поля attributes_in_filter
    """
    instance.attr_filter_ids = [attr.id for attr in instance.attributes_in_filter.all()]
    instance.save()
