from django.urls import path

from apps.catalog.views import BrandListView, BrandPageView


urlpatterns = [
    path('', BrandListView.as_view(), name='home'),
    path('<slug:brand>/', BrandPageView.as_view(), name='brand'),
]
