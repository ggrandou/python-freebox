"""Freebox VPN Server and VPN Client APIs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── VPN Server ─────────────────────────────────────────────────────────────────


@dataclass
class VPNServer:
    """Status of a VPN server instance."""

    name: str
    type: str
    state: str
    connection_count: int
    auth_connection_count: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNServer:
        return cls(
            name=d.get("name", ""),
            type=d.get("type", ""),
            state=d.get("state", ""),
            connection_count=d.get("connection_count", 0),
            auth_connection_count=d.get("auth_connection_count", 0),
        )


@dataclass
class VPNPPTPConfig:
    """PPTP-specific VPN server configuration."""

    mppe: str
    allowed_auth: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNPPTPConfig:
        return cls(
            mppe=d.get("mppe", ""),
            allowed_auth=d.get("allowed_auth", {}),
        )


@dataclass
class VPNOpenVpnConfig:
    """OpenVPN-specific VPN server configuration."""

    cipher: str
    disable_fragment: bool
    use_tcp: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNOpenVpnConfig:
        return cls(
            cipher=d.get("cipher", ""),
            disable_fragment=d.get("disable_fragment", False),
            use_tcp=d.get("use_tcp", False),
        )


@dataclass
class VPNWireGuardServerConfig:
    """WireGuard-specific VPN server configuration."""

    mtu: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNWireGuardServerConfig:
        return cls(mtu=d.get("mtu", 0))


@dataclass
class VPNIPSecAuthMode:
    """IPSec authentication mode."""

    id_source: str
    id_custom: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNIPSecAuthMode:
        return cls(
            id_source=d.get("id_source", ""),
            id_custom=d.get("id_custom", ""),
        )


@dataclass
class VPNIPSecConfig:
    """IPSec-specific VPN server configuration."""

    ike_version: int
    auth_modes: list[VPNIPSecAuthMode] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNIPSecConfig:
        return cls(
            ike_version=d.get("ike_version", 0),
            auth_modes=[VPNIPSecAuthMode._from_dict(m) for m in d.get("auth_modes", [])],
        )


@dataclass
class VPNServerConfig:
    """Full configuration of a VPN server."""

    id: str
    type: str
    enabled: bool
    enable_ipv4: bool
    enable_ipv6: bool
    port: int
    min_port: int
    max_port: int
    port_ike: int
    port_nat: int
    ip_start: str
    ip_end: str
    ip6_start: str
    ip6_end: str
    conf_pptp: VPNPPTPConfig | None = None
    conf_openvpn: VPNOpenVpnConfig | None = None
    conf_ipsec: VPNIPSecConfig | None = None
    conf_wireguard: VPNWireGuardServerConfig | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNServerConfig:
        conf_pptp = VPNPPTPConfig._from_dict(d["conf_pptp"]) if "conf_pptp" in d else None
        conf_openvpn = VPNOpenVpnConfig._from_dict(d["conf_openvpn"]) if "conf_openvpn" in d else None
        conf_ipsec = VPNIPSecConfig._from_dict(d["conf_ipsec"]) if "conf_ipsec" in d else None
        conf_wireguard = VPNWireGuardServerConfig._from_dict(d["conf_wireguard"]) if "conf_wireguard" in d else None
        return cls(
            id=d.get("id", ""),
            type=d.get("type", ""),
            enabled=d.get("enabled", False),
            enable_ipv4=d.get("enable_ipv4", False),
            enable_ipv6=d.get("enable_ipv6", False),
            port=d.get("port", 0),
            min_port=d.get("min_port", 0),
            max_port=d.get("max_port", 0),
            port_ike=d.get("port_ike", 0),
            port_nat=d.get("port_nat", 0),
            ip_start=d.get("ip_start", ""),
            ip_end=d.get("ip_end", ""),
            ip6_start=d.get("ip6_start", ""),
            ip6_end=d.get("ip6_end", ""),
            conf_pptp=conf_pptp,
            conf_openvpn=conf_openvpn,
            conf_ipsec=conf_ipsec,
            conf_wireguard=conf_wireguard,
        )


@dataclass
class VPNWireGuardUserConfig:
    """WireGuard-specific VPN user configuration."""

    keepalive: int
    psk: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNWireGuardUserConfig:
        return cls(
            keepalive=d.get("keepalive", 0),
            psk=d.get("psk", False),
        )


@dataclass
class VPNUser:
    """A VPN server user."""

    login: str
    type: str
    password_set: bool
    ip_reservation: str
    conf_wireguard: VPNWireGuardUserConfig | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNUser:
        conf_wg = VPNWireGuardUserConfig._from_dict(d["conf_wireguard"]) if "conf_wireguard" in d else None
        return cls(
            login=d.get("login", ""),
            type=d.get("type", "standard"),
            password_set=d.get("password_set", False),
            ip_reservation=d.get("ip_reservation", ""),
            conf_wireguard=conf_wg,
        )


@dataclass
class VPNIPReservation:
    """An IP address reservation in the VPN pool."""

    login: str
    ip: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNIPReservation:
        return cls(login=d.get("login", ""), ip=d.get("ip", ""))


@dataclass
class VPNIPPool:
    """VPN server IP address pool."""

    ip_start: str
    ip_end: str
    reservations: list[VPNIPReservation] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNIPPool:
        return cls(
            ip_start=d.get("ip_start", ""),
            ip_end=d.get("ip_end", ""),
            reservations=[VPNIPReservation._from_dict(r) for r in d.get("reservations", [])],
        )


@dataclass
class VPNConnection:
    """An active VPN server connection."""

    id: str
    vpn: str
    user: str
    authenticated: bool
    auth_time: int
    src_ip: str
    src_port: int
    local_ip: str
    rx_bytes: int
    tx_bytes: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNConnection:
        return cls(
            id=d.get("id", ""),
            vpn=d.get("vpn", ""),
            user=d.get("user", ""),
            authenticated=d.get("authenticated", False),
            auth_time=d.get("auth_time", 0),
            src_ip=d.get("src_ip", ""),
            src_port=d.get("src_port", 0),
            local_ip=d.get("local_ip", ""),
            rx_bytes=d.get("rx_bytes", 0),
            tx_bytes=d.get("tx_bytes", 0),
        )


# ── VPN Client ─────────────────────────────────────────────────────────────────


@dataclass
class VPNClientPPTPConfig:
    """PPTP-specific VPN client configuration."""

    remote_host: str
    username: str
    mppe: str
    allowed_auth: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNClientPPTPConfig:
        return cls(
            remote_host=d.get("remote_host", ""),
            username=d.get("username", ""),
            mppe=d.get("mppe", ""),
            allowed_auth=d.get("allowed_auth", {}),
        )


@dataclass
class VPNClientWireGuardIP:
    """An IP address entry for WireGuard client local addresses."""

    ip: str
    len: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNClientWireGuardIP:
        return cls(ip=d.get("ip", ""), len=d.get("len", 0))


@dataclass
class VPNClientWireGuardConfig:
    """WireGuard-specific VPN client configuration."""

    remote_addr: str
    remote_port: int
    remote_public_key: str
    remote_preshared_key: str
    local_priv_key: str
    local_addr: list[VPNClientWireGuardIP] = field(default_factory=list)
    dns: list[str] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNClientWireGuardConfig:
        return cls(
            remote_addr=d.get("remote_addr", ""),
            remote_port=d.get("remote_port", 0),
            remote_public_key=d.get("remote_public_key", ""),
            remote_preshared_key=d.get("remote_preshared_key", ""),
            local_priv_key=d.get("local_priv_key", ""),
            local_addr=[VPNClientWireGuardIP._from_dict(a) for a in d.get("local_addr", [])],
            dns=d.get("dns", []),
        )


@dataclass
class VPNClientConfig:
    """A VPN client configuration entry."""

    id: str
    description: str
    type: str
    active: bool
    conf_pptp: VPNClientPPTPConfig | None = None
    conf_wireguard: VPNClientWireGuardConfig | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNClientConfig:
        conf_pptp = VPNClientPPTPConfig._from_dict(d["conf_pptp"]) if "conf_pptp" in d else None
        conf_wg = VPNClientWireGuardConfig._from_dict(d["conf_wireguard"]) if "conf_wireguard" in d else None
        return cls(
            id=d.get("id", ""),
            description=d.get("description", ""),
            type=d.get("type", ""),
            active=d.get("active", False),
            conf_pptp=conf_pptp,
            conf_wireguard=conf_wg,
        )


@dataclass
class VPNClientStats:
    """VPN client connection statistics."""

    rate_up: int
    rate_down: int
    bytes_up: int
    bytes_down: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNClientStats:
        return cls(
            rate_up=d.get("rate_up", 0),
            rate_down=d.get("rate_down", 0),
            bytes_up=d.get("bytes_up", 0),
            bytes_down=d.get("bytes_down", 0),
        )


@dataclass
class VPNClientStatus:
    """Overall VPN client status."""

    enabled: bool
    active_vpn: str
    active_vpn_description: str
    type: str
    state: str
    last_up: int
    last_try: int
    next_try: int
    last_error: str
    stats: VPNClientStats | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VPNClientStatus:
        stats = VPNClientStats._from_dict(d["stats"]) if "stats" in d else None
        return cls(
            enabled=d.get("enabled", False),
            active_vpn=d.get("active_vpn", ""),
            active_vpn_description=d.get("active_vpn_description", ""),
            type=d.get("type", ""),
            state=d.get("state", ""),
            last_up=d.get("last_up", 0),
            last_try=d.get("last_try", 0),
            next_try=d.get("next_try", 0),
            last_error=d.get("last_error", ""),
            stats=stats,
        )


# ── API classes ────────────────────────────────────────────────────────────────


class VpnServer:
    """Freebox VPN Server API.

    Obtained via ``fb.vpn_server``::

        servers = fb.vpn_server.servers()
        cfg = fb.vpn_server.server_config("openvpn_routed")
        users = fb.vpn_server.users()
        conns = fb.vpn_server.connections()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def servers(self) -> list[VPNServer]:
        """Return the list of VPN servers and their current state."""
        result = self._client.get("vpn/")
        return [VPNServer._from_dict(s) for s in result]

    def server_config(self, vpn_id: str) -> VPNServerConfig:
        """Return the configuration of the given VPN server."""
        return VPNServerConfig._from_dict(self._client.get(f"vpn/{vpn_id}/config/"))

    def set_server_config(self, vpn_id: str, **kwargs: Any) -> VPNServerConfig:
        """Update the configuration of the given VPN server."""
        return VPNServerConfig._from_dict(self._client.put(f"vpn/{vpn_id}/config/", json=kwargs))

    def users(self) -> list[VPNUser]:
        """Return the list of VPN users."""
        result = self._client.get("vpn/user/")
        return [VPNUser._from_dict(u) for u in result]

    def user(self, login: str) -> VPNUser:
        """Return the VPN user with the given login."""
        return VPNUser._from_dict(self._client.get(f"vpn/user/{login}"))

    def add_user(self, login: str, password: str, **kwargs: Any) -> VPNUser:
        """Create a new VPN user."""
        payload = {"login": login, "password": password, **kwargs}
        return VPNUser._from_dict(self._client.post("vpn/user/", json=payload))

    def update_user(self, login: str, **kwargs: Any) -> VPNUser:
        """Update the VPN user with the given login."""
        return VPNUser._from_dict(self._client.put(f"vpn/user/{login}", json=kwargs))

    def delete_user(self, login: str) -> None:
        """Delete the VPN user with the given login."""
        self._client.delete(f"vpn/user/{login}")

    def ip_pool(self) -> VPNIPPool:
        """Return the VPN server IP pool and reservations."""
        return VPNIPPool._from_dict(self._client.get("vpn/ip_pool/"))

    def connections(self) -> list[VPNConnection]:
        """Return the list of active VPN server connections."""
        result = self._client.get("vpn/connection/")
        return [VPNConnection._from_dict(c) for c in result]

    def delete_connection(self, connection_id: str) -> None:
        """Close the active VPN connection with the given id."""
        self._client.delete(f"vpn/connection/{connection_id}")

    def download_config(self, server_name: str, login: str, fmt: str = "plain") -> str:
        """Download a client configuration file for the given VPN server and user.

        ``fmt`` must be ``"plain"`` or ``"json"``.
        Returns the configuration file contents as a string.

        .. warning::
            Downloading a new OpenVPN config invalidates any previous config
            file issued for that user.
        """
        return self._client.get_text(f"vpn/download_config/{server_name}/{login}/{fmt}")


