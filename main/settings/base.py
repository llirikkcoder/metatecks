from datetime import timedelta
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


load_dotenv()


def env_bool(key, _default=False):
    value = os.getenv(key, _default)
    return {
        'False': False,
        'True': True,
    }.get(value, bool(value))


def env_int(key, _default=None):
    value = None
    try:
        value = int(os.getenv(key, _default))
    except (TypeError, ValueError):
        pass
    return value


BASE_DIR = Path(__file__).resolve().parent.parent.parent

ADMINS = (
    ('Valentin Glinskiy', 'v@vlch.dev'),
)
MANAGERS = ADMINS


MEDIA_ROOT = str(BASE_DIR / 'media')
MEDIA_URL = 'media/'

STATIC_ROOT = str(BASE_DIR / 'static')
STATIC_URL = 'static/'
STATICFILES_DIRS = (str(BASE_DIR / 'assets'),)

INNER_STATIC_DIRS = ['css', 'fonts', 'images', 'js']
INNER_STATIC_URLPATTERNS = [
    (f'/{dir_name}/', str(BASE_DIR / 'assets' / dir_name))
    for dir_name in INNER_STATIC_DIRS
]

STATIC_URLS = [MEDIA_URL.strip('/'), STATIC_URL.strip('/')]
STATIC_URLS.extend(INNER_STATIC_DIRS)
STATIC_URLS_RE = '|'.join(STATIC_URLS)  # 'media|static|css|fonts|images|js'

FIXTURE_DIRS = (str(BASE_DIR / 'fixtures'),)

SECRET_KEY = os.getenv('SECRET_KEY', 'some_secret_key')


DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(' ')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
DEFAULT_SCHEME = os.getenv('DEFAULT_SCHEME', 'http')
DEFAULT_SITENAME = os.getenv('DEFAULT_SITENAME', 'localhost:8000')


INSTALLED_APPS = [
    'apps.third_party.suit_app',
    'apps.third_party.suit_app.config.SuitConfig',

    'django.contrib.admin',
    'apps.users.app.AuthConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'adminsortable2',
    'crequest',
    'django_extensions',
    'django_object_actions',
    'easy_thumbnails',
    'solo',
    'sorl.thumbnail',
    'galleryfield',
    'sortedm2m',
    'tinymce',
    'treenode',
    'watson',

    'apps.third_party.django_media_fixtures',

    'apps.users.app.UsersConfig',
    'apps.addresses.app.AddressesConfig',
    'apps.catalog.app.CatalogConfig',
    'apps.orders.app.OrdersConfig',
    'apps.settings.app.SettingsConfig',
    'apps.content.app.ContentConfig',
    'apps.media_content.app.MediaContentConfig',
    'apps.banners.app.BannersConfig',
    'apps.feedback.app.FeedbackConfig',
    'apps.promotions.app.PromotionsConfig',
    'apps.third_party.cml.app.CMLConfig',
    'apps.search',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'watson.middleware.SearchContextMiddleware',
    'apps.middleware.IsAjaxMiddleware',
    'apps.addresses.middleware.CurrentCityMiddleware',
    'apps.addresses.middleware.ChosenCityMiddleware',
    'crequest.middleware.CrequestMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR / 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # custom:
                'apps.content.context_processors.current_user',
                'apps.content.context_processors.header',
                'apps.content.context_processors.footer',
                'apps.settings.context_processors.settings',
                'apps.cart.context_processors.cart',
                'apps.addresses.context_processors.city_list',
            ],
            'debug': DEBUG,
        },
    },
]


AUTH_USER_MODEL = 'users.User'

ADMIN_SITE_HEADER = os.getenv('ADMIN_SITE_HEADER', 'Метатэкс')

TIME_INPUT_FORMATS = ['%H:%M',]

ROOT_URLCONF = 'main.urls'
WSGI_APPLICATION = 'main.wsgi.application'
ASGI_APPLICATION = 'main.asgi.application'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = ''

# APPEND_SLASH = True
# # REMOVE_SLASH = True

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
# FILE_UPLOAD_PERMISSIONS = 0755
# DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100mb


