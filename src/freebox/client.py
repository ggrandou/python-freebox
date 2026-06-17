from __future__ import annotations

import hashlib
import hmac
import time
from pathlib import Path
from typing import Any

import httpx

from freebox.discovery import DiscoveryInfo, discover_http, ssl_context
from freebox.exceptions import (
    AuthenticationError,
    FreeboxError,
    InsufficientRightsError,
    TokenRevoked,
)

_DEFAULT_HOST = "mafreebox.freebox.fr"
_API_BASE = "/api/v{version}/"


class Freebox:
    """Client for the Freebox API.

    Handles discovery, app-token registration, session management, and
    authenticated HTTP requests.

    Usage::

        fb = Freebox(app_id="com.example.myapp", app_name="My App",
                     app_version="1.0", device_name="my-pc",
                     token_file=Path("~/.freebox_token"))
        fb.open()          # registers app if needed, opens a session
        data = fb.get("connection/")
        fb.close()
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
    ) -> None:
        self._app_id = app_id
        self._app_name = app_name
        self._app_version = app_version
        self._device_name = device_name
        self._token_file = token_file
        self._host = host

        self._app_token: str | None = None
        self._session_token: str | None = None
        self.discovery: DiscoveryInfo | None = None

        base = f"https://{host}" + (f":{port}" if port else "")
        self._http = httpx.Client(base_url=base, verify=ssl_context())

    # ── Public API ─────────────────────────────────────────────────────────────

    def open(self) -> None:
        """Discover the Freebox, register the app if needed, and open a session."""
        self._discover()
        self._load_token()
        if not self._app_token:
            self._register()
        self._open_session()

    def close(self) -> None:
        """Close the current session."""
        if self._session_token:
            self._request("POST", "login/logout/", authenticated=True)
            self._session_token = None

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

    def _request(self, method: str, path: str, *, authenticated: bool = True, **kwargs: Any) -> Any:
        headers = {}
        if authenticated and self._session_token:
            headers["X-Fbx-App-Auth"] = self._session_token
        resp = self._http.request(method, self._url(path), headers=headers, **kwargs)
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success"):
            self._raise(body)
        return body.get("result")

    def _raise(self, body: dict) -> None:
        code = body.get("error_code", "unknown")
        msg = body.get("msg", code)
        if code in ("auth_required", "invalid_token"):
            raise AuthenticationError(msg, code)
        if code == "insufficient_rights":
            raise InsufficientRightsError(msg, code)
        if code == "pending_token":
            raise TokenRevoked(msg, code)
        raise FreeboxError(msg, code)

    # ── Discovery ──────────────────────────────────────────────────────────────

    def _discover(self) -> None:
        self.discovery = discover_http(self._host)

    # ── App token ──────────────────────────────────────────────────────────────

    def _load_token(self) -> None:
        if self._token_file and self._token_file.expanduser().exists():
            self._app_token = self._token_file.expanduser().read_text().strip() or None

    def _save_token(self, token: str) -> None:
        self._app_token = token
        if self._token_file:
            self._token_file.expanduser().write_text(token)

    def _register(self) -> None:
        result = self._request(
            "POST",
            "login/authorize/",
            authenticated=False,
            json={
                "app_id": self._app_id,
                "app_name": self._app_name,
                "app_version": self._app_version,
                "device_name": self._device_name,
            },
        )
        track_id = result["track_id"]
        app_token = result["app_token"]

        print("Please grant access on the Freebox front panel…")
        while True:
            status_result = self._request(
                "GET",
                f"login/authorize/{track_id}",
                authenticated=False,
            )
            status = status_result["status"]
            if status == "granted":
                break
            if status == "pending":
                time.sleep(2)
                continue
            raise AuthenticationError(f"Authorization {status}", status)

        self._save_token(app_token)

    # ── Session ────────────────────────────────────────────────────────────────

    def _open_session(self) -> None:
        login = self._request("GET", "login/", authenticated=False)
        challenge = login["challenge"]
        password = hmac.new(
            self._app_token.encode(),
            challenge.encode(),
            hashlib.sha1,
        ).hexdigest()
        result = self._request(
            "POST",
            "login/session/",
            authenticated=False,
            json={
                "app_id": self._app_id,
                "app_version": self._app_version,
                "password": password,
            },
        )
        self._session_token = result["session_token"]
