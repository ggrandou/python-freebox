"""Freebox Network Share (Samba / AFP) API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class SambaConfig:
    """Samba file-sharing configuration (GET/PUT /netshare/samba/)."""

    file_share_enabled: bool
    print_share_enabled: bool
    logon_enabled: bool
    logon_user: str
    workgroup: str
    smbv2_enabled: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SambaConfig:
        return cls(
            file_share_enabled=d.get("file_share_enabled", False),
            print_share_enabled=d.get("print_share_enabled", False),
            logon_enabled=d.get("logon_enabled", False),
            logon_user=d.get("logon_user", ""),
            workgroup=d.get("workgroup", ""),
            smbv2_enabled=d.get("smbv2_enabled", False),
        )


@dataclass
class AfpConfig:
    """AFP file-sharing configuration (GET/PUT /netshare/afp/)."""

    enabled: bool
    guest_allow: bool
    login_name: str
    server_type: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AfpConfig:
        return cls(
            enabled=d.get("enabled", False),
            guest_allow=d.get("guest_allow", False),
            login_name=d.get("login_name", ""),
            server_type=d.get("server_type", ""),
        )


class NetShare:
    """Freebox Network Share (Samba / AFP) API.

    Obtained via ``fb.netshare``::

        samba = fb.netshare.samba()
        afp   = fb.netshare.afp()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def samba(self) -> SambaConfig:
        """Return the current Samba configuration."""
        return SambaConfig._from_dict(self._client.get("netshare/samba/"))

    def set_samba(self, **kwargs: Any) -> SambaConfig:
        """Update the Samba configuration.

        Pass only the fields to change, e.g. ``set_samba(file_share_enabled=True)``.
        """
        return SambaConfig._from_dict(self._client.put("netshare/samba/", json=kwargs))

    def afp(self) -> AfpConfig:
        """Return the current AFP configuration."""
        return AfpConfig._from_dict(self._client.get("netshare/afp/"))

    def set_afp(self, **kwargs: Any) -> AfpConfig:
        """Update the AFP configuration.

        Pass only the fields to change, e.g. ``set_afp(guest_allow=False)``.
        """
        return AfpConfig._from_dict(self._client.put("netshare/afp/", json=kwargs))
