import json

from django.http import JsonResponse
from django.views.generic import View

from apps.addresses.models import Warehouse
from apps.addresses.constants import CHOSEN_CITY_ID, CHOSEN_WAREHOUSE_ID
from apps.utils.common import get_error_message


class ChooseWarehouseView(View):

    def post(self, request, *args, **kwargs):
        result = None
        try:
            body = request.body
            data = json.loads(request.body) if body else {}
            result = self.action(request, data)
        except ValueError:
            return JsonResponse({'result': 'error', 'error': 'Неправильный формат запроса'}, status=400)
        except Exception as exc:
            err_message = get_error_message(exc)
            return JsonResponse({'result': 'error', 'error': err_message}, status=400)

        response = {'result': 'ok'}
        if result:
            response.update(result)
        return JsonResponse(response)

    def action(self, request, data):
        warehouse_id = data['warehouse']
        current_url = data['current_url']
        redirect_url = current_url

        warehouse = Warehouse.objects.get(id=warehouse_id)
        city = warehouse.city

        request.session[CHOSEN_WAREHOUSE_ID] = warehouse.id
        request.session[CHOSEN_CITY_ID] = city.id

        if city != request.city:
            redirect_url = city.get_redirect_to(current_url)

        return {'redirect_url': redirect_url}
