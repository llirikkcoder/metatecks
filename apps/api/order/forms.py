from django import forms

from apps.orders.models import (
    OrderDeliveryAddressData, OrderContactsData,
    OrderPaymentCardData, OrderPaymentCashlessData
)


class AddressForm(forms.ModelForm):

    class Meta:
        model = OrderDeliveryAddressData
        exclude = ['order']


class ContactsForm(forms.ModelForm):

    class Meta:
        model = OrderContactsData
        exclude = ['order']


class PaymentCardForm(forms.ModelForm):

    class Meta:
        model = OrderPaymentCardData
        exclude = ['order']


class PaymentCashlessForm(forms.ModelForm):

    class Meta:
        model = OrderPaymentCashlessData
        exclude = ['order']
