from .models import City


def city_list(request):
    # city = getattr(request, 'city', None)
    cities = City.objects.prefetch_related('warehouses')\
                         .filter(warehouses__isnull=False)\
                         .distinct()
    # cities = (
    #     *cities.filter(id=city.id),
    #     *cities.exclude(id=city.id),
    # )
    return {'city_list': cities}
