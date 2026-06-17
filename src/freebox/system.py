"""Freebox System API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class SystemSensor:
    """Thermal sensor."""

    id: str
    name: str
    value: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SystemSensor:
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            value=d.get("value", 0),
        )


@dataclass
class SystemFan:
    """Cooling fan."""

    id: str
    name: str
    value: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SystemFan:
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            value=d.get("value", 0),
        )


@dataclass
class SystemExpansion:
    """Expansion slot module."""

    slot: int
    probe_done: bool
    present: bool
    supported: bool
    type: str
    bundle: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SystemExpansion:
        return cls(
            slot=d.get("slot", 0),
            probe_done=d.get("probe_done", False),
            present=d.get("present", False),
            supported=d.get("supported", False),
            type=d.get("type", ""),
            bundle=d.get("bundle", ""),
        )


@dataclass
class SystemModelInfo:
    """Device model information."""

    name: str
    pretty_name: str
    has_expansions: bool
    has_lan_sfp: bool
    has_dect: bool
    has_home_automation: bool
    has_femtocell_exp: bool
    has_fixed_femtocell: bool
    has_vm: bool
    has_dsl: bool
    has_standby: bool
    has_eco_wifi: bool
    has_wop: bool
    has_led_strip: bool
    has_status_led: bool
    has_usb3_enable: bool
    has_lcd_screensaver: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SystemModelInfo:
        return cls(
            name=d.get("name", ""),
            pretty_name=d.get("pretty_name", ""),
            has_expansions=d.get("has_expansions", False),
            has_lan_sfp=d.get("has_lan_sfp", False),
            has_dect=d.get("has_dect", False),
            has_home_automation=d.get("has_home_automation", False),
            has_femtocell_exp=d.get("has_femtocell_exp", False),
            has_fixed_femtocell=d.get("has_fixed_femtocell", False),
            has_vm=d.get("has_vm", False),
            has_dsl=d.get("has_dsl", False),
            has_standby=d.get("has_standby", False),
            has_eco_wifi=d.get("has_eco_wifi", False),
            has_wop=d.get("has_wop", False),
            has_led_strip=d.get("has_led_strip", False),
            has_status_led=d.get("has_status_led", False),
            has_usb3_enable=d.get("has_usb3_enable", False),
            has_lcd_screensaver=d.get("has_lcd_screensaver", False),
        )


@dataclass
class SystemConfig:
    """Freebox system information (GET /system/)."""

    firmware_version: str
    mac: str
    serial: str
    uptime: str
    uptime_val: int
    board_name: str
    box_authenticated: bool
    disk_status: str
    usb3_enable: bool
    user_main_storage: str
    user_storage_powered: bool
    sensors: list[SystemSensor] = field(default_factory=list)
    fans: list[SystemFan] = field(default_factory=list)
    expansions: list[SystemExpansion] = field(default_factory=list)
    model_info: SystemModelInfo | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SystemConfig:
        model_raw = d.get("model_info")
        return cls(
            firmware_version=d.get("firmware_version", ""),
            mac=d.get("mac", ""),
            serial=d.get("serial", ""),
            uptime=d.get("uptime", ""),
            uptime_val=d.get("uptime_val", 0),
            board_name=d.get("board_name", ""),
            box_authenticated=d.get("box_authenticated", False),
            disk_status=d.get("disk_status", ""),
            usb3_enable=d.get("usb3_enable", False),
            user_main_storage=d.get("user_main_storage", ""),
            user_storage_powered=d.get("user_storage_powered", False),
            sensors=[SystemSensor._from_dict(s) for s in d.get("sensors", [])],
            fans=[SystemFan._from_dict(f) for f in d.get("fans", [])],
            expansions=[SystemExpansion._from_dict(e) for e in d.get("expansions", [])],
            model_info=SystemModelInfo._from_dict(model_raw) if model_raw else None,
        )


class System:
    """Freebox System API.

    Obtained via ``fb.system``::

        info = fb.system.config()
        print(info.firmware_version, info.uptime)

        fb.system.reboot()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> SystemConfig:
        """Return the current system information."""
        return SystemConfig._from_dict(self._client.get("system/"))

    def reboot(self) -> None:
        """Reboot the Freebox."""
        self._client.post("system/reboot/")

    def shutdown(self) -> None:
        """Shut down the Freebox."""
        self._client.post("system/shutdown/")
