from django.conf import settings
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.safestring import mark_safe

from crequest.middleware import CrequestMiddleware


DEFAULT_SCHEME = settings.DEFAULT_SCHEME
DEFAULT_SITENAME = settings.DEFAULT_SITENAME
MEDIA_URL = settings.MEDIA_URL


def get_error_message(e, with_class=True):
    try:
        err_message = e.args[0]
    except (TypeError, IndexError):
        try:
            err_message = str(e).decode('utf-8')
        except AttributeError:
            err_message = str(e)
        except Exception:
            err_message = repr(e)

    err_class = e.__class__.__name__
    try:
        err_message = (
            '{}: {}'.format(err_class, err_message)
            if (with_class is True and err_message and err_class != 'Exception')
            else err_message
            if err_message
            else err_class
        )
    except UnicodeDecodeError:
        err_message = err_class
    return err_message


def get_current_request():
    return CrequestMiddleware.get_request()


def get_current_user(request=None):
    request = request or get_current_request()
    return request.user if (request and request.user.is_authenticated) else None


def get_current_city(request=None):
    from apps.addresses.models import City
    request = get_current_request()
    return request.city or City.get_default()


def get_site_url():
    request = get_current_request()
    site = ''
    try:
        site = '{}://{}'.format(request.scheme, request.get_host())
    except AttributeError:
        site = '{}://{}'.format(DEFAULT_SCHEME, DEFAULT_SITENAME)
    else:
        if not site:
            site = '{}://{}'.format(DEFAULT_SCHEME, DEFAULT_SITENAME)
    return site


def get_current_admin_object(model, request=None):
    request = request or get_current_request()
    obj = None

    if request:
        obj_id = None
        _path = request.path.split('/')[::-1]
        for _p in _path:
            try:
                obj_id = int(_p)
                break
            except Exception:
                pass
        try:
            obj = model.objects.get(id=obj_id)
        except Exception:
            pass
    return obj


def get_admin_url(obj):
    # FROM: django.contrib.admin.views.main.Changelist.url_for_result()
    opts = obj.__class__._meta
    return reverse(
        'admin:%s_%s_change' % (opts.app_label, opts.model_name),
        args=(quote(obj.pk),)
    )


def absolute(url=None, append_media_url=False, append_subdomain=True):
    media_url = MEDIA_URL if append_media_url else ''
    if url and not url.startswith('http'):
        _subdomain = ''
        if append_subdomain is True:
            request = get_current_request()
            if request.city and request.city.subdomain:
                _subdomain = f'{request.city.subdomain}.'
        url = (
            '{}://{}{}{}{}'.format(DEFAULT_SCHEME, _subdomain, DEFAULT_SITENAME, media_url, url)
            if url
            else None
        )
    return url


def bool_to_icon(value):
    if value not in [True, False, None]:
        value = bool(value)
    return mark_safe(_boolean_icon(value))
