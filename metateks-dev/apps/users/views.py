from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class BaseAccountView(LoginRequiredMixin, TemplateView):
    login_url = '/?p=login'

    def get_data(self):
        return {}

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = {'user': user}
        context.update(self.get_data(user=user))
        context.update(super().get_context_data(**kwargs))
        return context


class AccountHomeView(BaseAccountView):
    template_name = 'account/account_home.html'

    def get_data(self, user, **kwargs):
        card = user.payment_cards.first()
        orders = user.get_orders()
        orders_count = orders.count()
        order = orders.first()
        favorites = user.get_favorites()
        return {
            'card': card,
            'orders_count': orders_count,
            'order': order,
            'favorites': favorites,
        }


class AccountOrdersView(BaseAccountView):
    template_name = 'account/account_orders.html'

    def get_data(self, user, **kwargs):
        orders = user.get_orders()\
                     .prefetch_related(
                         'items',
                         'items__product',
                         'items__product__sub_category',
                     )\
                     .all()\
                     .order_by('-updated_at')
        last_order = orders.first()
        last_canceled_order = orders.filter(is_canceled=True)\
                                    .order_by('-canceled_at')\
                                    .first()
        return {
            'orders': orders,
            'last_order': last_order,
            'last_canceled_order': last_canceled_order,
        }


class AccountAddressesView(BaseAccountView):
    template_name = 'account/account_addresses.html'

    def get_data(self, user, **kwargs):
        addresses = user.addresses.all()
        return {
            'addresses': addresses,
        }


class AccountFavoritesView(BaseAccountView):
    template_name = 'account/account_favorites.html'

    def get_data(self, user, **kwargs):
        favorites = user.get_favorites()
        return {
            'favorites': favorites,
        }


class AccountProfileView(BaseAccountView):
    template_name = 'account/account_profile.html'

    def get_data(self, user, **kwargs):
        orders = user.get_orders()

        payment_methods = set(orders.values_list('payment_method', flat=True))
        cards = user.payment_cards.all()
        cashless_data = getattr(user, 'payment_cashless_data', None)

        return {
            'payment_methods': payment_methods,
            'cards': cards,
            'cashless_data': cashless_data,
        }
