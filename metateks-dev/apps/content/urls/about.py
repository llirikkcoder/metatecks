from django.urls import path

from apps.content.views.about import (
    AboutPageView, VideoView, PhotoView, FilesView
)


urlpatterns = [
    path('', AboutPageView.as_view(), name='home'),
    path('video/', VideoView.as_view(), name='video'),
    path('photo/', PhotoView.as_view(), name='photo'),
    path('files/', FilesView.as_view(), name='files'),
    path('video/<slug:tag>/', VideoView.as_view(with_tag=True), name='video_tag'),
    path('photo/<slug:tag>/', PhotoView.as_view(with_tag=True), name='photo_tag'),
    path('files/<slug:tag>/', FilesView.as_view(with_tag=True), name='files_tag'),
]
