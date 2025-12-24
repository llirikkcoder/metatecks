import json

from django.http import JsonResponse
from django.views.generic import View

from apps.addresses.models import Warehouse
from apps.cart.utils import (
    update_cart_count, get_cart_data, get_user_delivery,
    get_user_contacts, get_user_payment, get_order_data,
)
from apps.orders.constants import (
    DeliveryMethods, DELIVERY_METHODS,
    PaymentMethods, PAYMENT_METHODS,
    OrderStatuses,
)
from apps.orders.models import (
    DeliveryCompany, Order, OrderItem,
    OrderDeliveryAddressData, OrderContactsData, UserDeliveryAddress,
    OrderPaymentCardData, UserPaymentCard,
    OrderPaymentCashlessData, UserPaymentCashlessData,
)
from apps.utils.common import get_error_message
from ..samples import ORDER_DATA_SAMPLE
from .forms import AddressForm, ContactsForm, PaymentCardForm, PaymentCashlessForm


# --- обновление данных о заdказе: базовые вьюхи ---

class SetOrderDataAPIBaseView(View):

    # def get(self, request, *args, **kwargs):
    #     order_data = request.session.get('order_data', {})
    #     if True:
    #         order_data = ORDER_DATA_SAMPLE
    #         request.session['order_data'] = order_data
    #     return JsonResponse(order_data)

    def process_data(self, request, data, order_data):
        pass

    def post(self, request, *args, **kwargs):
        try:
            body = request.body
            data = json.loads(request.body) if body else {}
            order_data = request.session.get('order_data', {})
            response = self.process_data(request, data, order_data)
            if response:
                return response
        except ValueError:
            return JsonResponse({'result': 'error', 'error': 'Неправильный формат запроса'}, status=400)
        except Exception as exc:
            err_message = get_error_message(exc)
            return JsonResponse({'result': 'error', 'error': err_message}, status=400)
        return JsonResponse({'result': 'ok'})


class SetOrderDataAPIFormView(SetOrderDataAPIBaseView):
    form_class = None
    dict_key = None
    data_key = 'data'

    def get_form_errors(self, form):
        errors = []
        for k, v in form.errors.items():
            errors.append({'name': k, 'error_message': v[0]})
            # errors.append({'name': '__all__', 'error_message': v[0]})
        return errors

    def process_data(self, request, data, order_data):
        # - получаем данные
        data = data.get('data')
        # - получаем объект в сессии
        data_dict = order_data.get(self.dict_key, {})
        # - валидируем форму и сохраняем данные
        form = self.form_class(data)
        if form.is_valid():
            data_dict[self.data_key] = form.cleaned_data
            order_data[self.dict_key] = data_dict
            request.session['order_data'] = order_data
        else:
            errors = self.get_form_errors(form)
            return JsonResponse({'errors': errors}, status=400)


# --- обновление данных о заказе: вьюхи ---

class SetDeliveryMethodView(SetOrderDataAPIBaseView):
    """
    Тип доставки, транспортная компания
    """

    def process_data(self, request, data, order_data):
        # - получаем данные
        method = data.get('method')
        company_id = data.get('company_id')
        # - сохраняем в сессию
        delivery_data = order_data.get('delivery', {})
        if method:
            assert method in DELIVERY_METHODS
            delivery_data['method'] = method
        if company_id:
            delivery_data['company_id'] = int(company_id)
        order_data['delivery'] = delivery_data
        request.session['order_data'] = order_data


class SetDeliveryDataView(SetOrderDataAPIFormView):
    """
    Адрес доставки
    """
    form_class = AddressForm
    dict_key = 'delivery'


class SetContactsDataView(SetOrderDataAPIFormView):
    """
    Контактные данные
    """
    form_class = ContactsForm
    dict_key = 'contacts'


class SetPaymentMethodView(SetOrderDataAPIBaseView):
    """
    Тип оплаты
    """

    def process_data(self, request, data, order_data):
        # - получаем данные
        method = data.get('method')
        assert method in PAYMENT_METHODS
        # - сохраняем в сессию
        payment_data = order_data.get('payment', {})
        payment_data['method'] = method
        order_data['payment'] = payment_data
        request.session['order_data'] = order_data


class SetPaymentCardDataView(SetOrderDataAPIFormView):
    """
    Оплата онлайн: данные карты
    """
    form_class = PaymentCardForm
    dict_key = 'payment'
    data_key = 'card_data'


class SetPaymentCashlessDataView(SetOrderDataAPIFormView):
    """
    Безналичная оплата: данные организации
    """
    form_class = PaymentCashlessForm
    dict_key = 'payment'
    data_key = 'non_cash_data'


# --- оформление заказа ---

