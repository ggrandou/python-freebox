"""Freebox Connection API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── Status ─────────────────────────────────────────────────────────────────────

@dataclass
class ConnectionStatus:
    """Current WAN connection status (GET /connection/)."""

    state: str
    type: str
    media: str
    rate_up: int
    rate_down: int
    bandwidth_up: int
    bandwidth_down: int
    bytes_up: int
    bytes_down: int
    ipv4: str | None = None
    ipv6: str | None = None
    ipv4_port_range: tuple[int, int] | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ConnectionStatus:
        pr = d.get("ipv4_port_range")
        return cls(
            state=d["state"],
            type=d["type"],
            media=d["media"],
            rate_up=d["rate_up"],
            rate_down=d["rate_down"],
            bandwidth_up=d["bandwidth_up"],
            bandwidth_down=d["bandwidth_down"],
            bytes_up=d["bytes_up"],
            bytes_down=d["bytes_down"],
            ipv4=d.get("ipv4"),
            ipv6=d.get("ipv6"),
            ipv4_port_range=(int(pr[0]), int(pr[1])) if pr else None,
        )


# ── Configuration ──────────────────────────────────────────────────────────────

@dataclass
class ConnectionConfiguration:
    """WAN connection configuration (GET/PUT /connection/config/).

    Read-only fields: ``is_secure_pass``, ``remote_access_min_port``,
    ``remote_access_max_port``, ``remote_access_ip``, ``api_remote_access``,
    ``adblock_not_set``.
    """

    ping: bool
    remote_access: bool
    remote_access_port: int
    wol: bool
    adblock: bool
    allow_token_request: bool
    sip_alg: str
    is_secure_pass: bool = False
    remote_access_min_port: int = 0
    remote_access_max_port: int = 65535
    remote_access_ip: str | None = None
    api_remote_access: bool = False
    adblock_not_set: bool = False

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ConnectionConfiguration:
        return cls(
            ping=d["ping"],
            remote_access=d["remote_access"],
            remote_access_port=d["remote_access_port"],
            wol=d["wol"],
            adblock=d["adblock"],
            allow_token_request=d.get("allow_token_request", True),
            sip_alg=d.get("sip_alg", "disabled"),
            is_secure_pass=d.get("is_secure_pass", False),
            remote_access_min_port=d.get("remote_access_min_port", 0),
            remote_access_max_port=d.get("remote_access_max_port", 65535),
            remote_access_ip=d.get("remote_access_ip"),
            api_remote_access=d.get("api_remote_access", False),
            adblock_not_set=d.get("adblock_not_set", False),
        )


# ── IPv6 configuration ─────────────────────────────────────────────────────────

@dataclass
class ConnectionIpv6Delegation:
    prefix: str
    next_hop: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ConnectionIpv6Delegation:
        return cls(prefix=d["prefix"], next_hop=d.get("next_hop", ""))


@dataclass
class ConnectionIpv6Configuration:
    """IPv6 connection configuration (GET/PUT /connection/ipv6/config/).

    Read-only field: ``ipv6ll``.
    """

    ipv6_enabled: bool
    ipv6_firewall: bool
    ipv6_prefix_firewall: bool
    delegations: list[ConnectionIpv6Delegation] = field(default_factory=list)
    ipv6ll: str | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ConnectionIpv6Configuration:
        return cls(
            ipv6_enabled=d["ipv6_enabled"],
            ipv6_firewall=d["ipv6_firewall"],
            ipv6_prefix_firewall=d["ipv6_prefix_firewall"],
            delegations=[ConnectionIpv6Delegation._from_dict(e) for e in d.get("delegations", [])],
            ipv6ll=d.get("ipv6ll"),
        )


# ── xDSL status [UNSTABLE] ─────────────────────────────────────────────────────

@dataclass
class XdslStatus:
    status: str
    protocol: str
    modulation: str
    uptime: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> XdslStatus:
        return cls(
            status=d["status"],
            protocol=d["protocol"],
            modulation=d["modulation"],
            uptime=d["uptime"],
        )


@dataclass
class XdslStats:
    maxrate: int
    rate: int
    snr: int
    attn: int
    snr_10: int = 0
    attn_10: int = 0
    fec: int = 0
    crc: int = 0
    hec: int = 0
    es: int = 0
    ses: int = 0
    phyr: bool = False
    ginp: bool = False
    nitro: bool = False
    rxmt: int = 0
    rxmt_corr: int = 0
    rxmt_uncorr: int = 0
    rtx_tx: int = 0
    rtx_c: int = 0
    rtx_uc: int = 0

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> XdslStats:
        return cls(
            maxrate=d.get("maxrate", 0),
            rate=d.get("rate", 0),
            snr=d.get("snr", 0),
            attn=d.get("attn", 0),
            snr_10=d.get("snr_10", 0),
            attn_10=d.get("attn_10", 0),
            fec=d.get("fec", 0),
            crc=d.get("crc", 0),
            hec=d.get("hec", 0),
            es=d.get("es", 0),
            ses=d.get("ses", 0),
            phyr=d.get("phyr", False),
            ginp=d.get("ginp", False),
            nitro=d.get("nitro", False),
            rxmt=d.get("rxmt", 0),
            rxmt_corr=d.get("rxmt_corr", 0),
            rxmt_uncorr=d.get("rxmt_uncorr", 0),
            rtx_tx=d.get("rtx_tx", 0),
            rtx_c=d.get("rtx_c", 0),
            rtx_uc=d.get("rtx_uc", 0),
        )


@dataclass
class XdslInfos:
    """xDSL connection info (GET /connection/xdsl/) [UNSTABLE]."""

    status: XdslStatus
    down: XdslStats
    up: XdslStats

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> XdslInfos:
        return cls(
            status=XdslStatus._from_dict(d["status"]),
            down=XdslStats._from_dict(d["down"]),
            up=XdslStats._from_dict(d["up"]),
        )


# ── FTTH status [UNSTABLE] ─────────────────────────────────────────────────────

@dataclass
class FtthStatus:
    """FTTH connection status (GET /connection/ftth/) [UNSTABLE]."""

    sfp_present: bool
    sfp_alim_ok: bool
    sfp_has_power_report: bool
    sfp_has_signal: bool
    link: bool
    sfp_serial: str = ""
    sfp_model: str = ""
    sfp_vendor: str = ""
    sfp_pwr_tx: int = 0
    sfp_pwr_rx: int = 0

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FtthStatus:
        return cls(
            sfp_present=d["sfp_present"],
            sfp_alim_ok=d["sfp_alim_ok"],
            sfp_has_power_report=d["sfp_has_power_report"],
            sfp_has_signal=d["sfp_has_signal"],
            link=d["link"],
            sfp_serial=d.get("sfp_serial", ""),
            sfp_model=d.get("sfp_model", ""),
            sfp_vendor=d.get("sfp_vendor", ""),
            sfp_pwr_tx=d.get("sfp_pwr_tx", 0),
            sfp_pwr_rx=d.get("sfp_pwr_rx", 0),
        )


# ── LTE [UNSTABLE] ────────────────────────────────────────────────────────────

@dataclass
class LteRadioBand:
    band: int
    enabled: bool = False
    bandwidth: int = 0
    rsrq: int = 0
    rsrp: int = 0
    rssi: int = 0
    pci: int = 0

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteRadioBand:
        return cls(
            band=d.get("band", 0),
            enabled=d.get("enabled", False),
            bandwidth=d.get("bandwidth", 0),
            rsrq=d.get("rsrq", 0),
            rsrp=d.get("rsrp", 0),
            rssi=d.get("rssi", 0),
            pci=d.get("pci", 0),
        )


@dataclass
class LteRadio:
    associated: bool
    plmn: int
    signal_level: int
    gcid: str
    ue_active: bool
    bands: list[LteRadioBand] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteRadio:
        return cls(
            associated=d.get("associated", False),
            plmn=d.get("plmn", 0),
            signal_level=d.get("signal_level", 0),
            gcid=d.get("gcid", ""),
            ue_active=d.get("ue_active", False),
            bands=[LteRadioBand._from_dict(b) for b in d.get("bands", [])],
        )


@dataclass
class LteNetwork:
    pdn_up: bool
    has_ipv4: bool
    has_ipv6: bool
    ipv4: str = ""
    ipv4_netmask: str = ""
    ipv4_dns: str = ""
    ipv6: str = ""
    ipv6_netmask: str = ""
    ipv6_dns: str = ""

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteNetwork:
        return cls(
            pdn_up=d.get("pdn_up", False),
            has_ipv4=d.get("has_ipv4", False),
            has_ipv6=d.get("has_ipv6", False),
            ipv4=d.get("ipv4", ""),
            ipv4_netmask=d.get("ipv4_netmask", ""),
            ipv4_dns=d.get("ipv4_dns", ""),
            ipv6=d.get("ipv6", ""),
            ipv6_netmask=d.get("ipv6_netmask", ""),
            ipv6_dns=d.get("ipv6_dns", ""),
        )


@dataclass
class LteSim:
    present: bool
    pin_locked: bool
    puk_locked: bool
    iccid: str = ""
    pin_remaining: int = 0
    puk_remaining: int = 0

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteSim:
        return cls(
            present=d.get("present", False),
            pin_locked=d.get("pin_locked", False),
            puk_locked=d.get("puk_locked", False),
            iccid=d.get("iccid", ""),
            pin_remaining=d.get("pin_remaining", 0),
            puk_remaining=d.get("puk_remaining", 0),
        )


@dataclass
class LteConfiguration:
    """LTE module configuration (GET /connection/lte/{id}) [UNSTABLE].

    Valid ids: ``aggregation``, ``backup``.
    """

    enabled: bool
    state: str
    fsm_state: str
    radio: LteRadio
    network: LteNetwork
    sim: LteSim

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteConfiguration:
        return cls(
            enabled=d.get("enabled", False),
            state=d.get("state", ""),
            fsm_state=d.get("fsm_state", ""),
            radio=LteRadio._from_dict(d.get("radio", {})),
            network=LteNetwork._from_dict(d.get("network", {})),
            sim=LteSim._from_dict(d.get("sim", {})),
        )


@dataclass
class LteTunnelDetails:
    connected: bool
    last_error: str = ""
    tx_flows_rate: int = 0
    tx_max_rate: int = 0
    tx_used_rate: int = 0
    rx_flows_rate: int = 0
    rx_max_rate: int = 0
    rx_used_rate: int = 0

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteTunnelDetails:
        return cls(
            connected=d.get("connected", False),
            last_error=d.get("last_error", ""),
            tx_flows_rate=d.get("tx_flows_rate", 0),
            tx_max_rate=d.get("tx_max_rate", 0),
            tx_used_rate=d.get("tx_used_rate", 0),
            rx_flows_rate=d.get("rx_flows_rate", 0),
            rx_max_rate=d.get("rx_max_rate", 0),
            rx_used_rate=d.get("rx_used_rate", 0),
        )


@dataclass
class LteTunnel:
    lte: LteTunnelDetails
    xdsl: LteTunnelDetails

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteTunnel:
        return cls(
            lte=LteTunnelDetails._from_dict(d.get("lte", {})),
            xdsl=LteTunnelDetails._from_dict(d.get("xdsl", {})),
        )


@dataclass
class LteAggregation:
    """xDSL/LTE aggregation status (GET/PUT /connection/aggregation) [UNSTABLE]."""

    enabled: bool
    tunnel: LteTunnel

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LteAggregation:
        return cls(
            enabled=d.get("enabled", False),
            tunnel=LteTunnel._from_dict(d.get("tunnel", {})),
        )


# ── DynDNS ─────────────────────────────────────────────────────────────────────

@dataclass
class DDNSStatus:
    """DynDNS provider status (GET /connection/ddns/{provider}/status/)."""

    status: str
    next_refresh: int = 0
    last_refresh: int = 0
    next_retry: int = 0
    last_error: int = 0

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DDNSStatus:
        return cls(
            status=d["status"],
            next_refresh=d.get("next_refresh", 0),
            last_refresh=d.get("last_refresh", 0),
            next_retry=d.get("next_retry", 0),
            last_error=d.get("last_error", 0),
        )


@dataclass
class DDNSConfig:
    """DynDNS provider configuration (GET/PUT /connection/ddns/{provider}/).

    Write-only field: ``password`` (not returned by GET).
    """

    enabled: bool
    hostname: str
    user: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DDNSConfig:
        return cls(
            enabled=d["enabled"],
            hostname=d.get("hostname", ""),
            user=d.get("user", ""),
        )


# ── Connection API ─────────────────────────────────────────────────────────────

class Connection:
    """Freebox Connection API.

    Obtained via ``fb.connection``::

        status = fb.connection.status()
        print(status.state, status.ipv4)

        fb.connection.set_config(ping=True, wol=False)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def status(self) -> ConnectionStatus:
        """Return the current WAN connection status."""
        return ConnectionStatus._from_dict(self._client.get("connection/"))

    def config(self) -> ConnectionConfiguration:
        """Return the current connection configuration."""
        return ConnectionConfiguration._from_dict(self._client.get("connection/config/"))

    def set_config(self, **kwargs: Any) -> ConnectionConfiguration:
        """Update the connection configuration.

        Pass only the fields to change, e.g. ``set_config(ping=True, wol=False)``.
        """
        return ConnectionConfiguration._from_dict(self._client.put("connection/config/", json=kwargs))

    def ipv6_config(self) -> ConnectionIpv6Configuration:
        """Return the current IPv6 connection configuration."""
        return ConnectionIpv6Configuration._from_dict(self._client.get("connection/ipv6/config/"))

    def set_ipv6_config(self, **kwargs: Any) -> ConnectionIpv6Configuration:
        """Update the IPv6 connection configuration."""
        return ConnectionIpv6Configuration._from_dict(self._client.put("connection/ipv6/config/", json=kwargs))

    def xdsl(self) -> XdslInfos:
        """Return the current xDSL status [UNSTABLE]."""
        return XdslInfos._from_dict(self._client.get("connection/xdsl/"))

    def ftth(self) -> FtthStatus:
        """Return the current FTTH status [UNSTABLE]."""
        return FtthStatus._from_dict(self._client.get("connection/ftth/"))

    def lte(self, id: str) -> LteConfiguration:
        """Return the LTE configuration for the given id [UNSTABLE].

        Valid ids: ``aggregation``, ``backup``.
        """
        return LteConfiguration._from_dict(self._client.get(f"connection/lte/{id}"))

    def aggregation(self) -> LteAggregation:
        """Return the xDSL/LTE aggregation status [UNSTABLE]."""
        return LteAggregation._from_dict(self._client.get("connection/aggregation"))

    def set_aggregation(self, **kwargs: Any) -> LteAggregation:
        """Update the xDSL/LTE aggregation configuration [UNSTABLE]."""
        return LteAggregation._from_dict(self._client.put("connection/aggregation", json=kwargs))

    def ddns_status(self, provider: str) -> DDNSStatus:
        """Return the status of a DynDNS provider (ovh, dyndns, noip)."""
        return DDNSStatus._from_dict(self._client.get(f"connection/ddns/{provider}/status/"))

    def ddns_config(self, provider: str) -> DDNSConfig:
        """Return the configuration of a DynDNS provider."""
        return DDNSConfig._from_dict(self._client.get(f"connection/ddns/{provider}/"))

    def set_ddns_config(self, provider: str, **kwargs: Any) -> DDNSConfig:
        """Update the configuration of a DynDNS provider."""
        return DDNSConfig._from_dict(self._client.put(f"connection/ddns/{provider}/", json=kwargs))
