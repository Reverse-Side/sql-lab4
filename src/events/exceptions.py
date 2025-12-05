class EventException(Exception):
    """Базовий виняток для всіх помилок модуля Events."""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)

class EventNotFoundError(EventException):
    """Виняток, коли подію не знайдено."""
    def __init__(self, detail: str = "Подію не знайдено."):
        super().__init__(detail, status_code=404)

class EventPermissionError(EventException):
    """Виняток, коли користувач не має прав для виконання дії."""
    def __init__(self, detail: str = "Недостатньо прав для виконання дії. Ви можете змінювати лише власні події."):
        super().__init__(detail, status_code=403)