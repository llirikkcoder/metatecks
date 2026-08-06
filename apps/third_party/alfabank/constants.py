from apps.orders.constants import PaymentStatuses


# коды orderStatus из ответа getOrderStatusExtended.do -> наши статусы платежа
ALFA_STATUS_MAP = {
    0: PaymentStatuses.REGISTERED,   # заказ зарегистрирован, но не оплачен
    1: PaymentStatuses.AUTHORIZED,   # предавторизован (для двухстадийной оплаты)
    2: PaymentStatuses.PAID,         # авторизован полностью (списание подтверждено)
    3: PaymentStatuses.CANCELED,     # авторизация отменена
    4: PaymentStatuses.REFUNDED,     # по транзакции произведен возврат
    6: PaymentStatuses.DECLINED,     # авторизация отклонена
    7: PaymentStatuses.PENDING,      # заказ в очереди на автоматическое редактирование
}
