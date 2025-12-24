from django.utils.deprecation import MiddlewareMixin


class IsAjaxMiddleware(MiddlewareMixin):

    @staticmethod
    def _is_ajax(request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def process_request(self, request):
        request.is_ajax = self._is_ajax(request)
