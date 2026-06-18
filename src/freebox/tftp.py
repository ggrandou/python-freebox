"""Freebox TFTP server API."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class TftpConfig:
    """TFTP server configuration (GET/PUT /tftp/config/).

    The ``root`` field is the base64-encoded absolute path to the root
    directory served by the TFTP server.  Use ``root_path`` to get the
    decoded path as a plain string.
    """

    enabled: bool
    root: str

    @property
    def root_path(self) -> str:
        """Decoded path (base64 → plain string)."""
        if not self.root:
            return ""
        try:
            return base64.b64decode(self.root).decode()
        except Exception:
            return self.root

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> TftpConfig:
        return cls(
            enabled=d.get("enabled", False),
            root=d.get("root", ""),
        )


class Tftp:
    """Freebox TFTP server API.

    Obtained via ``fb.tftp``::

        cfg = fb.tftp.config()
        print(cfg.enabled, cfg.root_path)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> TftpConfig:
        """Return the current TFTP server configuration."""
        return TftpConfig._from_dict(self._client.get("tftp/config/"))

    def set_config(self, **kwargs: Any) -> TftpConfig:
        """Update the TFTP server configuration.

        Pass only the fields to change, e.g. ``set_config(enabled=True)``.
        To set the root path, pass the base64-encoded path as ``root``.
        """
        return TftpConfig._from_dict(self._client.put("tftp/config/", json=kwargs))
