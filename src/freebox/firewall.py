"""Freebox Firewall API (NAT, port forwarding, incoming ports)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── DMZ ────────────────────────────────────────────────────────────────────────


@dataclass
class DmzConfig:
    """DMZ configuration (GET/PUT /fw/dmz/)."""

    enabled: bool
    ip: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DmzConfig:
        return cls(
            enabled=d.get("enabled", False),
            ip=d.get("ip", ""),
        )


# ── Port Forwarding ────────────────────────────────────────────────────────────


@dataclass
class PortForwarding:
    """A port forwarding rule (GET/POST/PUT/DELETE /fw/redir/)."""

    id: int
    enabled: bool
    ip_proto: str
    wan_port_start: int
    wan_port_end: int
    lan_ip: str
    lan_port: int
    src_ip: str
    comment: str
    hostname: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PortForwarding:
        return cls(
            id=d.get("id", 0),
            enabled=d.get("enabled", False),
            ip_proto=d.get("ip_proto", "tcp"),
            wan_port_start=d.get("wan_port_start", 0),
            wan_port_end=d.get("wan_port_end", 0),
            lan_ip=d.get("lan_ip", ""),
            lan_port=d.get("lan_port", 0),
            src_ip=d.get("src_ip", "0.0.0.0"),
            comment=d.get("comment", ""),
            hostname=d.get("hostname", ""),
        )


# ── Incoming Port ──────────────────────────────────────────────────────────────


@dataclass
class IncomingPort:
    """An incoming port binding (GET/PUT /fw/incoming/)."""

    id: str
    enabled: bool
    active: bool
    type: str
    in_port: int
    min_port: int
    max_port: int
    netns: str
    readonly: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> IncomingPort:
        return cls(
            id=d.get("id", ""),
            enabled=d.get("enabled", False),
            active=d.get("active", False),
            type=d.get("type", "tcp"),
            in_port=d.get("in_port", 0),
            min_port=d.get("min_port", 0),
            max_port=d.get("max_port", 65535),
            netns=d.get("netns", ""),
            readonly=d.get("readonly", False),
        )


# ── Firewall API ───────────────────────────────────────────────────────────────


class Firewall:
    """Freebox Firewall API.

    Obtained via ``fb.firewall``::

        dmz = fb.firewall.dmz()
        rules = fb.firewall.port_forwardings()
        ports = fb.firewall.incoming_ports()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── DMZ ────────────────────────────────────────────────────────────────────

    def dmz(self) -> DmzConfig:
        """Return the current DMZ configuration."""
        return DmzConfig._from_dict(self._client.get("fw/dmz/"))

    def set_dmz(self, **kwargs: Any) -> DmzConfig:
        """Update the DMZ configuration.

        Pass only the fields to change, e.g. ``set_dmz(enabled=True, ip="192.168.1.42")``.
        """
        return DmzConfig._from_dict(self._client.put("fw/dmz/", json=kwargs))

    # ── Port Forwarding ────────────────────────────────────────────────────────

    def port_forwardings(self) -> list[PortForwarding]:
        """Return the list of port forwarding rules."""
        return [PortForwarding._from_dict(r) for r in self._client.get("fw/redir/")]

    def port_forwarding(self, redir_id: int) -> PortForwarding:
        """Return a specific port forwarding rule by id."""
        return PortForwarding._from_dict(self._client.get(f"fw/redir/{redir_id}"))

    def add_port_forwarding(
        self,
        ip_proto: str,
        wan_port_start: int,
        wan_port_end: int,
        lan_ip: str,
        lan_port: int,
        **kwargs: Any,
    ) -> PortForwarding:
        """Create a new port forwarding rule.

        Required fields: ``ip_proto``, ``wan_port_start``, ``wan_port_end``,
        ``lan_ip``, ``lan_port``. Optional fields (``enabled``, ``src_ip``,
        ``comment``) can be passed as keyword arguments.
        """
        payload = {
            "ip_proto": ip_proto,
            "wan_port_start": wan_port_start,
            "wan_port_end": wan_port_end,
            "lan_ip": lan_ip,
            "lan_port": lan_port,
            **kwargs,
        }
        return PortForwarding._from_dict(self._client.post("fw/redir/", json=payload))

    def set_port_forwarding(self, redir_id: int, **kwargs: Any) -> PortForwarding:
        """Update a port forwarding rule.

        Pass only the fields to change, e.g. ``set_port_forwarding(1, enabled=False)``.
        """
        return PortForwarding._from_dict(self._client.put(f"fw/redir/{redir_id}", json=kwargs))

    def delete_port_forwarding(self, redir_id: int) -> None:
        """Delete a port forwarding rule."""
        self._client.delete(f"fw/redir/{redir_id}")

    # ── Incoming Ports ─────────────────────────────────────────────────────────

    def incoming_ports(self) -> list[IncomingPort]:
        """Return the list of incoming port bindings."""
        return [IncomingPort._from_dict(p) for p in self._client.get("fw/incoming/")]

    def incoming_port(self, port_id: str) -> IncomingPort:
        """Return a specific incoming port binding by id."""
        return IncomingPort._from_dict(self._client.get(f"fw/incoming/{port_id}"))

    def set_incoming_port(self, port_id: str, **kwargs: Any) -> IncomingPort:
        """Update an incoming port binding.

        Pass only the fields to change, e.g. ``set_incoming_port("bittorrent-main", in_port=3615)``.
        """
        return IncomingPort._from_dict(self._client.put(f"fw/incoming/{port_id}", json=kwargs))
