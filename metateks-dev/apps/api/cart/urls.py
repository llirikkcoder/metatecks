from django.urls import path

from .views import UpdateItemView, UpdateExtraItemView, GroupToggleView, ClearCartView


urlpatterns = [
    path('update_item/', UpdateItemView.as_view(), name='update-item'),
    path('update_extra_item/', UpdateExtraItemView.as_view(), name='update-extra-item'),
    path('group_toggle/', GroupToggleView.as_view(), name='group-toggle'),
    path('clear_cart/', ClearCartView.as_view(), name='clear-cart'),
]
