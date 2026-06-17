"""Freebox DHCP API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from freebox.lan import LanHost

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── DHCP option type table ─────────────────────────────────────────────────────

# Maps each option identifier (RFC 2132) to its wire type.
_OPTION_TYPES: dict[str, str] = {
    # string
    "hostname":                 "string",
    "merit_dump_file":          "string",
    "root_path":                "string",
    "extensions_path":          "string",
    "nis_domain":               "string",
    "nis_plus_domain":          "string",
    "tftp_server_name":         "string",
    "bootfile_name":            "string",
    "nds_tree_name":            "string",
    "nds_context":              "string",
    "timezone_posix":           "string",
    "timezone_database":        "string",
    # bool ("true"/"false"/"1"/"0" on the wire)
    "ip_fwd":                   "bool",
    "ip_fwd_non_local":         "bool",
    "local_subnets":            "bool",
    "mask_discovery":           "bool",
    "mask_supplier":            "bool",
    "perform_rd":               "bool",
    "trailer_encapsulation":    "bool",
    "eth_encapsulation":        "bool",
    "tcp_keepalive_garbage":    "bool",
    # single IPv4 address (kept as str)
    "rs_address":               "ip",
    # comma-separated IPv4 address list
    "time_server":              "ip_list",
    "log_server":               "ip_list",
    "cookie_server":            "ip_list",
    "lpr_server":               "ip_list",
    "impress_server":           "ip_list",
    "resource_location_server": "ip_list",
    "swap_server":              "ip_list",
    "nis_server":               "ip_list",
    "ntp_server":               "ip_list",
    "nis_plus_server":          "ip_list",
    "mobile_ip_agent":          "ip_list",
    "smtp_server":              "ip_list",
    "pop3_server":              "ip_list",
    "nntp_server":              "ip_list",
    "www_server":               "ip_list",
    "finger_server":            "ip_list",
    "irc_server":               "ip_list",
    "streettalk_server":        "ip_list",
    "stda_server":              "ip_list",
    "slp_directory_agent":      "ip_list",
    "nds_servers":              "ip_list",
    "ldap_servers":             "ip_list",
    "capwap_ac":                "ip_list",
    "tftp_server_address":      "ip_list",
    # signed 32-bit integer
    "time_offset":              "s32",
    # unsigned integers
    "ip_ttl":                   "u8",
    "tcp_ttl":                  "u8",
    "ip_max_reassembly_size":   "u16",
    "mtu":                      "u16",
    "ip_pmtu_timeout":          "u32",
    "arp_cache_timeout":        "u32",
    "tcp_keepalive_interval":   "u32",
    # raw binary (hex string on the wire → bytes in Python)
    "vendor_specific":          "hexstring",
    "slp_service_scope":        "hexstring",
    "name_service":             "hexstring",
    "classless_static_route":   "hexstring",
    # RFC 3397 domain search list (hex string on the wire → list[str] in Python)
    "domain_search":            "domain_search",
}


# ── Wire-format ↔ Python conversion ───────────────────────────────────────────

def _decode_domain_search(hexval: str) -> list[str]:
    """Decode an RFC 3397 hex string to a list of plain domain names.

    Handles DNS compression pointers (RFC 1035 §4.1.4).
    """
    data = bytes.fromhex(hexval)
    domains: list[str] = []
    i = 0

    def _read_name(pos: int, visited: frozenset[int] = frozenset()) -> tuple[str, int]:
        labels: list[str] = []
        end_pos: int | None = None
        while pos < len(data):
            length = data[pos]
            if length == 0:
                pos += 1
                break
            if length & 0xC0 == 0xC0:
                if pos + 1 >= len(data):
                    raise ValueError("Truncated DNS compression pointer")
                target = ((length & 0x3F) << 8) | data[pos + 1]
                if end_pos is None:
                    end_pos = pos + 2
                if target in visited:
                    raise ValueError("DNS compression pointer loop")
                suffix, _ = _read_name(target, visited | {target})
                if suffix:
                    labels.append(suffix)
                break
            pos += 1
            labels.append(data[pos : pos + length].decode("ascii"))
            pos += length
        return ".".join(labels), end_pos if end_pos is not None else pos

    while i < len(data):
        name, i = _read_name(i)
        if name:
            domains.append(name)
    return domains


def _encode_domain_search(domains: list[str]) -> str:
    """Encode a list of domain names to RFC 3397 hex string (no compression)."""
    buf = bytearray()
    for domain in domains:
        for label in domain.rstrip(".").split("."):
            raw = label.encode("ascii")
            if len(raw) > 63:
                raise ValueError(f"DNS label too long (>63 bytes): {label!r}")
            buf.append(len(raw))
            buf.extend(raw)
        buf.append(0)
    return buf.hex().upper()


# Python-native type for a DHCP option value.
DhcpOptionValue = str | int | bool | list[str] | bytes


def _decode_val(opt_id: str, raw: str) -> DhcpOptionValue:
    t = _OPTION_TYPES.get(opt_id, "string")
    if t == "bool":
        return raw.lower() in ("true", "1")
    if t in ("s8", "s16", "s32", "u8", "u16", "u32"):
        return int(raw)
    if t == "ip_list":
        return [s.strip() for s in raw.split(",") if s.strip()]
    if t == "hexstring":
        return bytes.fromhex(raw)
    if t == "domain_search":
        return _decode_domain_search(raw) if raw else []
    return raw  # "string", "ip", or unknown option


def _encode_val(opt_id: str, val: DhcpOptionValue) -> str:
    t = _OPTION_TYPES.get(opt_id, "string")
    if t == "bool":
        if isinstance(val, bool):
            return "true" if val else "false"
        return str(val)
    if t in ("s8", "s16", "s32", "u8", "u16", "u32"):
        return str(int(val))  # type: ignore[arg-type]
    if t == "ip_list":
        if isinstance(val, list):
            return ", ".join(val)
        return str(val)
    if t == "hexstring":
        if isinstance(val, bytes):
            return val.hex().upper()
        return str(val)
    if t == "domain_search":
        if isinstance(val, list):
            return _encode_domain_search(val)
        return str(val)
    return str(val)  # "string", "ip", or unknown


# ── DHCP Option ────────────────────────────────────────────────────────────────

@dataclass
class DhcpOption:
    """A DHCP option (RFC 2132).

    The ``val`` attribute holds a Python-native value whose type depends on the
    option identifier:

    - ``bool`` — boolean options (e.g. ``ip_fwd``, ``tcp_keepalive_garbage``)
    - ``int`` — integer options (e.g. ``tcp_ttl``, ``mtu``, ``time_offset``)
    - ``list[str]`` — IP-list options (e.g. ``ntp_server``) **and** the
      ``domain_search`` option (list of plain domain names, transparently
      encoded/decoded with RFC 3397)
    - ``bytes`` — raw binary options (e.g. ``vendor_specific``,
      ``classless_static_route``)
    - ``str`` — string and single-IP options (e.g. ``hostname``, ``rs_address``)

    Unknown option identifiers are kept as ``str``.
    """

    id: str
    val: str | int | bool | list[str] | bytes

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DhcpOption:
        opt_id = d["id"]
        return cls(id=opt_id, val=_decode_val(opt_id, d.get("val", "")))

    def _to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "val": _encode_val(self.id, self.val)}


# ── DHCP Config ────────────────────────────────────────────────────────────────

@dataclass
class DhcpConfig:
    """DHCP server configuration (GET/PUT /dhcp/config/)."""

    enabled: bool
    sticky_assign: bool
    ip_range_start: str
    ip_range_end: str
    always_broadcast: bool
    ignore_out_of_range_hint: bool
    gateway: str
    netmask: str
    boot_server: str
    boot_file: str
    dns: list[str]
    options: list[DhcpOption]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DhcpConfig:
        return cls(
            enabled=d.get("enabled", False),
            sticky_assign=d.get("sticky_assign", False),
            ip_range_start=d.get("ip_range_start", ""),
            ip_range_end=d.get("ip_range_end", ""),
            always_broadcast=d.get("always_broadcast", False),
            ignore_out_of_range_hint=d.get("ignore_out_of_range_hint", False),
            gateway=d.get("gateway", ""),
            netmask=d.get("netmask", ""),
            boot_server=d.get("boot_server", ""),
            boot_file=d.get("boot_file", ""),
            dns=d.get("dns", []),
            options=[DhcpOption._from_dict(o) for o in d.get("options", [])],
        )


# ── DHCP Static Lease ──────────────────────────────────────────────────────────

@dataclass
class DhcpStaticLease:
    """A DHCP static lease (GET/PUT/DELETE /dhcp/static_lease/)."""

    id: str
    mac: str
    ip: str
    comment: str
    hostname: str
    options: list[DhcpOption]
    host: LanHost | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DhcpStaticLease:
        host_raw = d.get("host")
        return cls(
            id=d["id"],
            mac=d.get("mac", ""),
            ip=d.get("ip", ""),
            comment=d.get("comment", ""),
            hostname=d.get("hostname", ""),
            options=[DhcpOption._from_dict(o) for o in d.get("options", [])],
            host=LanHost._from_dict(host_raw) if host_raw else None,
        )


# ── DHCP Dynamic Lease ─────────────────────────────────────────────────────────

@dataclass
class DhcpDynamicLease:
    """A DHCP dynamic lease (GET /dhcp/dynamic_lease/)."""

    mac: str
    ip: str
    hostname: str
    lease_remaining: int
    assign_time: int
    refresh_time: int
    is_static: bool
    options: list[DhcpOption]
    host: LanHost | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DhcpDynamicLease:
        host_raw = d.get("host")
        return cls(
            mac=d.get("mac", ""),
            ip=d.get("ip", ""),
            hostname=d.get("hostname", ""),
            lease_remaining=d.get("lease_remaining", 0),
            assign_time=d.get("assign_time", 0),
            refresh_time=d.get("refresh_time", 0),
            is_static=d.get("is_static", False),
            options=[DhcpOption._from_dict(o) for o in d.get("options", [])],
            host=LanHost._from_dict(host_raw) if host_raw else None,
        )


# ── DHCP API ───────────────────────────────────────────────────────────────────

class Dhcp:
    """Freebox DHCP API.

    Obtained via ``fb.dhcp``::

        config = fb.dhcp.config()
        print(config.enabled, config.ip_range_start, config.ip_range_end)

        leases = fb.dhcp.static_leases()
        for lease in leases:
            print(lease.mac, lease.ip)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Config ─────────────────────────────────────────────────────────────────

    def config(self) -> DhcpConfig:
        """Return the current DHCP server configuration."""
        return DhcpConfig._from_dict(self._client.get("dhcp/config/"))

    def set_config(self, **kwargs: Any) -> DhcpConfig:
        """Update the DHCP server configuration.

        Pass only the fields to change, e.g. ``set_config(enabled=True)``.
        """
        return DhcpConfig._from_dict(self._client.put("dhcp/config/", json=kwargs))

    # ── Static leases ──────────────────────────────────────────────────────────

    def static_leases(self) -> list[DhcpStaticLease]:
        """Return the list of DHCP static leases."""
        return [DhcpStaticLease._from_dict(l) for l in self._client.get("dhcp/static_lease/")]

    def static_lease(self, lease_id: str) -> DhcpStaticLease:
        """Return a specific DHCP static lease by id (MAC address)."""
        return DhcpStaticLease._from_dict(self._client.get(f"dhcp/static_lease/{lease_id}"))

    def add_static_lease(self, mac: str, ip: str, **kwargs: Any) -> DhcpStaticLease:
        """Create a new DHCP static lease.

        ``mac`` and ``ip`` are required; other fields (``comment``, ``options``)
        can be passed as keyword arguments.
        """
        return DhcpStaticLease._from_dict(
            self._client.post("dhcp/static_lease/", json={"mac": mac, "ip": ip, **kwargs})
        )

    def set_static_lease(self, lease_id: str, **kwargs: Any) -> DhcpStaticLease:
        """Update a DHCP static lease.

        Pass only the fields to change, e.g. ``set_static_lease(id, comment="My PC")``.
        """
        return DhcpStaticLease._from_dict(
            self._client.put(f"dhcp/static_lease/{lease_id}", json=kwargs)
        )

    def delete_static_lease(self, lease_id: str) -> None:
        """Delete a DHCP static lease."""
        self._client.delete(f"dhcp/static_lease/{lease_id}")

    # ── Dynamic leases ─────────────────────────────────────────────────────────

    def dynamic_leases(self) -> list[DhcpDynamicLease]:
        """Return the list of current DHCP dynamic leases."""
        return [DhcpDynamicLease._from_dict(l) for l in self._client.get("dhcp/dynamic_lease/")]
