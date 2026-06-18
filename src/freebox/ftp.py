"""Freebox FTP server API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class FtpConfig:
    """FTP server configuration (GET/PUT /ftp/config/)."""

    enabled: bool
    allow_anonymous: bool
    allow_anonymous_write: bool
    allow_remote_access: bool
    weak_password: bool
    port_ctrl: int
    port_data: int
    username: str
    remote_domain: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FtpConfig:
        return cls(
            enabled=d.get("enabled", False),
            allow_anonymous=d.get("allow_anonymous", False),
            allow_anonymous_write=d.get("allow_anonymous_write", False),
            allow_remote_access=d.get("allow_remote_access", False),
            weak_password=d.get("weak_password", True),
            port_ctrl=d.get("port_ctrl", 0),
            port_data=d.get("port_data", 0),
            username=d.get("username", ""),
            remote_domain=d.get("remote_domain", ""),
        )


class Ftp:
    """Freebox FTP server API.

    Obtained via ``fb.ftp``::

        cfg = fb.ftp.config()
        print(cfg.enabled, cfg.allow_anonymous)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> FtpConfig:
        """Return the current FTP server configuration."""
        return FtpConfig._from_dict(self._client.get("ftp/config/"))

    def set_config(self, **kwargs: Any) -> FtpConfig:
        """Update the FTP server configuration.

        Pass only the fields to change, e.g. ``set_config(enabled=True)``.
        """
        return FtpConfig._from_dict(self._client.put("ftp/config/", json=kwargs))
