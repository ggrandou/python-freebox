class FreeboxError(Exception):
    """Base exception for all Freebox API errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


class AuthenticationError(FreeboxError):
    """Raised when authentication fails."""


class InsufficientRightsError(FreeboxError):
    """Raised when the app lacks permission for the requested API."""


class TokenRevoked(FreeboxError):
    """Raised when the app token has been revoked."""
