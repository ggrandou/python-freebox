"""Freebox Wi-Fi API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class WifiGlobalConfig:
    """Wi-Fi global configuration."""

    enabled: bool
    mac_filter_state: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiGlobalConfig:
        return cls(
            enabled=d.get("enabled", False),
            mac_filter_state=d.get("mac_filter_state", "disabled"),
        )


@dataclass
class WifiSteeringConfig:
    """Wi-Fi band-steering configuration."""

    steering_level: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiSteeringConfig:
        return cls(steering_level=d.get("steering_level", 0))


@dataclass
class ExpectedPhy:
    """Expected Wi-Fi card as reported in the global state."""

    band: str
    phy_id: int
    detected: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ExpectedPhy:
        return cls(
            band=d.get("band", ""),
            phy_id=d.get("phy_id", 0),
            detected=d.get("detected", False),
        )


@dataclass
class WifiGlobalState:
    """Wi-Fi global state."""

    state: str
    expected_phys: list[ExpectedPhy] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiGlobalState:
        return cls(
            state=d.get("state", ""),
            expected_phys=[ExpectedPhy._from_dict(p) for p in d.get("expected_phys", [])],
        )


@dataclass
class WifiApHtConfig:
    """802.11n/ac radio configuration for an AP."""

    ht_enabled: bool
    ac_enabled: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiApHtConfig:
        return cls(
            ht_enabled=d.get("ht_enabled", False),
            ac_enabled=d.get("ac_enabled", False),
        )


@dataclass
class WifiApHeConfig:
    """802.11ax (HE) radio configuration for an AP."""

    enabled: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiApHeConfig:
        return cls(enabled=d.get("enabled", False))


@dataclass
class WifiApConfig:
    """Configurable settings of a Wi-Fi access point."""

    band: str
    channel_width: str
    primary_channel: int
    secondary_channel: int
    dfs_enabled: bool
    ht: WifiApHtConfig | None
    he: WifiApHeConfig | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiApConfig:
        return cls(
            band=d.get("band", ""),
            channel_width=str(d.get("channel_width", "")),
            primary_channel=d.get("primary_channel", 0),
            secondary_channel=d.get("secondary_channel", 0),
            dfs_enabled=d.get("dfs_enabled", False),
            ht=WifiApHtConfig._from_dict(d["ht"]) if "ht" in d else None,
            he=WifiApHeConfig._from_dict(d["he"]) if "he" in d else None,
        )


@dataclass
class WifiApStatus:
    """Current (read-only) status of a Wi-Fi access point."""

    state: str
    channel_width: str
    primary_channel: int
    secondary_channel: int
    dfs_cac_remaining_time: int
    dfs_disabled: bool
    temp_disable_remaining_time: int | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiApStatus:
        return cls(
            state=d.get("state", ""),
            channel_width=str(d.get("channel_width", "")),
            primary_channel=d.get("primary_channel", 0),
            secondary_channel=d.get("secondary_channel", 0),
            dfs_cac_remaining_time=d.get("dfs_cac_remaining_time", 0),
            dfs_disabled=d.get("dfs_disabled", False),
            temp_disable_remaining_time=d.get("temp_disable_remaining_time"),
        )


@dataclass
class WifiAp:
    """Wi-Fi access point (AP)."""

    id: int
    name: str
    status: WifiApStatus | None
    # capabilities is [UNSTABLE] and uses non-identifier band names as keys
    capabilities: dict[str, Any]
    config: WifiApConfig | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiAp:
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            status=WifiApStatus._from_dict(d["status"]) if "status" in d else None,
            capabilities=d.get("capabilities", {}),
            config=WifiApConfig._from_dict(d["config"]) if "config" in d else None,
        )


@dataclass
class WifiAllowedComb:
    """Allowed channel combination for a Wi-Fi AP."""

    band: str
    channel_width: str
    need_dfs: bool
    dfs_cac_time: int
    psc: bool
    primary: int
    secondary: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiAllowedComb:
        return cls(
            band=d.get("band", ""),
            channel_width=str(d.get("channel_width", "")),
            need_dfs=d.get("need_dfs", False),
            dfs_cac_time=d.get("dfs_cac_time", 0),
            psc=d.get("psc", False),
            primary=d.get("primary", 0),
            secondary=d.get("secondary", 0),
        )


@dataclass
class WifiApChannelSurveyData:
    """Single sample from the AP channel survey history."""

    timestamp: int
    busy_percent: int
    tx_percent: int
    rx_percent: int
    rx_bss_percent: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiApChannelSurveyData:
        return cls(
            timestamp=d.get("timestamp", 0),
            busy_percent=d.get("busy_percent", 0),
            tx_percent=d.get("tx_percent", 0),
            rx_percent=d.get("rx_percent", 0),
            rx_bss_percent=d.get("rx_bss_percent", 0),
        )


@dataclass
class WifiNeighborCap:
    """Capabilities of a neighbouring Wi-Fi access point."""

    legacy: bool
    ht: bool
    vht: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiNeighborCap:
        return cls(
            legacy=d.get("legacy", False),
            ht=d.get("ht", False),
            vht=d.get("vht", False),
        )


@dataclass
class WifiNeighbor:
    """Neighbouring Wi-Fi access point detected by a scan."""

    bssid: str
    ssid: str
    band: str
    channel_width: str
    channel: int
    secondary_channel: int
    signal: int
    capabilities: WifiNeighborCap | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiNeighbor:
        return cls(
            bssid=d.get("bssid", ""),
            ssid=d.get("ssid", ""),
            band=d.get("band", ""),
            channel_width=str(d.get("channel_width", "")),
            channel=d.get("channel", 0),
            secondary_channel=d.get("secondary_channel", 0),
            signal=d.get("signal", 0),
            capabilities=WifiNeighborCap._from_dict(d["capabilities"]) if "capabilities" in d else None,
        )


@dataclass
class WifiChannelUsage:
    """Channel usage statistics as seen by a Wi-Fi AP."""

    channel: int
    band: str
    noise_level: int
    rx_busy_percent: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiChannelUsage:
        return cls(
            channel=d.get("channel", 0),
            band=d.get("band", ""),
            noise_level=d.get("noise_level", 0),
            rx_busy_percent=d.get("rx_busy_percent", 0),
        )


@dataclass
class WifiStationStats:
    """Per-direction link statistics for a connected Wi-Fi station."""

    bitrate: int
    mcs: int
    vht_mcs: int
    width: str
    shortgi: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiStationStats:
        return cls(
            bitrate=d.get("bitrate", -1),
            mcs=d.get("mcs", -1),
            vht_mcs=d.get("vht_mcs", -1),
            width=str(d.get("width", "")),
            shortgi=d.get("shortgi", False),
        )


@dataclass
class WifiStationFlags:
    """Capability flags for a connected Wi-Fi station."""

    legacy: bool
    ht: bool
    vht: bool
    he: bool
    authorized: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiStationFlags:
        return cls(
            legacy=d.get("legacy", False),
            ht=d.get("ht", False),
            vht=d.get("vht", False),
            he=d.get("he", False),
            authorized=d.get("authorized", False),
        )


@dataclass
class WifiStation:
    """Wi-Fi station (client) associated to an AP."""

    id: str
    mac: str
    bssid: str
    hostname: str
    state: str
    inactive: int
    conn_duration: int
    rx_bytes: int
    tx_bytes: int
    tx_rate: int
    rx_rate: int
    signal: int
    flags: WifiStationFlags | None
    last_rx: WifiStationStats | None
    last_tx: WifiStationStats | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiStation:
        return cls(
            id=d.get("id", ""),
            mac=d.get("mac", ""),
            bssid=d.get("bssid", ""),
            hostname=d.get("hostname", ""),
            state=d.get("state", ""),
            inactive=d.get("inactive", 0),
            conn_duration=d.get("conn_duration", 0),
            rx_bytes=d.get("rx_bytes", 0),
            tx_bytes=d.get("tx_bytes", 0),
            tx_rate=d.get("tx_rate", 0),
            rx_rate=d.get("rx_rate", 0),
            signal=d.get("signal", 0),
            flags=WifiStationFlags._from_dict(d["flags"]) if "flags" in d else None,
            last_rx=WifiStationStats._from_dict(d["last_rx"]) if "last_rx" in d else None,
            last_tx=WifiStationStats._from_dict(d["last_tx"]) if "last_tx" in d else None,
        )


@dataclass
class WifiBssStatus:
    """Current (read-only) status of a Wi-Fi BSS."""

    state: str
    sta_count: int
    authorized_sta_count: int
    custom_key_ssid: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiBssStatus:
        return cls(
            state=d.get("state", ""),
            sta_count=d.get("sta_count", 0),
            authorized_sta_count=d.get("authorized_sta_count", 0),
            custom_key_ssid=d.get("custom_key_ssid", ""),
        )


@dataclass
class WifiBssConfig:
    """Configurable settings of a Wi-Fi BSS."""

    enabled: bool
    ssid: str
    hide_ssid: bool
    encryption: str
    key: str
    eapol_version: int
    gcmp256: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiBssConfig:
        return cls(
            enabled=d.get("enabled", False),
            ssid=d.get("ssid", ""),
            hide_ssid=d.get("hide_ssid", False),
            encryption=d.get("encryption", ""),
            key=d.get("key", ""),
            eapol_version=d.get("eapol_version", 2),
            gcmp256=d.get("gcmp256", False),
        )


@dataclass
class WifiBss:
    """Wi-Fi BSS (Basic Service Set)."""

    id: str
    phy_id: int
    use_shared_params: bool
    config: WifiBssConfig | None
    bss_params: WifiBssConfig | None
    shared_bss_params: WifiBssConfig | None
    status: WifiBssStatus | None
    disable_wep: bool
    partners: list[int]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiBss:
        return cls(
            id=d.get("id", ""),
            phy_id=d.get("phy_id", 0),
            use_shared_params=d.get("use_shared_params", False),
            config=WifiBssConfig._from_dict(d["config"]) if "config" in d else None,
            bss_params=WifiBssConfig._from_dict(d["bss_params"]) if "bss_params" in d else None,
            shared_bss_params=WifiBssConfig._from_dict(d["shared_bss_params"]) if "shared_bss_params" in d else None,
            status=WifiBssStatus._from_dict(d["status"]) if "status" in d else None,
            disable_wep=d.get("disable_wep", False),
            partners=d.get("partners", []),
        )


@dataclass
class WifiPlanning:
    """Wi-Fi scheduling plan."""

    use_planning: bool
    resolution: int
    mapping: list[str]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiPlanning:
        return cls(
            use_planning=d.get("use_planning", False),
            resolution=d.get("resolution", 0),
            mapping=d.get("mapping", []),
        )


@dataclass
class WifiMacFilter:
    """Wi-Fi MAC address filter entry."""

    id: str
    mac: str
    comment: str
    type: str
    hostname: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> WifiMacFilter:
        return cls(
            id=d.get("id", ""),
            mac=d.get("mac", ""),
            comment=d.get("comment", ""),
            type=d.get("type", ""),
            hostname=d.get("hostname", ""),
        )


class Wifi:
    """Freebox Wi-Fi API.

    Obtained via ``fb.wifi``::

        cfg   = fb.wifi.config()
        state = fb.wifi.state()
        aps   = fb.wifi.aps()
        for ap in aps:
            stations = fb.wifi.ap_stations(ap.id)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Global config ──────────────────────────────────────────────────────────

    def config(self) -> WifiGlobalConfig:
        """Return the Wi-Fi global configuration."""
        return WifiGlobalConfig._from_dict(self._client.get("wifi/config/"))

    def set_config(self, **kwargs: Any) -> WifiGlobalConfig:
        """Update the Wi-Fi global configuration.

        Accepted keyword arguments: ``enabled``, ``mac_filter_state``.
        """
        return WifiGlobalConfig._from_dict(self._client.put("wifi/config/", json=kwargs))

    def reset_config(self) -> None:
        """Reset Wi-Fi configuration to factory defaults."""
        self._client.post("wifi/config/reset/")

    # ── Steering config ────────────────────────────────────────────────────────

    def steering_config(self) -> WifiSteeringConfig:
        """Return the Wi-Fi band-steering configuration."""
        return WifiSteeringConfig._from_dict(self._client.get("wifi/steering/config/"))

    def set_steering_config(self, **kwargs: Any) -> WifiSteeringConfig:
        """Update the Wi-Fi band-steering configuration.

        Accepted keyword arguments: ``steering_level`` (0–2).
        """
        return WifiSteeringConfig._from_dict(self._client.put("wifi/steering/config/", json=kwargs))

    # ── Global state ───────────────────────────────────────────────────────────

    def state(self) -> list[WifiGlobalState]:
        """Return the Wi-Fi global state."""
        return [WifiGlobalState._from_dict(s) for s in self._client.get("wifi/state/")]

    # ── Access Points ──────────────────────────────────────────────────────────

    def aps(self) -> list[WifiAp]:
        """Return the list of Wi-Fi access points."""
        return [WifiAp._from_dict(ap) for ap in self._client.get("wifi/ap/")]

    def ap(self, ap_id: int) -> WifiAp:
        """Return the Wi-Fi access point with the given id."""
        return WifiAp._from_dict(self._client.get(f"wifi/ap/{ap_id}"))

    def set_ap(self, ap_id: int, **kwargs: Any) -> WifiAp:
        """Update the Wi-Fi access point with the given id."""
        return WifiAp._from_dict(self._client.put(f"wifi/ap/{ap_id}", json=kwargs))

    def ap_allowed_channel_combs(self, ap_id: int) -> list[WifiAllowedComb]:
        """Return allowed channel combinations for the given AP."""
        return [WifiAllowedComb._from_dict(c) for c in self._client.get(f"wifi/ap/{ap_id}/allowed_channel_comb")]

    def ap_stations(self, ap_id: int) -> list[WifiStation]:
        """Return the list of stations currently associated to the given AP."""
        return [WifiStation._from_dict(s) for s in self._client.get(f"wifi/ap/{ap_id}/stations/")]

    def ap_station(self, ap_id: int, mac: str) -> WifiStation:
        """Return a specific station associated to the given AP."""
        return WifiStation._from_dict(self._client.get(f"wifi/ap/{ap_id}/stations/{mac}"))

    def ap_channel_survey_history(self, ap_id: int, timestamp: int) -> list[WifiApChannelSurveyData]:
        """Return channel survey history for the given AP since *timestamp*."""
        return [
            WifiApChannelSurveyData._from_dict(s)
            for s in self._client.get(f"wifi/ap/{ap_id}/channel_survey_history/{timestamp}")
        ]

    def ap_neighbors(self, ap_id: int) -> list[WifiNeighbor]:
        """Return Wi-Fi neighbours detected by the given AP."""
        return [WifiNeighbor._from_dict(n) for n in self._client.get(f"wifi/ap/{ap_id}/neighbors/")]

    def ap_channel_usage(self, ap_id: int) -> list[WifiChannelUsage]:
        """Return per-channel usage statistics for the given AP."""
        return [WifiChannelUsage._from_dict(c) for c in self._client.get(f"wifi/ap/{ap_id}/channel_usage/")]

    def restart_ap(self, ap_id: int) -> None:
        """Restart the given AP (it will be briefly unavailable)."""
        self._client.post(f"wifi/ap/{ap_id}/restart")

    def scan_ap_neighbors(self, ap_id: int) -> None:
        """Trigger a neighbour scan on the given AP (AP will be briefly unavailable)."""
        self._client.post(f"wifi/ap/{ap_id}/neighbors/scan")

    # ── BSS ───────────────────────────────────────────────────────────────────

    def bss_list(self) -> list[WifiBss]:
        """Return the list of Wi-Fi BSSes."""
        return [WifiBss._from_dict(b) for b in self._client.get("wifi/bss/")]

    def bss(self, bss_id: str) -> WifiBss:
        """Return the Wi-Fi BSS with the given id."""
        return WifiBss._from_dict(self._client.get(f"wifi/bss/{bss_id}"))

    def set_bss(self, bss_id: str, **kwargs: Any) -> WifiBss:
        """Update the Wi-Fi BSS with the given id."""
        return WifiBss._from_dict(self._client.put(f"wifi/bss/{bss_id}", json=kwargs))

    # ── Planning ───────────────────────────────────────────────────────────────

    def planning(self) -> WifiPlanning:
        """Return the Wi-Fi scheduling plan."""
        return WifiPlanning._from_dict(self._client.get("wifi/planning/"))

    def set_planning(self, **kwargs: Any) -> WifiPlanning:
        """Update the Wi-Fi scheduling plan.

        Accepted keyword arguments: ``use_planning``, ``mapping``.
        """
        return WifiPlanning._from_dict(self._client.put("wifi/planning/", json=kwargs))

    # ── MAC Filters ────────────────────────────────────────────────────────────

    def mac_filters(self) -> list[WifiMacFilter]:
        """Return the list of Wi-Fi MAC filters."""
        return [WifiMacFilter._from_dict(f) for f in self._client.get("wifi/mac_filter/")]

    def mac_filter(self, filter_id: str) -> WifiMacFilter:
        """Return the Wi-Fi MAC filter with the given id."""
        return WifiMacFilter._from_dict(self._client.get(f"wifi/mac_filter/{filter_id}"))

    def add_mac_filter(self, mac: str, type: str, comment: str = "") -> WifiMacFilter:  # noqa: A002
        """Create a new Wi-Fi MAC filter entry."""
        return WifiMacFilter._from_dict(
            self._client.post("wifi/mac_filter/", json={"mac": mac, "type": type, "comment": comment})
        )

    def set_mac_filter(self, filter_id: str, **kwargs: Any) -> WifiMacFilter:
        """Update a Wi-Fi MAC filter entry.

        Accepted keyword arguments: ``comment``, ``type``.
        """
        return WifiMacFilter._from_dict(self._client.put(f"wifi/mac_filter/{filter_id}", json=kwargs))

    def delete_mac_filter(self, filter_id: str) -> None:
        """Delete the Wi-Fi MAC filter with the given id."""
        self._client.delete(f"wifi/mac_filter/{filter_id}")
