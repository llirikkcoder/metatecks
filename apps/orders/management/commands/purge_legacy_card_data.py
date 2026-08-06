from django.core.management.base import BaseCommand

from apps.orders.models import OrderPaymentCardData, UserPaymentCard


class Command(BaseCommand):
    help = (
        'Удаляет legacy-данные карт (card_number/card_cvv/card_expire), собранные до '
        'перехода на hosted-оплату Альфа-Банка. По умолчанию — только dry-run.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes', action='store_true',
            help='Реально удалить записи (без флага — только подсчёт, ничего не удаляется).',
        )

    def handle(self, *args, **options):
        card_qs = OrderPaymentCardData.objects.all()
        user_card_qs = UserPaymentCard.objects.all()

        self.stdout.write(f'OrderPaymentCardData: {card_qs.count()} записей')
        self.stdout.write(f'UserPaymentCard: {user_card_qs.count()} записей')

        if not options['yes']:
            self.stdout.write(self.style.WARNING(
                'Dry-run: ничего не удалено. Запустите с --yes для реального удаления.'
            ))
            return

        confirm = input('Это необратимо. Подтвердите удаление, набрав "DELETE": ')
        if confirm != 'DELETE':
            self.stdout.write('Отменено.')
            return

        deleted_cards = card_qs.delete()
        deleted_user_cards = user_card_qs.delete()
        self.stdout.write(self.style.SUCCESS(
            f'Удалено: OrderPaymentCardData={deleted_cards}, UserPaymentCard={deleted_user_cards}'
        ))
