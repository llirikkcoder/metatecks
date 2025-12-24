from django.urls import path

from .views import LoginView, LogoutView, RegistrationView, ResetPasswordView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
]
