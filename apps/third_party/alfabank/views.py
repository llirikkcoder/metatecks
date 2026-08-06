import logging

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.orders.models import Order, Payment

from .exceptions import AlfaBankError
from .services import sync_payment_status


l = logging.getLogger('alfabank.views')


@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookView(View):
    """
    Точка входа для колбэка Альфа-Банка (если настроен в личном кабинете мерчанта).
    Статусу из тела запроса не доверяем — перепроверяем через getOrderStatusExtended.do.
    """

    def post(self, request, *args, **kwargs):
        alfa_order_id = request.POST.get('orderId') or request.POST.get('mdOrder')
        if not alfa_order_id:
            l.warning('[alfabank] webhook: no orderId/mdOrder in payload: %s', request.POST.dict())
            return HttpResponse(status=400)

        payment = Payment.objects.filter(alfa_order_id=alfa_order_id).order_by('-created_at').first()
        if not payment:
            l.warning('[alfabank] webhook: unknown alfa_order_id=%s', alfa_order_id)
            return HttpResponse(status=400)

        try:
            sync_payment_status(payment)
        except AlfaBankError as exc:
            l.error('[alfabank] webhook: sync failed for alfa_order_id=%s: %s', alfa_order_id, exc.message)
            return HttpResponse(status=502)

        return HttpResponse('OK')


class PaymentReturnView(View):
    """returnUrl — пользователь вернулся в браузере после оплаты."""

    def get(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        payment = order.active_payment

        if payment:
            try:
                sync_payment_status(payment)
            except AlfaBankError as exc:
                l.error('[alfabank] return: sync failed for order #%s: %s', order_id, exc.message)

        order.refresh_from_db()
        if order.is_paid:
            return redirect(order.get_created_url())
        return redirect(order.get_awaiting_payment_url())


class PaymentFailView(View):
    """failUrl — банк сообщил об отказе/отмене оплаты пользователем."""

    def get(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        payment = order.active_payment

        if payment:
            try:
                sync_payment_status(payment)
            except AlfaBankError as exc:
                l.error('[alfabank] fail: sync failed for order #%s: %s', order_id, exc.message)

        order.refresh_from_db()
        if order.is_paid:
            return redirect(order.get_created_url())
        return redirect(order.get_awaiting_payment_url())
