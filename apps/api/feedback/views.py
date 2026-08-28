from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import CreateView

from apps.addresses.geo_utils import get_ip_from_request
from apps.feedback.models import CallbackRequest
from apps.third_party.bitrix24.tasks import sync_callback_with_bitrix24
from apps.utils.views_mixins import JsonFormViewMixin
from .forms import CallbackForm


class CallbackView(JsonFormViewMixin, CreateView):
    """
    Заявка «Заказать звонок» из модального окна. Сохраняем CallbackRequest
    и асинхронно создаём лид в Битрикс24 (без вебхука синк — тихий no-op).
    """
    form_class = CallbackForm
    model = CallbackRequest

    def get_success_url(self):
        # чтобы Django не ругалась
        return reverse('home')

    def form_valid(self, form):
        callback = form.save(commit=False)
        if self.request.user.is_authenticated:
            callback.user = self.request.user
        callback.ip_address = get_ip_from_request(self.request)
        callback.save()

        sync_callback_with_bitrix24.delay(callback.id)

        return JsonResponse({'result': 'ok'})
