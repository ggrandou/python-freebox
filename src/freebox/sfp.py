"""Freebox SFP API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class SfpStatus:
    """SFP port status (GET /sfp/status)."""

    present: bool
    eeprom_valid: bool
    supported: bool
    type: str
    power_good: bool
    link: bool
    vendor_name: str
    part_number: str
    hardware_rev: str
    serial_number: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SfpStatus:
        return cls(
            present=d.get("present", False),
            eeprom_valid=d.get("eeprom_valid", False),
            supported=d.get("supported", False),
            type=d.get("type", ""),
            power_good=d.get("power_good", False),
            link=d.get("link", False),
            vendor_name=d.get("vendor_name", ""),
            part_number=d.get("part_number", ""),
            hardware_rev=d.get("hardware_rev", ""),
            serial_number=d.get("serial_number", ""),
        )


@dataclass
class SfpConfig:
    """SFP port configuration (GET/PUT /sfp/config).

    ``available_sfp_types`` is read-only and is ignored by the Freebox on PUT.
    """

    sfp_type_forced: bool
    sfp_type_forced_value: str
    available_sfp_types: list[str] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SfpConfig:
        return cls(
            sfp_type_forced=d.get("sfp_type_forced", False),
            sfp_type_forced_value=d.get("sfp_type_forced_value", ""),
            available_sfp_types=d.get("available_sfp_types", []),
        )


class Sfp:
    """Freebox SFP API.

    Obtained via ``fb.sfp``::

        status = fb.sfp.status()
        print(status.present, status.type, status.link)

        config = fb.sfp.config()
        fb.sfp.set_config(sfp_type_forced=True, sfp_type_forced_value="copper_1g")
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def status(self) -> SfpStatus:
        """Return the current SFP port status."""
        return SfpStatus._from_dict(self._client.get("sfp/status"))

    def config(self) -> SfpConfig:
        """Return the current SFP port configuration."""
        return SfpConfig._from_dict(self._client.get("sfp/config/"))

    def set_config(self, **kwargs: Any) -> SfpConfig:
        """Update the SFP port configuration.

        Pass only the fields to change, e.g.
        ``set_config(sfp_type_forced=True, sfp_type_forced_value="copper_1g")``.
        The ``available_sfp_types`` field is read-only and will be ignored.
        """
        return SfpConfig._from_dict(self._client.put("sfp/config/", json=kwargs))
