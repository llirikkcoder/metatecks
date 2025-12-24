from django.urls import path

from .views import (
    SetDeliveryMethodView, SetDeliveryDataView, SetContactsDataView,
    SetPaymentMethodView, SetPaymentCardDataView, SetPaymentCashlessDataView,
    OrderCheckoutView,
)


urlpatterns = [
    path('set_delivery_method/', SetDeliveryMethodView.as_view(), name='set-delivery-method'),
    path('set_delivery_data/', SetDeliveryDataView.as_view(), name='set-delivery-data'),
    path('set_contacts_data/', SetContactsDataView.as_view(), name='set-contacts-data'),
    path('set_payment_method/', SetPaymentMethodView.as_view(), name='set-payment-method'),
    path('set_payment_card_data/', SetPaymentCardDataView.as_view(), name='set-payment-card-data'),
    path('set_payment_cashless_data/', SetPaymentCashlessDataView.as_view(), name='set-payment-cashless-data'),

    path('checkout/', OrderCheckoutView.as_view(), name='checkout'),
]
