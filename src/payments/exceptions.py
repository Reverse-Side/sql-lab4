# =========================================================
# 1. ВИЗНАЧЕННЯ ВЛАСНИХ ВИКЛЮЧЕНЬ
# =========================================================
class PaymentServiceError(Exception):
    """Базовий виняток для всіх помилок платіжного сервісу."""

    pass


class TicketNotFoundError(PaymentServiceError):
    """Виняток, коли квиток не знайдено."""

    pass


class TicketAlreadyPaidError(PaymentServiceError):
    """Виняток, коли квиток вже оплачено."""

    pass


class NotEnoughFundsError(PaymentServiceError):
    """Виняток, коли сума платежу недостатня."""

    pass


class AccessDeniedError(PaymentServiceError):
    """Виняток, коли користувач не має доступу до квитка."""

    pass


# =========================================================
