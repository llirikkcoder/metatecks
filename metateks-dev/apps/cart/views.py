from django.views.generic import TemplateView

from apps.orders.models import DeliveryCompany
from .utils import get_cart_data, get_order_data


class CartPageView(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_cart_data(self.request))
        context.update(get_order_data(self.request))
        context['delivery_companies'] = DeliveryCompany.shown()
        return context
