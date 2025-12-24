from django.urls import path
from django.views.generic import RedirectView

from .views import (
    AccountHomeView, AccountOrdersView, AccountAddressesView, AccountFavoritesView, AccountProfileView,
)


urlpatterns = [
    path('', AccountHomeView.as_view(), name='home'),
    path('orders/', AccountOrdersView.as_view(), name='orders'),
    path('addresses/', AccountAddressesView.as_view(), name='addresses'),
    path('favorites/', AccountFavoritesView.as_view(), name='favorites'),
    path('profile/', AccountProfileView.as_view(), name='profile'),
    path('logout/', RedirectView.as_view(pattern_name='api:auth:logout', query_string=True), name='logout'),
]
