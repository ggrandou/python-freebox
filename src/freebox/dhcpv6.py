"""Freebox DHCPv6 API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class Dhcpv6Config:
    """DHCPv6 server configuration (GET/PUT /dhcpv6/config/).

    ``dns`` is read-only and reflects the IPv6 DNS servers currently advertised
    via RA RDNSS.  It is ignored by the Freebox when sent in a PUT request.
    """

    enabled: bool
    use_custom_dns: bool
    dns: list[str]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Dhcpv6Config:
        return cls(
            enabled=d.get("enabled", False),
            use_custom_dns=d.get("use_custom_dns", False),
            dns=d.get("dns", []),
        )


class Dhcpv6:
    """Freebox DHCPv6 API.

    Obtained via ``fb.dhcpv6``::

        config = fb.dhcpv6.config()
        print(config.enabled, config.use_custom_dns, config.dns)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> Dhcpv6Config:
        """Return the current DHCPv6 server configuration."""
        return Dhcpv6Config._from_dict(self._client.get("dhcpv6/config/"))

    def set_config(self, **kwargs: Any) -> Dhcpv6Config:
        """Update the DHCPv6 server configuration.

        Pass only the fields to change, e.g. ``set_config(enabled=True)``.
        The ``dns`` field is read-only and will be ignored by the Freebox.
        """
        return Dhcpv6Config._from_dict(self._client.put("dhcpv6/config/", json=kwargs))
