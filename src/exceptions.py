class RepositoryError(Exception):
    """Базовий клас помилок репозиторію."""


class EntityNotFoundError(RepositoryError):
    """Об’єкт не знайдено."""


class IntegrityRepositoryError(RepositoryError):
    """Помилка цілісності даних."""


class InvalidQueryError(RepositoryError):
    """Некоректні параметри фільтрації або запиту."""
