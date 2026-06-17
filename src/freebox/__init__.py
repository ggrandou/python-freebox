from freebox.auth import Auth, AuthorizationStatus
from freebox.client import Freebox
from freebox.discovery import DiscoveryInfo, discover, discover_http, discover_mdns, discover_remote_port
from freebox.exceptions import (
    AppsDenied,
    AuthenticationError,
    AuthorizationDenied,
    AuthorizationTimeout,
    DeniedFromExternalIP,
    FreeboxError,
    InsufficientRightsError,
    RateLimited,
    TokenRevoked,
)

__all__ = [
    # Client
    "Freebox",
    # Auth
    "Auth",
    "AuthorizationStatus",
    # Discovery
    "DiscoveryInfo",
    "discover",
    "discover_http",
    "discover_mdns",
    "discover_remote_port",
    # Exceptions
    "FreeboxError",
    "AuthenticationError",
    "AuthorizationDenied",
    "AuthorizationTimeout",
    "TokenRevoked",
    "InsufficientRightsError",
    "DeniedFromExternalIP",
    "RateLimited",
    "AppsDenied",
]
