from django.urls import path

from apps.content.views.news import NewsView, NewsPostView


urlpatterns = [
    path('', NewsView.as_view(), name='home'),
    path('<int:year>/', NewsView.as_view(with_year=True), name='year'),
    path('<slug:category>/', NewsView.as_view(with_category=True), name='category'),
    path('<int:year>/<slug:category>/', NewsView.as_view(with_year=True, with_category=True), name='year_category'),
    path('<post_date:date>/<slug:slug>/', NewsPostView.as_view(), name='post'),
]
