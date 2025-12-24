import copy
import re

from apps.catalog.models import Product, ExtraProduct
from apps.orders.constants import DeliveryMethods, PaymentMethods
from apps.orders.models import DeliveryCompany
from apps.promotions.models import Promotion


__all__ = [
    'update_cart_count', 'get_cart_data',
    'get_user_delivery', 'get_user_contacts', 'get_user_payment',
    'get_order_data',
]


def update_cart_count(request):
    cart = request.session.get('cart', {})
    count = 0
    for _, item in cart.items():
        quantity = item['quantity']
        is_enabled = item['is_enabled']
        if quantity and is_enabled is True:
            count += quantity
            for _, extra_item in item.get('extra', {}).items():
                quantity = extra_item['quantity']
                is_enabled = extra_item['is_enabled']
                if is_enabled is True:
                    count += quantity
    request.session['cart_count'] = count
    return count


def get_cart_data(request):
    """
    Получаем данные о позициях в заказе
    """
    cart = request.session.get('cart', {})
    products = []
    is_everything_enabled = True
    total_quantity = 0
    total_cost = 0

    if cart:
        product_ids = cart.keys()
        # qs = Product.objects.select_related('model', 'sub_category', 'category').filter(id__in=product_ids)
        qs = Product.objects.filter(id__in=product_ids)
        PRODUCTS = {str(p.id): p for p in qs}
        PRODUCT_IDS = PRODUCTS.keys()

        for product_id, item in cart.items():
            quantity = item['quantity']
            is_enabled = item['is_enabled']

            if quantity and product_id in PRODUCT_IDS:
                # - получаем товар
                p = PRODUCTS[product_id]
                product = {
                    'product': p,
                    'sub_category': p.sub_category,
                    'category': p.category,
                    'quantity': quantity,
                    'warehouse_id': item.get('warehouse_id'),
                    'is_enabled': is_enabled,
                    'extra': [],
                }

                # - получаем цену и стоимость
                price = p.price
                promo = Promotion.get_product_promotion(product=p)
                if promo:
                    price = promo.get_new_price(price)
                cost = price * quantity
                product.update({
                    'price': price,
                    'cost': cost,
                })

                # - обновляем суммы
                if is_enabled is True:
                    total_quantity += quantity
                    total_cost += cost
                else:
                    is_everything_enabled = False

                # - получаем экстра-товары
                if item.get('extra'):
                    extra = []
                    for extra_id, extra_item in item['extra'].items():
                        _quantity = extra_item['quantity']
                        _is_enabled = extra_item['is_enabled']

                        if _quantity:
                            extra_p = ExtraProduct.objects.filter(id=extra_id).first()
                            if not extra_p:
                                continue
                            _price = extra_p.price
                            _cost = _quantity * _price
                            extra.append({
                                'extra_product': extra_p,
                                'quantity': _quantity,
                                'is_enabled': _is_enabled,
                                'price': _price,
                                'cost': _cost,
                            })
                            if _is_enabled is True:
                                total_quantity += _quantity
                                total_cost += _cost
                            else:
                                is_everything_enabled = False
                    product['extra'] = extra

                products.append(product)

    if not products:
        is_everything_enabled = False

    return {
        'products': products,
        'is_everything_enabled': is_everything_enabled,
        'total_quantity': total_quantity,
        'total_cost': total_cost,
    }


def _hide_card_data(data_str):
    return re.sub(r'\d', '*', str(data_str))


def get_user_delivery(user):
    delivery = {}
    if user.is_authenticated:
        delivery = {
            'method': user.delivery_method,
            'company_id': user.delivery_company_id,
        }
        _address = user.addresses.first()
        if _address:
            delivery['data'] = _address.get_address_data()
    return delivery


def get_user_contacts(user):
    contacts = {}
    if user.is_authenticated:
        _address = user.addresses.first()
        contacts_data = (
            _address.get_contacts_data()
            if _address
            else user.get_contacts_data()
        )
        contacts['data'] = contacts_data
    return contacts


