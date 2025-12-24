from django.urls import path

from apps.content.views.articles import ArticlesView, ArticlePostView


urlpatterns = [
    path('', ArticlesView.as_view(), name='home'),
    path('<slug:category>/', ArticlesView.as_view(with_category=True), name='category'),
    path('<post_date:date>/<slug:slug>/', ArticlePostView.as_view(), name='post'),
]
