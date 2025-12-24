from .models import FavoriteProduct


__all__ = [
    'is_in_favorites',
    'add_to_favorites',
    'remove_from_favorites',
    'update_favorites_after_login',
]

FAV_KEY = 'favorites'


def _get_session_favorites(request):
    return request.session.get(FAV_KEY, [])


def _get_user_favorites(request):
    user = request.user
    if user.is_authenticated:
        fav_ids = user.favorites.all().values_list('product_id', flat=True)
        fav_ids = list(fav_ids)
        return fav_ids


def _get_favorites(request):
    if FAV_KEY in request.session:
        return _get_session_favorites(request)

    fav_ids = []
    user = request.user
    if user.is_authenticated:
        fav_ids = _get_user_favorites(request)

    request.session[FAV_KEY] = fav_ids
    return fav_ids


def is_in_favorites(request, product_id):
    fav_ids = _get_favorites(request)
    return product_id in fav_ids


def add_to_favorites(request, product_id):
    fav_ids = _get_favorites(request)
    if product_id not in fav_ids:
        fav_ids.insert(0, product_id)
        request.session[FAV_KEY] = fav_ids
        user = request.user
        if user.is_authenticated:
            FavoriteProduct.add(user, product_id)


def remove_from_favorites(request, product_id):
    fav_ids = _get_favorites(request)
    if product_id in fav_ids:
        fav_ids.remove(product_id)
        request.session[FAV_KEY] = fav_ids
        user = request.user
        if user.is_authenticated:
            FavoriteProduct.remove(user, product_id)


def update_favorites_after_login(request):
    fav_ids1 = _get_session_favorites(request)
    fav_ids2 = _get_user_favorites(request)
    user = request.user

    for product_id in reversed(fav_ids1):
        if product_id not in fav_ids2:
            FavoriteProduct.add(user, product_id)

    if FAV_KEY in request.session:
        del request.session[FAV_KEY]
