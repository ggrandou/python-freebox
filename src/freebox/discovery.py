"""Freebox discovery: mDNS, HTTP/HTTPS, and remote port change via DNS SRV."""
from __future__ import annotations

import ssl
import time
from dataclasses import dataclass
from importlib.resources import files
from typing import Any

import httpx

_MDNS_SERVICE = "_fbx-api._tcp.local."
_DEFAULT_HOST = "mafreebox.freebox.fr"


def ssl_context() -> ssl.SSLContext:
    """Return an SSL context that trusts the bundled Freebox Root CAs.

    VERIFY_X509_STRICT is disabled because Freebox certificates lack the
    Authority Key Identifier extension required by Python 3.13+.
    """
    ctx = ssl.create_default_context()
    ca_pem = files("freebox.certs").joinpath("freebox-ca.pem")
    ctx.load_verify_locations(cafile=str(ca_pem))
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return ctx


@dataclass
class DiscoveryInfo:
    """Information returned by the Freebox discovery endpoint."""

    uid: str
    device_name: str
    box_model: str
    box_model_name: str
    api_version: str
    api_base_url: str
    api_domain: str
    https_available: bool
    https_port: int

    @property
    def api_major_version(self) -> int:
        return int(self.api_version.split(".")[0])

    @property
    def local_url(self) -> str:
        """Base URL for local access via mafreebox.freebox.fr."""
        return f"https://{_DEFAULT_HOST}{self.api_base_url}"

    @property
    def remote_url(self) -> str:
        """Base URL for remote access via api_domain."""
        return f"https://{self.api_domain}:{self.https_port}{self.api_base_url}"

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> DiscoveryInfo:
        return cls(
            uid=data.get("uid", ""),
            device_name=data.get("device_name", ""),
            box_model=data.get("box_model", ""),
            box_model_name=data.get("box_model_name", ""),
            api_version=data.get("api_version", ""),
            api_base_url=data.get("api_base_url", "/api/"),
            api_domain=data.get("api_domain", ""),
            https_available=bool(data.get("https_available", False)),
            https_port=int(data.get("https_port", 443)),
        )


def discover_mdns(timeout: float = 5.0) -> DiscoveryInfo | None:
    """Discover a Freebox on the local network using mDNS.

    This is the preferred discovery method as it does not require knowing the
    Freebox IP address. Requires the ``zeroconf`` package to be installed;
    returns None if unavailable or if no Freebox is found within the timeout.
    """
    try:
        from zeroconf import ServiceBrowser, Zeroconf
    except ImportError:
        return None

    result: DiscoveryInfo | None = None

    class _Listener:
        def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            nonlocal result
            info = zc.get_service_info(type_, name)
            if not info or not info.properties:
                return
            props: dict[str, str] = {
                (k.decode() if isinstance(k, bytes) else k): (
                    v.decode() if isinstance(v, bytes) else v
                )
                for k, v in info.properties.items()
            }
            result = DiscoveryInfo(
                uid=props.get("uid", ""),
                device_name=name.removesuffix(f".{type_}"),
                box_model=props.get("box_model", ""),
                box_model_name=props.get("box_model_name", ""),
                api_version=props.get("api_version", ""),
                api_base_url=props.get("api_base_url", "/api/"),
                api_domain=props.get("api_domain", ""),
                https_available=props.get("https_available", "0") == "1",
                https_port=int(props.get("https_port", 443)),
            )

        def remove_service(self, *_: Any) -> None:
            pass

        def update_service(self, *_: Any) -> None:
            pass

    zc = Zeroconf()
    try:
        ServiceBrowser(zc, _MDNS_SERVICE, _Listener())
        deadline = time.monotonic() + timeout
        while result is None and time.monotonic() < deadline:
            time.sleep(0.05)
    finally:
        zc.close()
    return result


def discover_http(host: str = _DEFAULT_HOST) -> DiscoveryInfo:
    """Discover a Freebox via HTTPS (with Freebox CA validation).

    Falls back to plain HTTP if HTTPS fails. Use this method when mDNS is
    unavailable, or to resolve the api_domain and https_port for remote access.
    HTTPS discovery is preferred over HTTP discovery per the API documentation.
    """
    try:
        resp = httpx.get(
            f"https://{host}/api_version",
            verify=ssl_context(),
            timeout=5.0,
        )
        resp.raise_for_status()
        return DiscoveryInfo._from_dict(resp.json())
    except Exception:
        resp = httpx.get(f"http://{host}/api_version", timeout=5.0)
        resp.raise_for_status()
        return DiscoveryInfo._from_dict(resp.json())


def discover_remote_port(api_domain: str) -> int | None:
    """Check the current remote HTTPS port via DNS SRV record.

    The API documentation recommends implementing this as a fallback when the
    previously recorded remote port becomes unreachable, since the port can
    change automatically. Requires the ``dnspython`` package; returns None if
    unavailable or if the SRV record is absent.
    """
    try:
        import dns.resolver  # type: ignore[import-untyped]
        answers = dns.resolver.resolve(f"_https._tcp.{api_domain}", "SRV")
        return int(answers[0].port)
    except Exception:
        return None


def discover(timeout: float = 5.0) -> DiscoveryInfo:
    """Discover a Freebox using the recommended fallback chain.

    Tries mDNS first (preferred), then falls back to HTTPS/HTTP discovery.
    """
    info = discover_mdns(timeout=timeout)
    if info is not None:
        return info
    return discover_http()
