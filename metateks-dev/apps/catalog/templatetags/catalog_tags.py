from django import template

from apps.promotions.models import Promotion


register = template.Library()


@register.simple_tag
def get_subcat_full_name(subcat, category):
    return subcat.get_full_name(category=category, single=False)


@register.simple_tag
def get_product_list_attrs(product, attr_ids=None, attributes=None):
    return product.get_attrs_list_v3(attributes=attributes, in_filter=True)


@register.simple_tag
def get_product_page_attrs(product, attr_ids=None, attributes=None):
    return product.get_attrs_list_v3(attributes=attributes, in_filter=False)


@register.simple_tag
def get_model_promotion(model):
    return Promotion.get_product_promotion(model=model)


@register.simple_tag
def get_product_promotion(product):
    return Promotion.get_product_promotion(product=product)


@register.simple_tag
def get_promo_new_price(promo, old_price):
    return promo.get_new_price(old_price)
