from django.urls import path

from .views import (
    SetPaymentMethodView, CancelOrderView, PayOrderView, AddCashlessDataView,
    ChooseAddressView,
    RemoveAddressView,
    UpdateUserView, UpdateAddressView, UpdateCashlesDataView,
    ChangeAvatarView,
)


urlpatterns = [
    path('set_payment_method/', SetPaymentMethodView.as_view(), name='set-payment-method'),
    path('cancel_order/', CancelOrderView.as_view(), name='cancel-order'),
    path('pay_order/', PayOrderView.as_view(), name='pay-order'),
    path('add_cashless_data/', AddCashlessDataView.as_view(), name='add-cashless-data'),

    path('choose_address/', ChooseAddressView.as_view(), name='choose-address'),

    path('remove_address/', RemoveAddressView.as_view(), name='remove-address'),

    path('update_user/', UpdateUserView.as_view(), name='update-user'),
    path('update_address/', UpdateAddressView.as_view(), name='update-address'),
    path('update_cashless_data/', UpdateCashlesDataView.as_view(), name='update-cashless-data'),

    path('change_avatar/', ChangeAvatarView.as_view(), name='change-avatar'),
]
