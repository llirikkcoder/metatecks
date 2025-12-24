from django.urls import path

from .views import ChooseWarehouseView


urlpatterns = [
    path('choose_warehouse/', ChooseWarehouseView.as_view(), name='choose-warehouse'),
]
