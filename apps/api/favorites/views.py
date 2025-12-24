import json

from django.http import JsonResponse
from django.views.generic import View

from apps.users.favorites_utils import add_to_favorites, remove_from_favorites
from apps.utils.common import get_error_message


class FavoritesBaseAPIView(View):
    action = None

    def post(self, request, *args, **kwargs):
        try:
            body = request.body
            data = json.loads(request.body) if body else {}
            product_id = data['product_id']
            action_method = {
                'add': add_to_favorites,
                'remove': remove_from_favorites,
            }[self.action]
            action_method(request, product_id)
        except ValueError:
            return JsonResponse({'result': 'error', 'error': 'Неправильный формат запроса'}, status=400)
        except Exception as exc:
            err_message = get_error_message(exc)
            return JsonResponse({'result': 'error', 'error': err_message}, status=400)
        return JsonResponse({'result': 'ok'})


class AddToFavoritesView(FavoritesBaseAPIView):
    action = 'add'


class RemoveFromFavoritesView(FavoritesBaseAPIView):
    action = 'remove'