# Database configuration
# Use DATABASE_URL if provided (Docker/production), otherwise use SQLite (local development)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L10N = True
USE_TZ = True


SESSION_COOKIE_AGE = 31536000  # 1 year in seconds


SILENCED_SYSTEM_CHECKS = [
    'templates.E003',
    'gallery_field.I001',
]


# email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Метатэкс <noreply@metateks.ru>')


# # django-extensions
# SHELL_PLUS_IMPORTS = [
#     'from apps.utils.shell import *',
# ]


# logging
LOG_DIR = os.getenv('DJANGO_LOG_DIR', 'logs')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'normal': {
            # [2015-11-23 08:07:35,431: INFO/tasks]
            # 'format': '%(levelname)s %(message)s'
            'format': '[%(asctime)s: %(levelname)s/%(module)s] %(message)s'
        },
        'short': {
            'format': '[%(asctime)s: %(levelname)s] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'formatter': 'normal',
        },
        'errors_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['errors_file',],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# custom_loggers
LOGGING_KEYS = [
    'cml.sync', 'cml.tasks', 'cml.utils',
]
for k in LOGGING_KEYS:
    k2 = k.replace('.', '_')
    k3 = f'{k2}_file'
    LOGGING['handlers'][k3] = {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': os.path.join(LOG_DIR, f'{k2}.log'),
        'formatter': 'normal',
    }
    LOGGING['loggers'][k] = {
        'handlers': [k3, 'console', 'mail_admins'],
        'level': 'INFO',
    }


# redis + celery
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_IGNORE_RESULT = False


# django-tinymce
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'silver',
    'height': 500,
    # 'menubar': False,
    'menubar': True,
    'valid_styles': {'*': ''},
    'valid_elements': '*[*]',
    'plugins': 'advlist,autolink,lists,link,image,charmap,print,preview,anchor,'
    'searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,'
    'code,help,wordcount',
    'toolbar': 'undo redo | formatselect | '
    'bold italic backcolor | code | alignleft aligncenter '
    'alignright alignjustify | bullist numlist outdent indent | '
    'removeformat | help',
}


# django-galleryfield
DJANGO_GALLERY_FIELD_CONFIG = {
    'jquery_file_upload_ui_options': {
        'autoUpload': False,
        'imageMaxWidth': 2048,
        'imageMaxHeight': 2048,
        'loadImageFileTypes': r'/^image\/(gif|jpeg|png|bmp|webp|svg\+xml|x-icon)$/',
        'sequentialUploads': True,
        'acceptFileTypes': r'/(\.|\/)(png|gif|bmp|jpe?g|tif|ico|webp)$/i',
        'imageOrientation': True,
        'maxFileSize': 5 * 1024 ** 2,  # 5.0Mb
        'minFileSize': 0.0001 * 1024 ** 2,  # 0.0001Mb
        'disableImageResize': '/Android(?!.*Chrome)|Opera/.test(window.navigator '
                              '&& navigator.userAgent)',
    }
}

