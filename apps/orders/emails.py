import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.template.loader import render_to_string

from apps.utils.common import absolute, get_admin_url


l = logging.getLogger('orders.emails')


def _contacts(order):
    contacts = getattr(order, 'contacts_data', None)
    return {
        'contacts_name': contacts.name if contacts else '',
        'contacts_phone': contacts.phone if contacts else '',
    }


def _user_email(order):
    return getattr(order.user, 'email', None)


def send_order_paid_email(order):
    context = {'order': order, **_contacts(order)}

    to_email = _user_email(order)
    if to_email:
        html_body = render_to_string('emails/order_paid.html', context)
        message = EmailMultiAlternatives(
            subject=f'Заказ № {order.number} оплачен',
            body=f'Заказ № {order.number} на сумму {order.total_cost} ₽ успешно оплачен.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=True)
    else:
        l.warning('[orders] order #%d paid, but user has no email — user notification skipped', order.id)

    admin_body = render_to_string('emails/admin_order_paid.txt', {
        **context, 'admin_url': absolute(get_admin_url(order)),
    })
    mail_admins(f'Заказ № {order.number} оплачен', admin_body, fail_silently=True)


def send_payment_failed_email(order):
    to_email = _user_email(order)
    if not to_email:
        l.warning('[orders] order #%d payment failed, but user has no email — notification skipped', order.id)
        return

    context = {'order': order, **_contacts(order)}
    html_body = render_to_string('emails/order_payment_failed.html', context)
    message = EmailMultiAlternatives(
        subject=f'Не удалось оплатить заказ № {order.number}',
        body=f'Оплата заказа № {order.number} на сумму {order.total_cost} ₽ не была завершена.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=True)
