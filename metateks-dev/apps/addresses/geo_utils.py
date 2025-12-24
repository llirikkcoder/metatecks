from django.conf import settings

from ipware import get_client_ip
import ipinfo

from .models import City


ipinfo_handler = ipinfo.getHandler(settings.IPINFO_ACCESS_TOKEN)


def get_ip_from_request(request):
    ip, _ = get_client_ip(request)
    return ip


def get_city_from_request(ip=None, request=None):
    city = None
    assert (ip or request) is not None
    try:
        if not ip:
            ip = get_ip_from_request(request)
        ip_details = ipinfo_handler.getDetails(ip)
        _city = ip_details.city
        city = City.objects.filter(names_en__contains=[_city]).first()
        if not city:
            _region = ip_details.region
            city = City.objects.filter(region_names_en__contains=[_region]).first()
    except Exception:
        pass
    return city
