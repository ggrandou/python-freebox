"""Freebox Switch API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class SwitchPortMacEntry:
    """MAC address entry associated with a switch port."""

    mac: str
    hostname: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SwitchPortMacEntry:
        return cls(
            mac=d.get("mac", ""),
            hostname=d.get("hostname", ""),
        )


@dataclass
class SwitchPortStatus:
    """Current status of a switch port (read-only)."""

    id: int
    link: str
    duplex: str
    speed: str
    mode: str
    mac_list: list[SwitchPortMacEntry] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SwitchPortStatus:
        return cls(
            id=d.get("id", 0),
            link=d.get("link", ""),
            duplex=d.get("duplex", ""),
            speed=d.get("speed", ""),
            mode=d.get("mode", ""),
            mac_list=[SwitchPortMacEntry._from_dict(e) for e in d.get("mac_list", [])],
        )


@dataclass
class SwitchPortConfig:
    """Configuration of a switch port."""

    id: int
    speed: str
    duplex: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SwitchPortConfig:
        return cls(
            id=d.get("id", 0),
            speed=d.get("speed", "auto"),
            duplex=d.get("duplex", "auto"),
        )


@dataclass
class SwitchPortStats:
    """Traffic statistics for a switch port (unstable)."""

    rx_bad_bytes: int
    rx_broadcast_packets: int
    rx_bytes_rate: int
    rx_err_packets: int
    rx_fcs_packets: int
    rx_fragments_packets: int
    rx_good_bytes: int
    rx_good_packets: int
    rx_jabber_packets: int
    rx_multicast_packets: int
    rx_oversize_packets: int
    rx_packets_rate: int
    rx_pause: int
    rx_undersize_packets: int
    rx_unicast_packets: int
    tx_broadcast_packets: int
    tx_bytes: int
    tx_bytes_rate: int
    tx_collisions: int
    tx_deferred: int
    tx_excessive: int
    tx_fcs: int
    tx_late: int
    tx_multicast_packets: int
    tx_multiple: int
    tx_packets: int
    tx_packets_rate: int
    tx_pause: int
    tx_single: int
    tx_unicast_packets: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SwitchPortStats:
        return cls(
            rx_bad_bytes=d.get("rx_bad_bytes", 0),
            rx_broadcast_packets=d.get("rx_broadcast_packets", 0),
            rx_bytes_rate=d.get("rx_bytes_rate", 0),
            rx_err_packets=d.get("rx_err_packets", 0),
            rx_fcs_packets=d.get("rx_fcs_packets", 0),
            rx_fragments_packets=d.get("rx_fragments_packets", 0),
            rx_good_bytes=d.get("rx_good_bytes", 0),
            rx_good_packets=d.get("rx_good_packets", 0),
            rx_jabber_packets=d.get("rx_jabber_packets", 0),
            rx_multicast_packets=d.get("rx_multicast_packets", 0),
            rx_oversize_packets=d.get("rx_oversize_packets", 0),
            rx_packets_rate=d.get("rx_packets_rate", 0),
            rx_pause=d.get("rx_pause", 0),
            rx_undersize_packets=d.get("rx_undersize_packets", 0),
            rx_unicast_packets=d.get("rx_unicast_packets", 0),
            tx_broadcast_packets=d.get("tx_broadcast_packets", 0),
            tx_bytes=d.get("tx_bytes", 0),
            tx_bytes_rate=d.get("tx_bytes_rate", 0),
            tx_collisions=d.get("tx_collisions", 0),
            tx_deferred=d.get("tx_deferred", 0),
            tx_excessive=d.get("tx_excessive", 0),
            tx_fcs=d.get("tx_fcs", 0),
            tx_late=d.get("tx_late", 0),
            tx_multicast_packets=d.get("tx_multicast_packets", 0),
            tx_multiple=d.get("tx_multiple", 0),
            tx_packets=d.get("tx_packets", 0),
            tx_packets_rate=d.get("tx_packets_rate", 0),
            tx_pause=d.get("tx_pause", 0),
            tx_single=d.get("tx_single", 0),
            tx_unicast_packets=d.get("tx_unicast_packets", 0),
        )


class Switch:
    """Freebox Switch API.

    Obtained via ``fb.switch``::

        ports = fb.switch.status()
        for p in ports:
            print(p.id, p.link, p.speed)

        cfg = fb.switch.port_config(1)
        fb.switch.set_port_config(1, speed="100", duplex="full")

        stats = fb.switch.port_stats(1)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def status(self) -> list[SwitchPortStatus]:
        """Return the status of all switch ports."""
        result = self._client.get("switch/status/")
        return [SwitchPortStatus._from_dict(p) for p in result]

    def port_config(self, port_id: int) -> SwitchPortConfig:
        """Return the configuration of the given switch port."""
        return SwitchPortConfig._from_dict(self._client.get(f"switch/port/{port_id}"))

    def set_port_config(self, port_id: int, **kwargs: Any) -> SwitchPortConfig:
        """Update the configuration of the given switch port.

        Accepted keyword arguments: ``speed`` and ``duplex``.
        """
        return SwitchPortConfig._from_dict(
            self._client.put(f"switch/port/{port_id}", json=kwargs)
        )

    def port_stats(self, port_id: int) -> SwitchPortStats:
        """Return traffic statistics for the given switch port."""
        return SwitchPortStats._from_dict(
            self._client.get(f"switch/port/{port_id}/stats")
        )
