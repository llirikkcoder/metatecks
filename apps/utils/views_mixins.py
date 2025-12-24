import json

from django.http import JsonResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.urls import reverse

from apps.utils.common import get_error_message


class JsonFormViewMixin(object):
    custom_mapping = None
    form = None

    def get(self, request, *args, **kwargs):
        # GET not allowed
        return HttpResponse(status=405)

    def dispatch(self, request, *args, **kwargs):
        self.errors = []
        self.mapping = self.get_mapping()
        self.reverse_mapping = self.get_reverse_mapping()

        if self.request.method == 'POST':
            self.JSON_POST = {}
            if not self.request.is_ajax:
                self.JSON_POST = self.get_json_post_data()
            else:
                try:
                    self.JSON_POST = json.loads(request.body.decode('utf-8'))
                except Exception as e:
                    err_message = get_error_message(e)
                    error = {'name': '__all__', 'error_message': 'Ошибка при парсинге запроса: {}'.format(err_message)}
                    data = {'errors': [error]}
                    return JsonResponse(data, status=400)
            self.POST = self.get_post_data()

        response = super().dispatch(request, *args, **kwargs)

        if isinstance(response, JsonResponse) and not self.request.is_ajax:
            data = json.loads(response.content)
            redirect_url = data.get('redirect_url', reverse('home'))
            return HttpResponseRedirect(redirect_url)
        return response

    def get_mapping(self):
        mapping = {}
        form_class = (
            self.get_form_class()
            if hasattr(self, 'get_form_class')
            else None
        )
        if form_class:
            for k in form_class.base_fields.keys():
                mapping[k] = k
        custom_mapping = getattr(self, 'custom_mapping', {})
        if custom_mapping:
            for k, v in custom_mapping.items():
                mapping[k] = v
        return mapping

    def get_reverse_mapping(self):
        return {value: key for key, value in self.mapping.items()}

    def get_json_post_data(self):
        POST = self.request.POST
        JSON_POST = {}
        for key in POST.keys():
            if key != 'csrfmiddlewaretoken':
                value = POST.getlist(key)
                if len(value)>1:
                    JSON_POST[key] = value
                elif value:
                    JSON_POST[key] = value[0]
        return JSON_POST

    def get_post_data(self):
        POST = QueryDict(mutable=True)
        for key, value in self.JSON_POST.items():
            post_key = self.mapping.get(key, key)
            if isinstance(value, list):
                for val in value:
                    POST.appendlist(post_key, val)
            else:
                POST.appendlist(post_key, value)
        return POST

    def get_form_kwargs(self):
        kwargs = super(JsonFormViewMixin, self).get_form_kwargs()
        kwargs['data'] = self.POST  # instead of default "self.request.POST"
        return kwargs

    def do_response(self, request, *args, **kwargs):
        if len(self.errors):
            return self.form_invalid(self.form)
        return JsonResponse({'result': 'ok'}, status=200)

    def form_invalid(self, form=None):
        errors = self.errors
        if form:
            for k in form.errors:
                name = self.reverse_mapping.get(k, k)
                errors.append({'name': name, 'error_message': form.errors[k][0]})
        return JsonResponse({'errors': errors}, status=400)

    def _add_error(self, error, field_name='__all__'):
        self.errors.append({'name': field_name, 'error_message': error})
