"""Freebox LAN API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── LAN Config ─────────────────────────────────────────────────────────────────

@dataclass
class LanConfig:
    """LAN configuration (GET/PUT /lan/config/)."""

    ip: str
    name: str
    name_dns: str
    name_mdns: str
    name_netbios: str
    mode: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanConfig:
        return cls(
            ip=d["ip"],
            name=d["name"],
            name_dns=d.get("name_dns", ""),
            name_mdns=d.get("name_mdns", ""),
            name_netbios=d.get("name_netbios", ""),
            mode=d.get("mode", "router"),
        )


# ── Routes ─────────────────────────────────────────────────────────────────────

@dataclass
class Route:
    """Static route (GET/PUT /lan/routes)."""

    prefix: str
    gateway: str
    enabled: bool
    description: str = ""

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Route:
        return cls(
            prefix=d["prefix"],
            gateway=d["gateway"],
            enabled=d.get("enabled", True),
            description=d.get("description", ""),
        )

    def _to_dict(self) -> dict[str, Any]:
        return {
            "prefix": self.prefix,
            "gateway": self.gateway,
            "enabled": self.enabled,
            "description": self.description,
        }


# ── LAN Browser ────────────────────────────────────────────────────────────────

@dataclass
class LanInterface:
    """A browsable LAN interface (GET /lan/browser/interfaces/)."""

    name: str
    host_count: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanInterface:
        return cls(name=d["name"], host_count=d.get("host_count", 0))


@dataclass
class LanHostName:
    name: str
    source: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanHostName:
        return cls(name=d["name"], source=d.get("source", ""))


@dataclass
class LanHostL2Ident:
    id: str
    type: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanHostL2Ident:
        return cls(id=d["id"], type=d.get("type", ""))


@dataclass
class LanHostL3Connectivity:
    addr: str
    af: str
    active: bool
    reachable: bool
    last_activity: int = 0
    last_time_reachable: int = 0
    model: str = ""

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanHostL3Connectivity:
        return cls(
            addr=d["addr"],
            af=d.get("af", "ipv4"),
            active=d.get("active", False),
            reachable=d.get("reachable", False),
            last_activity=d.get("last_activity", 0),
            last_time_reachable=d.get("last_time_reachable", 0),
            model=d.get("model", ""),
        )


@dataclass
class LanHostNetworkControl:
    profile_id: int
    name: str
    current_mode: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanHostNetworkControl:
        return cls(
            profile_id=d.get("profile_id", 0),
            name=d.get("name", ""),
            current_mode=d.get("current_mode", ""),
        )


@dataclass
class LanHost:
    """A host on the local network (GET/PUT /lan/browser/{interface}/{hostid}/)."""

    id: str
    primary_name: str
    primary_name_manual: bool
    host_type: str
    persistent: bool
    reachable: bool
    active: bool
    last_time_reachable: int
    last_activity: int
    l2ident: list[LanHostL2Ident] = field(default_factory=list)
    l3connectivities: list[LanHostL3Connectivity] = field(default_factory=list)
    names: list[LanHostName] = field(default_factory=list)
    vendor_name: str = ""
    domain_name: str = ""
    first_activity: int = 0
    network_control: LanHostNetworkControl | None = None
    info: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanHost:
        l2raw = d.get("l2ident", {})
        if isinstance(l2raw, dict):
            l2list = [LanHostL2Ident._from_dict(l2raw)] if l2raw else []
        else:
            l2list = [LanHostL2Ident._from_dict(e) for e in l2raw]

        nc_raw = d.get("network_control")
        return cls(
            id=d["id"],
            primary_name=d.get("primary_name", ""),
            primary_name_manual=d.get("primary_name_manual", False),
            host_type=d.get("host_type", "other"),
            persistent=d.get("persistent", False),
            reachable=d.get("reachable", False),
            active=d.get("active", False),
            last_time_reachable=d.get("last_time_reachable", 0),
            last_activity=d.get("last_activity", 0),
            l2ident=l2list,
            l3connectivities=[LanHostL3Connectivity._from_dict(e) for e in d.get("l3connectivities", [])],
            names=[LanHostName._from_dict(e) for e in d.get("names", [])],
            vendor_name=d.get("vendor_name", ""),
            domain_name=d.get("domain_name", ""),
            first_activity=d.get("first_activity", 0),
            network_control=LanHostNetworkControl._from_dict(nc_raw) if nc_raw else None,
            info=d.get("info", {}),
        )


@dataclass
class LanHostType:
    """A host type descriptor (GET /lan/browser/types/)."""

    type: str
    name: str
    icon: str = ""
    category: str = ""

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanHostType:
        return cls(
            type=d["type"],
            name=d.get("name", ""),
            icon=d.get("icon", ""),
            category=d.get("category", ""),
        )


# ── LAN API ────────────────────────────────────────────────────────────────────

class Lan:
    """Freebox LAN API.

    Obtained via ``fb.lan``::

        config = fb.lan.config()
        print(config.ip, config.mode)

        hosts = fb.lan.hosts("pub")
        for h in hosts:
            print(h.primary_name, h.reachable)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── LAN config ─────────────────────────────────────────────────────────────

    def config(self) -> LanConfig:
        """Return the current LAN configuration."""
        return LanConfig._from_dict(self._client.get("lan/config/"))

    def set_config(self, **kwargs: Any) -> LanConfig:
        """Update the LAN configuration.

        Pass only the fields to change, e.g. ``set_config(ip="192.168.1.1")``.
        """
        return LanConfig._from_dict(self._client.put("lan/config/", json=kwargs))

    # ── Static routes ──────────────────────────────────────────────────────────

    def routes(self) -> list[Route]:
        """Return the list of static routes."""
        return [Route._from_dict(r) for r in self._client.get("lan/routes")]

    def set_routes(self, routes: list[Route]) -> list[Route]:
        """Replace the entire list of static routes."""
        return [Route._from_dict(r) for r in self._client.put("lan/routes/", json=[r._to_dict() for r in routes])]

    # ── LAN browser ────────────────────────────────────────────────────────────

    def interfaces(self) -> list[LanInterface]:
        """Return the list of browsable LAN interfaces."""
        return [LanInterface._from_dict(i) for i in self._client.get("lan/browser/interfaces/")]

    def hosts(self, interface: str) -> list[LanHost]:
        """Return the list of hosts on the given interface (e.g. ``"pub"``)."""
        result = self._client.get(f"lan/browser/{interface}/")
        return [LanHost._from_dict(h) for h in (result or [])]

    def host(self, interface: str, host_id: str) -> LanHost:
        """Return details for a single host."""
        return LanHost._from_dict(self._client.get(f"lan/browser/{interface}/{host_id}/"))

    def set_host(self, interface: str, host_id: str, **kwargs: Any) -> LanHost:
        """Update a host's properties (e.g. ``primary_name``, ``host_type``, ``persistent``).

        Pass only the fields to change.
        """
        return LanHost._from_dict(self._client.put(f"lan/browser/{interface}/{host_id}/", json=kwargs))

    def host_types(self) -> list[LanHostType]:
        """Return the list of available host types."""
        return [LanHostType._from_dict(t) for t in self._client.get("lan/browser/types/")]

    # ── Wake on LAN ────────────────────────────────────────────────────────────

    def wake_on_lan(self, interface: str, mac: str, password: str = "") -> None:
        """Send a Wake-on-LAN magic packet to the given MAC address."""
        self._client.post(f"lan/wol/{interface}/", json={"mac": mac, "password": password})
