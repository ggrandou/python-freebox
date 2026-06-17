"""App-token registration and session lifecycle management."""
from __future__ import annotations

import hashlib
import hmac
import time
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

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


class AuthorizationStatus(str, Enum):
    UNKNOWN = "unknown"
    PENDING = "pending"
    TIMEOUT = "timeout"
    GRANTED = "granted"
    DENIED  = "denied"


def _default_prompt(message: str) -> None:
    print(message)


# Type alias for the internal request callable passed from the client.
_RequestFn = Callable[..., Any]


class Auth:
    """Manages Freebox app-token and session-token lifecycle.

    The caller supplies a ``request`` callable matching the signature::

        request(method, path, *, authenticated=True, json=None) -> Any

    This keeps Auth decoupled from the HTTP transport.
    """

    POLL_INTERVAL: float = 2.0

    def __init__(
        self,
        app_id: str,
        app_name: str,
        app_version: str,
        device_name: str,
        token_file: Path | None = None,
        on_pending: Callable[[str], None] | None = None,
    ) -> None:
        self.app_id = app_id
        self.app_name = app_name
        self.app_version = app_version
        self.device_name = device_name
        self.token_file = token_file
        self.on_pending: Callable[[str], None] = on_pending or _default_prompt

        self.app_token: str | None = None
        self.session_token: str | None = None
        self.permissions: dict[str, bool] = {}

    # ── Token persistence ──────────────────────────────────────────────────────

    def load_token(self) -> bool:
        """Load app_token from file. Returns True if a token was found."""
        if not self.token_file:
            return False
        path = self.token_file.expanduser()
        if not path.exists():
            return False
        token = path.read_text().strip()
        if not token:
            return False
        self.app_token = token
        return True

    def save_token(self, token: str) -> None:
        """Persist app_token to disk with restricted permissions (0o600)."""
        self.app_token = token
        if not self.token_file:
            return
        path = self.token_file.expanduser()
        path.write_text(token)
        path.chmod(0o600)

    def clear_token(self) -> None:
        """Remove the stored app_token from memory and disk."""
        self.app_token = None
        if self.token_file:
            path = self.token_file.expanduser()
            if path.exists():
                path.unlink()

    # ── Registration ───────────────────────────────────────────────────────────

    def register(self, request: _RequestFn) -> None:
        """Request app authorization and block until the user grants it.

        Displays a prompt via ``on_pending`` while waiting. Raises an
        appropriate exception if the user denies, times out, or if
        registration is not permitted.
        """
        result = request(
            "POST",
            "login/authorize/",
            authenticated=False,
            json={
                "app_id":      self.app_id,
                "app_name":    self.app_name,
                "app_version": self.app_version,
                "device_name": self.device_name,
            },
        )
        track_id: int = result["track_id"]
        app_token: str = result["app_token"]

        self.on_pending("Please grant access on the Freebox front panel…")

        while True:
            status_result = request(
                "GET",
                f"login/authorize/{track_id}",
                authenticated=False,
            )
            status = AuthorizationStatus(status_result["status"])

            if status == AuthorizationStatus.GRANTED:
                break
            if status == AuthorizationStatus.PENDING:
                time.sleep(self.POLL_INTERVAL)
                continue
            if status == AuthorizationStatus.DENIED:
                raise AuthorizationDenied("Authorization denied by user", status.value)
            if status == AuthorizationStatus.TIMEOUT:
                raise AuthorizationTimeout("Authorization request timed out", status.value)
            raise AuthenticationError(f"Unexpected authorization status: {status.value}", status.value)

        self.save_token(app_token)

    # ── Session ────────────────────────────────────────────────────────────────

    def open_session(self, request: _RequestFn) -> None:
        """Open a new API session and store the session_token and permissions."""
        login = request("GET", "login/", authenticated=False)
        challenge: str = login["challenge"]
        password = _compute_password(self.app_token, challenge)
        result = request(
            "POST",
            "login/session/",
            authenticated=False,
            json={
                "app_id":      self.app_id,
                "app_version": self.app_version,
                "password":    password,
            },
        )
        self.session_token = result["session_token"]
        self.permissions = result.get("permissions", {})

    def close_session(self, request: _RequestFn) -> None:
        """Close the current session."""
        if not self.session_token:
            return
        try:
            request("POST", "login/logout/", authenticated=True)
        finally:
            self.session_token = None
            self.permissions = {}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _compute_password(app_token: str, challenge: str) -> str:
    return hmac.new(
        app_token.encode(),
        challenge.encode(),
        hashlib.sha1,
    ).hexdigest()


def raise_for_error_code(code: str, msg: str) -> None:
    """Translate an API error_code into the appropriate exception."""
    mapping: dict[str, type[FreeboxError]] = {
        "auth_required":           AuthenticationError,
        "invalid_token":           TokenRevoked,
        "pending_token":           AuthenticationError,
        "insufficient_rights":     InsufficientRightsError,
        "denied_from_external_ip": DeniedFromExternalIP,
        "ratelimited":             RateLimited,
        "new_apps_denied":         AppsDenied,
        "apps_denied":             AppsDenied,
    }
    raise mapping.get(code, FreeboxError)(msg, code)