# easy-thumbnails
THUMBNAIL_ALIASES = {
    '': {
        'admin_list_image': {
            'upscale': False,
            'size': (120, 80),
            'quality': 85,
        },
        'homepage_news': {
            'upscale': False,
            'size': (660, 1121),
            'quality': 90,
        },
        'homepage_article': {
            'upscale': False,
            'size': (826, 620),
            'quality': 90,
        },
        'homepage_photo_thumb': {
            'upscale': True,
            'crop': 'smart',
            'size': (630, 420),
            'quality': 90,
        },
        'homepage_photo_big': {
            'upscale': False,
            'size': (1980, 1320),
            'quality': 90,
        },
        'homepage_team': {
            'upscale': False,
            'size': (2000, 1000),
            'quality': 90,
        },
        'homepage_brand': {
            'upscale': False,
            'size': (300, 300),
            'quality': 100,
        },
        'homepage_warehouse': {
            'upscale': True,
            'crop': 'center',
            'size': (380, 235),
            'quality': 90,
        },
        'homepage_manager': {
            'upscale': False,
            'size': (661, 881),
            'quality': 95,
        },
        'category_icon': {
            'upscale': False,
            'size': (150, 134),
            'quality': 95,
        },
        'category_cover': {
            'upscale': False,
            'size': (800, 800),
            'quality': 90,
        },
        'brand_logo': {
            'upscale': False,
            'size': (200, 200),
            'quality': 100,
        },
        'brand_photo': {
            'upscale': False,
            'size': (1920, 1080),
            'quality': 90,
        },
        'sub_category_list_photo': {
            'upscale': True,
            'crop': 'smart',
            'size': (576, 576),
            'quality': 90,
        },
        'sub_category_photo': {
            'upscale': True,
            'crop': 'smart',
            'size': (1350, 900),
            'quality': 90,
        },
        'product_list_photo': {
            'upscale': True,
            'crop': 'smart',
            'size': (576, 576),
            'quality': 90,
        },
        'product_micro_photo': {
            'upscale': True,
            'crop': 'smart',
            'size': (150, 150),
            'quality': 90,
        },
        'product_photos_thumb': {
            'upscale': True,
            'crop': 'smart',
            'size': (960, 540),
            'quality': 90,
        },
        'product_photos_big': {
            'upscale': False,
            'size': (1980, 1113),
            'quality': 95,
        },
        'product_gallery_thumb': {
            'upscale': True,
            'crop': 'smart',
            'size': (230, 129),
            'quality': 90,
        },
        'product_gallery_big': {
            'upscale': True,
            'crop': 'smart',
            'size': (1220, 686),
            'quality': 95,
        },
        'product_gallery_3d': {
            'upscale': True,
            'size': (700, 467),
            'quality': 95,
        },
        'banner_1200': {
            'upscale': True,
            'size': (1200, 570),
            'quality': 95,
        },
        'banner_670': {
            'upscale': True,
            'size': (670, 950),
            'quality': 95,
        },
        'banner_430': {
            'upscale': True,
            'crop': 'smart',
            'size': (430, 645),
            'quality': 95,
        },
        'promo_1920': {
            'upscale': True,
            'size': (1920, 720),
            'quality': 95,
        },
        'promo_695': {
            'upscale': True,
            'size': (695, 522),
            'quality': 95,
        },
        'about_advantage_photo': {
            'upscale': True,
            'crop': 'smart',
            'size': (768, 512),
            'quality': 95,
        },
        'about_advantage_gallery_thumb': {
            'upscale': True,
            'crop': 'smart',
            'size': (768, 512),
            'quality': 90,
        },
        'about_advantage_gallery_big': {
            'upscale': False,
            'size': (2000, 1500),
            'quality': 95,
        },
        'about_brand': {
            'upscale': False,
            'size': (300, 140),
            'quality': 100,
        },
        'about_people_photo': {
            'upscale': True,
            'size': (2000, 942),
            'quality': 95,
        },
        'about_photos_thumb': {
            'upscale': True,
            'crop': 'smart',
            'size': (768, 512),
            'quality': 90,
        },
        'about_photos_big': {
            'upscale': False,
            'size': (1980, 1400),
            'quality': 95,
        },
        'page_cover': {
            'upscale': False,
            'size': (1920, 1080),
            'quality': 95,
        },
        'news_cover_thumb': {
            'upscale': True,
            'crop': 'smart',
            'size': (720, 480),
            'quality': 90,
        },
        'articles_cover_thumb': {
            'upscale': True,
            'crop': 'smart',
            'size': (826, 620),
            'quality': 90,
        },
        'user_avatar_header': {
            'upscale': True,
            'crop': 'smart',
            'size': (50, 50),
            'quality': 90,
        },
        'user_avatar_account': {
            'upscale': True,
            'crop': 'smart',
            'size': (200, 200),
            'quality': 95,
        },
    },
}


# django-cml
CML_PROJECT_PIPELINES = 'apps.third_party.cml.pipelines'
CML_DELETE_FILES_AFTER_IMPORT = False


# django-watson
WATSON_POSTGRES_SEARCH_CONFIG = 'pg_catalog.russian'


# ipinfo.io
IPINFO_ACCESS_TOKEN = os.getenv('IPINFO_ACCESS_TOKEN', '')
