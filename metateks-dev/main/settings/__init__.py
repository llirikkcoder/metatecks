import os

from dotenv import load_dotenv


load_dotenv()

DJANGO_ENV = os.getenv('DJANGO_ENV', 'local')


# settings base
from .base import *  # noqa

try:
    if DJANGO_ENV in ['local', 'dev']:
        DEBUG = True
        ALLOWED_HOSTS = ['*']
    elif DJANGO_ENV == 'prod':
        DEBUG = False
except ImportError:
    pass


# settings local
try:
    from .local import *  # noqa
except ImportError:
    pass

# necessary settings
SESSION_COOKIE_DOMAIN = f'.{DEFAULT_SITENAME}'

# settings fixes
try:
    TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
except NameError:
    pass
