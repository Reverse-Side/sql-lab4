class AuthServiceError(Exception):
    """Base exception for user service errors."""

    pass


class LoginError(AuthServiceError):
    pass


class RegistrationError(AuthServiceError):
    """Exception raised during user registration errors."""

    pass


class AuthenticationError(AuthServiceError):
    """Exception raised during user authentication errors."""

    pass

class InvalidRefreshToken(AuthServiceError):
    pass