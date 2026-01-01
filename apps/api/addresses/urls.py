from django.urls import path

from .views import choose_warehouse_view


urlpatterns = [
    path('choose_warehouse/', choose_warehouse_view, name='choose-warehouse'),
]
