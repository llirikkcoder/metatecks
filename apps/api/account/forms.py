from django import forms

from apps.users.models import User
from apps.orders.models import UserDeliveryAddress, UserPaymentCashlessData


class PartialFormMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class UpdateUserForm(PartialFormMixin, forms.ModelForm):

    class Meta:
        model = User
        # fields = ['last_name', 'first_name', 'patronymic_name', 'phone',]
        fields = ['last_name', 'first_name', 'patronymic_name', 'phone', 'email',]


class UpdateAddressForm(PartialFormMixin, forms.ModelForm):

    class Meta:
        model = UserDeliveryAddress
        exclude = ['user']


class CashlessDataForm(forms.ModelForm):

    class Meta:
        model = UserPaymentCashlessData
        exclude = ['user']


class UpdateCashlessDataForm(PartialFormMixin, CashlessDataForm):
    pass
