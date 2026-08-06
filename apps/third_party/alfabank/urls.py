from django.urls import include, path

from . import views


app_urlpatterns = [
    path('webhook/', views.PaymentWebhookView.as_view(), name='payment-webhook'),
    path('return/', views.PaymentReturnView.as_view(), name='payment-return'),
    path('fail/', views.PaymentFailView.as_view(), name='payment-fail'),
]

urlpatterns = [
    path('', include((app_urlpatterns, 'alfabank'), namespace='alfabank')),
]
