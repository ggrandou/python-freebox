from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from freebox.auth import Auth, raise_for_error_code
from freebox.connection import Connection
from freebox.dhcp import Dhcp
from freebox.dhcpv6 import Dhcpv6
from freebox.discovery import DiscoveryInfo, discover_http, ssl_context
from freebox.events import EventStream
from freebox.exceptions import AuthenticationError, FreeboxError, TokenRevoked
from freebox.lan import Lan
from freebox.rrd import Rrd
from freebox.sfp import Sfp
from freebox.switch import Switch
from freebox.system import System
from freebox.update import Update
from freebox.vpn import VpnClient, VpnServer
from freebox.wifi import Wifi

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
        self._port = port
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

    @property
    def connection(self) -> Connection:
        """Access the Connection API."""
        return Connection(self)

    @property
    def dhcp(self) -> Dhcp:
        """Access the DHCP API."""
        return Dhcp(self)

    @property
    def dhcpv6(self) -> Dhcpv6:
        """Access the DHCPv6 API."""
        return Dhcpv6(self)

    @property
    def lan(self) -> Lan:
        """Access the LAN API."""
        return Lan(self)

    @property
    def rrd(self) -> Rrd:
        """Access the RRD Stats API."""
        return Rrd(self)

    @property
    def sfp(self) -> Sfp:
        """Access the SFP API."""
        return Sfp(self)

    @property
    def switch(self) -> Switch:
        """Access the Switch API."""
        return Switch(self)

    @property
    def system(self) -> System:
        """Access the System API."""
        return System(self)

    @property
    def update(self) -> Update:
        """Access the Update API."""
        return Update(self)

    @property
    def vpn_server(self) -> VpnServer:
        """Access the VPN Server API."""
        return VpnServer(self)

    @property
    def vpn_client(self) -> VpnClient:
        """Access the VPN Client API."""
        return VpnClient(self)

    @property
    def wifi(self) -> Wifi:
        """Access the Wi-Fi API."""
        return Wifi(self)

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

    def get_text(self, path: str) -> str:
        """Send an authenticated GET and return the raw response text.

        Used for endpoints that return plain text rather than JSON (e.g. VPN
        client configuration file download).
        """
        headers = {}
        if self._auth.session_token:
            headers["X-Fbx-App-Auth"] = self._auth.session_token
        resp = self._http.get(self._url(path), headers=headers)
        try:
            resp.raise_for_status()
        except Exception as exc:
            raise FreeboxError(str(exc)) from exc
        return resp.text

    def events(self, events: list[str]) -> EventStream:
        """Return a WebSocket event stream subscribed to the given event names.

        The returned :class:`~freebox.EventStream` must be used as a context
        manager.  See :class:`~freebox.EventStream` for usage.

        Raises :class:`~freebox.AuthenticationError` if the client is not open.
        """
        if not self._auth.session_token:
            raise AuthenticationError("Not connected; call open() first")
        return EventStream(
            url=self._ws_url("ws/event"),
            session_token=self._auth.session_token,
            events=events,
            ssl_ctx=ssl_context(),
        )

    # ── Internal ───────────────────────────────────────────────────────────────

    @property
    def _api_version(self) -> int | None:
        return self.discovery.api_major_version if self.discovery else None

    def _url(self, path: str) -> str:
        return _API_BASE.format(version=self._api_version) + path.lstrip("/")

    def _ws_url(self, path: str) -> str:
        port_str = f":{self._port}" if self._port else ""
        return f"wss://{self._host}{port_str}" + _API_BASE.format(version=self._api_version) + path.lstrip("/")

    def _raw_request(self, method: str, path: str, *, authenticated: bool = True, **kwargs: Any) -> Any:
        """Send a request and return the result, raising on API errors."""
        headers = {}
        if authenticated and self._auth.session_token:
            headers["X-Fbx-App-Auth"] = self._auth.session_token
        resp = self._http.request(method, self._url(path), headers=headers, **kwargs)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise FreeboxError(str(exc)) from exc
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
