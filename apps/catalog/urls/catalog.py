from django.urls import path

from apps.catalog.views import CatalogHomeView, CategoryView, SubCategoryView, ProductView, ProductLinkView


urlpatterns = [
    path('', CatalogHomeView.as_view(), name='home'),
    path('p/<int:product_id>/', ProductLinkView.as_view(), name='product-link'),
    path('<slug:category>/', CategoryView.as_view(), name='category'),
    path('<slug:category>/<slug:sub_category>/', SubCategoryView.as_view(), name='sub_category'),
    path('<slug:category>/<slug:sub_category>/filter/', SubCategoryView.as_view(force_filter=True), name='sub_category_filter'),
    path('<slug:category>/<slug:sub_category>/model<int:model_id>/', SubCategoryView.as_view(with_model=True), name='model'),
    path('<slug:category>/<slug:sub_category>/<slug:product>-<int:product_id>/', ProductView.as_view(), name='product'),
    path('<slug:category>/<slug:sub_category>/<slug:brand>/', SubCategoryView.as_view(with_brand=True), name='sub_category_brand'),
]
