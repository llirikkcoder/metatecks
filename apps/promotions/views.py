from django.views.generic import ListView

from .models import Promotion


class PromotionsView(ListView):
    model = Promotion
    context_object_name = 'promo'
    template_name = 'promotions.html'

    def get_queryset(self, **kw):
        return Promotion.objects.active()       
