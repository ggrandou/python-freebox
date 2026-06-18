"""Freebox Freeplug (CPL) API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class FreeplugNode:
    """A single Freeplug device."""

    id: str
    net_id: str
    net_role: str
    model: str
    local: bool
    has_network: bool
    eth_port_status: str
    eth_full_duplex: bool
    eth_speed: int
    inactive: int
    rx_rate: int
    tx_rate: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FreeplugNode:
        return cls(
            id=d.get("id", ""),
            net_id=d.get("net_id", ""),
            net_role=d.get("net_role", ""),
            model=d.get("model", ""),
            local=d.get("local", False),
            has_network=d.get("has_network", False),
            eth_port_status=d.get("eth_port_status", "unknown"),
            eth_full_duplex=d.get("eth_full_duplex", False),
            eth_speed=d.get("eth_speed", 0),
            inactive=d.get("inactive", 0),
            rx_rate=d.get("rx_rate", -1),
            tx_rate=d.get("tx_rate", -1),
        )


@dataclass
class FreeplugNetwork:
    """A Freeplug CPL network, grouping member devices."""

    id: str
    members: list[FreeplugNode]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FreeplugNetwork:
        return cls(
            id=d.get("id", ""),
            members=[FreeplugNode._from_dict(m) for m in d.get("members", [])],
        )


class Freeplug:
    """Freebox Freeplug (CPL) API.

    Obtained via ``fb.freeplug``::

        networks = fb.freeplug.networks()
        for net in networks:
            for node in net.members:
                print(node.id, node.rx_rate, node.tx_rate)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def networks(self) -> list[FreeplugNetwork]:
        """Return the list of Freeplug networks."""
        result = self._client.get("freeplug/")
        return [FreeplugNetwork._from_dict(n) for n in result] if result else []

    def node(self, node_id: str) -> FreeplugNode:
        """Return a specific Freeplug device by id."""
        return FreeplugNode._from_dict(self._client.get(f"freeplug/{node_id}/"))

    def reset(self, node_id: str) -> None:
        """Reset a Freeplug device."""
        self._client.post(f"freeplug/{node_id}/reset/")