class OrderCheckoutView(View):

    def post(self, request, *args, **kwargs):
        error = ''
        if not request.user.is_authenticated:
            error = 'Войдите или зарегистрируйте аккаунт'
        elif not request.session.get('cart'):
            error = 'Корзина пуста'
        else:
            is_data_filled = get_order_data(request)['is_data_filled']
            if not is_data_filled:
                error = 'Не хватает данных для оформления заказа'

        if error:
            return JsonResponse({'result': 'error', 'error': error}, status=400)

        try:
            response = self.create_order(request)
            if response:
                return response
        except Exception as exc:
            err_message = get_error_message(exc)
            return JsonResponse({'result': 'error', 'error': err_message}, status=400)
        return JsonResponse({'result': 'ok'})

    def create_order(self, request):
        # получение данных из сессии
        user = request.user
        cart_data = get_cart_data(request)
        order_data = request.session.get('order_data', {})

        # создание заказа и заполнение данных

        # -- заказ
        order = Order.objects.create(
            user=user, total_quantity=cart_data['total_quantity'],
            total_cost=cart_data['total_cost'], total_without_discount=cart_data['total_cost'],
        )

        # -- список товаров
        order_warehouse_id = None
        default_warehouse_id = Warehouse.get_default_id()

        for p in cart_data['products']:
            if p['is_enabled']:
                _subtitle = p['category'].get_name_product()
                _warehouse_id = p.get('warehouse_id') or default_warehouse_id
                if not order_warehouse_id:
                    order_warehouse_id = _warehouse_id
                item = OrderItem.objects.create(
                    order=order,
                    item_type='product', product=p['product'],
                    item_name=p['product'].name, item_subtitle=_subtitle,
                    quantity=p['quantity'],
                    price=p['price'], price_without_discount=p['price'],
                    cost=p['cost'], cost_without_discount=p['cost'],
                    warehouse_id=_warehouse_id,
                )
                for e in p['extra']:
                    if e['is_enabled']:
                        OrderItem.objects.create(
                            order=order,
                            item_type='extra', base_item=item, extra_product=e['extra_product'],
                            item_name=e['extra_product'].name, item_subtitle=_subtitle,
                            quantity=e['quantity'],
                            price=e['price'], price_without_discount=e['price'],
                            cost=e['cost'], cost_without_discount=e['cost'],
                            warehouse_id=_warehouse_id,
                        )
        order.warehouse_id = order_warehouse_id

        # -- данные о доставке
        _delivery = order_data.get('delivery', {})
        _udelivery = get_user_delivery(user)
        delivery_method = _delivery.get('method') or _udelivery.get('method')
        delivery_company_id = _delivery.get('company_id') or _udelivery.get('company_id')
        delivery_data = _delivery.get('data') or _udelivery.get('data') or {}

        # -- контактные данные
        contacts = order_data.get('contacts', get_user_contacts(user))
        contacts_data = contacts.get('data', {})
        OrderContactsData.objects.create(order=order, **contacts_data)

        # 1) способ доставки
        order.delivery_method = delivery_method
        user.delivery_method = delivery_method
        # 2) транспортная компания
        if delivery_method == DeliveryMethods.COMPANY:
            _company = DeliveryCompany.objects.filter(id=delivery_company_id).first()
            if _company:
                order.delivery_company = _company
                order.delivery_company_name = _company.name
                if not user.delivery_company:
                    user.delivery_company = _company
        # 3) адрес доставки
        if delivery_method != DeliveryMethods.PICKUP:
            OrderDeliveryAddressData.objects.create(order=order, **delivery_data)
            delivery_data.update(contacts_data)
            UserDeliveryAddress.objects.get_or_create(user=user, **delivery_data)

        # -- данные об оплате
        _payment = order_data.get('payment', {})
        _upayment = get_user_payment(user)
        payment_method = _payment.get('method') or _upayment.get('method')
        card_data = _payment.get('card_data') or _upayment.get('card_data') or {}
        non_cash_data = _payment.get('non_cash_data') or _upayment.get('non_cash_data') or {}
        # 1) метод оплаты
        order.payment_method = payment_method
        if not user.payment_method:
            user.payment_method = payment_method
        # 2) детальные данные по оплате
        if payment_method == PaymentMethods.ONLINE:
            OrderPaymentCardData.objects.create(order=order, **card_data)
            UserPaymentCard.objects.get_or_create(user=user, **card_data)
        elif payment_method == PaymentMethods.NON_CASH:
            OrderPaymentCashlessData.objects.create(order=order, **non_cash_data)
            if not getattr(user, 'payment_cashless_data', None):
                UserPaymentCashlessData.objects.create(user=user, **non_cash_data)

        # -- сохраняем заказ и человека
        order.status = OrderStatuses.CREATED
        order.save()
        user.save()

        # очищаем сессию
        request.session['cart'] = {}
        request.session['order_data'] = {}
        update_cart_count(request)

        # отдаем ответ
        redirect_url = order.get_created_url()
        return JsonResponse({'result': 'ok', 'order_id': order.id, 'redirect_url': redirect_url})
