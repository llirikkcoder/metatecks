from django.urls import include, path


urlpatterns = [
    path('auth/', include(('apps.api.auth.urls', 'auth'))),
    path('cart/', include(('apps.api.cart.urls', 'cart'))),
    path('order/', include(('apps.api.order.urls', 'order'))),
    path('account/', include(('apps.api.account.urls', 'account'))),
    path('favorites/', include(('apps.api.favorites.urls', 'favorites'))),
    path('addresses/', include(('apps.api.addresses.urls', 'addresses'))),
]
