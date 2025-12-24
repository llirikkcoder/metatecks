from django.apps import AppConfig
from django.contrib.auth.apps import AuthConfig as _AuthConfig


class UsersConfig(AppConfig):
    name = 'apps.users'
    verbose_name = 'Пользователи'


class AuthConfig(_AuthConfig):
    verbose_name = 'Пользователи'