def get_user_payment(user):
    payment = {}
    if user.is_authenticated:
        payment = {
            'method': user.payment_method,
        }
        _card_obj = user.payment_cards.first()
        if _card_obj:
            payment['card_data'] = _card_obj.get_data()
        _cashless_obj = getattr(user, 'payment_cashless_data', None)
        if _cashless_obj:
            payment['non_cash_data'] = _cashless_obj.get_data()
    return payment


def _check_non_cash(data):
    for v in data.values():
        if not v:
            return False
    return True


def get_order_data(request):
    """
    Получаем сохраненные данные о заказе для передачи в cart.html
    """
    order_data = request.session.get('order_data', {})
    order_data = copy.deepcopy(order_data)
    user = request.user

    is_data_filled = True

    _delivery = order_data.get('delivery', {})
    _udelivery = get_user_delivery(user)
    delivery_method = _delivery.get('method') or _udelivery.get('method')
    delivery_company = _delivery.get('company_id') or _udelivery.get('company_id')
    delivery_data = _delivery.get('data') or _udelivery.get('data') or {}

    delivery_str = DeliveryMethods.get_label(delivery_method)
    if delivery_method == DeliveryMethods.COMPANY and delivery_company:
        _company = DeliveryCompany.shown().filter(id=delivery_company).first()
        if _company:
            delivery_str = f'{delivery_str}, {_company.name}'

    address_str = ', '.join(delivery_data.values())

    if (
        not delivery_method
        or (delivery_method != 'pickup' and not delivery_data)
    ):
        is_data_filled = False

    contacts = order_data.get('contacts', get_user_contacts(user))
    contacts_data = contacts.get('data', {})
    contacts_str = ''
    if contacts_data:
        _c = contacts_data
        _name_str = ' '.join([_c.get('first_name', ''), _c.get('last_name', '')]).strip()
        contacts_str = (
            f"{_c['phone']}, {_name_str}"
            if (_name_str and _c.get('phone'))
            else _name_str
        )

    if not contacts_data: is_data_filled = False

    _payment = order_data.get('payment', {})
    _upayment = get_user_payment(user)
    payment_method = _payment.get('method') or _upayment.get('method')

    card_payment_data = _payment.get('card_data') or _upayment.get('card_data') or {}
    for k, v in card_payment_data.items():
        card_payment_data[k] = (
            f'{_hide_card_data(v[:-4])}{v[-4:]}'
            if k == 'card_number'
            else v
            if k == 'card_expire'
            else _hide_card_data(v)
        )

    non_cash_payment_data = _payment.get('non_cash_data') or _upayment.get('non_cash_data') or {}

    cart_payment_str = PaymentMethods.get_label(PaymentMethods.ONLINE)
    if 'card_number' in card_payment_data:
        cart_payment_str = f'{cart_payment_str}, карта **{card_payment_data["card_number"][-4:]} {card_payment_data["card_expire"]}'
    non_cash_payment_str = PaymentMethods.get_label(PaymentMethods.NON_CASH)
    if 'organization' in non_cash_payment_data:
        non_cash_payment_str = f'{non_cash_payment_str}, {non_cash_payment_data["organization"]}'
    on_receipt_payment_str = PaymentMethods.get_label(PaymentMethods.ON_RECEIPT)

    payment_str = {
        PaymentMethods.ONLINE: cart_payment_str,
        PaymentMethods.NON_CASH: non_cash_payment_str,
        PaymentMethods.ON_RECEIPT: on_receipt_payment_str,
    }.get(payment_method, '')

    if (
        not payment_method
        or (payment_method == PaymentMethods.ONLINE and not card_payment_data)
        or (payment_method == PaymentMethods.NON_CASH and not _check_non_cash(non_cash_payment_data))
    ):
        is_data_filled = False

    return {
        'is_data_filled': is_data_filled,

        'delivery_method': delivery_method,
        'delivery_company': delivery_company,
        'delivery_data': delivery_data,
        'contacts_data': contacts_data,
        'payment_method': payment_method,
        'card_data': card_payment_data,
        'cashless_data': non_cash_payment_data,

        'delivery_str': delivery_str,
        'address_str': address_str,
        'contacts_str': contacts_str,
        'payment_str': payment_str,

        'cart_payment_str': cart_payment_str,
        'non_cash_payment_str': non_cash_payment_str,
        'on_receipt_payment_str': on_receipt_payment_str,
    }
