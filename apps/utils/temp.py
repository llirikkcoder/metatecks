import random

from apps.catalog.models import ProductModel


def _get_attr_value(attr):
    _id = attr.id
    if _id == 1:
        return random.randint(1,9)
    elif _id == 2:
        return random.randint(1,9)*10
    elif _id == 3:
        return random.randint(100,999)/10
    elif _id == 4:
        return random.randint(1,90)
    elif _id == 5:
        return random.randint(1,9)*100
    elif _id == 6:
        return random.choice([1,2])
    elif _id == 7:
        return random.choice(['true', 'false'])

    _type = attr.attr_type
    if attr_type == 'int':
        return random.randint(1,9)*10
    elif attr_type == 'float':
        return random.randint(100,999)/10
    else:
        return random.choice(['true', 'false'])


def fill_product_attrs(log=True):
    for p in ProductModel.objects.filter(sub_category__attributes__isnull=False):
        p.attrs = {a.attrs_slug: _get_attr_value(a) for a in p.sub_category.attributes.all()}
        p.save()
        if log:
            print(p)
            print(p.attrs)
            print()