class VpnClient:
    """Freebox VPN Client API.

    Obtained via ``fb.vpn_client``::

        configs = fb.vpn_client.configs()
        status = fb.vpn_client.status()
        log = fb.vpn_client.log()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def configs(self) -> list[VPNClientConfig]:
        """Return the list of VPN client configurations."""
        result = self._client.get("vpn_client/config/")
        return [VPNClientConfig._from_dict(c) for c in result]

    def config(self, config_id: str) -> VPNClientConfig:
        """Return the VPN client configuration with the given id."""
        return VPNClientConfig._from_dict(self._client.get(f"vpn_client/config/{config_id}"))

    def add_config(self, **kwargs: Any) -> VPNClientConfig:
        """Create a new VPN client configuration."""
        return VPNClientConfig._from_dict(self._client.post("vpn_client/config/", json=kwargs))

    def update_config(self, config_id: str, **kwargs: Any) -> VPNClientConfig:
        """Update the VPN client configuration with the given id."""
        return VPNClientConfig._from_dict(self._client.put(f"vpn_client/config/{config_id}", json=kwargs))

    def delete_config(self, config_id: str) -> None:
        """Delete the VPN client configuration with the given id."""
        self._client.delete(f"vpn_client/config/{config_id}")

    def status(self) -> VPNClientStatus:
        """Return the current VPN client status."""
        return VPNClientStatus._from_dict(self._client.get("vpn_client/status"))

    def log(self) -> str:
        """Return the VPN client log as a string."""
        result = self._client.get("vpn_client/log")
        return result if isinstance(result, str) else ""
