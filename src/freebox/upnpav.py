"""Freebox UPnP AV API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class UpnpAvConfig:
    """UPnP AV configuration (GET /upnpav/config/)."""

    enabled: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UpnpAvConfig:
        return cls(enabled=d.get("enabled", False))


class UpnpAv:
    """Freebox UPnP AV API.

    Obtained via ``fb.upnpav``::

        cfg = fb.upnpav.config()
        fb.upnpav.set_config(enabled=True)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> UpnpAvConfig:
        """Return the current UPnP AV configuration."""
        return UpnpAvConfig._from_dict(self._client.get("upnpav/config/"))

    def set_config(self, *, enabled: bool) -> UpnpAvConfig:
        """Update the UPnP AV configuration."""
        return UpnpAvConfig._from_dict(
            self._client.put("upnpav/config/", json={"enabled": enabled})
        )
