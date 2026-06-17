class FreeboxError(Exception):
    """Base exception for all Freebox API errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


class AuthenticationError(FreeboxError):
    """Session token is missing, invalid, or expired."""


class TokenRevoked(FreeboxError):
    """App token has been revoked by the user; re-registration is required."""


class AuthorizationDenied(FreeboxError):
    """User denied the authorization request on the Freebox front panel."""


class AuthorizationTimeout(FreeboxError):
    """User did not respond to the authorization request in time."""


class InsufficientRightsError(FreeboxError):
    """App permissions do not allow accessing this API."""


class DeniedFromExternalIP(FreeboxError):
    """App registration is only allowed from the local network."""


class RateLimited(FreeboxError):
    """Too many failed authentication attempts from this IP."""


class AppsDenied(FreeboxError):
    """API access from third-party apps has been disabled on this Freebox."""
