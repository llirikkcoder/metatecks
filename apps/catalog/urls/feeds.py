from django.urls import path

from apps.catalog.views.feeds import products_feed, models_feed, models_work_feed


urlpatterns = [
    path('products.xml', products_feed, name='products'),
    path('models.xml', models_feed, name='models'),
    path('models-work.xml', models_work_feed, name='models_work'),
]
