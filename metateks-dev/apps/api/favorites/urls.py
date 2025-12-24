from django.urls import path

from .views import AddToFavoritesView, RemoveFromFavoritesView


urlpatterns = [
    path('add/', AddToFavoritesView.as_view(), name='add'),
    path('remove/', RemoveFromFavoritesView.as_view(), name='remove'),
]
