import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View
from django.urls import reverse

from apps.orders.constants import PAYMENT_METHODS, OrderStatuses
from apps.orders.models import Order, UserDeliveryAddress, UserPaymentCard, UserPaymentCashlessData
from apps.utils.common import get_error_message
from .forms import UpdateUserForm, UpdateAddressForm, CashlessDataForm, UpdateCashlessDataForm


# --- аккаунт: базовые вьюхи ---

class AccountAPIBaseView(LoginRequiredMixin, View):
    """
    Базовая вьюха
    """

    def add_to_response(self):
        return {}

    def action(self, request, data):
        pass

    def post(self, request, *args, **kwargs):
        try:
            body = request.body
            data = json.loads(request.body) if body else {}
            response = self.action(request, data)
            if response:
                return response
        except ValueError:
            return JsonResponse({'result': 'error', 'error': 'Неправильный формат запроса'}, status=400)
        except Exception as exc:
            err_message = get_error_message(exc)
            return JsonResponse({'result': 'error', 'error': err_message}, status=400)
        result = {'result': 'ok'}
        result.update(self.add_to_response())
        return JsonResponse(result)


class AccountAPIChooseView(AccountAPIBaseView):
    """
    Выбор одного из объектов (адрес, карта для оплаты)
    """
    model = None
    related_name = ''

    def get_object(self, data=None):
        return self.model.objects.get(id=data['value'], user=self.request.user)

    def action(self, request, data):
        obj = self.get_object(data)
        user = request.user
        self.model.objects.filter(user=user).update(is_selected=False)
        obj.is_selected = True
        obj.save()


class AccountAPIRemoveView(AccountAPIBaseView):
    """
    Удаление одного из объектов (адрес, карта для оплаты)
    """
    model = None

    def get_object(self, data=None):
        return self.model.objects.get(id=data['value'], user=self.request.user)

    def action(self, request, data):
        obj = self.get_object(data)
        obj.delete()


class AccountAPIFormView(AccountAPIBaseView):
    """
    Редактирование полей (профиль, адрес, данные для безналичной оплаты)
    """
    form_class = None

    def get_object(self, data=None):
        return None

    def get_form_error(self, form):
        error = None
        for k, v in form.errors.items():
            error = v[0]
            break
        return error

    def action(self, request, data):
        obj = self.get_object(data)
        form_data = data.get('data')
        form = self.form_class(form_data)
        if form.is_valid():
            _data = form.cleaned_data
            for k, v in form_data.items():
                if k in _data:
                    setattr(obj, k, _data[k])
                    obj.save()
        else:
            error = self.get_form_error(form)
            return JsonResponse({'error': error}, status=400)


# --- аккаунт: установка способа оплаты ---

class SetPaymentMethodView(AccountAPIBaseView):

    def action(self, request, data):
        method = data.get('value')
        assert method in PAYMENT_METHODS
        user = request.user
        user.payment_method = method
        user.save()


# --- аккаунт: отмена заказа ---

class CancelOrderView(AccountAPIBaseView):

    def get_object(self, data=None):
        return Order.objects.get(id=data['value'], user=self.request.user)

    def action(self, request, data):
        order = self.get_object(data)

        if order.is_canceled:
            return
        if not order.can_be_canceled:
            raise Exception('Заказ не может быть отменен')

        order.status = OrderStatuses.CANCELED
        order.is_canceled = True
        order.is_canceled_by_user = True
        order.save()

        data = {'result': 'ok', 'redirect_url': order.get_canceled_url()}
        return JsonResponse(data)


# --- аккаунт: добавление данных для безналичной оплаты ---

class AddCashlessDataView(AccountAPIBaseView):
    form_class = CashlessDataForm

    def get_form_errors(self, form):
        errors = []
        for k, v in form.errors.items():
            errors.append({'name': k, 'error_message': v[0]})
            # errors.append({'name': '__all__', 'error_message': v[0]})
        return errors

    def action(self, request, data):
        form = self.form_class(data)
        user = request.user
        if form.is_valid():
            if hasattr(user, 'payment_cashless_data'):
                user.payment_cashless_data.delete()
            UserPaymentCashlessData.objects.get_or_create(user=user, **form.cleaned_data)
            redirect_url = f"{reverse('account:profile')}#non-cash"
            data = {'result': 'ok', 'redirect_url': redirect_url}
            return JsonResponse(data)
        else:
            errors = self.get_form_errors(form)
            return JsonResponse({'errors': errors}, status=400)


# --- аккаунт: выбор из объектов ---

class ChooseAddressView(AccountAPIChooseView):
    model = UserDeliveryAddress


class ChoosePaymentCardView(AccountAPIChooseView):
    model = UserPaymentCard


# --- аккаунт: удаление объектов ---

class RemoveAddressView(AccountAPIRemoveView):
    model = UserDeliveryAddress


class RemovePaymentCardView(AccountAPIRemoveView):
    model = UserPaymentCard


# --- аккаунт: обновление данных ---

class UpdateUserView(AccountAPIFormView):
    form_class = UpdateUserForm

    def get_object(self, data=None):
        return self.request.user

    def add_to_response(self):
        user = self.get_object()
        if not user.avatar:
            return {'initials': user.initials}
        return {}


class UpdateAddressView(AccountAPIFormView):
    model = UserDeliveryAddress
    form_class = UpdateAddressForm

    def get_object(self, data=None):
        return self.model.objects.get(id=data['id'], user=self.request.user)


class UpdateCashlesDataView(AccountAPIFormView):
    model = UserPaymentCashlessData
    form_class = UpdateCashlessDataForm

    def get_object(self, data=None):
        obj, _ = self.model.objects.get_or_create(user=self.request.user)
        return obj


# --- аккаунт: смена аватара ---

class ChangeAvatarView(AccountAPIBaseView):

    def post(self, request, *args, **kwargs):
        user = request.user
        if not request.FILES:
            return JsonResponse({})
        try:
            file = request.FILES['file']
            user.avatar = file
            user.save()
            user.refresh_from_db()
        except ValueError:
            return JsonResponse({'result': 'error', 'error': 'Неправильный формат запроса'}, status=400)
        except Exception as exc:
            err_message = get_error_message(exc)
            return JsonResponse({'result': 'error', 'error': err_message}, status=400)

        result = {
            'result': 'ok',
            'account_avatar': user.get_account_avatar_url(),
            'header_avatar': user.header_avatar_url,
        }
        return JsonResponse(result)
