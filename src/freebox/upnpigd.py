"""Freebox UPnP IGD API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class UpnpIgdConfig:
    """UPnP IGD service configuration (GET/PUT /upnpigd/config/)."""

    enabled: bool
    version: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UpnpIgdConfig:
        return cls(
            enabled=d.get("enabled", False),
            version=d.get("version", 1),
        )


@dataclass
class UpnpIgdRedir:
    """A UPnP IGD redirection (read-only, GET/DELETE /upnpigd/redir/)."""

    id: str
    enabled: bool
    ext_src_ip: str
    ext_port: int
    int_ip: str
    int_port: int
    proto: str
    desc: str
    remaining: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UpnpIgdRedir:
        return cls(
            id=d.get("id", ""),
            enabled=d.get("enabled", False),
            ext_src_ip=d.get("ext_src_ip", ""),
            ext_port=d.get("ext_port", 0),
            int_ip=d.get("int_ip", ""),
            int_port=d.get("int_port", 0),
            proto=d.get("proto", ""),
            desc=d.get("desc", ""),
            remaining=d.get("remaining", 0),
        )


class UpnpIgd:
    """Freebox UPnP IGD API.

    Obtained via ``fb.upnpigd``::

        cfg = fb.upnpigd.config()
        redirs = fb.upnpigd.redirs()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> UpnpIgdConfig:
        """Return the current UPnP IGD configuration."""
        return UpnpIgdConfig._from_dict(self._client.get("upnpigd/config/"))

    def set_config(self, **kwargs: Any) -> UpnpIgdConfig:
        """Update the UPnP IGD configuration.

        Pass only the fields to change, e.g. ``set_config(enabled=True, version=2)``.
        """
        return UpnpIgdConfig._from_dict(self._client.put("upnpigd/config/", json=kwargs))

    def redirs(self) -> list[UpnpIgdRedir]:
        """Return the list of active UPnP IGD redirections."""
        return [UpnpIgdRedir._from_dict(r) for r in self._client.get("upnpigd/redir/")]

    def delete_redir(self, redir_id: str) -> None:
        """Delete a UPnP IGD redirection by id."""
        self._client.delete(f"upnpigd/redir/{redir_id}")
