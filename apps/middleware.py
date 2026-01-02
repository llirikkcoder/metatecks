from django.utils.deprecation import MiddlewareMixin


class IsAjaxMiddleware(MiddlewareMixin):

    @staticmethod
    def _is_ajax(request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def process_request(self, request):
        request.is_ajax = self._is_ajax(request)


class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """Отключает CSRF проверку для API эндпоинта выбора склада"""

    def process_request(self, request):
        if request.path == '/api/addresses/choose_warehouse/':
            setattr(request, '_dont_enforce_csrf_checks', True)
