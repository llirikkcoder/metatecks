import os

from dotenv import load_dotenv


load_dotenv()

# Безопасный дефолт: без явного указания окружение считается боевым.
# Раньше дефолтом был 'local', и забытая переменная включала на проде
# режим отладки со всеми трассировками наружу (исправлено 14.09.2026).
DJANGO_ENV = os.getenv('DJANGO_ENV', 'prod')


# settings base
from .base import *  # noqa

if DJANGO_ENV in ('local', 'dev'):
    DEBUG = True
    ALLOWED_HOSTS = ['*']
else:
    # Любое иное значение, включая 'prod' и 'production', — боевой режим.
    DEBUG = False


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
