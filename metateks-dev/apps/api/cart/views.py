import copy
import json

from django.http import JsonResponse
from django.views.generic import View

from apps.cart.utils import update_cart_count
from apps.utils.common import get_error_message
from ..samples import CART_DATA_SAMPLE


DEFAULT_CART_ITEM = {
    'quantity': 1,
    'warehouse_id': None,
    'is_enabled': True,
    'extra': {},
}
DEFAULT_EXTRA_ITEM = {
    'quantity': 1,
    'is_enabled': True,
}


def get_default_cart_item():
    return copy.deepcopy(DEFAULT_CART_ITEM)


def get_default_extra_item():
    return copy.deepcopy(DEFAULT_EXTRA_ITEM)


class CartAPIBaseView(View):

    # def get(self, request, *args, **kwargs):
    #     cart = request.session.get('cart', {})
    #     if not cart:
    #         cart = CART_DATA_SAMPLE
    #         request.session['cart'] = cart
    #     return JsonResponse(cart)

    def update_cart(self, request, data):
        pass

    def post(self, request, *args, **kwargs):
        cart_count = None
        try:
            body = request.body
            data = json.loads(request.body) if body else {}
            self.update_cart(request, data)
            cart_count = update_cart_count(request)
        except ValueError:
            return JsonResponse({'result': 'error', 'error': 'Неправильный формат запроса'}, status=400)
        except Exception as exc:
            err_message = get_error_message(exc)
            return JsonResponse({'result': 'error', 'error': err_message}, status=400)
        return JsonResponse({'result': 'ok', 'cart_count': cart_count})


class UpdateItemView(CartAPIBaseView):

    def update_cart(self, request, data):
        # - получаем данные из запроса
        product_id = str(data['product_id'])
        quantity = data.get('quantity')
        is_enabled = data.get('is_enabled')
        warehouse_id = data.get('warehouse_id')
        extra_ids = data.get('extra_ids', [])

        # - обновляем товар в корзине
        cart = request.session.get('cart', {})
        if quantity == 0:
            del cart[product_id]
        else:
            cart_item = cart.get(product_id, get_default_cart_item())
            if quantity is not None:
                cart_item['quantity'] = quantity
            if is_enabled is not None:
                cart_item['is_enabled'] = is_enabled
                if 'extra' in cart_item:
                    for extra in cart_item['extra'].values():
                        extra['is_enabled'] = is_enabled
            if warehouse_id is not None:
                cart_item['warehouse_id'] = warehouse_id
            if extra_ids:
                cart_item['extra'] = {str(e): get_default_extra_item() for e in extra_ids}
            cart[product_id] = cart_item
        request.session['cart'] = cart


class UpdateExtraItemView(CartAPIBaseView):

    def update_cart(self, request, data):
        # - получаем данные из запроса
        product_id = str(data['product_id'])
        extra_id = str(data['extra_id'])
        quantity = data.get('quantity')
        is_enabled = data.get('is_enabled')

        # - обновляем доп.товар в корзине
        cart = request.session.get('cart', {})
        cart_item = cart[product_id]
        extra = cart_item.get('extra', {})
        extra_item = extra.get(extra_id, get_default_extra_item())
        if quantity == 0:
            del cart_item['extra'][extra_id]
        else:
            if quantity is not None:
                extra_item['quantity'] = quantity
            if is_enabled is not None:
                if is_enabled is True:
                    cart_item['is_enabled'] = True
                extra_item['is_enabled'] = is_enabled
            extra[extra_id] = extra_item
            cart_item['extra'] = extra
        request.session['cart'] = cart


class GroupToggleView(CartAPIBaseView):

    def update_cart(self, request, data):
        if 'cart' in request.session:
            cart = request.session.get('cart', {})
            is_enabled = data.get('is_enabled', True)
            for obj in cart.values():
                obj['is_enabled'] = is_enabled
                for extra in obj.get('extra', {}).values():
                    extra['is_enabled'] = is_enabled
            request.session['cart'] = cart


class ClearCartView(CartAPIBaseView):

    def update_cart(self, request, data):
        if 'cart' in request.session:
            del request.session['cart']
