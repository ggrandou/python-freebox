from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from freebox.auth import Auth, raise_for_error_code
from freebox.discovery import DiscoveryInfo, discover_http, ssl_context
from freebox.exceptions import TokenRevoked

_DEFAULT_HOST = "mafreebox.freebox.fr"
_API_BASE = "/api/v{version}/"


class Freebox:
    """Client for the Freebox API.

    Handles discovery, app-token registration, session management, and
    authenticated HTTP requests. Expired sessions are renewed automatically;
    a revoked app token triggers re-registration.

    Can be used as a context manager::

        with Freebox(app_id="com.example.app", app_name="My App",
                     app_version="1.0", device_name="my-pc",
                     token_file=Path("~/.freebox_token")) as fb:
            status = fb.get("connection/")
    """

    def __init__(
        self,
        *,
        app_id: str,
        app_name: str,
        app_version: str,
        device_name: str,
        host: str = _DEFAULT_HOST,
        port: int | None = None,
        token_file: Path | None = None,
        on_pending: Callable[[str], None] | None = None,
    ) -> None:
        self._host = host
        self._auth = Auth(
            app_id=app_id,
            app_name=app_name,
            app_version=app_version,
            device_name=device_name,
            token_file=token_file,
            on_pending=on_pending,
        )
        self.discovery: DiscoveryInfo | None = None

        base = f"https://{host}" + (f":{port}" if port else "")
        self._http = httpx.Client(base_url=base, verify=ssl_context())

    # ── Context manager ────────────────────────────────────────────────────────

    def __enter__(self) -> Freebox:
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ── Public API ─────────────────────────────────────────────────────────────

    @property
    def permissions(self) -> dict[str, bool]:
        """App permissions granted by the user."""
        return self._auth.permissions

    def open(self) -> None:
        """Discover the Freebox, register the app if needed, and open a session."""
        self._discover()
        self._auth.load_token()
        if not self._auth.app_token:
            self._auth.register(self._raw_request)
        self._auth.open_session(self._raw_request)

    def close(self) -> None:
        """Close the current session."""
        self._auth.close_session(self._raw_request)

    def get(self, path: str, **kwargs: Any) -> Any:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, json: Any = None, **kwargs: Any) -> Any:
        return self._request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: Any = None, **kwargs: Any) -> Any:
        return self._request("PUT", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self._request("DELETE", path, **kwargs)

    # ── Internal ───────────────────────────────────────────────────────────────

    @property
    def _api_version(self) -> int | None:
        return self.discovery.api_major_version if self.discovery else None

    def _url(self, path: str) -> str:
        return _API_BASE.format(version=self._api_version) + path.lstrip("/")

    def _raw_request(self, method: str, path: str, *, authenticated: bool = True, **kwargs: Any) -> Any:
        """Send a request and return the result, raising on API errors."""
        headers = {}
        if authenticated and self._auth.session_token:
            headers["X-Fbx-App-Auth"] = self._auth.session_token
        resp = self._http.request(method, self._url(path), headers=headers, **kwargs)
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success"):
            raise_for_error_code(body.get("error_code", "unknown"), body.get("msg", ""))
        return body.get("result")

    def _request(self, method: str, path: str, *, _retry: bool = True, **kwargs: Any) -> Any:
        """Send an authenticated request, auto-recovering from auth errors.

        - auth_required: session expired → renew session and retry once.
        - invalid_token: app token revoked → re-register, renew, retry once.
        """
        try:
            return self._raw_request(method, path, **kwargs)
        except TokenRevoked:
            if not _retry:
                raise
            self._auth.clear_token()
            self._auth.register(self._raw_request)
            self._auth.open_session(self._raw_request)
            return self._request(method, path, _retry=False, **kwargs)
        except Exception as exc:
            if not _retry or getattr(exc, "error_code", None) != "auth_required":
                raise
            self._auth.open_session(self._raw_request)
            return self._request(method, path, _retry=False, **kwargs)

    def _discover(self) -> None:
        self.discovery = discover_http(self._host)
