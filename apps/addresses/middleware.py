import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

from .constants import (
    CHOSEN_CITY_ID, RESET_CITY_PARAM, CHOSEN_WAREHOUSE_ID, RESET_WAREHOUSE_PARAM
)
from .geo_utils import get_city_from_request
from .models import City, Warehouse


ADMIN_OR_STATIC = re.compile(f'^/(admin|{settings.STATIC_URLS_RE})/*')


def is_request_static(request):
    # TODO: не проверять, если зашел бот
    return re.match(ADMIN_OR_STATIC, request.path)


def get_subdomain(request):
    return request.get_host().split(settings.DEFAULT_SITENAME)[0].strip('.')


class CurrentCityMiddleware(MiddlewareMixin):
    """
    1) Берем город из текущего поддомена и сохраняем в реквесте
    2) Сохраняем в реквесте склад (из сессии или из города)
    """

    def _get_city(self, request):
        subdomain = get_subdomain(request)
        return City.objects.filter(subdomain=subdomain).first() or City.get_default()

    def _get_warehouse(self, request, city):
        warehouse = None
        warehouse_id = (
            request.session.get(CHOSEN_WAREHOUSE_ID, None)
            if not RESET_WAREHOUSE_PARAM in request.GET
            else None
        )
        if warehouse_id:
            try:
                warehouse = Warehouse.objects.filter(id=warehouse_id, city=city).first()
            except:
                pass
        return warehouse or city.warehouses.first()

    def process_request(self, request):
        if is_request_static(request):
            return
        request.city = self._get_city(request) or City.get_default()
        if request.city:
            request.city_id = request.city.id 
            _warehouse_ids = request.city.warehouses.values_list('id', flat=True)
            request.city_warehouses = list(_warehouse_ids)
            request.warehouse = self._get_warehouse(request, city=request.city)


class ChosenCityMiddleware(MiddlewareMixin):
    """
    Если посетитель заходит на главный поддомен (и в первый раз на нашем сайте):
        - определяем по геолокации его город;
        - редиректим на поддомен
    """

    def process_request(self, request):
        if is_request_static(request):
            return
        chosen_city_id = request.session.get(CHOSEN_CITY_ID, None)
        if (
            get_subdomain(request) == ''
            and (not chosen_city_id or RESET_CITY_PARAM in request.GET)
        ):
            default_city = City.get_default()
            city = get_city_from_request(request=request)
            request.session[CHOSEN_CITY_ID] = city.id if city else default_city.id
            if city and default_city != city:
                path = request.get_full_path()
                redirect_to = city.get_redirect_to(path)
                return HttpResponseRedirect(redirect_to)
